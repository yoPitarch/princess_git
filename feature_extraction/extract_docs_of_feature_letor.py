import sys,os
import pymongo
from pymongo import MongoClient
import numpy as np
import pprint
import operator



collections = ["NP2003",'NP2004',"TD2003", 'TD2004', 'HP2003','HP2004','OHSUMED']
combinateurs = ["RRF", "Borda", "Combsum","Combmnz"]


	
def generate_file(c,f,n): 
	# ********************************************
	# Pour une feature argv[1] et une collection argv[2] passees en parametre, 
	# renvoie un fichier argv[3] au format trev_eval contenant les documents tries selon feature par requete
	# ********************************************

	
	def isDocOk(q,d,c):
		pathBest = "/osirim/sig/PROJET/PRINCESS/code/tools/best_competitors_letor/"+c.upper()+"/docs/"+q+".txt"
		tab = []
		with open(pathBest,"r") as file :
			for l in file:
				tab.extend(l.split(" "))
			#print tab
			#sys.exit()
		return d in tab

	# ********************************************
	# CONNEXION DANS MONGODB
	# ********************************************

	collection_name = c
	feature = f
	fileout_name = n

	connection = MongoClient(host='co2-ni01.irit.fr',port=28018)
	db = connection.princess
	collection = db[collection_name]
	queries = collection.distinct('query')
	for q in queries:
		valFeatures = {}
		# la requete qui liste tous les documents 
		list = collection.find({'query':q},{'_id':0,'docs':1})
		for d in list[0]['docs'] :
			#print d
			if len(valFeatures)  < 50 :
				if isDocOk(q,d['doc_name'],c):
					#print "ok"
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


for col in collections:
	dirCol = "/projets/sig/PROJET/PRINCESS/results/combinateurs/"+col
	os.system("rm -r "+dirCol)
	os.system("mkdir "+dirCol)
	print col
	if "OHS" in col:
		for el in ["f"+str(i) for i in range(1,46)]:
			print el
			generate_file(col.lower(),el,dirCol+'/'+el+".txt")
		param = " ".join([dirCol+'/f'+str(i)+".txt" for i in range(1,46)])
		for comb in combinateurs :
			print comb
			command = "java /osirim/sig/PROJET/PRINCESS/code/tools/combinateurs/main -combinateur "+comb+" "+param+" >  "+"/projets/sig/PROJET/PRINCESS/results/combinateurs/"+col+"/"+comb+".txt"
			print coommand
			os.system(command)
	else : 
		for el in ["f"+str(i) for i in range(1,65)]:
			print el
			generate_file(col.lower(),el,dirCol+'/'+el+".txt")
		param = " ".join([dirCol+'/f'+str(i)+".txt" for i in range(1,65)])
		for comb in combinateurs :
			print comb
			command = "java /osirim/sig/PROJET/PRINCESS/code/tools/combinateurs/main -combinateur "+comb+" "+param+" >  "+"/projets/sig/PROJET/PRINCESS/results/combinateurs/"+col+"/"+comb+".txt"
			print command
			os.system(command)






