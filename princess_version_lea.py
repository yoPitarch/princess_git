#! /usr/bin/python

import random
import os
import getopt, sys
import subprocess 
from game import *
from document.document import Document
from document.feature import Feature


#Path des fichiers de donnees LETOR
pathLETOR = "/projets/sig/PROJET/PRINCESS/LETOR/data/"

# Test round robin
#robin = RoundRobin()
#leaders = [Document("First document"), Document("Second document")]
#robin.competitors = leaders
#robin.schedule()
#robin.runCompetition()
#print(robin.ranking)


dictQRels = {}

def evaluateQRels(collection_name):
	# One tournament per query
	# with open("/osirim/sig/CORPUS/TREC-ADHOC/QRELS/qrels.351-400.disk4.disk5","r") as qrels :
	collections_infos = collection_name.split('_')
	collection = collections_infos[0]
	fold = collections_infos[1]
	with open(pathLETOR + collection + "/" + fold + "/test.txt","r") as qrels :
		for l in qrels :
			l = l.rstrip()
			tab = l.split(" ")
			end = l.split("#docid")
			#print tab
			q = tab[1].split(":")[1]
			doc = end[1].split(" = ")[1].split(" ")[0]
			pertinent = False
			if tab[0] is not "0" :
				pertinent = True
			if q not in dictQRels.keys():
				dictQRels[q] = {}
			dictQRels[q][doc]=pertinent

def main():

	# Handle user options
	try:
		opts,args = getopt.getopt(sys.argv[1:], "dht:i:l:s:n:r:f:vc:b:g:am:o:", ["debug","help", "type=", "impact=", "life=", "strategy=","nbFeats=", "rounds=",  "featureList=", "verbose",'collection=','group=','accepted','model=','optim'])
	except getopt.GetoptError as err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
    # Set the default values
	
	optim = "order"
	debug = False
	nb_rounds = 10
	nb_groups = 10
	nb_documents = 16
	nbFeats = 0
	group = 1
	type_tournament = "robin"
	collection_name = 'HP2003'
	output_directory = "/projets/sig/PROJET/PRINCESS/code/result_letor/"
	impact = 0
	features_to_remove = []
	strategy =1
	life=0
	best= 0.1
	accepted = False
	verbose = False
	model = "1"

	#strategy = ['f48', 'f17', 'f19', 'f16', 'f46', 'f9', 'f21', 'f3', 'f39', 'f7', 'f40', 'f6', 'f37', 'f42', 'f2', 'f15', 'f25', 'f33', 'f36', 'f10', 'f30', 'f51', 'f28', 'f43', 'f45', 'f34', 'f24', 'f13', 'f50', 'f27', 'f31', 'f1', 'f35', 'f14', 'f47', 'f41', 'f4', 'f22', 'f12', 'f8', 'f26', 'f44']

	for o, a in opts:
		if o in ("-v","--verbose"):
			verbose = True
		elif o in ("-a","--accepted"):
			accepted = True	
		elif o in ("-o","--optim"):
			optim = a	
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-t", "--type"):
			type_tournament = a	
		elif o in ("-g", "--group"):
			group = int(a)				
		elif o in ("-f", "--featureList"):
			features_to_remove = str(a).split(",")
			print features_to_remove
		elif o in ("-r", "--rounds"): 
			nb_rounds = int(a)
		elif o in ("-m", "--model"): 
			model = str(a)			
		elif o in ("-b", "--best"): 
			best = float(a)			
		elif o in ("-c", "--collection"):
			collection_name = a	
		elif o in ("-i","--impact"):
			impact = int(a)
		elif o in ("-l","--life"):
			life = int(a)
		elif o in ("-n","--nbFeats"):
			nbFeats = int(a)
		elif o in ("-s","--strategy"):
			strategy = int(a)		
		elif o in ("-d", "--debug"):
			debug = True
			evaluateQRels(collection_name)																																				
		else:
			assert False, "unhandled option"


	# One tournament per query
	#connection = MongoClient(host='co2-ni01.irit.fr',port=28018)
	#db = connection.princess
	#collection = db[collection_name]
	collections_infos = collection_name.split('_')
	collection = collections_infos[0]
	fold = collections_infos[1]
	queries = {}
	evaluateQRels(collection_name)
	qname = pathLETOR + collection + "/" + fold + "/qids.txt"
	with open(qname,"r") as qids :
		qInd = 1
		for q in qids :
			qid = q.replace('\n','')
			queries[qInd] = qid
			qInd += 1

	outputFolderName= ''

	if len(features_to_remove) > 0 :
		outputFolderName='t:'+type_tournament+'-o:'+optim+'-r:'+str(nb_rounds)+'-b:'+str(best)+'-c:'+collection_name+'-i:'+str(impact)+'-l:'+str(life)+'-n:'+str(nbFeats)+'-s:'+str(strategy)+'-g:'+str(group)+'-f:'+','.join(features_to_remove)
		if accepted :
			outputFolderName+='-a'
	else :
		outputFolderName='t:'+type_tournament+'-o:'+optim+'-r:'+str(nb_rounds)+'-b:'+str(best)+'-c:'+collection_name+'-i:'+str(impact)+'-l:'+str(life)+'-n:'+str(nbFeats)+'-s:'+str(strategy)+'-g:'+str(group)

	outputFolderName+='/'	
	output_directory += outputFolderName

	if not os.path.exists(output_directory):
		os.makedirs(output_directory)
	
	fname = pathLETOR + collection + "/" + fold + "/test.txt"

	#print dictQRels

	for q in queries.values():
		print "Query "+q
		count = 0
		list_doc = []
		toFind = "qid:"+q
		qExtract = subprocess.Popen('grep %s %s'%(toFind,fname),stdout=subprocess.PIPE,shell=True)
		#print qExtract.communicate()[0]

		for line in qExtract.stdout.readlines() :
			count += 1
			line = line.rstrip()
			tab = line.split("#docid = ")
			docId = tab[1].rstrip().split(' ')[0]
			tmp = tab[0].rstrip().split(' ')
			qId = tmp[1].split('qid:')[1]
			list_feat = {}
			for i in range(2,len(tmp)):
				f = tmp[i].split(":")
				name = f[0]
				list_feat[name] = Feature(name,float(f[1]))
			if model not in list_feat.keys():
				list_feat[model] = Feature(model,0.0)
			list_doc.append(Document(docId,list_feat,count))

		
		if type_tournament == "robin" :
			to = RoundRobin(query=q,impact=impact,health=life,nbFeat=nbFeats,strategy=strategy,nbRound=nb_rounds,featsToRemove=features_to_remove,qrel=dictQRels[q],accepted=accepted,optim=optim)
		elif type_tournament == "return" :
			to = RoundRobinReturnMatch(query=q,impact=0,health=life,nbFeat=nbFeats,strategy=strategy,nbRound=nb_rounds,featsToRemove=features_to_remove,accepted=accepted,optim=optim)
		elif type_tournament == "swiss" :
			to = SwissSystem(query=q,impact=impact,health=life,nbFeat=nbFeats,strategy=strategy,nbRound=nb_rounds,featsToRemove=features_to_remove,accepted=accepted,optim=optim)
		elif type_tournament == "random" :
			to = RandomTournament(query=q,impact=impact,health=life,nbFeat=nbFeats,strategy=strategy,nbRound=nb_rounds,featsToRemove=features_to_remove,qrel=dictQRels[q],accepted=accepted,optim=optim)
		elif type_tournament == "grouprobin" :
			to = GroupStage(query=q,impact=impact,health=life,nbFeat=nbFeats,strategy=strategy,nbGroups=group,featsToRemove=features_to_remove,qrel=dictQRels[q],best=best,accepted=accepted,optim=optim)
		elif type_tournament == "grouprobinoptim" :
			to = GroupStageOptim(query=q,impact=impact,health=life,nbFeat=nbFeats,strategy=strategy,nbGroups=group,featsToRemove=features_to_remove,qrel=dictQRels[q],best=best,accepted=accepted,model=model,optim=optim)			
		elif type_tournament == "groupswiss" :
			to = GroupSwiss(query=q,impact=impact,health=life,nbFeat=nbFeats,strategy=strategy,nbGroups=group,nbRound=nb_rounds,featsToRemove=features_to_remove,qrel=dictQRels[q],best=best,accepted=accepted,optim=optim)
		elif type_tournament == "groupswissoptim" :
			to = GroupSwissOptim(query=q,impact=impact,health=life,nbFeat=nbFeats,strategy=strategy,nbGroups=group,nbRound=nb_rounds,featsToRemove=features_to_remove,qrel=dictQRels[q],best=best,accepted=accepted,model=model,optim=optim)				
		elif type_tournament == "seed" :
			to = Seed(query=q,impact=impact,health=life,nbFeat=nbFeats,strategy=strategy,nbRound=nb_rounds,featsToRemove=features_to_remove,qrel=dictQRels[q],accepted=accepted,model=model,optim=optim)
		elif type_tournament == "upper" :
			to = Upper(query=q,impact=impact,health=life,nbFeat=nbFeats,strategy=strategy,nbRound=nb_rounds,featsToRemove=features_to_remove,qrel=dictQRels[q],accepted=accepted,model=model,optim=optim)
        
		print "setCompetitors"	
		to.setCompetitors(list_doc)
		
		print "runCompetition"
		to.runCompetition()
		
		print "printResults"
		to.printResultsLetor(output_directory)


"""		
		# Generation aleatoire de documents 
		leaders = []
		random.seed()
		for i in range(nb_documents):
			feats =[]
			for j in range(nb_features):
				feats.append(Feature("F"+str(j),random.randint(0,10)))
			doc = Document("Document "+str(i),feats)
			print doc
			leaders.append(doc)
		swiss.competitors = leaders

		
		for id_x in range(1,nb_rounds):
			swiss.schedule(id_x)
			swiss.run_round_k(id_x)

		swiss.print_results()
		sys.exit()
"""


def usage():
	print "Usage: \
		-h [--help] Print this help \n\
		-t [--type] Set the type of the tournament \n\
		-d [--documents] Set the number of documents that shall participate to the final tournament (preferably a power of 2) \n \
		-r [--rounds] Set the number of rounds in the swiss style tournament \n\
		-g [--groups] Set the nuumber of groups in the swiss style tournament \n\
		-v [--verbose] Activate the verbose mode (for debugging purpose)"	


def function_to_debug():
	doc_a = Document("DocA",[Feature("f0",10),Feature("f1",5),Feature("f2",10),Feature("f3",20),Feature("f4",10),Feature("f5",10),Feature("f6",10)])
	doc_b = Document("DocB",[Feature("f0",10),Feature("f3",5),Feature("f5",8),Feature("f6",1)])

	m = Match(doc_a,doc_b)
	m.elaborated_match_v2()

	sys.exit(0)

if __name__ == "__main__":
    main()		
    #function_to_debug()


