import sys
import pymongo
from pymongo import MongoClient
import numpy as np
import pprint
import operator

# ********************************************
# Pour une feature argv[1] et une collection argv[2] passees en parametre, 
# renvoie un fichier argv[3] au format trev_eval contenant les documents tries selon feature par requete
# ********************************************


# ********************************************
# CONNEXION DANS MONGODB
# ********************************************
collection_name = sys.argv[2]
feature = sys.argv[1]
fileout_name = sys.argv[3]

connection = MongoClient(host='co2-ni01.irit.fr',port=28018)
db = connection.princess
collection = db[collection_name]
queries = collection.distinct('query')
for q in queries:
	valFeatures = {}
	# la requete qui liste tous les documents 
	list = collection.find({'query':q},{'_id':0,'docs':1})
	for d in list[0]['docs'] :
		trouve = False
		for f in d['features'] :
			if f == feature:
				trouve = True
				valFeatures.setdefault(d['doc_name'], 0.0)
				valFeatures[d['doc_name']] = d['features'][f]
		if not trouve:
			valFeatures.setdefault(d['doc_name'], 0.0)

	sortedList = sorted(valFeatures.items(),key=operator.itemgetter(1), reverse=True)
	#for e in valFeatures:
	#	print e, valFeatures[e]

	#print "************"

	with open(fileout_name, "a") as f:
		for i,e in enumerate(sortedList):
			f.write(q+" Q0 "+e[0]+" "+str(i+1)+" "+str(e[1])+" "+feature+"\n")





