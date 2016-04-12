#! /usr/bin/python
import getopt, sys
from game import *
from operator import attrgetter

seedSet = set()

class  Seed(Tournament):  
	''' ==========================================
	Name: Seed
	Creation: September, 11th 2015
    Author: G. Hubert (hubert@irit.fr)
    Last modification: September, 11th 2015
    Description: 
    ==========================================
	'''

	def __init__(self,query=None,impact=0,health=0,nbFeat=0,strategy=1,nbRound=10,featsToRemove=[],qrel={},accepted=False,model="f45",optim="order",listStd = {}):
		'''
        Constructor:
            - Set the number of round to 1
            - Initialisation of board
		'''
		Tournament.__init__(self,query,impact,health,nbFeat,strategy,nbRound,featsToRemove,qrel,accepted,optim)
		self.board = []
		self._competitors = []
		self.listStd = listStd
		self.results = {}
		#self.ranking = {}
		self.nb_round = 1

		self.model = model

		#print self.qrel

		for idX in range(self.nb_round):
			self.board.append(list())


	def schedule(self):

		#print "Size competitors =>"+str(len(self._competitors))
		for id_x in range(len(self._competitors)):
			for id_y in range(id_x+1,len(self._competitors)):
				self.board[0].append(Match(self._competitors[id_x],self._competitors[id_y],impact=self.impact,health=self.health,nbFeat=self.nbFeat,strategy=self.strategy,optim=self.optim))


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

		boost = 3.0

		count = 1
		for id_round in range(len(self.board)):
			for id_match in range(len(self.board[id_round])):
				current_match = self.board[id_round][id_match]
				(points_a, points_b,draw_point) = current_match.run(self.listStd) # Run the match and get the respective number of points

				#if points_a > points_b and current_match.doc_a.name not in seedSet and current_match.doc_b.name in seedSet:
				if points_a > points_b and current_match.doc_b.name in seedSet:
					current_match.doc_a.score += boost * points_a
					#print "1 " +current_match.doc_a.name+" "+str(current_match.doc_a.score)
				#elif points_a < points_b and current_match.doc_b.name not in seedSet and current_match.doc_a.name in seedSet:
				elif points_a < points_b and current_match.doc_a.name in seedSet:
					current_match.doc_b.score += boost * points_b
					#print "2 " +current_match.doc_b.name+" "+str(current_match.doc_b.score)
				else :
					current_match.doc_a.score += points_a
					current_match.doc_b.score += points_b

				if len(self.qrel) > 0 : 

					pertinent_a = False
					if current_match.doc_a.name in self.qrel :
						pertinent_a = self.qrel[current_match.doc_a.name]
					pertinent_b = False
					if current_match.doc_b.name in self.qrel :
						pertinent_b = self.qrel[current_match.doc_b.name]

					if pertinent_a and not pertinent_b :
						if points_a > points_b :
							self.stats[0] += 1
						elif points_a < points_b :
							self.stats[1] += 1
						else :
							self.stats[2] += 1	

					if pertinent_b and not pertinent_a :
						if points_a > points_b :
							self.stats[1] += 1
						elif points_a < points_b :
							self.stats[0] += 1
						else :
							self.stats[2] += 1						

				current_match.doc_a.opponents.append(current_match.doc_b.name)
				current_match.doc_b.opponents.append(current_match.doc_a.name)
				#if count % 1000 == 0 :
					#print str(count)+"/"+str(len(self.board[id_round]))
				count += 1
                # Il manque a enregistrer le resultat de la partie (doit on le faire ? => En suspens)

	def setCompetitors(self,listCompetitors):
		global seedSet

		self._competitors = listCompetitors
		if len(self.featsToRemove) > 0 :
			for c in self._competitors :
				if not self.accepted :
					c.features = dict((key,value) for key, value in c.features.iteritems() if key not in self.featsToRemove)
					#c.features = [x for x in c.features if x.name not in self.featsToRemove]
				else:
					c.features = dict((key,value) for key, value in c.features.iteritems() if key in self.featsToRemove)
					#c.features = [x for x in c.features if x.name in self.featsToRemove]			
		
		self._competitors.sort(key = lambda x: x.features[self.model].value, reverse = True)

		seedSet = set()

		for c in self._competitors[0:min(20,int(len(self._competitors)*0.20))] :
			seedSet.add(c.name)

		#print seedSet

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
