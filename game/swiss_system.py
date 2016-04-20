#! /usr/bin/python
# -*- coding: utf-8 -*-

import multiprocessing
from operator import attrgetter

from game import *
from pypair import SwissTournamentAPI


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

    def __init__(self, query=None, impact=0, health=0, nbFeat=0, strategy=1, nbRound=10, featsToRemove=[],
                 accepted=False, optim="order", listStd={}, process=100):
        """
        Constructor:
            - Set the number of round to 1
            - Initialisation of board
        """
        self.tournament = SwissTournamentAPI()
        #  self.ranking = {} # Store the on-going ranking
        self.nb_rounds = nbRound
        self.mappingDoc = {}
        self.dictDoc = {}
        self._competitors = []
        self.listStd = listStd
        self.mapping = {}
        self.process = process
        Tournament.__init__(self, query, impact, health, nbFeat, strategy, nbRound, featsToRemove, accepted, optim)

    def setCompetitors(self, listCompetitors):
        for l in listCompetitors:
            self.mapping[l.name] = l
        count = 0
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

        for doc in listCompetitors:
            self.tournament.addPlayer(count, doc.name)
            self.mappingDoc[count] = doc
            self.dictDoc[doc.name] = count
            count += 1

    def runParallel(self, id, match, out_q):
        out_q.put([id, match.run(self.listStd)])

    def runCompetition(self):

        process = self.process
        jobs = []
        out_q = multiprocessing.Queue()
        for i in range(self.nb_rounds):
            pairings = self.tournament.pairRound()
            count = 0
            for table in pairings:
                if not type(pairings[table]) is str:
                    if count == 0 and count % process == 0:
                        for e in jobs: e.start()
                        for e in jobs: e.join()
                        while not out_q.empty():
                            l = out_q.get()
                            self.tournament.reportMatch(l[0], l[1])
                        jobs = []
                        out_q = multiprocessing.Queue()

                    # print table
                    idPlayer1 = self.tournament.roundPairings[table][0]
                    idPlayer2 = self.tournament.roundPairings[table][1]

                    m = Match(self.mappingDoc[idPlayer1], self.mappingDoc[idPlayer2], impact=self.impact,
                              health=self.health, nbFeat=self.nbFeat, strategy=self.strategy, optim=self.optim)
                    jobs.append(multiprocessing.Process(target=self.runParallel, args=(table, m, out_q)))
                    count += 1
                    # self.tournament.reportMatch(table, m.run(self.listStd))

            for e in jobs: e.start()
            for e in jobs: e.join()
            while not out_q.empty():
                l = out_q.get()
                self.tournament.reportMatch(l[0], l[1])
            jobs = []
            out_q = multiprocessing.Queue()

        self.feedCompetitors()

    def feedCompetitors(self):
        # print len(self.dictDoc.keys())
        # print len(self.tournament.playersDict.keys())
        # print len(self._competitors)
        for id in self.tournament.playersDict.keys():
            doc = self.tournament.playersDict[id]
            # print self.dictDoc[doc["Name"]]
            self._competitors[self.dictDoc[doc["Name"]]].score = doc["Points"]

    def printResults(self, path):
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

        file.close()

    def printResultsLetor(self, path):

        file = open(path + "result_" + self.query + ".txt", "w")
        file2 = open(path + "details_" + self.query + ".txt", "w")

        # print "=============================\n    RESULTS    \n============================="
        self._competitors = sorted(self._competitors, key=attrgetter('position'), reverse=False)
        for current_doc in self._competitors:
            file.write("{0}\n".format(current_doc.score));
            file2.write(
                "{0} {1} {2} {3}\n".format(self.query, current_doc.name, current_doc.score, current_doc.position));
        file.close()
        file2.close()
