import pandas as pd
import numpy as np
import scipy.sparse as sparse
import argparse
import implicit
import os
import pickle

os.environ["OPENBLAS_NUM_THREADS"] = "1"

#________________________________________________________________DEFINIZIONI FUNZIONI__________________________________________

#Purchase_history serve solo per gli asterischi alla fine
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
    print('Check Columns:')
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
        print('Done')
    else:
        print('\x1b[0;31;40m'+'Missing Column Reference'+'\x1b[0m')
        exit(0)
    
    #Controlla se l'USER può essere convertito in intero, se non è possibile termina con errore
    if(not(user is None)):
        try:
            us = int(user)
        except:
            print('\x1b[0;31;40m'+'Error 02 - UserId must be an Integer Value'+'\x1b[0m')
            exit(0)
        #Se l'USER non è presente all'interno del DATABASE, solleva un errore e termina
        check = 0    
        for i in data['UserId']:
            if(int(i) == us):
                check = 1
        if(check == 1):
            print('Found "UserId" With Value', us,'...')
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
parser.add_argument('-u','--user', default = None , help ='select user', type=str)
args = parser.parse_args()

#Richiama funzione check, che esegue controlli di integrità
raw_data = check(args.database, args.user)

us = args.user


#--------------------------------------------------------------------------------------------------------------------------------

#Assegna labels alle colonne di data
#raw_data.columns = ['UserId', 'ItemId','Name','CatCode','CatName', 'Quantity']
raw_data.columns = ['UserId', 'ItemId','Name', 'Quantity']
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

data['Sum'] = data.groupby('ItemId').Quantity.transform(np.sum)
data['Count'] = data.groupby('ItemId').Quantity.transform(func='count')
data['ConsumptionRate'] = data.groupby('ItemId').Quantity.transform(np.mean)
data['ratio'] = data.Quantity / data.ConsumptionRate


# The implicit library expects data as a item-user matrix so we create two matricies, one for fitting 
#the model (item-user) and one for recommendations (user-item)
#Il prototipo della funzione sparse.csr_matrix è: sparse.csr_matrix((data, (row_ind, col_ind)))
sparse_item_user_quantity = sparse.csr_matrix((data['Quantity'].astype(float), (data['item_id'], data['user_id'])))
sparse_user_item_quantity = sparse.csr_matrix((data['Quantity'].astype(float), (data['user_id'], data['item_id'])))

sparse_item_user_consumption = sparse.csr_matrix((data['ratio'].astype(float), (data['item_id'], data['user_id'])))
sparse_user_item_consumption = sparse.csr_matrix((data['ratio'].astype(float), (data['user_id'], data['item_id'])))






if (not(us is None)):

    #-------------------------------------------------------------------------------------------------------------------------------
    #Ricava il codice category assegnato all'utente us, ovvero quello passato come parametro
    user_id = data.loc[data["UserId"] == us, "user_id"].iloc[0]
    #print("Printing user_id : ",user_id)

    #Ricava tutti gli oggetti acquistati dall'utente us, ovvero quello passato come parametro
    all_items_purchased = data.item_id.loc[data['user_id'] == user_id].tolist()
    #print("All items purchased by user {}: \n".format(user_id), all_items_purchased)


    #Ricava i nomi di tutti gli oggetti acquistati dall'utente us, ovvero quello passato come parametro
    all_items_purchased_name = data.Name.loc[data['user_id'] == user_id].tolist()
    print("All items purchased by user {} : \n".format(user_id), all_items_purchased_name)

    #-------------------------------------ALLENAMENTO DEL MODELLO------------------------------------------------------------------

    print("Training model using quantity...")

    #Si crea il modello, si allena con la matrice sparsa user_item
    model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=30)
    #print('\x1b[1;32;40m','Model Training ...' , '\x1b[0m')
    model.fit(sparse_item_user_quantity)

    print("Done")



    print('Recommending (using quantity) to user: ', us)

    #Si effettuano raccomandazioni utilizzando il modello
    #Il prototipo è recommend(utente, matrice_user_item, numero di raccomandazioni, flag per utente/oggetto nuovo)
    recommended = model.recommend(user_id, sparse_user_item_quantity, N=10, filter_already_liked_items=False)

    #Recommended: lista di tuple(int64, float32)
    #INSERITI I VALORI REALI DI UserId E user_id
    print("Recommended for userId "+str(us)+" (as user_id "+str(user_id), recommended)


    #Chiama print_result, all_items_purchased serve per verificare se un oggetto è già stato acquistato da questo utente
    print_results(recommended)


    #Raccomandazioni consumption

    print("Training model using consumption rate ratio...")

    model.fit(sparse_item_user_consumption)

    print("Done")


    print('Recommending (using consumption rate ratio) to user: ', us)

    #Si effettuano raccomandazioni utilizzando il modello
    #Il prototipo è recommend(utente, matrice_user_item, numero di raccomandazioni, flag per utente/oggetto nuovo)
    recommended_cons = model.recommend(user_id, sparse_user_item_consumption, N=10, filter_already_liked_items=False)

    #Recommended: lista di tuple(int64, float32)
    #INSERITI I VALORI REALI DI UserId E user_id
    print("Recommended for userId "+str(us)+" (as user_id "+str(user_id), recommended_cons)


    #Chiama print_result, all_items_purchased serve per verificare se un oggetto è già stato acquistato da questo utente
    print_results(recommended_cons)

    items_quantity = []
    items_consumption = []
    items_quantity_code = []
    items_consumption_code = []

    pos=0
    for i in recommended:
        pos = pos + 1
        items_quantity.append((i[0], pos))
        items_quantity_code.append(i[0])

    pos=0
    for i in recommended_cons:
        pos = pos + 1
        items_consumption.append((i[0], pos))
        items_consumption_code.append(i[0])

    items_quantity_set = set(items_quantity)
    items_consumption_set = set(items_consumption)

    items_quantity_code_set = set(items_quantity_code)
    items_consumption_code_set = set(items_consumption_code)

    intersection = items_quantity_code_set.intersection(items_consumption_code_set)
    print("Intersection: ",intersection)
    print("Percentage: ", len(intersection)/len(items_quantity)*100,"%")

    intersection_rank = items_quantity_set.intersection(items_consumption_set)
    print("Intersection (with rank): ",intersection_rank)
    print("Percentage: ", len(intersection_rank)/len(items_quantity)*100,"%")

    for i in intersection:
        print("Item: ",i," rank in recommended_quantity: ",items_quantity_code.index(i)+1," rank in recommended_cons: ",items_consumption_code.index(i)+1)






else:

    print("Training model using quantity...")

    #NUMERO RACCOMANDAZIONI
    Num_rec = 30
    #Si crea il modello, si allena con la matrice sparsa user_item
    model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=30)
    #print('\x1b[1;32;40m','Model Training ...' , '\x1b[0m')
    #NORMAL FORM
    #model.fit(sparse_item_user_quantity)
    #INVERTED FORM
    model.fit(sparse_user_item_quantity)

    print("Done")

    print('Recommending (using quantity)')

    #Si effettuano raccomandazioni utilizzando il modello
    #Il prototipo è recommend(utente, matrice_user_item, numero di raccomandazioni, flag per utente/oggetto nuovo)
    #NORMAL FORM
    #recommended = model.recommend_all(sparse_user_item_quantity, N=Num_rec, filter_already_liked_items=False)
    #INVERTED FORM
    recommended = model.recommend_all(sparse_item_user_quantity, N=Num_rec, filter_already_liked_items=False)
    #Raccomandazioni consumption

    print("Training model using consumption rate ratio...")

    #model.fit(sparse_item_user_consumption)
    #INVERTED FORM
    model.fit(sparse_user_item_consumption)

    print("Done")


    print('Recommending (using consumption rate ratio)')

    #Si effettuano raccomandazioni utilizzando il modello
    #Il prototipo è recommend(utente, matrice_user_item, numero di raccomandazioni, flag per utente/oggetto nuovo)
    #NORMAL FORM
    #recommended_cons = model.recommend_all(sparse_user_item_consumption, N=Num_rec, filter_already_liked_items=False)
    #INVERTED FORM
    recommended_cons = model.recommend_all(sparse_item_user_consumption, N=Num_rec, filter_already_liked_items=False)

    num_intersections = 0
    num_intersections_rank = 0
    SPercRow = 0
    listofper = []

    for i in range(len(recommended)):
        intersection = set(recommended[i]).intersection(set(recommended_cons[i]))
        num_intersections = num_intersections+len(intersection)
        intersection_rank = [j for j, k in zip(recommended[i], recommended_cons[i]) if j == k]
        SPercRow = len(intersection) * 100 / Num_rec
        #INSERISCO TUTTE LE PERCENTUALI SU UNA LISTA PER LAVORARCI MEGLIO DOPO
        listofper.append(SPercRow) 
        num_intersections_rank = num_intersections_rank +  len(intersection_rank)


    SPerCount = 0
    uniqueValue = set(listofper)
    listofuserid = []
    #res = open("risultati_comp_interrank_superfit1.txt","w+")

    #res.write("-------------------------------- RISULTATI_COMPARISON_INTERSECTIONRANK -------------------------\n")
    """

    	scorro tutti i valori percentuali di intersezione che ho calcolato precedentemente, per poi andare
    	a calcolare il numero di utenti che appartengono a quella percentuale. La posizione ricoperta all'
    	interno di listofper (che sta listadellepercentualiperogniutente) indica l'user_id dell'utente a cui
    	è associata tale percentuale. Una volta preso quell'indice calcolo il vero codice e ottengo la lista
    	degli utenti reali che ha intersezione di tot% fra modello con quantity e modello con consumption.

    """

    for value in uniqueValue:
    	listofuserid = []
    	SPerCount = 0
    	#res.write("\n----------------------------------------------------\n")
    	#res.write("****************************************************\n")
    	#res.write("Evaluation of how many " + str(value) + " percentage there are\n")
    	for index in range(len(listofper)):
    		if(value == listofper[index]):
    			SPerCount = SPerCount + 1
    			user_id = data.loc[data["item_id"] == index, "ItemId"].iloc[0]
    			listofuserid.append(user_id)
    	print("Percentage ", value ," repeat N. ", SPerCount, " Times( ", SPerCount * 100 / len(listofper),"% compare with the total length )")
    	#print("ID with the before Percentage are ", listofuserid)
    	#res.write("Percentage " + str(value) + " reapet N. " + str(SPerCount) + " Times( " + str((SPerCount * 100 / len(listofper))) +"% compare with the total length )\n")
    	#res.write("ID with the before Percentage are " + ' '.join(listofuserid))
    	print("----------------------------------------------------")

    print("Percentage: ", num_intersections/(len(recommended)*Num_rec)*100,"%")
    print("Percentage with same rank: ",num_intersections_rank/(len(recommended)*Num_rec)*100,"%")