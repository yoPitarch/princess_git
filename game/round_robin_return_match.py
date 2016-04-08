#! /usr/bin/python
import getopt, sys
from game import *
from operator import attrgetter

class  RoundRobinReturnMatch(Tournament):  
	''' ==========================================
	Name: RoundRobinReturnMatch
	Creation: May, 18th 2015
    Author: Princess team (princess@irit.fr)
    Last modification: May, 18th 2015
    Description: 
    ==========================================
	'''
    
	def __init__(self,query=None,impact=0,health=0,nbFeat=0,strategy=1,nbRound=10,featsToRemove=[],accepted=False,optim="order"):
		'''
        Constructor:
            - Set the number of round to 1
            - Initialisation of board
		'''
		Tournament.__init__(self,query,impact,health,nbFeat,strategy,nbRound,featsToRemove,accepted,optim)
		self.board = []
		self._competitors = []
		self.results = {}
#        self.ranking = {}
		self.nb_round = 1
		for idX in range(self.nb_round):
			self.board.append(list())



	def schedule(self):
		#print "Size competitors =>"+str(len(self._competitors))
		for id_x in range(len(self._competitors)):
			for id_y in range(id_x+1,len(self._competitors)):
				self.board[0].append(Match(self._competitors[id_x],self._competitors[id_y],impact=self.impact,health=self.health,nbFeat=self.nbFeat,strategy=self.strategy,start=1,optim=self.optim))
		for id_x in range(len(self._competitors)):
			for id_y in range(id_x+1,len(self._competitors)):
				self.board[0].append(Match(self._competitors[id_x],self._competitors[id_y],impact=self.impact,health=self.health,nbFeat=self.nbFeat,strategy=self.strategy,start=2,optim=self.optim))		
#print self.board[0]


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

	def runCompetition(self):

		self.schedule()

		count = 1
		for id_round in range(len(self.board)):
			for id_match in range(len(self.board[id_round])):
				current_match = self.board[id_round][id_match]
				(points_a, points_b,draw_point) = current_match.run() # Run the match and get the respective number of points
				current_match.doc_a.score += points_a
				current_match.doc_b.score += points_b
				current_match.doc_a.opponents.append(current_match.doc_b.name)
				current_match.doc_b.opponents.append(current_match.doc_a.name)
				#print str(count)+"/"+str(len(self.board[id_round]))
				count += 1
                # Il manque a enregistrer le resultat de la partie (doit on le faire ? => En suspens)


	def printResults(self,path):
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
