# -----------------------------------------------------------
# Dato un dataset ed il numero di raccomandazioni da generare per ogni utente
# restituisce la coverage del modello allenato utilizzando tale dataset.
#
# Prototipo di chiamata del programma:
# python coverage standalone.py -db nome_dataset.csv -n numero_raccomandazioni
# -----------------------------------------------------------

import pandas as pd
import scipy.sparse as sparse
import implicit
import argparse
import numpy as np
import os
import scipy.special

#Prototipo di chiamata del programma:
#python coverage_standalone.py -db (nome database) -n (numero di raccomandazioni per utente)
#Esempio: python coverage_standalone.py -db db_1.csv -n 10

def check(db,rank):
	if db is None or rank is None:
		print("Error - Database path and number of recommendations per user required")
		Exit(0)
	else:
		try:
			rank = int(rank)
		except:
			print("Error - the number of recommendations per user must be an integer")
			exit(0)


		try:
			data = pd.read_csv(db, sep=';', dtype = str)
		except:
			print('Error - database not found in inserted path')
	    	exit(0)

		num_item = len(set(data.UserId))
		if rank > num_item:
			print("Error - the number of recommendations per user must be lower than the total number of items (",num_item,")")
			exit(0)


#Nasconde il warning 'A value is trying to be set on a copy of a slice from a DataFrame.'
pd.set_option('mode.chained_assignment', None)

parser = argparse.ArgumentParser()
parser.add_argument('-db','--database', help ='import database', type = str)
parser.add_argument('-n','--rank', help ='insert number of recommendations per user', type = str)

args = parser.parse_args()

#Esegue controlli sugli argomenti passati alla funzione, se si verificano problemi il programma termina restituendo un messaggio di errore
check(args.database, args.rank)

#Importazione del database e creazione delle colonne category di users ed items
data = pd.read_csv(args.database, sep=';', dtype = str)
data['UserId'] = data['UserId'].astype("category")
data['ItemId'] = data['ItemId'].astype("category")
data['user_id'] = data['UserId'].cat.codes
data['item_id'] = data['ItemId'].cat.codes
data.Quantity= data.Quantity.astype(int)
recommendations_number = int(args.rank)


print("Training model...")

sparse_item_user = sparse.csr_matrix((data['Quantity'].astype(float), (data['item_id'], data['user_id'])))
sparse_user_item = sparse.csr_matrix((data['Quantity'].astype(float), (data['user_id'], data['item_id'])))

#Ricava il numero totale di oggetti nel dataset
numero_oggetti = len(set(data.ItemId.tolist()))
insieme = set()

model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=30, use_gpu= False)
model.fit(sparse_item_user)
	
print("Processing coverage...")

#Esegue N raccomandazioni per tutti gli utenti
recommended_all = model.recommend_all(sparse_user_item , N = recommendations_number)

#Aggiunge all'insieme ogni oggetto nuovo che incontra
for row in recommended_all:
	for column in row:
		insieme.add(column)

#La coverage è data dalla dimensione dell'insieme / il numero totale di oggetti nel dataset (*100 per avere il valore in percentuale)
coverage = len(insieme)/numero_oggetti*100

print("Coverage: ",coverage,"%")
