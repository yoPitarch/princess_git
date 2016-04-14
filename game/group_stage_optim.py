#! /usr/bin/python
import multiprocessing
from math import *
from operator import attrgetter

from game import *


class  GroupStageOptim(Tournament):
    ''' ==========================================
    Name: GroupStage
    Creation: June, 9th 2015
    Author: Y. Pitarch (pitarch@irit.fr)
    Last modification: June, 9th 2015
    Description: 
    ==========================================
    '''

    def __init__(self, query=None, impact=0, health=0, nbFeat=0, strategy=1, nbRound=10, featsToRemove=[], qrel={},
                 nbGroups=4, best=0.1, accepted=False, model="f45", optim="order", listStd={}, process=100):
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
        self.listStd = listStd
        self.nb_round = 1
        self.nb_groups = nbGroups
        self.best = best
        self.groups = []
        self.model = model
        self.accepted = accepted
        self.process = 100
        self.mapping = {}

        for idX in range(self.nb_groups):
            self.board.append(list())

    def schedule(self):

        # First let split into nb_groups the competitor list

        self._competitors.sort(key=lambda x: x.features[self.model].value, reverse=True)

        for i in range(self.nb_groups):
            self.groups.append([])

        for i in range(len(self._competitors)):
            idGroup = i % self.nb_groups
            self.groups[idGroup].append(self._competitors[i])
            #print 	self._competitors[i].name+" ("+str(self._competitors[i].features[self.model])+") dans groupe "+str(idGroup)

        # random.shuffle(self._competitors)
        #self.groups = [self._competitors[i::self.nb_groups] for i in range(self.nb_groups)]


        #self._competitors.sort(key = lambda x: x.resultType)

        #print self.groups


        for idGroup in range(self.nb_groups):
            for id_x in range(len(self.groups[idGroup])):
                for id_y in range(id_x + 1, len(self.groups[idGroup])):
                    self.board[idGroup].append(
                        Match(self.groups[idGroup][id_x], self.groups[idGroup][id_y], impact=self.impact,
                              health=self.health, nbFeat=self.nbFeat, strategy=self.strategy, optim=self.optim))

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

        self.schedule()

        count = 0
        nb_process = self.process
        jobs = []
        out_q = multiprocessing.Queue()

        for idGroup in range(len(self.groups)):
            # print "Running robin in group "+str(idGroup+1)
            for id_match in range(len(self.board[idGroup])):

                if count != 0 and count % nb_process == 0:
                    for e in jobs: e.start()
                    for e in jobs: e.join()
                    while not out_q.empty():
                        l = out_q.get()
                        self.mapping[l[0][0]].score += l[0][1]
                        self.mapping[l[1][0]].score += l[1][1]

                    jobs = []
                    out_q = multiprocessing.Queue()

                current_match = self.board[idGroup][id_match]
                # p = multiprocessing.Process(target=self.runParallel, args=(current_match, out_q))
                jobs.append(multiprocessing.Process(target=self.runParallel, args=(current_match, out_q)))
                count += 1
                """
                current_match = self.board[idGroup][id_match]
                (points_a, points_b,draw_point) = current_match.run(self.listStd) # Run the match and get the respective number of points
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
                """

        for e in jobs: e.start()
        for e in jobs: e.join()
        while not out_q.empty():
            l = out_q.get()
            self.mapping[l[0][0]].score += l[0][1]
            self.mapping[l[1][0]].score += l[1][1]

            # current_match.doc_a.opponents.append(current_match.doc_b.name)
            # current_match.doc_b.opponents.append(current_match.doc_a.name)
            # if count % 1000 == 0 :
            #print str(count)+"/"+str(len(self.board[id_round]))

            # Il manque a enregistrer le resultat de la partie (doit on le faire ? => En suspens)

        # It's time to order the groups by score
        count = 0
        jobs = []
        out_q = multiprocessing.Queue()
        finalist = []
        for group in self.groups:
            group = sorted(group, key=attrgetter('score'), reverse=True)
            nbFinalist = int(ceil(float(len(group) * self.best)))
            finalist.extend(group[:nbFinalist])

        # print "Size of finalist: "+str(len(finalist))

        self.board.append(list())
        for id_x in range(len(finalist)):
            for id_y in range(id_x + 1, len(finalist)):
                self.board[self.nb_groups].append(
                    Match(finalist[id_x], finalist[id_y], impact=self.impact, health=self.health, nbFeat=self.nbFeat,
                          strategy=self.strategy, optim=self.optim))

        for id_match in range(len(self.board[self.nb_groups])):

            if count != 0 and count % nb_process == 0:
                for e in jobs: e.start()
                for e in jobs: e.join()
                while not out_q.empty():
                    l = out_q.get()
                    self.mapping[l[0][0]].score += l[0][1]
                    self.mapping[l[1][0]].score += l[1][1]

                jobs = []
                out_q = multiprocessing.Queue()

            current_match = self.board[self.nb_groups][id_match]
            # p = multiprocessing.Process(target=self.runParallel, args=(current_match, out_q))
            jobs.append(multiprocessing.Process(target=self.runParallel, args=(current_match, out_q)))
            count += 1

            """
            current_match = self.board[self.nb_groups][id_match]
            (points_a, points_b,draw_point) = current_match.run(self.listStd) # Run the match and get the respective number of points
            current_match.doc_a.score += points_a
            current_match.doc_b.score += points_b
            """

            """
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
            """

        for e in jobs: e.start()
        for e in jobs: e.join()
        while not out_q.empty():
            l = out_q.get()
            self.mapping[l[0][0]].score += l[0][1]
            self.mapping[l[1][0]].score += l[1][1]

    def setCompetitors(self, listCompetitors):

        for l in listCompetitors:
            self.mapping[l.name] = l

        self._competitors = listCompetitors
        # print self.featsToRemove
        # print self.accepted
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

                    # print c.features

    def printResults(self, path):

        if len(self.qrel) > 0:
            print "=============================  " + self.query + "  ============================="
            print "Victoire pertinent sur pertinent: " + str(self.stats[0])
            print "Defaite pertinent sur non pertinent: " + str(self.stats[1])
            print "Match nul: " + str(self.stats[2])

        file = open(path + "result_" + self.query + ".txt", "w")
        # print "=============================\n    RESULTS    \n============================="
        self._competitors = sorted(self._competitors, key=attrgetter('score'), reverse=True)
        counter = 1
        for current_doc in self._competitors:
            file.write(
                "{0} Q0 {1} {2} {3} {4}-princess\n".format(self.query, current_doc.name, counter, current_doc.score,
                                                           self.query));
            counter += 1
        # print current_doc

        file.close()
