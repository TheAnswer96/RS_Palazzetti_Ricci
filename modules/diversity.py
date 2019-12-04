# -----------------------------------------------------------
# Dato un dataset ed una lista di oggetti restituisce la diversity di questa lista.
#
# Prototipo di chiamata del metodo:
# calculate_diversity("nome_database.csv", [lista, di, oggetti])
# -----------------------------------------------------------

import pandas as pd
import scipy.sparse as sparse
import implicit
import numpy as np
import os
import scipy.special
from pathlib import Path

def check(db,items_list):
	if db is None or items_list is None:
		print("Error - database path and item list required")
		exit(0)
	if not (type(items_list) == list):
		print("Error - the item list must be a list")
		exit(0)

	try:
		data = pd.read_csv(db, sep=';', dtype = str)
	except:
		print('Error - database not found in inserted path')
	exit(0)

	setId = set(data.ItemId)
	for item in items_list:
		if not(str(item) in setId):
			print("Error - the list contains an ID not belonging in the database")
			exit(0)


def calculate_diversity(database, item_list):

	os.environ["OPENBLAS_NUM_THREADS"] = "1"
	#Nasconde il warning 'A value is trying to be set on a copy of a slice from a DataFrame.'
	pd.set_option('mode.chained_assignment', None)


	#Richiama funzione check, che esegue controlli di integrità
	check(database, item_list)

	data = pd.read_csv(database, sep=';', dtype = str)
	data['UserId'] = data['UserId'].astype("category")
	data['ItemId'] = data['ItemId'].astype("category")
	data['user_id'] = data['UserId'].cat.codes
	data['item_id'] = data['ItemId'].cat.codes
	data.Quantity= data.Quantity.astype(int)



	print("Training model...")

	sparse_item_user = sparse.csr_matrix((data['Quantity'].astype(float), (data['item_id'], data['user_id'])))
	sparse_user_item = sparse.csr_matrix((data['Quantity'].astype(float), (data['user_id'], data['item_id'])))

	#Ricava il numero totale di oggetti nel dataset
	numero_oggetti = len(set(data.ItemId.tolist()))
	insieme = set()

	model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=30, use_gpu= False)
	model.fit(sparse_item_user)

	print("Processing diversity...")

	for item in item_list:
		item = int(item)

	item_list_code = []
	recommended = []

	#Numero di raccomandazioni per utente in recommend_all, viene settato al numero totale di oggetti perchè vogliamo tutte le corrispondenze
	n = len(set(data.ItemId.tolist()))

	#Ricava ID category degli oggetti facenti parte della lista
	for i in item_list:
		item_list_code.append(data.loc[data["ItemId"] == str(i), "item_id"].iloc[0])

	obj = 0
	sum_sim = 0
	while len(item_list_code) > 1:
		#Finchè ci sono elementi nella lista degli oggetto, faccio pop uno alla volta ed effettuo confronto con tutti gli altri ancora nella lista
	    idx = item_list_code.pop(0)
	    print("Current list: ",item_list_code)
	    ls_similar_items = model.similar_items(idx , N=n)
	    #Effettuo confronto a coppie, SCOMMENTARE I PRINT PER VEDERE VALORI PARZIALI
	    for j in item_list_code:
	        #print("Comparing ",idx,"(",data.loc[data["item_id"] == idx, "ItemId"].iloc[0],") and ",j,"(",data.loc[data["item_id"] == j, "ItemId"].iloc[0],")")
	        found = False
	        i = 0
	        while i < n and found != True:
	            if ls_similar_items[i][0] == j:
	                found = True
	                obj = ls_similar_items[i][1]
	                #print("Match found in position ",i," with score ",obj)
	                #Se lo score è maggiore di 1 viene considerato 1, stessa cosa per -1
	                if obj > 1:
	                    obj = 1
	                elif obj < -1:
	                    obj = -1
	                #Contatore che contiene la somma parziale della similarità di tutte le coppie
	                sum_sim = sum_sim + obj
	                #print("Similarity between the two items: ", obj)
	            i = i + 1
	        #print("-----------------")
	print("-------------------------------------------------------------------")
	#La similarità sarà il valore del contatore / il numero totale di confronti effettuati
	similarity = sum_sim / scipy.special.comb(len(item_list), 2, exact = True)
	print("Similarity of items belonging in the list: ",similarity)
	#La diversity è (1 - similarity)
	diversity = 1 - similarity
	print("Diversity of items belonging in the list: ",diversity)
