import pandas as pd
import scipy.sparse as sparse
import implicit
import pickle
import numpy as np
import os
import scipy.special
import argparse
from pathlib import Path

os.environ["OPENBLAS_NUM_THREADS"] = "1"

#Nasconde il warning 'A value is trying to be set on a copy of a slice from a DataFrame.'
pd.set_option('mode.chained_assignment', None)

#Prototipo di chiamata del programma:
#python rank_standalone.py -db (path database) -i (oggetto del quale calcolare il rank) -u (lista degli utenti da considerare nel calcolo del rank))
#Esempio:python rank_standalone.py -db db_1.csv -i 01111111 -u 00000001 02245645 9994524

def check(database, item, users_list):
    #Se il nome del database non è inserito o non esiste, viene restituito errore e termina
    if(database is None or item is None or users_list is None):
        print('Error - database path, item and users list required')
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
    if not(str(item) in set(data.ItemId)):
        print("Error - the inserted item does not belong to the database")
        exit(0)
    setId = set(data.UserId)
    for user in users_list:
        if not(str(user) in setId):
            print("Error - the list contains an user ID not belonging to the database")
            exit(0)
    return data

parser = argparse.ArgumentParser()
parser.add_argument('-db','--database', help ='import database', type = str)
parser.add_argument('-i','--item', help ='item to calculate rank for', type = str)
parser.add_argument('-u','--userslist',nargs='+', help ='insert users list whose ranks to process')

args = parser.parse_args()

data=check(args.database, args.item, args.userslist)

data['UserId'] = data['UserId'].astype("category")
data['ItemId'] = data['ItemId'].astype("category")
data['user_id'] = data['UserId'].cat.codes
data['item_id'] = data['ItemId'].cat.codes
data.Quantity= data.Quantity.astype(int)
users_list = args.userslist
item = args.item

users_list_DF = pd.DataFrame(columns=data.columns)
results = []

#Per ogni utente nella lista estraggo le informazioni dal dataset
for i in users_list:
    users_list_DF = users_list_DF.append(data.loc[data["UserId"] == str(i)])

print("Training model...")

sparse_item_user = sparse.csr_matrix((data['Quantity'].astype(float), (data['item_id'], data['user_id'])))
sparse_user_item = sparse.csr_matrix((data['Quantity'].astype(float), (data['user_id'], data['item_id'])))

model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=30, use_gpu= False)
model.fit(sparse_item_user)

print("Generating recommendations for item ", item, "...")

#Il numero di raccomandazioni per utente deve essere uguale al numero totale di oggetti, per poter ricavare il rank anche se è molto basso
n = len(set(data.ItemId.tolist()))

#Per ogni utente nella lista vengono generate le raccomandazioni, poi si aggiunge al dataframe results la coppia [utente, raccomandazioni]
for i in users_list:
    user = users_list_DF.loc[users_list_DF["UserId"] == str(i), "user_id"].iloc[0]
    to_append = model.recommend(user, sparse_user_item, N=n, filter_already_liked_items=False)
    row = [i, to_append]
    results.append(row)

pos = []
somma = 0
std = 0
b = []

item_code = data.loc[data["ItemId"] == str(item), "item_id"].iloc[0]

#Per ogni coppia [utente, raccomandazioni]
for i in results:
    count = 0
    found = False

    #Per ogni raccomandazione della lista
    for j in i[1]:
        count = count + 1

        if j[0] == item_code:
            found = True
            pos.append(count)
            b.append(i[0])

    if(found==False):
        print("Error: Item not found in recommendations for user ", i[0])
        exit(0)

try:
    #Calcolo di rank medio e deviazione standard
    for i in range(len(pos)):
        somma = somma + pos[i]
        print("User: ",b[i]," Rank: ", pos[i])
    media = somma/len(pos)
    print("Mean rank: ", media)
    std = np.std(pos)
    print("Standard deviation: ",std)
except:
    print("Error: Item not found in recommendations")
