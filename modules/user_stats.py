# -----------------------------------------------------------
# Dato un dataset ed una lista di utenti restituisce informazioni su di essi.
#
# Prototipo di chiamata del metodo:
# print_user_stats("nome_dataset.csv", [lista, di, id, utenti])
# -----------------------------------------------------------

import pandas as pd
import math
import scipy.stats as sp
from sklearn import preprocessing
from progressbar import ProgressBar
import matplotlib.pyplot as plt

#Prototipo di chiamata del metodo:
#print_user_stats((path database), (lista utenti))
#Esempio: print_user_stats(db_1.csv, [908943, 1055485])

#Removes the 'A value is trying to be set on a copy of a slice from a DataFrame.' warning
pd.set_option('mode.chained_assignment', None)

def Entropy(Items, tot):
	somma = 0
	prob = 0
	for item in Items:
		prob = int(item) / tot
		somma = somma - prob * math.log(prob,2)
	return somma

def GiniIndex(Items, tot):
	somma = 0
	prob = 0
	for item in Items:
		prob = int(item) / tot
		somma = somma + prob**2
	return 1 - somma

pbar = ProgressBar()

def check(database, users_list):
	#Se il nome del database non è inserito o non esiste, viene restituito errore e termina
	if(database is None or users_list is None):
	    print('Error - database path and users list required')
	    exit(0)
	if not (type(users_list) == list):
		print("Error - the users list must be a list")
		exit(0)
	try:
	    print('Reading Data...')
	    data = pd.read_csv(database, sep=';', dtype = str)
	    print('Done')
	except:
	    print('Error - database not found in inserted path')
	    exit(0)
	setId = set(data.UserId)
	for user in users_list:
		if not(str(user) in setId):
			print("Error - the list contains an user ID not belonging to the database")
			exit(0)
	return data

def print_user_stats(database, users_list):

	dataset = check(database, users_list)

	for user in pbar(users_list):
		print("-->Utente: ",user)	
		df_IQ = dataset.loc[dataset['UserId'] == str(user), ['ItemId','Name', 'Quantity']]
		print("-->Lista degli acquisti:")
		print(df_IQ)
		print("----------------------------------------")
		tot_purchase = pd.to_numeric(df_IQ['Quantity']).sum()
		numberpurchaseU = len(df_IQ.Quantity.tolist())
		print("-->Numero delle Transazioni:",numberpurchaseU)
		print("----------------------------------------")
		print("-->Quantità di prodotti acquistata:",tot_purchase)
		print("----------------------------------------")
		print("-->Media della quantità di acquisti: ",tot_purchase / numberpurchaseU)
		maxQ = pd.to_numeric(df_IQ['Quantity']).max()
		maxI = df_IQ.ItemId.loc[pd.to_numeric(df_IQ['Quantity']) == maxQ].iloc[0]
		minQ = pd.to_numeric(df_IQ['Quantity']).min()
		minI = df_IQ.ItemId.loc[pd.to_numeric(df_IQ['Quantity']) == minQ].iloc[0]
		print("----------------------------------------")
		print("-->ID oggetto acquistato più volte:", maxI, "con quantita': ",maxQ)
		print("----------------------------------------")
		print("-->ID oggetto acquistato meno volte:", minI, "con quantita': ",minQ)
		print("----------------------------------------")
		valueQ =  Entropy(df_IQ["Quantity"].values, tot_purchase)
		print("-->Entropia degli acquisti: ",valueQ)
		valueQ = GiniIndex(df_IQ["Quantity"].values, tot_purchase)
		print("-->Gini degli acquisti: ",valueQ)
		print("----------------------------------------------------")
