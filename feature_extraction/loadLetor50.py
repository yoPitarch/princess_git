import os
from os.path import join

from pymongo import MongoClient

dirData = "/projets/sig/PROJET/PRINCESS/data/LETOR_50/"
dirQueries = "/osirim/sig/PROJET/PRINCESS/queries"

listdataset = os.listdir(dirData)

for dataset in listdataset:
    # ********************************************
    # CONNEXION DANS MONGODB
    # ********************************************
    datasetLower = dataset.lower()+"_50"
    connection = MongoClient(host='co2-ni01.irit.fr', port=28018)
    db = connection.princess
    collection = db[datasetLower]
    collection.remove({})

    command = "rm -r " + dirQueries + "/" + datasetLower
    os.system(command)
    command = "mkdir " + dirQueries + "/" + datasetLower
    os.system(command)
    command = "mkdir " + dirQueries + "/" + datasetLower + "/folds"
    os.system(command)

    valFeats = {}

    pathDataset = join(dirData, dataset)
    listFold = os.listdir(pathDataset)
    for fold in listFold:
        print fold
        if "all" not in fold:
            if "Store" not in fold:
                idFold = fold.replace("Fold", "")
                command = "cp " + pathDataset + "/" + fold + "/qids.txt " + dirQueries + "/" + datasetLower + "/" + idFold + ".txt"
                os.system(command)

                with open(pathDataset + "/" + fold + "/test.txt") as f:
                    for l in f:
                        t = l.split(' ')
                        qid = t[1].split(':')[1]
                        docid = t[-1].strip()
                        valFeats.setdefault(qid, {})
                        valFeats[qid].setdefault("query", qid)
                        valFeats[qid].setdefault("docs", [])
                        # valFeats[qid]["docs"] = []
                        dictDoc = {}
                        dictDoc["doc_name"] = docid
                        dictDoc["features"] = {}
                        for f in t[2:-3]:
                            tf = f.split(':')
                            dictDoc["features"]["f" + tf[0]] = float(tf[1])

                        valFeats[qid]["docs"].append(dictDoc)
    for q in valFeats:
        data = collection.save(valFeats[q])
