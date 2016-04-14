#! /usr/bin/python
import multiprocessing
import pprint
import sys
from operator import attrgetter

from game import *

relStats = {}
irrelStats = {}

class  RoundRobin(Tournament):
    ''' ==========================================
    Name: RoundRobin
    Creation: April, 15th 2014
    Author: Y. Pitarch (pitarch@irit.fr)
    Last modification: April, 15th 2014
    Description: 
    ==========================================
    '''

    def __init__(self, query=None, impact=0, health=0, nbFeat=0, strategy=1, nbRound=10, featsToRemove=[], qrel={},
                 accepted=False, optim="order", listStd={}):
        '''
        Constructor:
            - Set the number of round to 1
            - Initialisation of board
        '''
        Tournament.__init__(self, query, impact, health, nbFeat, strategy, nbRound, featsToRemove, qrel, accepted,
                            optim)
        self.board = []
        self._competitors = []
        self.results = {}
        # self.ranking = {}
        self.nb_round = 1
        self.mapping = {}
        self.listStd = listStd

        #print self.qrel

        for idX in range(self.nb_round):
            self.board.append(list())

    def schedule(self):
        # print "Size competitors =>"+str(len(self._competitors))
        for id_x in range(len(self._competitors)):
            for id_y in range(id_x + 1, len(self._competitors)):
                self.board[0].append(
                    Match(self._competitors[id_x], self._competitors[id_y], impact=self.impact, health=self.health,
                          nbFeat=self.nbFeat, strategy=self.strategy, optim=self.optim))

    def _set_competitors(self, leaders):
        self._competitors = list(leaders)
        self.results = {}
        self.ranking = {}
        for doc in self._competitors:
            self.results[doc.name] = list()
            doc.score = 0

    def _get_competitors(self):
        return self._competitors

    competitors = property(_get_competitors, _set_competitors)  #Competitor description

    def runParallel(self, match, out_q):
        (points_a, points_b, draw_point) = match.run(
            self.listStd)  # Run the match and get the respective number of points
        out_q.put([(match.doc_a.name, points_a), (match.doc_b.name, points_b)])
        # match.doc_a.score += points_a
        # match.doc_b.score += points_b
        # self.mapping[match.doc_a.name].score += points_a
        # self.mapping[match.doc_b.name].score += points_b

    def runCompetition(self):
        global relStats, irrelStats

        self.schedule()

        relStats = {}
        irrelStats = {}

        count = 1

        jobs = []
        out_q = multiprocessing.Queue()
        for id_round in range(len(self.board)):
            for id_match in range(len(self.board[id_round])):

                if count < 5:
                    current_match = self.board[id_round][id_match]
                    # print 'before'
                    # pprint(self.competitors)
                    p = multiprocessing.Process(target=self.runParallel, args=(current_match, out_q))
                    jobs.append(p)
                    p.start()
                    # (points_a, points_b, draw_point) = current_match.run(self.listStd)  # Run the match and get the respective number of points
                    # current_match.doc_a.score += points_a
                    # current_match.doc_b.score += points_b
                    # print 'after'
                    # pprint(self.competitors)
                    # sys.exit(0)
                    count += 1
                """

                if len(self.qrel) > 0 :

                    pertinent_a = False
                    if current_match.doc_a.name in self.qrel:
                        pertinent_a = self.qrel[current_match.doc_a.name]
                    pertinent_b = False
                    if current_match.doc_b.name in self.qrel:
                        pertinent_b = self.qrel[current_match.doc_b.name]

                    if pertinent_a:
                        relStats.setdefault(current_match.doc_a.name, [0, 0, 0, 0, 0, 0])
                    else:
                        irrelStats.setdefault(current_match.doc_a.name, [0, 0, 0, 0, 0, 0])

                    if pertinent_b:
                        relStats.setdefault(current_match.doc_b.name, [0, 0, 0, 0, 0, 0])
                    else:
                        irrelStats.setdefault(current_match.doc_b.name, [0, 0, 0, 0, 0, 0])

                    if pertinent_a and not pertinent_b:
                        if points_a > points_b:
                            self.stats[0] += 1
                            relStats[current_match.doc_a.name][3] += 1
                            irrelStats[current_match.doc_b.name][1] += 1
                        elif points_a < points_b:
                            self.stats[1] += 1
                            relStats[current_match.doc_a.name][4] += 1
                            irrelStats[current_match.doc_b.name][0] += 1
                        else:
                            self.stats[2] += 1
                            relStats[current_match.doc_a.name][2] += 1
                            irrelStats[current_match.doc_b.name][5] += 1
                    elif pertinent_b and not pertinent_a:
                        if points_a > points_b:
                            self.stats[1] += 1
                            relStats[current_match.doc_b.name][4] += 1
                            irrelStats[current_match.doc_a.name][0] += 1
                        elif points_a < points_b:
                            self.stats[0] += 1
                            relStats[current_match.doc_b.name][3] += 1
                            irrelStats[current_match.doc_a.name][1] += 1
                        else:
                            self.stats[2] += 1
                            relStats[current_match.doc_b.name][2] += 1
                            irrelStats[current_match.doc_a.name][5] += 1
                    elif pertinent_a and pertinent_b:
                        if points_a > points_b:
                            # self.stats[1] += 1
                            relStats[current_match.doc_a.name][0] += 1
                            relStats[current_match.doc_b.name][1] += 1
                        elif points_a < points_b:
                            # self.stats[0] += 1
                            relStats[current_match.doc_b.name][0] += 1
                            relStats[current_match.doc_a.name][1] += 1
                        else:
                            # self.stats[2] += 1
                            relStats[current_match.doc_b.name][2] += 1
                            relStats[current_match.doc_a.name][2] += 1
                    else:
                        if points_a > points_b:
                            # self.stats[1] += 1
                            irrelStats[current_match.doc_a.name][3] += 1
                            irrelStats[current_match.doc_b.name][4] += 1
                        elif points_a < points_b:
                            # self.stats[0] += 1
                            irrelStats[current_match.doc_b.name][3] += 1
                            irrelStats[current_match.doc_a.name][4] += 1
                        else:
                            # self.stats[2] += 1
                            irrelStats[current_match.doc_b.name][5] += 1
                            irrelStats[current_match.doc_a.name][5] += 1

                """


                # current_match.doc_a.opponents.append(current_match.doc_b.name)
                # current_match.doc_b.opponents.append(current_match.doc_a.name)
                # if count % 1000 == 0 :
                # print str(count)+"/"+str(len(self.board[id_round]))
                # count += 1
                # Il manque a enregistrer le resultat de la partie (doit on le faire ? => En suspens)

        for j in jobs:
            j.join()

        while not out_q.empty():
            print out_q.get()
        # pprint.pprint(out_q)
        pprint.pprint(self._competitors)
        sys.exit()

    def setCompetitors(self, listCompetitors):
        self._competitors = listCompetitors
        if len(self.featsToRemove) > 0:
            for c in self._competitors:
                if not self.accepted:
                    c.features = dict(
                        (key, value) for key, value in c.features.iteritems() if key not in self.featsToRemove)
                    # c.features = [x for x in c.features if x.name not in self.featsToRemove]
                else:
                    c.features = dict(
                        (key, value) for key, value in c.features.iteritems() if key in self.featsToRemove)
                    # c.features = [x for x in c.features if x.name in self.featsToRemove]
        for l in listCompetitors:
            self.mapping[l.name] = l

    def printResults(self, path):

        # 	def f(v):
        # 		return (v[0]+v[3],v[1]+v[4])
        # 	"""
        # 	print "=============================  "+self.query+"  ============================="
        # 	print "Victoire pertinent sur non pertinent: "+str(self.stats[0])
        # 	print "Defaite pertinent sur non pertinent: "+str(self.stats[1])
        # 	print "Match nul: "+str(self.stats[2])

        # 	"""

        # 	#print "Qrels"
        # 	#print self.qrel

        # 	print "--"
        # 	print "--relevant"
        # 	print "winners"
        # 	#sortedrelStats = OrderedDict(sorted(relStats.items(), key=itemgetter(1), reverse=True))
        # 	#sortedirrelStats = OrderedDict(sorted(irrelStats.items(), key=itemgetter(1), reverse=True))
        # 	mergerelStats = {k:f(v) for k,v in relStats.items()}
        # 	sortedrelStats = OrderedDict(sorted(mergerelStats.items(), key=lambda x:x[1][0], reverse=True))
        # 	mergeirrelStats = {k:f(v) for k,v in irrelStats.items()}
        # 	sortedirrelStats = OrderedDict(sorted(mergeirrelStats.items(), key=lambda x:x[1][0], reverse=True))
        # 	'''
        # 	mergeStats = dict(mergeirrelStats, **mergerelStats)
        # 	#mergeStats = dict(mergeirrelStats)
        # 	sortedmergeStats = OrderedDict(sorted(mergeStats.items(), key=lambda x:x[1][0]-x[1][1], reverse=True))
        # 	'''
        # 	with open(path+"relevant_winners.txt", "a") as f:
        # 		nb = 0
        # 		for k,v in sortedrelStats.iteritems():
        # 			if v[0]>v[1]:
        # 				#print k,v[0],v[1],relStats.get(k),sorted(self.mapping[k].features.values(), key=attrgetter('value'), reverse=True)
        # 				orderFeatures = sorted(self.mapping[k].features.values(), key=attrgetter('value'), reverse=True)
        # 				for l in orderFeatures:
        # 					f.write(l.name.replace('f','')+" -1 ")
        # 				f.write("-2\n")
        # 				nb +=1
        # 		print str(nb)+" relevant winners"
        # 	print "-"
        # 	print "loosers"
        # 	with open(path+"relevant_loosers.txt", "a") as f:
        # 		nb = 0
        # 		for k,v in sortedrelStats.iteritems():
        # 			if v[1]>v[0]:
        # 				#print k,v[0],v[1],relStats.get(k),sorted(self.mapping[k].features.values(), key=attrgetter('value'), reverse=True)
        # 				orderFeatures = sorted(self.mapping[k].features.values(), key=attrgetter('value'), reverse=True)
        # 				for l in orderFeatures:
        # 					f.write(l.name.replace('f','')+" -1 ")
        # 				f.write("-2\n")
        # 				nb +=1
        # 		print str(nb)+" relevant loosers"
        # 	print "--"
        # 	print "--irrelevant"
        # 	print "winners"
        # 	with open(path+"irrelevant_winners.txt", "a") as f:
        # 		nb = 0
        # 		for k,v in sortedirrelStats.iteritems():
        # 			if v[0]>v[1]:
        # 				#print k,v[0],v[1],irrelStats.get(k),sorted(self.mapping[k].features.values(), key=attrgetter('value'), reverse=True)
        # 				orderFeatures = sorted(self.mapping[k].features.values(), key=attrgetter('value'), reverse=True)
        # 				for l in orderFeatures:
        # 					f.write(l.name.replace('f','')+" -1 ")
        # 				f.write("-2\n")
        # 				nb +=1
        # 		print str(nb)+" irrelevant winners"
        # 	print "-"
        # 	print "loosers"
        # 	with open(path+"irrelevant_loosers.txt", "a") as f:
        # 		nb = 0
        # 		for k,v in sortedirrelStats.iteritems():
        # 			if v[1]>v[0]:
        # 				#print k,v[0],v[1],irrelStats.get(k),sorted(self.mapping[k].features.values(), key=attrgetter('value'), reverse=True)
        # 				orderFeatures = sorted(self.mapping[k].features.values(), key=attrgetter('value'), reverse=True)
        # 				for l in orderFeatures:
        # 					f.write(l.name.replace('f','')+" -1 ")
        # 				f.write("-2\n")
        # 				nb += 1
        # 		print str(nb)+" irrelevant loosers"

        file = open(path + "result_" + self.query + ".txt", "w")
        # print "=============================\n    RESULTS    \n============================="
        self._competitors = sorted(self._competitors, key=attrgetter('score'), reverse=True)
        counter = 1
        for current_doc in self._competitors:
            '''
            if current_doc.score>0:
                file.write("{0} Q0 {1} {2} {3} {4}-princess\n".format(self.query,current_doc.name,counter,current_doc.score,self.query));
                counter += 1
            '''
            file.write(
                "{0} Q0 {1} {2} {3} {4}-princess\n".format(self.query, current_doc.name, counter, current_doc.score,
                                                           self.query));
            counter += 1
        #print current_doc

        file.close()

    """
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
    """
