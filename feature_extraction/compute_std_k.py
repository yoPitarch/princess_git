import pprint

import numpy as np
from pymongo import MongoClient

# ********************************************
# CONNEXION DANS MONGODB
# ********************************************
tColName = ["np2003", "np2004",
            "ohsumed", "td2003", "td2004", "hp2003", "hp2004"]

tSizeIndex = ["10", "50", "100", "1000"]


connection = MongoClient(host='co2-ni01.irit.fr',port=28018)
db = connection.princess
for colName in tColName :

    for sizeIndex in tSizeIndex:

        collection_name = colName+"_"+sizeIndex
        collection = db[collection_name]
        queries = collection.distinct('query')
        result_collection = db[collection_name + "_std"]
        result_collection.remove({})
        for q in queries:
            toInsert = {}
            toInsert["query"] = q
            toInsert["stds"] = {}
            valFeatures = {}
            stdFeatures = {}
            # la requete qui liste tous les documents
            list = collection.find({'query': q}, {'_id': 0, 'docs': 1})
            count = 0
            list_doc = []
            for d in list[0]['docs']:
                # print "**********"
                count += 1
                # name = d['doc_name']

                list_feat = {}
                for f in d['features']:
                    toInsert["stds"].setdefault(f, {})
                    valFeatures.setdefault(f, [])
                    valFeatures[f].append(d['features'][f])

            for feat in valFeatures:
                std = np.std(np.array(valFeatures[feat]))
                toInsert["stds"][feat] = std
                print valFeatures[feat]
                print "std"
                print std

            data = result_collection.save(toInsert)
            pprint.pprint(data)
