#! /usr/bin/python
# -*- coding: utf-8 -*-

import os
import random
from operator import attrgetter

from document.feature import Feature


class Match(object):
    """ ==========================================
    Name: Match
    Creation: April, 15th 2014
    Author: Y. Pitarch (pitarch@irit.fr)
    Last modification: April, 15th 2014
    Description: 
        - impact : 0 si un point par coup, 1 si on prend le delta
        - gauge : 0 si infini, val sinon (niveau de la jauge de vie)
        - nbFeat : 0 si toutes, val sinon (le nb de features total - pour les deux jouerus- à jouer)
        - strategy : 0 tant que je gagne je joue, n le nb de coups par tour
    ========================================== """

    def __init__(self, a, b, impact=0, health=0, nbFeat=0, strategy=1, start=0, optim="order"):
        self.doc_a = a
        self.doc_b = b
        self.impact = impact
        self.health = health
        self.start = start
        self.optim = optim
        if nbFeat == 0:
            self.nbFeat = 1000
        else:
            self.nbFeat = nbFeat
        self.strategy = strategy
        self.strategy_feat = ['f48', 'f17', 'f19', 'f16', 'f46', 'f9', 'f21', 'f3', 'f39', 'f7', 'f40', 'f6', 'f37',
                              'f42', 'f2', 'f15', 'f25', 'f33', 'f36', 'f10', 'f30', 'f51', 'f28', 'f43', 'f45', 'f34',
                              'f24', 'f13', 'f50', 'f27', 'f31', 'f1', 'f35', 'f14', 'f47', 'f41', 'f4', 'f22', 'f12',
                              'f8', 'f26', 'f44']

    def random_match(self):
        score_a = random.random()
        score_b = random.random()
        if score_a > score_b:
            return (3, 0, 0)
        elif score_b > score_a:
            return (0, 3, 0)
        else:
            return (1, 1, 1)

    def compareFeatures(self, p, np, t):
        hash_p = {}
        hash_np = {}
        feats = set()
        p_sup = 0
        np_sup = 0
        kdom_p = False
        kdom_np = False

        for el_p in p:
            hash_p.setdefault(el_p.name, el_p.value)

        for el_np in np:
            hash_np.setdefault(el_np.name, el_p.value)

        dom_p = False
        for k, v in hash_p.iteritems():
            if k not in hash_np.keys():
                if v > 0:
                    dom_p = True
                    p_sup += 1
                elif v == 0:
                    p_sup += 1

            else:
                if v > hash_np[k]:
                    dom_p = True
                    p_sup += 1
                elif v == hash_np[k]:
                    p_sup += 1

        dom_np = False
        for k, v in hash_np.iteritems():
            if k not in hash_p.keys():
                if v > 0:
                    dom_np = True
                    np_sup += 1
                elif v == 0:
                    np_sup += 1

            else:
                if v > hash_p[k]:
                    dom_np = True
                    np_sup += 1
                elif v == hash_p[k]:
                    np_sup += 1

        if dom_np and np_sup >= t and not (dom_p and p_sup >= t):
            return -1
        elif dom_p and p_sup >= t and not (dom_np and np_sup >= t):
            return 1
        else:
            return 0

    def play(self, std):

        # initialization
        nbRound = 0

        # print std

        # 1 Set the player's health
        if self.health == 0:
            health_a = 100
            health_b = 100
        else:
            health_a = self.health
            health_b = self.health

        # 2 Order the features in descending order per player
        if self.optim == "order":
            rankedFeat_a = sorted(self.doc_a.features.values(), key=attrgetter('value'), reverse=True)
            rankedFeat_b = sorted(self.doc_b.features.values(), key=attrgetter('value'), reverse=True)
        elif self.optim == "freq":
            rankedFeat_a = []
            rankedFeat_b = []

            for el in self.strategy_feat:
                if el not in self.doc_a.features:
                    rankedFeat_a.append(Feature(el, 0.0))
                else:
                    rankedFeat_a.append(self.doc_a.features[el])

                if el not in self.doc_b.features:
                    rankedFeat_b.append(Feature(el, 0.0))
                else:
                    rankedFeat_b.append(self.doc_b.features[el])
        elif self.optim == "kdomin":
            rankedFeat_a = sorted(self.doc_a.features.values(), key=attrgetter('value'), reverse=True)
            rankedFeat_b = sorted(self.doc_b.features.values(), key=attrgetter('value'), reverse=True)
            val = self.compareFeatures(rankedFeat_a, rankedFeat_b, 10)
            if val == 1:
                return [3, 0, 0]
            elif val == -1:
                return [0, 3, 0]
            elif val == 0:
                return [1, 1,1]

        # print self.doc_a.name
        #print rankedFeat_a

        '''
        if len(rankedFeat_a)==1 and len(rankedFeat_b)==1 :
            print "[FEAT A]", rankedFeat_a
            print "[FEAT B]", rankedFeat_b
        else :
            print "OK"
        '''

        # 3 Toss a coin to determine who gonna start the match


        if self.start == 0:
            score_a = random.random()
            score_b = random.random()
            current_player = ""
            if score_a > score_b:
                current_player = self.doc_a
            else:
                current_player = self.doc_b
        elif self.start == 1:
            current_player = self.doc_a
        else:
            current_player = self.doc_b

        coeff = 1

        sameplayer = False
        nbRun = 1
        # while nbRound < self.nbFeat and rankedFeat_a and rankedFeat_b and health_a > 0 and health_b > 0 :
        while nbRound < self.nbFeat and (len(rankedFeat_a) + len(rankedFeat_b) > 0) and health_a > 0 and health_b > 0:
            if current_player == self.doc_a:
                # Nombre de coups sur le tour courant
                if not sameplayer:
                    nbRun = 1
                if rankedFeat_a:
                    shoot = rankedFeat_a.pop(0)

                    # print "\tPlay with feature {0}".format(shoot.name)
                    # print "\tStrategy B => {0}".format(str(strategy_b))
                    feat_name = shoot.name
                    feat_value_a = shoot.value
                    feat_filtered = filter(lambda x: x.name == feat_name, rankedFeat_b)

                    feat_value_b = 0
                    if len(feat_filtered) > 0:
                        feat_value_b = feat_filtered[0].value

                    #print "[PLayer 1 joue "+feat_name+" => "+str(feat_value_a)+" (player 2: "+str(feat_value_b)+"]"

                    rankedFeat_b = filter(lambda x: x.name != feat_name, rankedFeat_b)

                    # And the winner is....

                    if self.impact == 0:
                        if feat_value_a > feat_value_b:
                            health_b -= 1
                        # print "\t Player 1 gagne (health_1: "+str(health_a)+" / health_2: "+str(health_b)
                        elif feat_value_a < feat_value_b:
                            health_a -= 1
                    # print "\t Player 2 gagne (health_1: "+str(health_a)+" / health_2: "+str(health_b)
                    else:
                        delta = (feat_value_a - feat_value_b)
                        #print delta

                        # if abs(delta) > 1 :
                        #print "Feature "+feat_name + " (A: "+str(feat_value_a)+" / B: "+str(feat_value_b)+")"

                        if delta > 0:
                            health_b -= (abs(delta) * coeff) / std[feat_name]
                        elif delta < 0:
                            health_a -= (abs(delta) * coeff) / std[feat_name]

                    if self.strategy == 0:
                        if feat_value_a > feat_value_b:
                            # if health_a >= health_b :
                            current_player = self.doc_a
                        else:
                            current_player = self.doc_b
                    else:
                        if nbRun < self.strategy:
                            current_player = self.doc_a
                            nbRun += 1
                            sameplayer = True
                        else:
                            current_player = self.doc_b
                            sameplayer = False
            else:
                # Nombre de coups sur le tour courant
                if not sameplayer:
                    nbRun = 1
                if rankedFeat_b:
                    shoot = rankedFeat_b.pop(0)
                    # print "\tPlay with feature {0}".format(shoot.name)
                    # print "\tStrategy A => {0}".format(str(strategy_a))
                    feat_name = shoot.name
                    feat_value_b = shoot.value
                    feat_filtered = filter(lambda x: x.name == feat_name, rankedFeat_a)

                    feat_value_a = 0
                    if len(feat_filtered) > 0:
                        feat_value_a = feat_filtered[0].value

                    # print "[PLayer 2 joue "+feat_name+" => "+str(feat_value_a)+" (player 1: "+str(feat_value_a)+"]"
                    rankedFeat_a = filter(lambda x: x.name != feat_name, rankedFeat_a)

                    if self.impact == 0:
                        if feat_value_a > feat_value_b:
                            health_b -= 1
                        elif feat_value_a < feat_value_b:
                            health_a -= 1
                    else:
                        # And the winner is....
                        delta = (feat_value_b - feat_value_a)
                        # if abs(delta) > 1 :
                        #	print "Feature "+feat_name + " (A: "+str(feat_value_a)+" / B: "+str(feat_value_b)+")"
                        if delta > 0:
                            health_a -= (abs(delta) * coeff) / std[feat_name]
                        elif delta < 0:
                            health_b -= (abs(delta) * coeff) / std[feat_name]

                    if self.strategy == 0:
                        if feat_value_b > feat_value_a:
                            # if health_b >= health_a :
                            current_player = self.doc_b
                        else:
                            current_player = self.doc_a
                    else:
                        if nbRun < self.strategy:
                            current_player = self.doc_b
                            nbRun += 1
                            sameplayer = True
                        else:
                            current_player = self.doc_a
                            sameplayer = False
            nbRound += 1

        '''
        400 0 LA121289-0033 0
        400 0 LA121290-0147 1
        '''

        '''
        if self.doc_a.name == 'LA121289-0033' and self.doc_b.name == 'LA121290-0147' :
            print "Health uninteresing : "+str(health_a)+" / "+"Health interesing : "+str(health_b)
            sys.exit()

        if self.doc_a.name == 'LA121290-0147' and self.doc_b.name == 'LA121289-0033' :
            print "Health interesing : "+str(health_a)+" / "+"Health uninteresing : "+str(health_b)
            sys.exit()
        '''
        #print health_a,health_b

        dev = 1.0

        if health_a > dev * health_b:
            # print self.doc_a
            return [3, 0, 0]
            #return [3,-3,0]

        elif health_b > dev * health_a:
            # print self.doc_b
            return [0, 3, 0]
            # return [-3,3,0]
        else:
            return [1, 1, 1]
            #return [2,2,1]

    def elaborated_match(self):
        # 1 Set health and current_feat_id's
        health_a = 100
        health_b = 100
        feat_id_a = 0
        feat_id_b = 0
        # 2 Strategy elaboration
        strategy_a = sorted(self.doc_a.features, key=attrgetter('value'), reverse=True)
        strategy_b = sorted(self.doc_b.features, key=attrgetter('value'), reverse=True)

        feats = []
        if len(self.doc_a.features) > len(self.doc_b.features):
            feats = [x.name for x in self.doc_a.features]
        else:
            feats = [x.name for x in self.doc_b.features]

        # print "FEAT "
        # print feats

        # 3 Toss a coin to determine who gonna start the match
        score_a = random.random()
        score_b = random.random()
        current_player = ""
        if score_a > score_b:
            current_player = self.doc_a
        else:
            current_player = self.doc_b

        # 4 Let us play

        print("Let's play !!!")

        while feats and health_a > 0 and health_b > 0:
            if current_player == self.doc_a:
                print "[PLAYER 1] Strategy : " + str(strategy_a)

                # n'existe pas dans b ou egal a 0 ou deja joue
                while not any(d.name == strategy_a[0].name for d in self.doc_b.features) or strategy_a[
                    0].name == 'f0' or not strategy_a[0].name in feats:

                    if not any(d.name == strategy_a[0].name for d in self.doc_b.features):
                        print "\t{0} does'nt exist in document B".format(strategy_a[0].name)

                    if strategy_a[0].name == 'f0':
                        print "\tFeature f0"

                    if not strategy_a[0].name in feats:
                        print "\t{0} has been already played".format(strategy_a[0].name)

                    # Il faut depiler dans feat et dans strategy_a
                    item = strategy_a.pop(0)
                    if item.name in feats:
                        feats.remove(item.name)

                shoot = strategy_a.pop(0)
                print "\tPlay with feature {0}".format(shoot.name)
                feats.remove(shoot.name)
                feat_name = shoot.name
                feat_value_a = shoot.value
                feat_filtered = filter(lambda x: x.name == feat_name, strategy_b)
                feat_value_b = feat_filtered[0].value
                # And the winner is....
                delta = feat_value_a - feat_value_b
                if delta > 0:
                    health_b -= delta
                else:
                    health_a -= delta
                current_player = self.doc_b
            else:
                print "[PLAYER 2] Strategy : " + str(strategy_b)
                # n'existe pas dans b ou egal a 0 ou deja joue
                while not any(d.name == strategy_b[0].name for d in self.doc_a.features) or strategy_b[
                    0].name == 'f0' or not strategy_b[0].name in feats:

                    if not any(d.name == strategy_b[0].name for d in self.doc_b.features):
                        print "\t{0} does'nt exist in document A".format(strategy_b[0].name)

                    if strategy_b[0].name == 'f0':
                        print "\tFeature f0"

                    if not strategy_b[0].name in feats:
                        print "\t{0} has been already played".format(strategy_b[0].name)

                    # Il faut depiler dans feat et dans strategy_a
                    item = strategy_b.pop(0)
                    # print "\tFeature {0} is deleted".format(item.name)
                    if item.name in feats:
                        feats.remove(item.name)

                shoot = strategy_b.pop(0)
                print "\tPlay with feature {0}".format(shoot.name)
                feats.remove(shoot.name)
                feat_name = shoot.name
                feat_value_b = shoot.value
                feat_filtered = filter(lambda x: x.name == feat_name, strategy_a)
                feat_value_a = feat_filtered[0].value
                # And the winner is....
                delta = feat_value_b - feat_value_a
                if delta > 0:
                    health_a -= delta
                else:
                    health_b -= delta
                current_player = self.doc_a

        if health_a > health_b:
            return (3, 0)
        elif health_b > health_a:
            return (0, 3)
        else:
            return (1, 1)

    def elaborated_match_v2(self):
        # 1 Set health and current_feat_id's
        health_a = 100
        health_b = 100
        feat_id_a = 0
        feat_id_b = 0
        # 2 Strategy elaboration
        strategy_a = sorted(self.doc_a.features, key=attrgetter('value'), reverse=True)
        strategy_b = sorted(self.doc_b.features, key=attrgetter('value'), reverse=True)

        # 3 Toss a coin to determine who gonna start the match
        score_a = random.random()
        score_b = random.random()
        current_player = ""
        if score_a > score_b:
            current_player = self.doc_a
        else:
            current_player = self.doc_b

        # 4 Let us play

        # print("Let's play !!!")

        # print "\t[PLAYER 1] => {0}".format(str(strategy_a))
        # print "\t[PLAYER 2] => {0}".format(str(strategy_b))

        while strategy_a and strategy_b and health_a > 0 and health_b > 0:
            if current_player == self.doc_a:

                if strategy_a:
                    shoot = strategy_a.pop(0)

                    # print "\tPlay with feature {0}".format(shoot.name)
                    # print "\tStrategy B => {0}".format(str(strategy_b))
                    feat_name = shoot.name
                    feat_value_a = shoot.value
                    feat_filtered = filter(lambda x: x.name == feat_name, strategy_b)

                    feat_value_b = 0
                    if len(feat_filtered) > 0:
                        feat_value_b = feat_filtered[0].value

                    # print "[PLayer 1 joue "+feat_name+" => "+str(feat_value_a)+" (player 2: "+str(feat_value_b)+"]"

                    strategy_b = filter(lambda x: x.name != feat_name, strategy_b)

                    # And the winner is....

                    if feat_value_a > feat_value_b:
                        health_b -= 1
                        # print "\t Player 1 gagne (health_1: "+str(health_a)+" / health_2: "+str(health_b)
                    elif feat_value_a < feat_value_b:
                        health_a -= 1
                        # print "\t Player 2 gagne (health_1: "+str(health_a)+" / health_2: "+str(health_b)

                    """
                    # Si features normalisees
                    delta = feat_value_a - feat_value_b
                    if delta > 0 :
                        health_b -= delta
                    else :
                        health_a -= delta
                    """
                current_player = self.doc_b

            else:

                if strategy_b:
                    shoot = strategy_b.pop(0)
                    # print "\tPlay with feature {0}".format(shoot.name)
                    # print "\tStrategy A => {0}".format(str(strategy_a))
                    feat_name = shoot.name
                    feat_value_b = shoot.value
                    feat_filtered = filter(lambda x: x.name == feat_name, strategy_a)

                    feat_value_a = 0
                    if len(feat_filtered) > 0:
                        feat_value_a = feat_filtered[0].value

                    # print "[PLayer 2 joue "+feat_name+" => "+str(feat_value_a)+" (player 1: "+str(feat_value_a)+"]"
                    strategy_a = filter(lambda x: x.name != feat_name, strategy_a)

                    if feat_value_a > feat_value_b:
                        health_b -= 1
                        # print "\t Player 1 gagne (health_1: "+str(health_a)+" / health_2: "+str(health_b)
                    elif feat_value_a < feat_value_b:
                        health_a -= 1
                        # print "\t Player 2 gagne (health_1: "+str(health_a)+" / health_2: "+str(health_b)

                    """
                    # And the winner is....
                    delta = feat_value_b - feat_value_a
                    if delta > 0 :
                        health_a -= delta
                    else :
                        health_b -= delta
                    """

                current_player = self.doc_a

        if health_a > health_b:
            return (3, 0)
        elif health_b > health_a:
            return (0, 3)
        else:
            return (1, 1)

    def run(self, std):
        "Run the match"
        # print("Match between {0} and {1}".format(self.doc_a, self.doc_b))
        # return self.random_match() # while no clever strategy is implemented, let the power of randomness do the stuff
        # return self.elaborated_match_v2()
        # if hasattr(os, 'getppid'):  # only available on Unix
        #	print 'parent process:', os.getppid()
        print 'process id:', os.getpid()
        # print 'Doc A:', self.doc_a.name
        # print 'Doc B:', self.doc_b.name
        res = self.play(std)
        # print res
        #print "----------------------"
        return res

    def __str__(self):
        "Match representation"
        return "{0} vs {1}".format(self.doc_a.name, self.doc_b.name)

    def __repr__(self):
        "Match representation"
        return "{0} vs {1}".format(self.doc_a.name,self.doc_b.name)
