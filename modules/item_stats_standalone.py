import pandas as pd
import math
import argparse
import scipy.stats as sp
from sklearn import preprocessing
from progressbar import ProgressBar
import matplotlib.pyplot as plt

#Prototipo di chiamata del programma:
#python item_stats_standalone.py -db (path database) -i (lista oggetti)
#Esempio: python item_stats_standalone.py -db db_1.csv -i 904553094 904570886

#Removes the 'A value is trying to be set on a copy of a slice from a DataFrame.' warning
pd.set_option('mode.chained_assignment', None)


def check(database, items_list):
	#Se il nome del database non è inserito o non esiste, viene restituito errore e termina
	if(database is None or items_list is None):
	    print('Error - database path and items list required')
	    exit(0)
	if not (type(items_list) == list):
		print("Error - the items list must be a list")
		exit(0)
	try:
	    print('Reading Data...')
	    data = pd.read_csv(database, sep=';', dtype = str)
	    print('Done')
	except:
	    print('Error - database not found in inserted path')
	    exit(0)
	setId = set(data.ItemId)
	for item in items_list:
		if not(str(item) in setId):
			print("Error - the list contains an item ID not belonging to the database")
			exit(0)
	return data


parser = argparse.ArgumentParser()
parser.add_argument('-db','--database', help ='import database', type = str)
parser.add_argument('-i','--itemslist',nargs='+', help ='insert the list of items whose stats you want to print')
args = parser.parse_args()

dataset = check(args.database, args.itemslist)
items_list = args.itemslist

pbar = ProgressBar()

for item in pbar(items_list):
	print("-->Oggetto: ",item)
	df_UQ = dataset.loc[dataset['ItemId'] == str(item), ['UserId','Quantity']]
	print("-->Lista degli acquirenti:")
	print(df_UQ)
	print("----------------------------------------")
	numberpurchaseU = len(df_UQ.Quantity.tolist())
	tot_purchase = pd.to_numeric(df_UQ.Quantity.values).sum()	
	print("-->Numero degli acquirenti:",numberpurchaseU)
	print("----------------------------------------")
	print("-->Quantità di prodotto acquistata:",tot_purchase)
	print("----------------------------------------")
	print("-->Media della quantità di acquisto:",tot_purchase / numberpurchaseU)
	maxQ = pd.to_numeric(df_UQ['Quantity']).max()
	maxI = df_UQ.UserId.loc[pd.to_numeric(df_UQ['Quantity']) == maxQ].iloc[0]
	minQ = pd.to_numeric(df_UQ['Quantity']).min()
	minI = df_UQ.UserId.loc[pd.to_numeric(df_UQ['Quantity']) == minQ].iloc[0]
	print("----------------------------------------")
	print("-->Utente che ha acquistato più volte :", maxI, "con quantita': ",maxQ)
	print("----------------------------------------")
	print("-->Utente che ha acquistato meno volte :", minI, "con quantita': ",minQ)
	print("---------------------------------------------------")
