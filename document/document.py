#! /usr/bin/python
#import pymongo
#from pymongo import MongoClient

import random

class Document(object):
	""" ==========================================
    Name: Match
    Creation: April, 15th 2014
    Author: Y. Pitarch (pitarch@irit.fr)
    Last modification: April, 15th 2014
    Description: 
	========================================== """	

	def __init__(self,name,feats=None,pos=None):
		"Constructor with feats being facultative"
		self.name = name
		self.features = dict(feats) if feats is not None else {}
		#self.features = list(feats) if feats is not None else list()
		#print self.features
		self.sim = random.random() # for debugging purpose
		self.score = 0 
		self.opponents = []
		self.position = pos if pos is not None else 0
		#generateOppponents

	def __str__(self):
		"Providing the user with a nice string representation of the document"
		return "{0} (features={1})".format(self.name,self.features)

	def __repr__(self):
		"Providing the user with a nice string representation of the document"
		#return "{} (score={})".format(self.name,str(self.score))
		return self.name+": "+str(self.score)
