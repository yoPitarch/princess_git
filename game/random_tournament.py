#! /usr/bin/python
import getopt, sys,random
from game import *
from operator import attrgetter

class  RandomTournament(Tournament):  
	''' ==========================================
	Name: RandomTournament
	Creation: April, 15th 2014
    Author: Y. Pitarch (pitarch@irit.fr)
    Last modification: April, 15th 2014
    Description: 
    ==========================================
	'''
    
	def __init__(self,query=None,impact=0,health=0,nbFeat=0,strategy=1,nbRound=10,featsToRemove=[],qrel={},accepted=False,listStd={}):
		'''
        Constructor:
            - Set the number of round to 1
            - Initialisation of board
		'''
		Tournament.__init__(self,query,impact,health,nbFeat,strategy,nbRound,featsToRemove,qrel,accepted)
		self.board = []
		self._competitors = []
		self.results = {}
		self.listStd = listStd
		#self.ranking = {}
		self.nb_round = 1

		#print self.qrel

		for idX in range(self.nb_round):
			self.board.append(list())



	def schedule(self):
		return ""


	def _set_competitors(self,leaders):
		return ""

	def _get_competitors(self):
		return _competitors
    
	def runCompetition(self):
		return ""

	def setCompetitors(self,listCompetitors):
		self._competitors = listCompetitors
		if len(self.featsToRemove) > 0 :
			for c in self._competitors :
				if not self.accepted :
					c.features = [x for x in c.features if x.name not in self.featsToRemove]
				else:
					c.features = [x for x in c.features if x.name in self.featsToRemove]				


	def printResults(self,path):

		file = open(path+"result_"+self.query+".txt", "w")
		#print "=============================\n    RESULTS    \n============================="
		random.shuffle(self._competitors)
		#self._competitors = sorted(self._competitors, key=attrgetter('score'), reverse=True)
		counter = 1
		for current_doc in self._competitors:
			file.write("{0} Q0 {1} {2} {3} {4}-princess\n".format(self.query,current_doc.name,counter,current_doc.score,self.query));
			counter += 1
		#print current_doc

		file.close()
