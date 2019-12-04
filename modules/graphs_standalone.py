# -----------------------------------------------------------
# Dato un dataset ed un intero n (opzionale) stampa dei grafici informativi.
#
# Il numero di righe da prendere in considerazione per lo zoom (n)
# se omesso assume il valore di default 10.
#
# Esempio di chiamata del programma:
# python graphs standalone.py -db nome_dataset.csv -n num_zoom
# -----------------------------------------------------------

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

#Nasconde il warning 'A value is trying to be set on a copy of a slice from a DataFrame.'
pd.set_option('mode.chained_assignment', None)

#Prototipo di chiamata del programma:
#python graphs_standalone.py -db (path database) [-n] (numero di righe sul quale effettuare lo zoom, opzionale)
#Esempio: python graphs_standalone.py -db db_1.csv -n 50

def check(db,nrows):

	if db is None:
		print("Error - Database path required")
		Exit(0)

	else:
		try:
			nrows = int(nrows)
		except:
			print("Error - the number of rows must be an integer")
			exit(0)

		try:
			data = pd.read_csv(db, sep=';', dtype = str)
		except:
			print('Error - database not found in inserted path')
			exit(0)

		num_users = len(data.UserId)
		if nrows > num_users:
			print("Error - the number of rows to zoom on must be less than the total number of rows (",num_users,")")
			exit(0)
	return data


parser = argparse.ArgumentParser()
parser.add_argument('-db','--database', help ='import database', type = str)
parser.add_argument('-n','--nrows', default=10, help ='choose the number of rows to zoom on', type = int)
args = parser.parse_args()

dataset = check(args.database, args.nrows)
nrows = args.nrows


#Produce un dataset composto dalle prime nrows righe
dataset_reduced = dataset.iloc[:nrows]


#UTENTI SU ASSE X, QUANTITA' DI OGGETTI ACQUISTATI SU ASSE Y

#Grafico in alto a sinistra
plt.subplot(2,2,1)

#Liste di utenti ed oggetti:
lista_utenti = dataset.UserId
lista_oggetti = dataset.ItemId

lista_acquisti = dataset[['UserId','Quantity']]
lista_acquisti.Quantity = lista_acquisti.Quantity.astype(int)
somma_acquisti = lista_acquisti.groupby(['UserId']).sum()
somma_acquisti = somma_acquisti.sort_values(by=['Quantity'], ascending=False)
somma_acquisti.reset_index(level=0, inplace=True)

media = somma_acquisti.mean().iloc[1]

utente = somma_acquisti['UserId']
utente = utente.values.tolist()
#Per ridurre i tempi di testing riduco gli insiemi di user ed item ad 1/64 di quello originale
"""
del utente[1::2]
del utente[1::2]
del utente[1::2]
del utente[1::2]
del utente[1::2]
del utente[1::2]
"""
quantita = somma_acquisti['Quantity']
quantita = quantita.values.tolist()
#Per ridurre i tempi di testing riduco gli insiemi di user ed item ad 1/64 di quello originale
"""
del quantita[1::2]
del quantita[1::2]
del quantita[1::2]
del quantita[1::2]
del quantita[1::2]
del quantita[1::2]
"""

#Indici fittizi per l'asse x del grafico (non vengono stampati)
xi = list(range(len(utente)))

frame1 = plt.gca()

#Elimina spazio tra il frame del grafico e gli assi
frame1.margins(0)

plt.plot(xi, quantita)
#Imposta l'inizio dei valori per l'asse y a 0
frame1.set_ylim(ymin=0)
#Stampa della media
plt.axhline(y = media, color = 'r', linestyle = '--', label='Avg purchased quantity = %.3f' %media)
plt.xlabel('Users')
plt.ylabel('Purchased quantity')
plt.legend()

#Per scrivere valore media come tick dell'asse y
"""
yt = frame1.get_yticks() 
yt=np.append(yt,media)
frame1.set_yticks(yt)
"""

#Per scrivere valore media sopra alla retta che rappresenta la media nel grafico
"""
plt.text(1, media, round(media,3), fontsize=12, color='RED')
"""


#Nasconde nomi degli indici per asse x
frame1.axes.get_xaxis().set_ticks([0,])
#Mostra griglia orizzontale
frame1.yaxis.grid(True, linewidth=0.2)


#OGGETTI SU ASSE X, QUANTITA' DI OGGETTI ACQUISTATI SU ASSE Y

#Grafico in basso a sinistra
plt.subplot(2,2,3)

lista_vendite = dataset[['ItemId','Quantity']]
lista_vendite.Quantity = lista_vendite.Quantity.astype(int)
somma_vendite = lista_vendite.groupby(['ItemId']).sum()
somma_vendite = somma_vendite.sort_values(by=['Quantity'], ascending=False)
somma_vendite.reset_index(level=0, inplace=True)

media = somma_vendite.mean().iloc[1]

oggetto = somma_vendite['ItemId']
oggetto = oggetto.values.tolist()

quantita = somma_vendite['Quantity']
quantita = quantita.values.tolist()

xi = list(range(len(oggetto)))

frame1 = plt.gca()

frame1.margins(0)

plt.plot(xi, quantita)
frame1.set_ylim(ymin=0)
plt.axhline(y = media, color = 'r', linestyle = '--', label='Avg purchased quantity = %.3f' %media)
plt.xlabel('Items')
plt.ylabel('Purchased quantity')
plt.legend()
frame1.axes.get_xaxis().set_ticks([0,])
frame1.yaxis.grid(True, linewidth=0.2)


#UTENTI SU ASSE X, QUANTITA' DI OGGETTI ACQUISTATI SU ASSE Y (TAGLIATO, PRENDO SOLO LE PRIME NROWS RIGHE)

#Grafico in alto a sinistra
plt.subplot(2,2,2)

#Liste di utenti ed oggetti:
lista_utenti = dataset_reduced.UserId
lista_oggetti = dataset_reduced.ItemId

lista_acquisti = dataset_reduced[['UserId','Quantity']]
lista_acquisti.Quantity = lista_acquisti.Quantity.astype(int)
somma_acquisti = lista_acquisti.groupby(['UserId']).sum()
somma_acquisti = somma_acquisti.sort_values(by=['Quantity'], ascending=False)
somma_acquisti.reset_index(level=0, inplace=True)

media = somma_acquisti.mean().iloc[1]

utente = somma_acquisti['UserId']
utente = utente.values.tolist()

quantita = somma_acquisti['Quantity']
quantita = quantita.values.tolist()
xi = list(range(len(utente)))

frame1 = plt.gca()

frame1.margins(0)

plt.plot(xi, quantita)
frame1.set_ylim(ymin=0)
plt.axhline(y = media, color = 'r', linestyle = '--', label='Avg purchased quantity = %.3f' %media)
plt.title("Graph considering only the first %i rows of the dataset" %nrows)
plt.xlabel('Users')
plt.ylabel('Purchased quantity')
plt.legend()
frame1.axes.get_xaxis().set_ticks([0,])
frame1.yaxis.grid(True, linewidth=0.2)


#OGGETTI SU ASSE X, QUANTITA' DI OGGETTI ACQUISTATI SU ASSE Y

#Grafico in basso a sinistra
plt.subplot(2,2,4)

lista_vendite = dataset_reduced[['ItemId','Quantity']]
lista_vendite.Quantity = lista_vendite.Quantity.astype(int)
somma_vendite = lista_vendite.groupby(['ItemId']).sum()
somma_vendite = somma_vendite.sort_values(by=['Quantity'], ascending=False)
somma_vendite.reset_index(level=0, inplace=True)

media = somma_vendite.mean().iloc[1]

oggetto = somma_vendite['ItemId']
oggetto = oggetto.values.tolist()

quantita = somma_vendite['Quantity']
quantita = quantita.values.tolist()

xi = list(range(len(oggetto)))

frame1 = plt.gca()

frame1.margins(0)

plt.plot(xi, quantita)
frame1.set_ylim(ymin=0)
plt.axhline(y = media, color = 'r', linestyle = '--', label='Avg purchased quantity = %.3f' %media)
plt.title("Graph considering only the first %i rows of the dataset" %nrows)
plt.xlabel('Items')
plt.ylabel('Purchased quantity')
plt.legend()
frame1.axes.get_xaxis().set_ticks([0,])
frame1.yaxis.grid(True, linewidth=0.2)


#Setta i margini della figure, che contiene tutti e 6 i grafici
plt.subplots_adjust(left=0.05, right=0.98, top=0.93, bottom=0.09, hspace=0.35, wspace=0.22)
#Pagina con grafici viene aperta in fullscreen
mng = plt.get_current_fig_manager()
mng.window.showMaximized()

print("Printing first graphs page...")
plt.show()
print("Done")







































#GRAFICO A BARRE, QUANTITA' DI OGGETTI ACQUISTATI SU ASSE X, NUMERO DI UTENTI SU ASSE Y
#Quanti utenti hanno acquistato una quantità di prodotti cumulativa compresa tra u e v?

#Grafico in alto al centro
plt.subplot(2,2,1)

lista_acquisti = dataset[['UserId','Quantity']]
lista_acquisti.Quantity = lista_acquisti.Quantity.astype(int)
somma_acquisti = lista_acquisti.groupby(['UserId']).sum()

media = somma_acquisti.mean().iloc[0]

#Contatori, uno per ogni barra (e quindi ogni intervallo) del grafico
slices = [0,0,0,0,0,0,0,0,0,0]
#Gli slices per la prima barra a sinistra
slices_first = [0,0,0,0,0]

#Definizione degli intervalli della prima barra a sinistra
slices_first[0] = len(somma_acquisti[somma_acquisti.Quantity == 1])
slices_first[1] = len(somma_acquisti[somma_acquisti.Quantity == 2]) + slices_first[0]
slices_first[2] = len(somma_acquisti[somma_acquisti.Quantity == 3]) + slices_first[1]
slices_first[3] = len(somma_acquisti[somma_acquisti.Quantity == 4]) + slices_first[2]
slices_first[4] = len(somma_acquisti[somma_acquisti.Quantity == 5]) + slices_first[3]

#Definizione degli intervalli delle altre barre
slices[0] = len(somma_acquisti[(somma_acquisti.Quantity > 5) & (somma_acquisti.Quantity < 11)])
slices[1] = len(somma_acquisti[(somma_acquisti.Quantity > 10) & (somma_acquisti.Quantity < 16)])
slices[2] = len(somma_acquisti[(somma_acquisti.Quantity > 15) & (somma_acquisti.Quantity < 21)])
slices[3] = len(somma_acquisti[(somma_acquisti.Quantity > 20) & (somma_acquisti.Quantity < 26)])
slices[4] = len(somma_acquisti[(somma_acquisti.Quantity > 25) & (somma_acquisti.Quantity < 31)])
slices[5] = len(somma_acquisti[(somma_acquisti.Quantity > 30) & (somma_acquisti.Quantity < 36)])
slices[6] = len(somma_acquisti[(somma_acquisti.Quantity > 35) & (somma_acquisti.Quantity < 41)])
slices[7] = len(somma_acquisti[(somma_acquisti.Quantity > 40) & (somma_acquisti.Quantity < 46)])
slices[8] = len(somma_acquisti[(somma_acquisti.Quantity > 45) & (somma_acquisti.Quantity < 51)])
slices[9] = len(somma_acquisti[somma_acquisti.Quantity > 50])

#Assegno i nomi alle etichette dei valori sull'asse x
xi = ["6-10","11-15","16-20","21-25","26-30","31-35","36-40","41-45","46-50","50+"]

frame1 = plt.gca()
#Plot della prima barra
plt.bar([""], slices_first[4], color='C1', label='Purchased quantity = 5')
plt.bar([""], slices_first[3], color='C2', label='Purchased quantity = 4')
plt.bar([""], slices_first[2], color='C3', label='Purchased quantity = 3')
plt.bar([""], slices_first[1], color='C4', label='Purchased quantity = 2')
plt.bar([""], slices_first[0], color='C9', label='Purchased quantity = 1')

#Plot delle barre rimanenti
plt.bar(xi, slices, color='C0')
#Disegna la media
plt.axhline(y = media, color = 'r', linestyle = '--', label='Avg purchased quantity = %.3f' %media)
#Ruota etichette di 45 gradi
plt.xticks(rotation=45)
plt.xlabel('Purchased quantity')
plt.ylabel('# users')
plt.legend()

#Scrive etichette impresse sulla prima barra
#Scrive etichetta della prima barra in basso ("1-5"), se si prova a metterla direttamente al momento
#della creazione della barra ne viene creata un'altra vuota tra la prima e le altre
frame1.text(-0.19, -4400, '1-5', rotation=45)

frame1.yaxis.grid(True, linewidth=0.2)






















#GRAFICO A BARRE, NUMERO DI OGGETTI UNICI ACQUISTATI SU ASSE X, NUMERO DI UTENTI SU ASSE Y
#Quanti utenti hanno acquistato un numero di oggetti unici compreso tra u e v??

#Grafico in basso al centro
plt.subplot(2,2,3)

lista_acquisti = dataset[['UserId','ItemId']]
numero_acquisti = lista_acquisti.groupby(['UserId']).count()

media = numero_acquisti.mean().iloc[0]

slices = [0,0,0,0,0,0,0,0,0,0]
slices_first = [0,0,0,0,0]

slices_first[0] = len(numero_acquisti[numero_acquisti.ItemId == 1])
slices_first[1] = len(numero_acquisti[numero_acquisti.ItemId == 2]) + slices_first[0]
slices_first[2] = len(numero_acquisti[numero_acquisti.ItemId == 3]) + slices_first[1]
slices_first[3] = len(numero_acquisti[numero_acquisti.ItemId == 4]) + slices_first[2]
slices_first[4] = len(numero_acquisti[numero_acquisti.ItemId == 5]) + slices_first[3]

slices[0] = len(numero_acquisti[(numero_acquisti.ItemId > 5) & (numero_acquisti.ItemId < 11)])
slices[1] = len(numero_acquisti[(numero_acquisti.ItemId > 10) & (numero_acquisti.ItemId < 16)])
slices[2] = len(numero_acquisti[(numero_acquisti.ItemId > 15) & (numero_acquisti.ItemId < 21)])
slices[3] = len(numero_acquisti[(numero_acquisti.ItemId > 20) & (numero_acquisti.ItemId < 26)])
slices[4] = len(numero_acquisti[(numero_acquisti.ItemId > 25) & (numero_acquisti.ItemId < 31)])
slices[5] = len(numero_acquisti[(numero_acquisti.ItemId > 30) & (numero_acquisti.ItemId < 36)])
slices[6] = len(numero_acquisti[(numero_acquisti.ItemId > 35) & (numero_acquisti.ItemId < 41)])
slices[7] = len(numero_acquisti[(numero_acquisti.ItemId > 40) & (numero_acquisti.ItemId < 46)])
slices[8] = len(numero_acquisti[(numero_acquisti.ItemId > 45) & (numero_acquisti.ItemId < 51)])
slices[9] = len(numero_acquisti[numero_acquisti.ItemId > 50])

xi = ["6-10","11-15","16-20","21-25","26-30","31-35","36-40","41-45","46-50","50+"]

frame1 = plt.gca()
plt.bar([""], slices_first[4], color='C1', label='Purchased quantity = 5')
plt.bar([""], slices_first[3], color='C2', label='Purchased quantity = 4')
plt.bar([""], slices_first[2], color='C3', label='Purchased quantity = 3')
plt.bar([""], slices_first[1], color='C4', label='Purchased quantity = 2')
plt.bar([""], slices_first[0], color='C9', label='Purchased quantity = 1')

plt.bar(xi, slices, color='C0')
plt.axhline(y = media, color = 'r', linestyle = '--', label='Avg purchased quantity = %.3f' %media)
plt.xticks(rotation=45)
plt.xlabel('# different products')
plt.ylabel('# users')
plt.legend()

frame1.text(-0.19, -5300, '1-5', rotation=45)

frame1.yaxis.grid(True, linewidth=0.2)























#Grafico a barre, numero di oggetti venduti in una certa quantità
#GRAFICO A BARRE, QUANTITA' DI OGGETTI VENDUTA SU ASSE X, NUMERO DI OGGETTI SU ASSE Y
#Quanti oggetti sono stati venduti in quantità compresa tra u e v?

#Grafico in alto a sinistra
plt.subplot(2,2,2)

lista_acquisti = dataset[['ItemId','Quantity']]
lista_acquisti.Quantity = lista_acquisti.Quantity.astype(int)
somma_acquisti = lista_acquisti.groupby(['ItemId']).sum()

media = somma_acquisti.mean().iloc[0]

slices = [0,0,0,0,0,0,0,0,0,0]
slices_first = [0,0,0,0,0]

slices_first[0] = len(somma_acquisti[somma_acquisti.Quantity == 1])
slices_first[1] = len(somma_acquisti[somma_acquisti.Quantity == 2]) + slices_first[0]
slices_first[2] = len(somma_acquisti[somma_acquisti.Quantity == 3]) + slices_first[1]
slices_first[3] = len(somma_acquisti[somma_acquisti.Quantity == 4]) + slices_first[2]
slices_first[4] = len(somma_acquisti[somma_acquisti.Quantity == 5]) + slices_first[3]

slices[0] = len(somma_acquisti[(somma_acquisti.Quantity > 5) & (somma_acquisti.Quantity < 11)])
slices[1] = len(somma_acquisti[(somma_acquisti.Quantity > 10) & (somma_acquisti.Quantity < 16)])
slices[2] = len(somma_acquisti[(somma_acquisti.Quantity > 15) & (somma_acquisti.Quantity < 21)])
slices[3] = len(somma_acquisti[(somma_acquisti.Quantity > 20) & (somma_acquisti.Quantity < 26)])
slices[4] = len(somma_acquisti[(somma_acquisti.Quantity > 25) & (somma_acquisti.Quantity < 31)])
slices[5] = len(somma_acquisti[(somma_acquisti.Quantity > 30) & (somma_acquisti.Quantity < 36)])
slices[6] = len(somma_acquisti[(somma_acquisti.Quantity > 35) & (somma_acquisti.Quantity < 41)])
slices[7] = len(somma_acquisti[(somma_acquisti.Quantity > 40) & (somma_acquisti.Quantity < 46)])
slices[8] = len(somma_acquisti[(somma_acquisti.Quantity > 45) & (somma_acquisti.Quantity < 51)])
slices[9] = len(somma_acquisti[somma_acquisti.Quantity > 50])

xi = ["6-10","11-15","16-20","21-25","26-30","31-35","36-40","41-45","46-50","50+"]

frame1 = plt.gca()
plt.bar([""], slices_first[4], color='C1', label='Purchased quantity = 5')
plt.bar([""], slices_first[3], color='C2', label='Purchased quantity = 4')
plt.bar([""], slices_first[2], color='C3', label='Purchased quantity = 3')
plt.bar([""], slices_first[1], color='C4', label='Purchased quantity = 2')
plt.bar([""], slices_first[0], color='C9', label='Purchased quantity = 1')

plt.bar(xi, slices, color='C0')
plt.axhline(y = media, color = 'r', linestyle = '--', label='Avg purchased quantity = %.3f' %media)
plt.xticks(rotation=45)
plt.xlabel('Purchased quantity')
plt.ylabel('# items')
plt.legend()

frame1.text(-0.19, -3000, '1-5', rotation=45)

frame1.yaxis.grid(True, linewidth=0.2)






















#Grafico a barre, numero di oggetti acquistati un certo numero di volte
#GRAFICO A BARRE, NUMERO DI OGGETTI UNICI VENDUTI SU ASSE X, NUMERO DI OGGETTI SU ASSE Y
#Quanti oggetti sono stati venduti un numero di volte compreso tra u e v (ignorando la quantità)?

#Grafico in basso a destra
plt.subplot(2,2,4)

lista_acquisti = dataset[['UserId','ItemId']]
numero_acquisti = lista_acquisti.groupby(['ItemId']).count()

media = numero_acquisti.mean().iloc[0]

slices = [0,0,0,0,0,0,0,0,0,0]
slices_first = [0,0,0,0,0]

slices_first[0] = len(numero_acquisti[numero_acquisti.UserId == 1])
slices_first[1] = len(numero_acquisti[numero_acquisti.UserId == 2]) + slices_first[0]
slices_first[2] = len(numero_acquisti[numero_acquisti.UserId == 3]) + slices_first[1]
slices_first[3] = len(numero_acquisti[numero_acquisti.UserId == 4]) + slices_first[2]
slices_first[4] = len(numero_acquisti[numero_acquisti.UserId == 5]) + slices_first[3]


slices[0] = len(numero_acquisti[(numero_acquisti.UserId > 5) & (numero_acquisti.UserId < 11)])
slices[1] = len(numero_acquisti[(numero_acquisti.UserId > 10) & (numero_acquisti.UserId < 16)])
slices[2] = len(numero_acquisti[(numero_acquisti.UserId > 15) & (numero_acquisti.UserId < 21)])
slices[3] = len(numero_acquisti[(numero_acquisti.UserId > 20) & (numero_acquisti.UserId < 26)])
slices[4] = len(numero_acquisti[(numero_acquisti.UserId > 25) & (numero_acquisti.UserId < 31)])
slices[5] = len(numero_acquisti[(numero_acquisti.UserId > 30) & (numero_acquisti.UserId < 36)])
slices[6] = len(numero_acquisti[(numero_acquisti.UserId > 35) & (numero_acquisti.UserId < 41)])
slices[7] = len(numero_acquisti[(numero_acquisti.UserId > 40) & (numero_acquisti.UserId < 46)])
slices[8] = len(numero_acquisti[(numero_acquisti.UserId > 45) & (numero_acquisti.UserId < 51)])
slices[9] = len(numero_acquisti[numero_acquisti.UserId > 50])

xi = ["6-10","11-15","16-20","21-25","26-30","31-35","36-40","41-45","46-50","50+"]

frame1 = plt.gca()
plt.bar([""], slices_first[4], color='C1', label='Purchased quantity = 5')
plt.bar([""], slices_first[3], color='C2', label='Purchased quantity = 4')
plt.bar([""], slices_first[2], color='C3', label='Purchased quantity = 3')
plt.bar([""], slices_first[1], color='C4', label='Purchased quantity = 2')
plt.bar([""], slices_first[0], color='C9', label='Purchased quantity = 1')

plt.bar(xi, slices, color='C0')
plt.axhline(y = media, color = 'r', linestyle = '--', label='Avg purchased quantity = %.3f' %media)
plt.xticks(rotation=45)
plt.xlabel('# different products')
plt.ylabel('# products')
plt.legend()

frame1.text(-0.19, -3100, '1-5', rotation=45)

frame1.yaxis.grid(True, linewidth=0.2)









#Setta i margini della figure, che contiene tutti e 6 i grafici
plt.subplots_adjust(left=0.05, right=0.98, top=0.93, bottom=0.09, hspace=0.35, wspace=0.22)
#Pagina con grafici viene aperta in fullscreen
mng = plt.get_current_fig_manager()
mng.window.showMaximized()

print("Printing second graphs page...")
plt.show()
print("Done")
