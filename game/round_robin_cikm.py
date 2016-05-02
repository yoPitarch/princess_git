#! /usr/bin/python
import multiprocessing
import time
from operator import attrgetter

from game import *

relStats = {}
irrelStats = {}


class RoundRobin(Tournament):
    ''' ==========================================
    Name: RoundRobin
    Creation: April, 15th 2014
    Author: Y. Pitarch (pitarch@irit.fr)
    Last modification: April, 15th 2014
    Description: 
    ==========================================
    '''

    def __init__(self, query=None, impact=0, health=0, nbFeat=0, strategy=1, nbRound=10, featsToRemove=[], qrel={},
                 accepted=False, optim="order", listStd={}, process=100, boost="undifferentiated", alpha=3,
                 topx=20,model="f45",listTop = []):
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
        self.process = process
        self.boost = boost
        self.alpha = alpha
        self.topx = topx
        self.model = model
        self.upperSet = []
        self.seedSet = set()
        self.listTop = listTop

        # print self.qrel

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

    competitors = property(_get_competitors, _set_competitors)  # Competitor description

    def runParallel(self, match, out_q):
        rank_a = self.upperSet.index(match.doc_a.name)
        rank_b = self.upperSet.index(match.doc_b.name)
        (points_a, points_b, draw_point) = match.run(
            self.listStd)  # Run the match and get the respective number of points

        if self.boost == "upper":
            if points_a > points_b and rank_b > rank_a:
                points_a = self.alpha * points_a
            # print "1 " +current_match.doc_a.name+" "+str(current_match.doc_a.score)
            # elif points_a < points_b and current_match.doc_b.name not in seedSet and current_match.doc_a.name in seedSet:
            elif points_a < points_b and rank_a > rank_b:
                points_b = self.alpha * points_b
        elif self.boost == "seed":
            if points_a > points_b and match.doc_b.name in self.seedSet:
                points_a = self.alpha * points_a
            # print "1 " +current_match.doc_a.name+" "+str(current_match.doc_a.score)
            # elif points_a < points_b and current_match.doc_b.name not in seedSet and current_match.doc_a.name in seedSet:
            elif points_a < points_b and match.doc_a.name in self.seedSet:
                points_b = self.alpha * points_b

        out_q.put([(match.doc_a.name, points_a), (match.doc_b.name, points_b)])

    def runCompetition(self):
        global relStats, irrelStats

        begin = time.time()
        self.schedule()

        relStats = {}
        irrelStats = {}

        count = 0
        nb_process = self.process
        jobs = []
        out_q = multiprocessing.Queue()
        for id_round in range(len(self.board)):
            for id_match in range(len(self.board[id_round])):
                # print count, id_match
                if count != 0 and count % nb_process == 0:
                    for e in jobs: e.start()
                    for e in jobs: e.join()
                    while not out_q.empty():
                        l = out_q.get()
                        self.mapping[l[0][0]].score += l[0][1]
                        self.mapping[l[1][0]].score += l[1][1]

                    jobs = []
                    out_q = multiprocessing.Queue()

                current_match = self.board[id_round][id_match]
                jobs.append(multiprocessing.Process(target=self.runParallel, args=(current_match, out_q)))
                count += 1

        for e in jobs: e.start()
        for e in jobs: e.join()
        while not out_q.empty():
            l = out_q.get()
            self.mapping[l[0][0]].score += l[0][1]
            self.mapping[l[1][0]].score += l[1][1]



            # pprint.pprint(self._competitors)
            # print "[n=", nb_process, "] total time: ", (time.time() - begin), "ms"
            # sys.exit()

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

        if len(self.listTop) == 0:
            self._competitors.sort(key=lambda x: x.features[self.model].value, reverse=True)
            for c in self._competitors:
                self.upperSet.append(c.name)

            for c in self._competitors[0:int(len(self._competitors) * (self.topx / 100))]:
                self.seedSet.add(c.name)
        else :
            self.upperSet = self.listTop
            self.seedSet = set(self.listTop[0:int(len(self.listTop) * (self.topx / 100))])

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

        file = open(path + "results.txt", "a")
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
        # print current_doc

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
