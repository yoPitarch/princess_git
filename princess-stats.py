#! /usr/bin/python

import random
import os
import getopt, sys
import pymongo
import pprint
from game import *
#from sets import Set
import operator
from operator import itemgetter, attrgetter
from pymongo import MongoClient
from document.document import Document
from document.feature import Feature
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


# Test round robin
#robin = RoundRobin()
#leaders = [Document("First document"), Document("Second document")]
#robin.competitors = leaders
#robin.schedule()
#robin.runCompetition()
#print(robin.ranking)


dictQRels = {}
dictStatFeat = {}
dictStatFeatAll = {}
docs = set()
dictStatDoc ={}
dictStatDocAll ={}
collection_name = 'trec_adhoc_lee'

plt.ioff()

with open("/osirim/sig/CORPUS/TREC-ADHOC/QRELS/qrels.351-400.disk4.disk5","r") as qrels :
	for l in qrels :
		tab = l.split(" ")
		#print tab
		q = tab[0]
		doc = tab[2]
		pertinent = False
		dictQRels.setdefault(q,{'pertinent':[],'nonpertinent':[]})
		if "1" in tab[3] :
			dictQRels[q]['pertinent'].append(doc)
		else :
			dictQRels[q]['nonpertinent'].append(doc)	



connection = MongoClient(host='co2-ni01.irit.fr',port=28018)
db = connection.princess
collection = db[collection_name]
queries = collection.distinct('query')
 
nb_match_total = 0
nb_match_total_np = 0
nb_match_query = {}
nb_match_missed_total = 0
nb_match_missed_query = {}
order_feat = {}
k = 20
nb_p_kdomine = 0
nb_np_kdomine = 0

def compareFeatures(p,np,t):
	hash_p = {}
	hash_np = {}
	feats = set()
	p_sup = 0
	np_sup = 0
	kdom_p = False
	kdom_np = False

	for el_p in  p :
		hash_p.setdefault(el_p.name,el_p.value)

	for el_np in  np :
		hash_np.setdefault(el_np.name,el_p.value)

	dom_p = False
	for k, v in hash_p.iteritems():
		if k not in hash_np.keys() :
			if v > 0 :
				dom_p = True
				p_sup += 1
			elif v == 0 : 
				p_sup += 1	

		else :
			if v > hash_np[k] :
				dom_p = True
				p_sup += 1
			elif v == hash_np[k] :	
				p_sup += 1				


	dom_np = False
	for k, v in hash_np.iteritems():
		if k not in hash_p.keys():
			if v > 0 :
				dom_np = True
				np_sup += 1
			elif v == 0 : 
				np_sup += 1	

		else :
			if v > hash_p[k] :
				dom_np = True
				np_sup += 1
			elif v == hash_p[k] :	
				np_sup += 1		


	if dom_np and np_sup >= t and not (dom_p and p_sup >= t) :
		return -1
	elif dom_p and p_sup >= t and not (dom_np and np_sup >= t) :
		return 1
	else :
		return 0		


for q in queries:


	print q
	dict_order_feat = {}
	nb_match_query[q] = 0 
	nb_match_missed_query[q] = 0
	list_doc = {}
	docs = set()
	dictStatDoc[q] = {}
	dictStatFeat[q] = {}

	list = collection.find({'query':q},{'_id':0,'docs':1})
	count = 0
	for i in list :
		for d in i['docs'] :
			#print "**********"
			count += 1
			name = d['doc_name']
			#list_feat = []
			list_feat ={}
			for f in d['features'] :
				list_feat[f] = Feature(f,d['features'][f])	
			list_doc[name] = Document(name,list_feat)

	
	for p in dictQRels[q]['pertinent'] :
		if p in list_doc :
			rankedFeat_p = sorted(list_doc[p].features.values(), key=attrgetter('value'), reverse=True)
			for np in dictQRels[q]['nonpertinent'] :
				if np in list_doc :
					rankedFeat_np = sorted(list_doc[np].features.values(), key=attrgetter('value'), reverse=True)
					val = compareFeatures(rankedFeat_p,rankedFeat_np,k)
					if val == 1 :
						nb_p_kdomine += 1

					nb_match_total += 1



	for i in range(len(dictQRels[q]['nonpertinent'])) :
		np1 = dictQRels[q]['nonpertinent'][i]
		if np1 in list_doc :
			rankedFeat_np1 = sorted(list_doc[np1].features.values(), key=attrgetter('value'), reverse=True)
			for j in range(i+1,len(dictQRels[q]['nonpertinent'])) :
				np2 = dictQRels[q]['nonpertinent'][j]
				if np2 in list_doc :
					rankedFeat_np2 = sorted(list_doc[np2].features.values(), key=attrgetter('value'), reverse=True)
					val = compareFeatures(rankedFeat_np1,rankedFeat_np2,k)
					if val == 1 :
						nb_np_kdomine += 1

					nb_match_total_np += 1





print "pertinent"
ratio_p = float(nb_p_kdomine / nb_match_total)
print "k="+str(k)+" => "+str(nb_p_kdomine)+"/"+str(nb_match_total)+"( "+str(ratio_p)+")"			

print "non pertinent"
ratio_np = float(nb_np_kdomine / nb_match_total_np)
print "k="+str(k)+" => "+str(nb_np_kdomine)+"/"+str(nb_match_total_np)+"( "+str(ratio_np)+")"		

'''
	for p in dictQRels[q]['pertinent'] :

		if p in list_doc :
			rankedFeat_p = sorted(list_doc[p].features.values(), key=attrgetter('value'), reverse=True)
			#print rankedFeat_p
			if p not in docs :
				docs.add(p)
				pos = 0 
				rankedFeat_p = sorted(list_doc[p].features.values(), key=attrgetter('value'), reverse=True)
				str_p =  ','.join(map(str,rankedFeat_p))

				posFeat = 0
				for feat in map(str,rankedFeat_p) :
					dict_order_feat.setdefault(feat,[0]*51)
					dict_order_feat[feat][posFeat] += 1
					posFeat += 1

				order_feat.setdefault(str_p,0)
				order_feat[str_p] += 1

				for fp in rankedFeat_p : 
					dictStatFeat[q].setdefault(fp.name,[0]*51)
					dictStatFeatAll.setdefault(fp.name,[0]*51)
					dictStatFeat[q][fp.name][pos] += 1
					dictStatFeatAll[fp.name][pos] += 1
					pos += 1

			for np in dictQRels[q]['nonpertinent'] :
				if np in list_doc :
					if np not in docs :
						docs.add(np)
						pos = 0 
						rankedFeat_np = sorted(list_doc[np].features.values(), key=attrgetter('value'), reverse=True)
						str_np =  ','.join(map(str,rankedFeat_np))
						order_feat.setdefault(str_np,0)
						order_feat[str_np] += 1

						posFeat = 0
						for feat in map(str,rankedFeat_np) :
							dict_order_feat.setdefault(feat,[0]*51)
							dict_order_feat[feat][posFeat] += 1
							posFeat += 1


						#print rankedFeat_np		
						for fnp in rankedFeat_np : 
							dictStatFeat[q].setdefault(fnp.name,[0]*51)
							dictStatFeatAll.setdefault(fnp.name,[0]*51)
							dictStatFeat[q][fnp.name][pos] += 1
							dictStatFeatAll[fnp.name][pos] += 1
							pos += 1
					
					nb_match_query[q] += 1
					nb_match_total += 1


					for feat in list_doc[p].features.values() :
						if feat.name not in list_doc[np].features :
							if feat.value > 0 : 
								dictStatDoc[q].setdefault(fp.name,0)
								dictStatDocAll.setdefault(fp.name,0)

								dictStatDoc[q][fp.name] += 1
								dictStatDocAll[fp.name] += 1
						else : 	
							if feat.value > list_doc[np].features[feat.name].value : 	
								dictStatDoc[q].setdefault(fp.name,0)
								dictStatDocAll.setdefault(fp.name,0)

								dictStatDoc[q][fp.name] += 1
								dictStatDocAll[fp.name] += 1
				else :
					nb_match_missed_query[q] += 1
					nb_match_missed_total += 1									

		else :
			for np in dictQRels[q]['nonpertinent'] :
				nb_match_missed_query[q] += 1
				nb_match_missed_total += 1

'''



'''
	for key in dict_order_feat.keys() :
		fig,bins, patches = plt.hist(dict_order_feat[key],51,histtype='stepfilled')
		plt.savefig("histograms/"+q+"-"+key)
		plt.clf()
'''
	#print(dict_order_feat)


'''							
	for el in dictStatFeat[q] :
		dictStatFeat[q][el] = [(x*100)/nb_match_query[q] for x in dictStatFeat[q][el]]
	for el in dictStatDoc[q] :	
		dictStatDoc[q][el] = (dictStatDoc[q][el]*100)/nb_match_query[q] 
'''
	#print dictStatFeat[q]
	#print dictStatDoc[q]

'''
for el in dictStatFeatAll :
	dictStatFeatAll[el] = [(x*100)/nb_match_total for x in dictStatFeatAll[el]]
for el in dictStatDocAll :
	dictStatDocAll[el] = (dictStatDocAll[el]*100)/nb_match_total
'''

#print order_feat


#print dictStatFeatAll
#print dictStatDocAll

'''
for q in nb_match_query :
	print "Nb match joue ("+q+") = "+str(nb_match_query[q]) + " / "+str(nb_match_missed_query[q])+" / "+str(len(dictQRels[q]['pertinent'])*len(dictQRels[q]['nonpertinent']))

print "Nb match total = "+str(nb_match_total)
print "Nb match manque = "+str(nb_match_missed_total)
sorted_x = sorted(dictStatDocAll, key=dictStatDocAll.__getitem__, reverse = True)
#sorted_x = sorted(dictStatDocAll.keys(), key=operator.itemgetter(1))
print sorted_x
'''