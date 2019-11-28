import pandas as pd
import math
import scipy.stats as sp
from sklearn import preprocessing
from progressbar import ProgressBar
import matplotlib.pyplot as plt
import argparse

#Removes the 'A value is trying to be set on a copy of a slice from a DataFrame.' warning
pd.set_option('mode.chained_assignment', None)

#Prototipo di chiamata del programma:
#python stats_standalone.py -db (path database)
#Esempio:python stats_standalone.py -db db_1.csv

def check(database):
	#Se il nome del database non è inserito o non esiste, viene restituito errore e termina
	if(database is None):
	    print('Error - database path required')
	    exit(0)
	try:
	    print('Reading Data...')
	    data = pd.read_csv(database, sep=';', dtype = str)
	    print('Done')
	except:
	    print('Error - database not found in inserted path')
	    exit(0)
	return data



parser = argparse.ArgumentParser()
parser.add_argument('-db','--database', help ='import database', type = str)
args = parser.parse_args()
dataset = check(args.database)

print("INFORMAZIONI GENERICHE\n")
transaction = len(dataset.ItemId)
print("-->Numero di transazioni totali: ", transaction)
totalsell = pd.to_numeric(dataset['Quantity']).sum()
print("-->Numero di oggetti: ", len(set(dataset.ItemId)))
print("-->Quantità cumulativa di oggetti venduti: ", totalsell)
maxSell = pd.to_numeric(dataset['Quantity']).max()
listofmax = dataset.loc[dataset["Quantity"] == str(maxSell)]
print("-->Prodotti maggiormente venduti:\n",listofmax)
minSell = pd.to_numeric(dataset['Quantity']).min()
listofmin = dataset.loc[dataset["Quantity"] == str(minSell)]
print("-->Prodotti maggiormente venduti:\n",listofmin)
subData = dataset[["UserId","Quantity"]]
subData.Quantity = subData.Quantity.astype(float)
maxQBuyer = subData.groupby(["UserId"]).sum()#cambiato
maxQBuyer.reset_index(level=0,inplace=True)#cambiato
maxB = maxQBuyer.max()
minB = maxQBuyer.min()
print("Lista delle quantità totali: ", maxQBuyer)
print("Utente che ha acquistato la maggior quantità: ", int(maxB[0]), " con quantita': ", maxB[1])
print("Utente che ha acquistato la minor quantità: ", int(minB[0]), " con quantita': ", minB[1])
print("Gli utenti hanno acquistato in media: ",maxQBuyer.mean()[1])