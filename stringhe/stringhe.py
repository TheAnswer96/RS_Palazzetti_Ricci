import pandas as pd
import numpy as np
import scipy.sparse as sparse
import argparse
import implicit
import pickle
import os
#import textdistance
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
os.environ["OPENBLAS_NUM_THREADS"] = "1"

#Parametri: -db nome_database -u utente da raccomandare -n numero di raccomandazioni (opzionale, di default settato a 10) -t soglia per il valore
#di similarità (opzionale, di default settato a 65, se la similarità fra due nomi è superiore alla soglia quello con score minore viene eliminato)

#________________________________________________________________DEFINIZIONI FUNZIONI__________________________________________

"""
def get_jaccard_sim(str1, str2): 
    a = set(str1.split()) 
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c))
"""

def print_results(recommended_list):
    products_name = []
    scores = []
    products_id = []
    products_code = []
    asterics = []
    cat_code = []
    cat_name = []
    for item in recommended_list:
        idx, score = item

        #Retrieve dal dataframe data delle informazioni abbinate agli ID degli item raccomandati (per la stampa)
        products_id.append(data.ItemId.loc[data.item_id == idx].iloc[0])
        products_code.append(data.item_id.loc[data.item_id == idx].iloc[0])
        products_name.append(data.Name.loc[data.item_id == idx].iloc[0])
        cat_name.append(data.CatName.loc[data.item_id == idx].iloc[0])
        cat_code.append(data.CatCode.loc[data.item_id == idx].iloc[0])
        scores.append(score)

        #creazione del dataframe contenente tutte le informazioni per la stampa
        recommendations = pd.DataFrame({'products Id': products_id,'products code': products_code,'products name': products_name, 'Cat Code': cat_code,'Cat name': cat_name,'score': scores})

    print (recommendations)


def check(database, user):
    #Il campo DATABASE è obbligatorio, se non inserito termina con errore
    if(database is None):
        print('\x1b[0;31;40m' + 'Error 01.a - Missing Database' + '\x1b[0m')
        print('\x1b[0;31;40m' + 'Use -db to import Dataset and -u to select User' + '\x1b[0m')
        exit(0)
    #Cerca di leggere il file CSV, se non riesce restituisce errore e termina
    try:
        #print('Reading Data:')
        data = pd.read_csv(database, sep=';', dtype = str)
        #print('Done')
    except:
        print('\x1b[0;31;40m' + 'Dataframe Issue - Not Reading csv' + '\x1b[0m')
        exit(0)

    #Controlla se i nomi delle colonne sono quelli giusti.
    #Gli unici header obbligatori sono USERID, ITEMIT e QUANTITY, se non corrispondono tutti e tre
    #ad una delle colonne viene segnalato con un errore e il programma termina.
    #Non è rilevante l'ordine delle colonne, l'importante è che ci siano.
    #print('Check Columns:')
    headers = list(data.columns.values)
    check_nc = [0,0,0]
    for i in headers:
        if (i == 'UserId'):
            check_nc[0] = 1
        if (i == 'ItemId'):
            check_nc[1] = 1
        if (i == 'Quantity'):
            check_nc[2] = 1
    if(check_nc == [1,1,1]):
        #print('Done')
        print()
    else:
        print('\x1b[0;31;40m'+'Missing Column Reference'+'\x1b[0m')
        exit(0)
    
    #Controlla se l'USER può essere convertito in intero, se non è possibile termina con errore
    if(not(user is None)):
        try:
            us = user
        except:
            print('\x1b[0;31;40m'+'Error 02 - UserId must be an Integer Value'+'\x1b[0m')
            exit(0)
        #Se l'USER non è presente all'interno del DATABASE, solleva un errore e termina
        check = 0    
        for i in data['UserId']:
            if(i == us):
                check = 1
        if(check == 1):
            print('Found "UserId" with value', us,'...')
        #ELSE ELIMINATO PER FARE I TEST SU RECALCULATE USER, CI VUOLE IN CASI "NORMALI"
        else:
            print('\x1b[0;31;40m'+'Error 03 - User Not Found'+'\x1b[0m')
            exit(0)

    #Controlli di integrità terminati, restituisce il DATAFRAME data
    return(data)


#____________________________________________________________INIZIO ESECUZIONE____________________________________________________
#--------------------------------------------------------------- PARSERS ---------------------------------------------------------

parser = argparse.ArgumentParser()
parser.add_argument('-db','--database', help ='import database', type = str)
parser.add_argument('-u','--user', help ='select user', type=str)
parser.add_argument('-n','--number', help='number of recommendations per user', type=int, default=10)
parser.add_argument('-t','--threshold', help='similarity index threshold', type=int, default=65)
args = parser.parse_args()

#Richiama funzione check, che esegue controlli di integrità
raw_data = check(args.database, args.user)

us = args.user
n=args.number
threshold = args.threshold

#--------------------------------------------------------------------------------------------------------------------------------

#Assegna labels alle colonne di data
raw_data.columns = ['UserId', 'ItemId','Name','CatCode','CatName', 'Quantity']

#Rimuove missing values
data = raw_data.dropna()
data = data.copy()

data.sort_values(by=['ItemId']) #Ordina i item_id in ordine lessicografico

#Crea due nuove colonne user_id e item_id di tipo category.
#Sono valori interi ordinali (da 0 a num_elementi)
#Da qui in poi i valori di UserId e ItemId non vengono più utilizzati se non per stampe a schermo
data['UserId'] = data['UserId'].astype("category")
data['ItemId'] = data['ItemId'].astype("category")
data['user_id'] = data['UserId'].cat.codes
data['item_id'] = data['ItemId'].cat.codes
data.Quantity= data.Quantity.astype(int)

#data['Sum'] = data.groupby('ItemId').Quantity.transform(np.sum)
#data['Count'] = data.groupby('ItemId').Quantity.transform(func='count')
#data['ConsumptionRate'] = data.groupby('ItemId').Quantity.transform(np.mean)
#data['ratio'] = data.Quantity / data.ConsumptionRate


# The implicit library expects data as a item-user matrix so we create two matricies, one for fitting 
#the model (item-user) and one for recommendations (user-item)
#Il prototipo della funzione sparse.csr_matrix è: sparse.csr_matrix((data, (row_ind, col_ind)))
sparse_item_user_quantity = sparse.csr_matrix((data['Quantity'].astype(float), (data['item_id'], data['user_id'])))
sparse_user_item_quantity = sparse.csr_matrix((data['Quantity'].astype(float), (data['user_id'], data['item_id'])))

#sparse_item_user_consumption = sparse.csr_matrix((data['ratio'].astype(float), (data['item_id'], data['user_id'])))
#sparse_user_item_consumption = sparse.csr_matrix((data['ratio'].astype(float), (data['user_id'], data['item_id'])))

#-------------------------------------------------------------------------------------------------------------------------------
#Ricava il codice category assegnato all'utente us, ovvero quello passato come parametro
user_id = data.loc[data["UserId"] == us, "user_id"].iloc[0]
#print("Printing user_id : ",user_id)

#Ricava tutti gli oggetti acquistati dall'utente us, ovvero quello passato come parametro
#all_items_purchased = data.item_id.loc[data['user_id'] == user_id].tolist()
#print("All items purchased by user {}: \n".format(user_id), all_items_purchased)


#Ricava i nomi di tutti gli oggetti acquistati dall'utente us, ovvero quello passato come parametro
#all_items_purchased_name = data.Name.loc[data['user_id'] == user_id].tolist()
#print("All items purchased by user {} : \n".format(user_id), all_items_purchased_name)

#-------------------------------------ALLENAMENTO DEL MODELLO------------------------------------------------------------------

model = pickle.load(open("trained_model_fit.sav", 'rb'))
"""
print("Training model using quantity...")

#Si crea il modello, si allena con la matrice sparsa user_item
model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=30)
#print('\x1b[1;32;40m','Model Training ...' , '\x1b[0m')
model.fit(sparse_item_user_quantity)
pickle.dump(model, open("trained_model_fit.sav", 'wb'))
print("Done")
"""

print('Processing recommendations...')

#Si effettuano raccomandazioni utilizzando il modello
#Il prototipo è recommend(utente, matrice_user_item, numero di raccomandazioni, flag per utente/oggetto nuovo)
recommended = model.recommend(user_id, sparse_user_item_quantity, N=n*3, filter_already_liked_items=False)

item_name = []
#item_cat = []
score_list = []
final_list = []
final_list_score = []

for item in recommended:
    idx , score = item
    item_name.append(data.Name.loc[data.item_id == idx].iloc[0])
    #item_cat.append(data.CatName.loc[data.item_id == idx].iloc[0])
    score_list.append(score)

print()
print("recommendations before the cut:")
print()
print_results(recommended)

print()
print("Deleted items (and why):")
print()

#Utilizzando fuzz.token_sort_ratio l'ordine delle parole all'interno della stringa non conta.
#Per calcolare tenendo in considerazione ordine utilizzare fuzz.ratio

for i in item_name:
	if(len(final_list) ==  n):
		break
	to_delete = False
	for j in final_list:
		if(to_delete):
			break
		if(fuzz.token_sort_ratio(i,j)>threshold):
			to_delete = True
			print("Deleted",i,"( in position",item_name.index(i),") because too similar to",j," (similarity index (fuzzywazzy con token): ",fuzz.token_sort_ratio(i,j),")")
	if(not(to_delete)):
		final_list.append(i)
		final_list_score.append(score_list[item_name.index(i)])

print()
print("Final recommendations:")
print()

result_temp = []
result = []

for i in range(len(final_list)):
	result_temp.append((final_list[i],final_list_score[i]))
for i in result_temp:
	result.append(((data.item_id.loc[data.Name == i[0]].iloc[0]), i[1]))

print_results(result)

#print(final_list[i]," ",final_list_score[i])
