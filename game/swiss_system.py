#! /usr/bin/python
# -*- coding: utf-8 -*-

from operator import itemgetter, attrgetter
import pymongo
from pymongo import MongoClient


from pypair import SwissTournamentAPI
from game import *

class  SwissSystem(Tournament):  
	""" ==========================================
	Name: SwissSystem
	Creation: April, 15th 2014
	Author: Y. Pitarch (pitarch@irit.fr)
	Last modification: April, 15th 2014
	Description: 
	Assumptions:
		(1) Features are not calculated in this class
		(2) The function get_most_similar_documents(query) returns 
			the list of the most similar documents
		(3) It exists an attribute 'sim' in the Document class
	========================================== """

	
	def __init__(self,query=None,impact=0,health=0,nbFeat=0,strategy=1,nbRound=10,featsToRemove=[],accepted=False, optim="order"):
		"""
		Constructor:
			- Set the number of round to 1
			- Initialisation of board
		"""
		self.tournament = SwissTournamentAPI()
	  #  self.ranking = {} # Store the on-going ranking 
		self.nb_rounds = nbRound
		self.mappingDoc = {}
		self.dictDoc ={}
		self._competitors = []
		Tournament.__init__(self,query,impact,health,nbFeat,strategy,nbRound,featsToRemove,accepted,optim)


	def setCompetitors(self,listCompetitors):
		count = 0
		self._competitors = listCompetitors
		if len(self.featsToRemove) > 0 :
			for c in self._competitors :
				if not self.accepted :
					c.features = dict((key,value) for key, value in c.features.iteritems() if key not in self.featsToRemove)
					#c.features = [x for x in c.features if x.name not in self.featsToRemove]
				else:
					c.features = dict((key,value) for key, value in c.features.iteritems() if key in self.featsToRemove)
					#c.features = [x for x in c.features if x.name in self.featsToRemove]					

		for doc in listCompetitors:
			self.tournament.addPlayer( count, doc.name )
			self.mappingDoc[count] = doc
			self.dictDoc[doc.name]=count
			count += 1

	def runCompetition(self):
		for i in range(self.nb_rounds):
			pairings = self.tournament.pairRound()
			for table in pairings:
				if not type(pairings[table]) is str:
					idPlayer1 = self.tournament.roundPairings[table][0]
					idPlayer2 = self.tournament.roundPairings[table][1]

					m = Match(self.mappingDoc[idPlayer1],self.mappingDoc[idPlayer2],impact=self.impact,health=self.health,nbFeat=self.nbFeat,strategy=self.strategy,optim=self.optim)
					self.tournament.reportMatch(table,m.run())
		self.feedCompetitors()


	def feedCompetitors(self):
	   # print len(self.dictDoc.keys())
	   # print len(self.tournament.playersDict.keys())
	   # print len(self._competitors)
		for id in self.tournament.playersDict.keys():
			doc = self.tournament.playersDict[id]
		   # print self.dictDoc[doc["Name"]]
			self._competitors[self.dictDoc[doc["Name"]]].score = doc["Points"]




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






'''
	def schedule(self,id_round):
		"""
		Schedule the round id_round
		The adopted swiss system is 'Système accéléré Bruntrutain'
		It is thus required to: 
			(1) Order documents by similarity
			(2) Split them into nb_groups groups
			(3) Make the pairing accordingly
			(4) Add fictive points to group members accordingly
		"""
		points_max = self.nb_groups - id_round

		if id_round == 1 :
			# Order
			self._competitors = sorted(self._competitors, key=attrgetter('sim'), reverse=True) # order documents/sim
			#print self._groups
			# Split into groups

			for index,current_doc in enumerate(self._competitors): # Split them into nb_groups groups
				print ("Length competitors : {0}".format(len(self._competitors)))
				self._groups[int(index/(len(self._competitors)/self.nb_groups))].append(current_doc)
				#print self._groups
			# Pairing
			for current_tuple_group in enumerate(self._groups):
				current_group = current_tuple_group[1]
				for id_current_doc in range(int(len(current_group)/2)):  # A voir comment on définiti le board (dictionnaire commencant par 1)
					id_opponent = len(current_group) - id_current_doc - 1
					self.board[id_round].append(Match(current_group[id_current_doc],current_group[id_opponent]))
					current_group[id_current_doc].opponents.append(current_group[id_opponent].name) # Ajout de l'un comme opposant de l'autre
					current_group[id_opponent].opponents.append(current_group[id_current_doc].name) # Ajout de l'autre comme opposant de l'un
			# Add fictive points
			for id_x in range(0,points_max):
				for current_doc in self._groups[id_x]:
					current_doc.score += (points_max - id_x)
			print "========== Affichage des groupes (round {0}) ==========".format(id_round)
			print self._groups
			print "========== Affichage du board (round {0}) ==========".format(id_round)
			print self.board
			print "========== End affichage =========="

		else:
			print("Let's schedule round {0}".format(id_round))
			# Order
			self._competitors = sorted(self._competitors, key=attrgetter('score'), reverse=True) # order documents/sim
			# Group reinitialization
			self._groups = []
			for id_x in range(self.nb_groups):
				self._groups.append(list())
			# Split into groups    
			for index,current_doc in enumerate(self._competitors): # Split them into nb_groups groups
				self._groups[int(index/(len(self._competitors)/self.nb_groups))].append(current_doc)
			# Pairing
			_comp = [x.name for x in self._competitors]
			print "-----------------"            
			print _comp
			print "-----------------"

			for current_id_group, current_group in enumerate(self._groups):
				for current_id_doc, current_doc in enumerate(current_group): 
					if _comp.count(current_doc.name) > 0: # S'il ne fait pas déjà parti d'un match
						current_id_doc_in_comp = _comp.index(current_doc.name)
						opponent_name = ""
						for current_id_potential_opponent in range(current_id_doc_in_comp+1,len(_comp)): # A la recherche du candidat (non encore affronté) le plus proche du doc
							if current_doc.opponents.count(_comp[current_id_potential_opponent]) == 0:
								opponent_name = _comp[current_id_potential_opponent]
								break
						opponent_doc = self.find_opponent_doc(opponent_name)
						
						_comp = [ x for x in _comp if x != opponent_name and x != current_doc.name] # cette ligne remplace les deux suivantes
					   # _comp.remove(current_doc.name) # On les supprime des candidats potentiels
					   # _comp.remove(opponent_name)
						self.board[id_round].append(Match(current_doc,opponent_doc))
						current_doc.opponents.append(opponent_name) # Ajout de l'un comme opposant de l'autre
						opponent_doc.opponents.append(current_doc.name) # Ajout de l'autre comme opposant de l'un

			#print self.board
			# Add fictive points
			for id_x in range(0,points_max):
				for current_doc in self._groups[id_x]:
					current_doc.score += (points_max - id_x)
			print "========== Affichage des groupes (round {0}) ==========".format(id_round)
			print self._groups
			print "========== Affichage du board (round {0}) ==========".format(id_round)
			print self.board
			print "========== End affichage =========="


	def find_opponent_doc(self,name):
		for current_doc in self._competitors:
			if current_doc.name == name:
				return current_doc


	def _set_competitors(self,leaders):
		self._competitors = list(leaders)
		self.results = {}
	   # self.ranking ={}
		for doc in self._competitors:
			self.results[doc.name] = list()
			doc.score = 0 

	def _get_competitors(self):
	   return _competitors

	competitors = property(_get_competitors,_set_competitors)

	def run_round_k(self, k):
		for current_match in self.board[k]:
			(point_a, point_b) = current_match.run() # Run the match and get the respective number of points
			current_match.doc_a.score += point_a
			current_match.doc_b.score += point_b
			#self.ranking[current_match.doc_a.name] += point_a
			#self.ranking[current_match.doc_b.name] += point_b

	def print_results(self):
		
		file = open("result_prelim.txt", "w")
		print "=============================\n    RESULTS    \n============================="
		self._competitors = sorted(self._competitors, key=attrgetter('score'), reverse=True)
		counter = 1
		for current_doc in self._competitors:
			file.write("{0} Q0 {1} {2} {3} {4}-princess\n".format(Tournament.query,current_doc.name,counter,current_doc.score,Tournament.query));
			print current_doc
			counter += 1
		file.close()

'''
