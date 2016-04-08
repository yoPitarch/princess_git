#! /usr/bin/python
import sys
import pymongo
from pymongo import MongoClient

from document.document import Document
from document.feature import Feature

class  Tournament(object):
	""" ==========================================
	Name: Tournament
	Creation: April, 15th 2014
	Author: Y. Pitarch (pitarch@irit.fr)
	Last modification: April, 15th 2014
	Description: 
	========================================== """


	def __init__(self,query,impact=0,health=0,nbFeat=0,strategy=1,nbRound=1,featsToRemove=[],qrel={},accepted=False,optim="order",verbose=True):
		#print("initialisation of Tournament")
		self.query = query
		self.verbose = verbose
		self.collection_name = "trec_adhoc" # semble inutile
		self.nb_documents = 0 #semble inutile
		self.impact=impact
		self.health=health
		self.nbFeat=nbFeat
		self.strategy=strategy
		self._competitors = [] 
		self.featsToRemove = featsToRemove
		self.qrel =qrel
		self.stats = [0,0,0]  # ind = 0 victoire Pertinent non sur pertinent / ind = 1 defaite pertinent sur non pertinent / ind = 2 match nul 
		self.accepted = accepted
		self.optim = optim




					

