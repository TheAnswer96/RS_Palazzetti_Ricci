import pandas as pd
import scipy.sparse as sparse
import argparse
import implicit
import os
import pickle
import numpy as np

#IMPEDISCE MULTITHREADING (??????)
os.environ["OPENBLAS_NUM_THREADS"] = "1"

#________________________________________________________________DEFINIZIONI FUNZIONI__________________________________________

#Purchase_history serve solo per gli asterischi alla fine
def print_results(recommended_list, purchase_history):
    scores = []
    user_id = []
    user_code = []
    #asterics = []
    for user in recommended_list:
        idx, score = user
        #L'asterisco mostra se l'oggetto in questione è già stato acquistato da questo utente
        #if idx in purchase_history:
        #    asterics.append("*")
        #else:
        #    asterics.append("-")

        #Retrieve dal dataframe data delle informazioni abbinate agli ID degli item raccomandati (per la stampa)
        user_id.append(int(data.UserId.loc[data.user_id == idx].iloc[0]))
        user_code.append(data.user_id.loc[data.user_id == idx].iloc[0])
        scores.append(score)

        #creazione del dataframe contenente tutte le informazioni per la stampa
        recommendations = pd.DataFrame({'UserId': user_id,'user_id': user_code, 'score': scores})

    print (recommendations)


    #Stampa una lista contenente i user_id raccomandati
    """
    print("-------------------------------------")
    print(user_id)
    print("-------------------------------------")
    """

def check(database, item, algo):
    #Il campo DATABASE è obbligatorio, se non inserito termina con errore
    if(database is None):
        print('\x1b[0;31;40m' + 'Error 01.a - Missing Database' + '\x1b[0m')
        print('\x1b[0;31;40m' + 'Use -db to import Dataset and -u to select User' + '\x1b[0m')
        exit(0)
    #Il campo USER è obbligatorio, se non inserito termina con errore
    elif(item is None):
        print('\x1b[0;31;40m' + 'Error 01.b - Missing ItemId' + '\x1b[0m')
        print('\x1b[0;31;40m' + 'Use -db to import Dataset and -i to select Item' + '\x1b[0m')
        exit(0)
    #Cerca di leggere il file CSV, se non riesce restituisce errore e termina
    try:
        print('\x1b[1;32;40m','Reading Data:', '\x1b[0m')
        data = pd.read_csv(database, sep=';', dtype = str)
        print('\x1b[1;32;40m','Done','\x1b[0m')
    except:
        print('\x1b[0;31;40m' + 'Dataframe Issue - Not Reading csv' + '\x1b[0m')
        exit(0)

    #Controlla se i nomi delle colonne sono quelli giusti.
    #Gli unici header obbligatori sono USERID, ITEMIT e QUANTITY, se non corrispondono tutti e tre
    #ad una delle colonne viene segnalato con un errore e il programma termina.
    #Non è rilevante l'ordine delle colonne, l'importante è che ci siano.
    print('\x1b[1;32;40m','Check Columns:' , '\x1b[0m')
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
        print('\x1b[1;32;40m','Done','\x1b[0m')
    else:
        print('\x1b[0;31;40m'+'Missing Column Reference'+'\x1b[0m')
        exit(0)
    
    #Controlla se l'USER può essere convertito in intero, se non è possibile termina con errore
    try:
        it = int(item)
    except:
        print('\x1b[0;31;40m'+'Error 02 - ItemId must be an Integer Value'+'\x1b[0m')
        exit(0)
    
    #Se l'USER non è presente all'interno del DATABASE, solleva un errore e termina
    check = 0    
    for i in data['ItemId']:
        if(int(i) == it):
            check = 1
    if(check == 1):
        print('\x1b[1;32;40m' + 'Found "ItemId" With Value', it,'...'+ '\x1b[0m')
    #ELSE ELIMINATO PER FARE I TEST SU RECALCULATE USER, CI VUOLE IN CASI "NORMALI"
    #else:
        #print('\x1b[0;31;40m'+'Error 03 - Item Not Found'+'\x1b[0m')
        #exit(0)

    #In base all'algoritmo inserito come parametro, assegna il valore alla variabile alg
    #e stampa a schermo.
    if(algo == None or algo == 'ALS_u'):
        alg = 'ALS_u'
        print('\x1b[1;32;40m' + 'Using Algorithm:', alg,'...' + '\x1b[0m')
    elif(algo == 'ALS_i'):
        alg = 'ALS_i'
        print('\x1b[1;32;40m' + 'Using Algorithm:', alg,'...' + '\x1b[0m')
    elif(algo == 'BPR_u'):
        alg = 'BPR_u'
        print('\x1b[1;32;40m' + 'Using Algorithm:', alg,'...' + '\x1b[0m')
    elif(algo == 'BPR_i'):
        alg = 'BPR_i'
        print('\x1b[1;32;40m' + 'Using Algorithm:', alg,'...' + '\x1b[0m')
    elif(algo == 'HYB'):
        alg = 'HYB'
        print('\x1b[1;32;40m' + 'Using Algorithm:', alg,'...' + '\x1b[0m')
    else:
        print('\x1b[0;31;40m' + 'Error 04 - Unrecognised Algorithm' + '\x1b[0m')

    #Controlli di integrità terminati, restituisce il DATAFRAME data
    return(data)

#____________________________________________________________INIZIO ESECUZIONE____________________________________________________
#--------------------------------------------------------------- PARSERS ---------------------------------------------------------
print('\n','\033[1m','\x1b[6;30;42m', "RecSys Framework v0.7", '\x1b[0m')
parser = argparse.ArgumentParser()
parser.add_argument('-db','--database', help ='import database', type = str)
parser.add_argument('-alg','--algorithm', help ='choose algorithm, ALS_u, ALS_i, BYS_u, BYS_i , HYB; Default = ALS_u', type = str)
parser.add_argument('-i','--item', help ='select item')
args = parser.parse_args()

#Richiama funzione check, che esegue controlli di integrità
raw_data = check(args.database, args.item, args.algorithm)

it = args.item

#--------------------------------------------------------------------------------------------------------------------------------
#In base al nome del database considerato, assegna un nome diverso al modello allenato risultante (MANCA UN DEFAULT!!!)
if(args.database == "db_full_fit_EN.csv"):
    filename = 'trained_model_fit_it.sav'
if(args.database == "db_full_out_EN.csv"):
    filename = 'trained_model_out.sav'
if(args.database == "db_full_super_EN.csv"):
    filename = 'trained_model_super.sav'

print("the trained models is : ", filename)
#Carico il modello già allenato in precedenza (Commentare se il modello non è ancora stato allenato in modo da farlo)
model = pickle.load(open(filename, 'rb'))
#--------------------------------------------------------------------------------------------------------------------------------
print("Printing ItemId: ", it)

#Assegna labels alle colonne di data
raw_data.columns = ['UserId', 'ItemId','Name','CatCode','CatName', 'Quantity']

#Rimuove missing values
data = raw_data.dropna()
data = data.copy()

print(data.sort_values(by=['UserId'])) #Ordina i item_id in ordine lessicografico, male male

#Per aggiungere elementi al dataset in maniera manuale
#data_append=pd.DataFrame({"UserId": ["842024"], "ItemId":["922965912"], "Name": ["PRO50+ CIOCCOLATO BIANCO 50G"], "CatCode": ["4AA2F16"], "CatName": ["SPORT"], "Quantity": ["5"]})
#data_append2=pd.DataFrame({"UserId": ["842024"], "ItemId":["903205437"], "Name": ["COMPETITION ARANCIA ROSSA 500G"], "CatCode": ["4AA2F16"], "CatName": ["SPORT"], "Quantity": ["6"]})
#data_append3=pd.DataFrame({"UserId": ["920150"], "ItemId":["999999999"], "Name": ["NON ESISTO"], "CatCode": ["ZZZZ"], "CatName": ["NON ESISTO"], "Quantity": ["1"]})
#frames = [data, data_append3]
#data=pd.concat(frames, ignore_index=True)

#Crea due nuove colonne user_id e item_id di tipo category.
#Sono valori interi ordinali (da 0 a num_elementi)
#Da qui in poi i valori di UserId e ItemId non vengono più utilizzati se non per stampe a schermo
data['UserId'] = data['UserId'].astype("category")
data['ItemId'] = data['ItemId'].astype("category")
data['user_id'] = data['UserId'].cat.codes
data['item_id'] = data['ItemId'].cat.codes
data.Quantity= data.Quantity.astype(int)

# The implicit library expects data as a item-user matrix so we create two matricies, one for fitting 
#the model (item-user) and one for recommendations (user-item)
#Il prototipo della funzione sparse.csr_matrix è: sparse.csr_matrix((data, (row_ind, col_ind)))
sparse_item_user = sparse.csr_matrix((data['Quantity'].astype(float), (data['item_id'], data['user_id'])))
sparse_user_item = sparse.csr_matrix((data['Quantity'].astype(float), (data['user_id'], data['item_id'])))

#-------------------------------------------------------------------------------------------------------------------------------
#Ricava il codice category assegnato all'utente us, ovvero quello passato come parametro
item_id = data.loc[data["ItemId"] == it, "item_id"].iloc[0]
print("Printing item_id : ",item_id)

print("Printing item name: ", data.loc[data["ItemId"] == it, "Name"].iloc[0])
print("Printing item category name: ", data.loc[data["ItemId"] == it, "CatName"].iloc[0])
print("Printing item category code: ", data.loc[data["ItemId"] == it, "CatCode"].iloc[0])

#Ricava tutti gli oggetti acquistati dall'utente us, ovvero quello passato come parametro
all_user_buyers = data.user_id.loc[data['item_id'] == item_id].tolist()
print("All users buying {}: \n".format(item_id), all_user_buyers)

#-------------------------------------ALLENAMENTO DEL MODELLO------------------------------------------------------------------

#Se l'algoritmo scelto dall'utente è del tipo ALS, viene allenato il modello qui sotto
if(args.algorithm == 'ALS_u' or args.algorithm == 'ALS_i' or args.algorithm is None):

    #factors: numero di fattori latenti delle due matrici risultanti dalla fattorizzazione
    #regularization: valore di lambda all'interno della formula dei modelli latent factors
    #iterations: numero di epoche
    #use_gpu: NON FUNZIONANTE (C++ not found)
    #Decommentare per allenare il modello

    #Si crea il modello, si allena con la matrice sparsa user_item e si salva il modello con un dump di pickle
    #model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=30, use_gpu= False)
    #print('\x1b[1;32;40m','Model Training ...' , '\x1b[0m')
    #model.fit(sparse_user_item)
    #pickle.dump(model, open(filename, 'wb'))

    #------------------------------------------------------ 1st Method - User Based --------------------------------------------
    if(args.algorithm == 'ALS_u' or args.algorithm is None):

        print('\x1b[1;32;40m' , 'ALS_u: ', it ,' (as item_id', item_id ,')', '\x1b[0m')

        #Si effettuano raccomandazioni utilizzando il modello
        #Il prototipo è recommend(utente, matrice_user_item, numero di raccomandazioni, flag per utente/oggetto nuovo)
        recommended = model.recommend(item_id, sparse_item_user, N=10, recalculate_user=False)
        
        #Recommended: lista di tuple(int64, float32)
        print("Recommended for itemId "+str(it)+" (as item_id "+str(item_id), recommended)

        #Chiama print_result, all_items_purchased serve per verificare se un oggetto è già stato acquistato da questo utente
        print_results(recommended, all_user_buyers)


        """
        #Stampa un dataframe contenente gli acquisti effettuati dagli utenti simili a quelli (best 3) che hanno comprato l'oggetto inserito
        #come parametro (PER TESTING)
        for i in recommended:
	        idx, score = i
	        x = []
	        x.append((idx, data.loc[data['user_id'] == idx, "UserId"].iloc[0], data.loc[data['user_id'] == idx, "Name"].tolist(), data.loc[data['user_id'] == idx, "Quantity"].tolist(), data.loc[data['user_id'] == idx, "CatName"].tolist()))        
	        us_id = []
	        UsId = []
	        ItName = []
	        Cat = []
	        Qty = []
	        for element in x:
	            idx, idr, name, quantity, cat = element
	            for i in range(len(name)):
	                us_id.append(idx)
	                UsId.append(int(idr))
	                ItName.append(name[i])
	                Cat.append(cat[i])
	                Qty.append(quantity[i])
	            print(pd.DataFrame({'user_id': us_id,'UserId': UsId, 'Product Name': ItName, "Quantity": Qty, 'Category Name': Cat}))
	            print('\n')
	    """
		


    #------------------------------------------------------ 2nd Method - Item Based -----------------------------------------------------------------
    if(args.algorithm == 'ALS_i'):
    #-------------------------------------------------------- FINDING 3 BEST ITEMS --------------------------------------------------------------
        #NON SERVE, GIA' DEFINITO
        #user_id = data.loc[data["UserId"] == us, "user_id"].iloc[0]

        #Ricava tutte le righe riguardanti l'utente in questione
        best_df = data.loc[data['item_id'] == item_id]
        #Ordina le righe in base alla quantità acquistata (in ordine discendente), poi prende i top 3
        best_df = best_df.sort_values(by='Quantity', ascending=False)
        best_df2 = best_df['user_id'].head(3)
        best_users = best_df2.tolist()
        print('best 3 users : ',best_users)

        #-----------------------------------------------TROVARE OGGETTI SIMILI AI BEST 3-----------------------------------------------------------

        #Viene creato il dizionario
        rec_users= {}
        if(best_users is not None):
            for i in best_users:
                recommendations = model.similar_items(i,11)
                #Non si prende in considerazione il primo risultato in quanto è l'oggetto stesso                
                recommendations = recommendations[1:]
                #recommendations è lista di tuple, formate da (int64, float32)
                print('ALS_i recommendations for best user {}'.format(i), recommendations)

                #Se l'oggetto è già presente nella lista dei consigliati, il suo score viene sommato a quello già presente
                for i in recommendations:
                    idx, score = i

                    if not idx in rec_users:
                        rec_users[idx] = score
                    else:
                        temp = rec_users[idx] + score
                        #PERCHE' QUESTA NORMALIZZAZIONE SI FA SOLO NELL'ITEM BASED E NON NELL'USER BASED?
                        rec_users[idx] =  min(temp, 1)

                    
                    """
                    #Stampa un dataframe contenente gli acquisti effettuati dagli utenti simili a quelli (best 3) che hanno comprato l'oggetto inserito
                    #come parametro (PER TESTING)
                    x = []
                    x.append((idx, data.loc[data['user_id'] == idx, "UserId"].iloc[0], data.loc[data['user_id'] == idx, "Name"].tolist(), data.loc[data['user_id'] == idx, "Quantity"].tolist(), data.loc[data['user_id'] == idx, "CatName"].tolist()))          
                    us_id = []
                    UsId = []
                    ItName = []
                    Cat = []
                    Qty = []
                    for element in x:
                        idx, idr, name, quantity, cat = element
                        for i in range(len(name)):
                            us_id.append(idx)
                            UsId.append(int(idr))
                            ItName.append(name[i])
                            Cat.append(cat[i])
                            Qty.append(quantity[i])
                        print(pd.DataFrame({'user_id': us_id,'UserId': UsId, 'Product Name': ItName, "Quantity": Qty, "Category Name": Cat}))
                        print('\n')
                    """
                    

        #Ordina gli oggetti raccomandati in ordine decrescente in base al valore di score
        rec_sorted_users = sorted(rec_users.items(), key=lambda key_value : -key_value[1])
        #Stampa i primi 10
        n_recommendations = 10
        final_recommended_users = rec_sorted_users[:n_recommendations]
        print("First "+str(n_recommendations)+" sorted d_users:",final_recommended_users)
        print("Recommended users based on 3 best users : \n")
        
        #Chiama print_result, all_items_purchased serve per verificare se un oggetto è già stato acquistato da questo utente
        print_results(final_recommended_users, all_user_buyers)
