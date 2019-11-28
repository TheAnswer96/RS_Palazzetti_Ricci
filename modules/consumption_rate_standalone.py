import pandas as pd
import numpy as np
import argparse

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

expanded_dataset = dataset

print("Dataset modificato con aggiunta di colonne inerenti il consumption rate")

expanded_dataset['UserId'] = dataset['UserId'].astype("category")
expanded_dataset['ItemId'] = dataset['ItemId'].astype("category")
expanded_dataset['user_id'] = dataset['UserId'].cat.codes
expanded_dataset['item_id'] = dataset['ItemId'].cat.codes
expanded_dataset.Quantity= dataset.Quantity.astype(int)

modified_dataset = expanded_dataset

dataset['Sum'] = dataset.groupby('ItemId').Quantity.transform(np.sum)
dataset['Count'] = dataset.groupby('ItemId').Quantity.transform(func='count')
dataset['ConsumptionRate'] = dataset.groupby('ItemId').Quantity.transform(np.mean)
dataset['ratio'] = dataset.Quantity / dataset.ConsumptionRate
dataset.to_csv("modified.csv", sep=";")
print(expanded_dataset.head(10))

print("--------------------------------------------------------------------------------------------------------------------------------------------------------")

print("Dataset modificato con quantity sostituita dal ratio del consumption rate")

modified_dataset['Quantity'] = dataset['ratio']
modified_dataset=modified_dataset.rename(columns = {'Quantity':'Modified_Quantity'})
modified_dataset = modified_dataset[['UserId', 'ItemId', 'Name', 'CatCode', 'CatName', 'Modified_Quantity', 'user_id', 'item_id']]
print(modified_dataset.head(10))