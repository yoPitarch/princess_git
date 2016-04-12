#! /usr/bin/python
import getopt, sys, random
from math import *
from game import *
from operator import attrgetter

class  GroupSwissOptim(Tournament):  
	''' ==========================================
	Name: GroupStage
	Creation: June, 9th 2015
    Author: Y. Pitarch (pitarch@irit.fr)
    Last modification: June, 9th 2015
    Description: 
    ==========================================
	'''
    
	def __init__(self,query=None,impact=0,health=0,nbFeat=0,strategy=1,nbRound=10,featsToRemove=[],qrel={},nbGroups=4,best=0.1,accepted=False,model="f45",optim="order",listStd={}):
		'''
        Constructor:
            - Set the number of round to 1
            - Initialisation of board
		'''
		Tournament.__init__(self,query,impact,health,nbFeat,strategy,nbRound,featsToRemove,qrel,accepted,optim)
		self.board = []
		self._competitors = []
		self.results = {}
		self.listStd = listStd
		self.nb_round = nbRound
		self.nb_groups = nbGroups
		self.best = best
		self.groups =[]
		self.swisses =[]
		self.model = model

		for idX in range(self.nb_groups):
			self.swisses.append(SwissSystem(query=query,impact=impact,health=health,nbFeat=nbFeat,strategy=strategy,nbRound=nbRound,featsToRemove=featsToRemove,optim=optim,listStd=self.listStd))

		self.swisses.append(SwissSystem(query=query,impact=impact,health=health,nbFeat=nbFeat,strategy=strategy,nbRound=nbRound,featsToRemove=featsToRemove,optim=optim,listStd=self.listStd))




	def schedule(self):

		#First let split into nb_groups the competitor list
		self._competitors.sort(key = lambda x: x.features[self.model].value, reverse = True)

		for i in range(self.nb_groups):
			self.groups.append([])

		for i in range(len(self._competitors)) :
			idGroup = i % self.nb_groups
			self.groups[idGroup].append(self._competitors[i])			

		#random.shuffle(self._competitors)
		#self.groups = [self._competitors[i::self.nb_groups] for i in range(self.nb_groups)]

		#print self.groups


		for idGroup in range(self.nb_groups):
			self.swisses[idGroup].setCompetitors(self.groups[idGroup])


	def _set_competitors(self,leaders):
		self._competitors = list(leaders)
		self.results = {}
		self.ranking = {}
		for doc in self._competitors:
			self.results[doc.name] = list()
			doc.score = 0

	def _get_competitors(self):
		return _competitors

	competitors = property(_get_competitors, _set_competitors) #Competitor description
    
	def runCompetition(self):

		self.schedule()

		count = 1
		for idGroup in range(self.nb_groups):
			self.swisses[idGroup].runCompetition()
			#print self._competitors


		

		# It's time to order the groups by score    
		finalist = []
		for group in self.groups:
			group = sorted(group, key=attrgetter('score'), reverse=True)
			nbFinalist = int(ceil(float(len(group)*self.best)))
			finalist.extend(group[:nbFinalist])

		#print "Size of finalist: "+str(len(finalist))
		self.swisses[self.nb_groups].setCompetitors(finalist)
		self.swisses[self.nb_groups].runCompetition()




	def setCompetitors(self,listCompetitors):
		self._competitors = listCompetitors
		if len(self.featsToRemove) > 0 :
			for c in self._competitors :
				if not self.accepted :
					c.features = dict((key,value) for key, value in c.features.iteritems() if key not in self.featsToRemove)
					#c.features = [x for x in c.features if x.name not in self.featsToRemove]
				else:
					c.features = dict((key,value) for key, value in c.features.iteritems() if key in self.featsToRemove)
					#c.features = [x for x in c.features if x.name in self.featsToRemove]		

	def printResults(self,path):

		if len(self.qrel) > 0 : 
			print "=============================  "+self.query+"  ============================="
			print "Victoire pertinent sur pertinent: "+str(self.stats[0])
			print "Defaite pertinent sur non pertinent: "+str(self.stats[1])
			print "Match nul: "+str(self.stats[2])

		file = open(path+"result_"+self.query+".txt", "w")
		#print "=============================\n    RESULTS    \n============================="
		self._competitors = sorted(self._competitors, key=attrgetter('score'), reverse=True)
		counter = 1
		for current_doc in self._competitors:
			file.write("{0} Q0 {1} {2} {3} {4}-princess\n".format(self.query,current_doc.name,counter,current_doc.score,self.query));
			counter += 1
		#print current_doc

		file.close()
		
	def printResultsLetor(self,path):

		file = open(path+"result_"+self.query+".txt", "w")
		file2 = open(path+"details_"+self.query+".txt","w")

		#print "=============================\n    RESULTS    \n============================="
		self._competitors = sorted(self._competitors, key=attrgetter('position'), reverse=False)
		for current_doc in self._competitors:
			file.write("{0}\n".format(current_doc.score));
			file2.write("{0} {1} {2} {3}\n".format(self.query,current_doc.name,current_doc.score,current_doc.position));
		file.close()
		file2.close()
