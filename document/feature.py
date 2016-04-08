#! /usr/bin/python

class Feature(object):

	def __init__(self,name,value):
		self.name =  name
		self.value = value

	def __str__(self):
		#return "{}: {}".format(self.name,self.value)
		#return self.name+" : "+str(self.value)
		return self.name

	def __repr__(self):
		#return "{}: {}".format(self.name,self.value)
		#return self.name+" : "+str(self.value)
		return self.name