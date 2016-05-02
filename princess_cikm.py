#! /usr/bin/python

import errno
import getopt
import os
import sys
import time

from pymongo import MongoClient

from document.document import Document
from document.feature import Feature
from game import *

# Test round robin
# robin = RoundRobin()
# leaders = [Document("First document"), Document("Second document")]
# robin.competitors = leaders
# robin.schedule()
# robin.runCompetition()
# print(robin.ranking)




#
# ADDING W, Y, Z options (upper, seed et tout le bordel pour CIKM
#
#

dictQRels = {}


def evaluateQRels(c):
    if "trec8" in c:
        # print 'ici'
        with open("/osirim/sig/CORPUS/TREC-ADHOC/QRELS/qrels.401-450.disk4.disk5", "r") as qrels:
            for l in qrels:
                tab = l.split(" ")
                # print tab
                q = tab[0]
                doc = tab[2]
                pertinent = False
                if "1" in tab[3]:
                    pertinent = True
                if q not in dictQRels.keys():
                    dictQRels[q] = {}
                dictQRels[q][doc] = pertinent
    elif "trec7" in c:
        with open("/osirim/sig/CORPUS/TREC-ADHOC/QRELS/qrels.351-400.disk4.disk5", "r") as qrels:
            # with open("/osirim/sig/CORPUS/CLUEWEB12/QRELS/qrels.all.web2014.txt","r") as qrels :
            for l in qrels:
                tab = l.split(" ")
                # print tab
                q = tab[0]
                doc = tab[2]
                pertinent = False
                if "1" in tab[3]:
                    pertinent = True
                if q not in dictQRels.keys():
                    dictQRels[q] = {}
                dictQRels[q][doc] = pertinent
    else:
        with open("/osirim/sig/CORPUS/CLUEWEB12/QRELS/qrels.all.web2014dedup.txt", "r") as qrels:
            for l in qrels:
                tab = l.split(" ")
                # print tab
                q = tab[0]
                doc = tab[2]
                pertinent = False
                if "1" in tab[3]:
                    pertinent = True
                if q not in dictQRels.keys():
                    dictQRels[q] = {}
                dictQRels[q][doc] = pertinent
                # print dictQRels


def secure_mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def loadDocsToCompete(c, q):
    res = []
    file = '/osirim/sig/PROJET/PRINCESS/code/tools/best_competitors_letor/' + c + '/docs/' + q + ".txt"
    with open(file, "r") as f:
        for l in f:
            res.extend(l.split(' '))
    return res


def main():
    # Handle user options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dht:i:l:s:n:r:f:vc:b:g:am:o:p:x:w:y:z:",
                                   ["debug", "help", "type=", "impact=", "life=", "strategy=", "nbFeats=", "rounds=",
                                    "featureList=", "verbose", 'collection=', 'group=', 'accepted', 'model=', 'optim',
                                    'process=', "cross=", "boost=", "alpha=", "topX="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    # Set the default values

    optim = "order"
    debug = False
    nb_rounds = 10
    nb_groups = 10
    nb_documents = 16
    nbFeats = 0
    group = 1
    type_tournament = "robin"
    collection_name = ''
    output_directory = "/osirim/sig/PROJET/PRINCESS/results_cikm/princess/"
    impact = 0
    boost = "undifferentiated"  # or upper or seed
    alpha = 3  # valide si upper or seed
    topx = 20  # valide si seed

    features_to_remove = []
    strategy = 1
    process = 100
    life = 0
    best = 0.1
    accepted = False
    verbose = False
    model = "f45"
    fold = -1
    step = "training"  # ou "test"
    queriesToProcess = []

    strategy = ['f48', 'f17', 'f19', 'f16', 'f46', 'f9', 'f21', 'f3', 'f39', 'f7', 'f40', 'f6', 'f37', 'f42', 'f2',
                'f15', 'f25', 'f33', 'f36', 'f10', 'f30', 'f51', 'f28', 'f43', 'f45', 'f34', 'f24', 'f13', 'f50', 'f27',
                'f31', 'f1', 'f35', 'f14', 'f47', 'f41', 'f4', 'f22', 'f12', 'f8', 'f26', 'f44']

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-a", "--accepted"):
            accepted = True
        elif o in ("-o", "--optim"):
            optim = a
        elif o in ("-d", "--debug"):
            debug = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-t", "--type"):
            type_tournament = a
        elif o in ("-g", "--group"):
            group = int(a)
        elif o in ("-f", "--featureList"):
            features_to_remove = str(a).split(",")
            # print features_to_remove
        elif o in ("-r", "--rounds"):
            nb_rounds = int(a)
        elif o in ("-m", "--model"):
            model = str(a)
        elif o in ("-p", "--process"):
            process = int(a)
        elif o in ("-b", "--best"):
            best = float(a)
        elif o in ("-c", "--collection"):
            collection_name = a
        elif o in ("-i", "--impact"):
            impact = int(a)
        elif o in ("-l", "--life"):
            life = int(a)
        elif o in ("-n", "--nbFeats"):
            nbFeats = int(a)
        elif o in ("-s", "--strategy"):
            strategy = int(a)
        elif o in ("-w", "--boost"):
            boost = str(a)
        elif o in ("-y", "--alpha"):
            alpha = int(a)
        elif o in ("-z", "--topX"):
            topx = int(a)
        elif o in ("-x", "--cross"):
            fold = a
            if '-' in fold:
                step = "training"
                fold = -int(a)
            else:
                step = "test"

        else:
            assert False, "unhandled option"

    # load appropriate queries for this run
    if "web" in collection_name:
        output_directory += "web2014/" + str(fold) + "/"
        with open("/osirim/sig/PROJET/PRINCESS/queries/web2014/folds/" + str(fold) + ".txt", "r") as fq:
            for l in fq:
                queriesToProcess.append(l.strip())
    elif "robust" in collection_name:
        output_directory += "robust2004/" + str(fold) + "/"
        with open("/osirim/sig/PROJET/PRINCESS/queries/robust2004/folds/" + str(fold) + ".txt", "r") as fq:
            for l in fq:
                queriesToProcess.append(l.strip())
    else:
        output_directory += collection_name + "/" + str(fold) + "/"
        with open("/osirim/sig/PROJET/PRINCESS/queries/" + collection_name.lower() + "/folds/" + str(fold) + ".txt",
                  "r") as fq:
            for l in fq:
                queriesToProcess.append(l.strip())

    # One tournament per query
    connection = MongoClient(host='co2-ni01.irit.fr', port=28018)
    db = connection.princess
    collection = db[collection_name.lower()]
    queries = collection.distinct('query')

    if debug:
        evaluateQRels(collection_name)

    outputFolderName = ''

    if step == "training":
        output_directory += "training/"
    else:
        output_directory += "test/"

    if len(features_to_remove) > 0:
        outputFolderName = 't:' + type_tournament + '-o:' + optim + '-r:' + str(nb_rounds) + '-b:' + str(
            best) + '-c:' + collection_name + '-i:' + str(impact) + '-l:' + str(life) + '-n:' + str(
            nbFeats) + '-s:' + str(strategy) + '-g:' + str(group) + '-f:' + ','.join(features_to_remove)
        if accepted:
            outputFolderName += '-a'
    else:
        outputFolderName = 't:' + type_tournament + '-o:' + optim + '-r:' + str(nb_rounds) + '-b:' + str(
            best) + '-c:' + collection_name + '-i:' + str(impact) + '-l:' + str(life) + '-n:' + str(
            nbFeats) + '-s:' + str(strategy) + '-g:' + str(group)

    outputFolderName += "-w:" + boost + "-y:" + str(alpha) + "-z:" + str(topx)

    outputFolderName += '/'
    output_directory += outputFolderName

    if os.path.exists(output_directory):
        os.system("rm -r " + output_directory)

    secure_mkdir(output_directory)

    # print "output directory", output_directory
    os.system("rm " + output_directory + "*")

    print "Nb process", process

    begin = time.time()

    for q in queries:

        # print("docstoCompete:", docsToCompete)

        processQuery = False
        if step == "training":
            if q in queriesToProcess:
                processQuery = False
            else:
                processQuery = True
        else:
            if q in queriesToProcess:
                processQuery = True
            else:
                processQuery = False

        if processQuery:
            print "Query " + q

            deb = time.time()

            docsToCompete = []
            if "indri" not in collection_name:
                docsToCompete = loadDocsToCompete(collection_name, q)

            dictQRels.setdefault(q, {})
            qstr = str(q)
            list = collection.find({'query': qstr}, {'_id': 0, 'docs': 1})
            count = 0
            list_doc = []
            for i in list:
                # print i
                for d in i['docs']:
                    # print "**********"
                    count += 1
                    name = d['doc_name']
                    if len(docsToCompete) == 0 or (len(docsToCompete) > 0 and name in docsToCompete):
                        # list_feat = []
                        list_feat = {}
                        for f in d['features']:
                            # print f
                            list_feat[f] = Feature(f, d['features'][f])
                            # if float(d['features'][f]) > 1.0 :
                            #	print f + " = "+ str(d['features'][f])
                        if model not in list_feat:
                            list_feat[model] = Feature(model, 0.0)
                        list_doc.append(Document(name, list_feat))
                        # sys.exit()

            colName = collection_name.lower() + "_std"
            # print colName
            collection_std = db[colName]
            listStd = {}
            res = collection_std.find({'query': str(q)}, {'_id': 0})
            # print colName
            # print q
            # print res[0]
            listStd = res[0]['stds']

            if type_tournament == "robin":
                to = RoundRobin(query=q, impact=impact, health=life, nbFeat=nbFeats, strategy=strategy,
                                nbRound=nb_rounds,
                                featsToRemove=features_to_remove, qrel=dictQRels[q], accepted=accepted, optim=optim,
                                listStd=listStd, process=process, boost=boost, alpha=alpha, topx=topx,model=model)
            elif type_tournament == "swiss":
                to = SwissSystem(query=q, impact=impact, health=life, nbFeat=nbFeats, strategy=strategy,
                                 nbRound=nb_rounds,
                                 featsToRemove=features_to_remove, accepted=accepted, optim=optim, listStd=listStd,
                                 process=process, boost=boost, alpha=alpha, topx=topx,model=model)
            elif type_tournament == "random":
                to = RandomTournament(query=q, impact=impact, health=life, nbFeat=nbFeats, strategy=strategy,
                                      nbRound=nb_rounds, featsToRemove=features_to_remove, qrel=dictQRels[q],
                                      accepted=accepted, optim=optim, listStd=listStd)
            elif type_tournament == "grouprobinoptim":
                to = GroupStageOptim(query=q, impact=impact, health=life, nbFeat=nbFeats, strategy=strategy,
                                     nbGroups=group,
                                     featsToRemove=features_to_remove, qrel=dictQRels[q], best=best, accepted=accepted,
                                     model=model, optim=optim, listStd=listStd, process=process, boost=boost,
                                     alpha=alpha, topx=topx)
            elif type_tournament == "groupswissoptim":
                to = GroupSwissOptim(query=q, impact=impact, health=life, nbFeat=nbFeats, strategy=strategy,
                                     nbGroups=group,
                                     nbRound=nb_rounds, featsToRemove=features_to_remove, qrel=dictQRels[q], best=best,
                                     accepted=accepted, model=model, optim=optim, listStd=listStd, process=process,
                                     boost=boost, alpha=alpha, topx=topx)

            print "setCompetitors"
            to.setCompetitors(list_doc)
            # print len(list_doc)
            print "runCompetition"
            to.runCompetition()
            print "printResults"
            to.printResults(output_directory)

            print "Query processing time:", (time.time() - deb), "sec"

    print "[ n=", process, type_tournament, "] total time:", (time.time() - begin), "ms"
    with open(output_directory + "completed.txt", "w") as f:
        f.write("completed!!")


"""
        # Generation aleatoire de documents
        leaders = []
        random.seed()
        for i in range(nb_documents):
            feats =[]
            for j in range(nb_features):
                feats.append(Feature("F"+str(j),random.randint(0,10)))
            doc = Document("Document "+str(i),feats)
            print doc
            leaders.append(doc)
        swiss.competitors = leaders


        for id_x in range(1,nb_rounds):
            swiss.schedule(id_x)
            swiss.run_round_k(id_x)

        swiss.print_results()
        sys.exit()
"""


def usage():
    print "Usage: \
        -h [--help] Print this help \n\
        -t [--type] Set the type of the tournament \n\
        -d [--documents] Set the number of documents that shall participate to the final tournament (preferably a power of 2) \n \
        -r [--rounds] Set the number of rounds in the swiss style tournament \n\
        -g [--groups] Set the nuumber of groups in the swiss style tournament \n\
        -v [--verbose] Activate the verbose mode (for debugging purpose)" \
          "" \
          "" \
          ""


# TODO: mettre a jour le usage

def function_to_debug():
    doc_a = Document("DocA",
                     [Feature("f0", 10), Feature("f1", 5), Feature("f2", 10), Feature("f3", 20), Feature("f4", 10),
                      Feature("f5", 10), Feature("f6", 10)])
    doc_b = Document("DocB", [Feature("f0", 10), Feature("f3", 5), Feature("f5", 8), Feature("f6", 1)])

    m = Match(doc_a, doc_b)
    m.elaborated_match_v2()

    sys.exit(0)


if __name__ == "__main__":
    main()
    # function_to_debug()
