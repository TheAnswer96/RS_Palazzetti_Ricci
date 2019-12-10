# -----------------------------------------------------------
# Dato un dataset restituisce informazioni inerenti le categorie, in versione normale o verbose.
# Le informazioni sono ad esempio il numero degli oggetti che hanno quella classe, il numero cumulativo di prodotti ecc.
# Il parametro v è opzionale, se impostato a True restituisce anche informazioni su ogni singolo
# oggetto facente parte di una categoria.
# Di default il parametro v è impostato a False, quindi può essere omesso se non necessario.
#
# Prototipo di chiamata del metodo:
# print cat("nome_dataset.csv", v=True)
# -----------------------------------------------------------

import pandas as pd
import numpy as np
import time
start_time = time.time()

#Prototipo di chiamata del metodo:
#print_cat((path database), [verbose=True se si desidera stampare versione verbose])
#Esempio: print_cat(db_1.csv, verbose=True)
#Se si omette l'argomento verbose, questo è False di default

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


def print_cat(database, verbose=False):

	data = check(database)

	#Assegna labels alle colonne di data
	data.columns = ['UserId', 'ItemId','Name','CatCode','CatName', 'Quantity']
	data.Quantity= data.Quantity.astype(int)

	#Dataframe contenente i CatCode e la quantità totale venduta corrispondente
	calc_quantity = data.groupby('CatCode').Quantity.sum()

	#Dataframe contenente i CatCode ed il numero di oggetti che ne fanno parte nel database
	calc_number = data.groupby('CatCode').ItemId.nunique()


	newDF = pd.DataFrame()

	print('Computing categories info...')

	#Versione verbose, se l'utente ha inserito verbose=True
	if(verbose):

		#Lista di tutti i dataframe (da una riga, corrispondente alla categoria) che andranno ad essere concatenati alla fine per creare il dataframe di tutte le categorie
		frames = [newDF,]

		#Per ogni CatCode calcola il Catname corrispondente, il numero degli oggetti e la quantità venduta cumulativa di tutti gli oggetti che ne fanno parte
		for i in calc_quantity.index:
			cat_name = data.loc[data.CatCode == i].CatName.iloc[0]
			items_number = calc_number.loc[calc_number.index == i].iloc[0]
			total_quantity = calc_quantity.loc[calc_quantity.index == i].iloc[0]

			#Per ogni oggetto appartenente alla categoria viene trovato il Name corrispondente all'interno di data e viene calcolata la quantità totale venduta
			item_info = data.loc[data.CatCode == i][['ItemId', 'Name', 'Quantity']]
			item_info = item_info.groupby(['ItemId','Name']).Quantity.sum()

			#Lista che conterrà le informazioni su tutti gli oggetti
			product_list = []

			#idx è una tupla contenente (ItemId, Name), somma è la somma delle quantità, vengono appese a product list come una lista di 3 elementi [id, nome, somma]
			for idx, somma in item_info.iteritems():
				product_list.append([idx[0], idx[1], somma])

			#Viene costruita e salvata nella lista la riga da aggiungere al dataframe
			data_append = pd.DataFrame({'CatCode': [i], 'CatName': [cat_name], 'ItemsNumber': [items_number], 'PurchasedQuantity': [total_quantity], 'ItemsInfo [ItemId, Name, PurchasedQuantity]': [product_list]})
			frames.append(data_append)

		#Viene effettuata la concatenazione di tutte le righe presenti nella lista frames
		newDF = pd.concat(frames, ignore_index=True)
		print('Done')

		print('Writing (verbose) category info on \'category_info_verbose.csv\'...')
		#newDF = newDF.sort_values(by=['ItemsNumber'], ascending=True)
		newDF.to_csv('category_info_verbose.csv', sep=';', encoding='utf-8')
		print('Done')


	#Versione non verbose, se l'utente ha inserito verbose=False (o omesso)
	else:

		#Lista di tutti i dataframe (da una riga, corrispondente alla categoria) che andranno ad essere concatenati alla fine per creare il dataframe di tutte le categorie
		frames = [newDF,]

		#Per ogni CatCode calcola il Catname corrispondente, il numero degli oggetti e la quantità venduta cumulativa di tutti gli oggetti che ne fanno parte
		for i in calc_quantity.index:
			cat_name = data.loc[data.CatCode == i].CatName.iloc[0]
			items_number = calc_number.loc[calc_number.index == i].iloc[0]
			total_quantity = calc_quantity.loc[calc_quantity.index == i].iloc[0]
			#Viene costruita e salvata nella lista la riga da aggiungere al dataframe
			data_append = pd.DataFrame({'CatCode': [i], 'CatName': [cat_name], 'ItemsNumber': [items_number], 'PurchasedQuantity': [total_quantity]})
			frames.append(data_append)

		#Viene effettuata la concatenazione di tutte le righe presenti nella lista frames
		newDF = pd.concat(frames, ignore_index=True)

		print('Done')

		print('Writing (not verbose) category info on \'category_info.csv\'...')
		#newDF = newDF.sort_values(by=['TotalQuantity'], ascending=False)
		newDF.to_csv('category_info.csv', sep=';', encoding='utf-8')
		print('Done')

	print('--- Execution time: %s seconds ---' % (time.time() - start_time))
