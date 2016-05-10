# -*- coding: utf-8 -*-
import operator
import os
import re
import time
from os.path import join

dirname = '/osirim/sig/PROJET/PRINCESS/code/script_experiments/'
dirResult = '/osirim/sig/PROJET/PRINCESS/results_cikm/princess/'

# DEBUG
'''
listType = ['robin']
listFeature = ['']
listImpact = ['0', '1']
listRound = ['10']
listCollection = ['indri_web2014clueweb12_adhoc_max50']
listCollectionDir = ["web2014"]
listLife = ['0', '10']
listStrategy = ['0']
'''
nbProc = 20
listFold = ["1", "2", "3", "4", "5"]
# listFold = ["1", "2"]
listType = ['robin', 'grouprobinoptim', 'swiss', 'groupswissoptim']
listFeature = ['', ','.join(['f' + str(x) for x in range(3, 52, 3)]),
               ','.join(['f' + str(x) for x in range(28, 46)])]
listImpact = ['0', '1']
listRound = ['10', '20', '30']
listCollection = ['indri_web2014clueweb12_adhoc_max50', 'indri_robust2004_max50',"NP2003", "NP2004", "OHSUMED",
                  "TD2003", "TD2004", "HP2003", "HP2004"]
# listCollection = ['indri_web2014clueweb12_adhoc_max50']
listCollectionDir = ["web2014", 'robust2004', "NP2003", "NP2004", "OHSUMED", "TD2003", "TD2004", "HP2003", "HP2004"]
#listCollectionDir = ["web2014"]
listLife = ['0', '2', '5', '10', '20']
listStrategy = ['0']
listGroup = ['5', '10']
listBest = ['0.1', '0.2']

regex = '^(map)\s+([\w\d]{3})(.*)'
analyzedXp = []
maps = {}
xpNb = len(listType) * len(listFeature) * len(listImpact) * len(listRound) * len(listLife) * len(listStrategy) * len(
    listGroup) * len(listBest)

print "[Nb expe:", xpNb, "]"


def get_running_jobs():
    command = "squeue -u quaesig |wc -l > nbProc.txt"
    os.system(command)
    runningJobs = 0
    with open("nbProc.txt", "r") as f:
        for l in f:
            runningJobs = int(l.strip()) - 1
            # print "line: ", l, "/ jobs:", runningJobs
    return runningJobs


def checkDoneXp():
    def runOk(dirFold):
        # print '\tChecking if ', dirFold, "is over...."
        if not os.path.exists(dirFold): return False
        listDirXp = os.listdir(dirFold)
        print dirFold
        #print '\t\t nb expe:', len(listDirXp), ' vs nbRequired expe:', xpNb

        if len(listDirXp) < xpNb:
            # print '\t\tNot enough....'
            return False

        for dir in listDirXp:
            dirExpe = join(dirFold, dir)
            filesInExpe = os.listdir(dirExpe)
            if "completed.txt" not in filesInExpe: return False
        # print 'Fold completed!!'
        return True

    listCompleted = []
    for el in listCollectionDir:
        print "list dataset:", el
        for fold in listFold:
            print fold
            dirResultRun = dirResult + el + "/" + fold + "/training/"
            # if runOk(dirResultRun): listCompleted.append(dirResultRun)
            listCompleted.append((dirResultRun,el))

    return listCompleted


def extractMapXp(el):
    print "[extractMapXp", el, "]"
    fold = el[0]
    dataset = el[1]
    maps[fold] = {}
    table = []

    for xp in os.listdir(fold):
        print "\t xp:", xp
        outfilename = join(fold, xp) + "/results.txt"
        outfilenameeval = join(fold, xp) + "/results_trec.txt"

        if not (os.path.exists(outfilenameeval)):

            # print "\t\t outfilename:", outfilename
            # print "\t\t outfilenameeval:", outfilenameeval
            if "web2014" in xp:
                table = ["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/trec_eval.9.0/trec_eval", '-M50', "-q",
                         "/osirim/sig/PROJET/PRINCESS/qrels/web2014/qrels.txt",
                         '"' + outfilename + '"',
                         ">",
                         '"' + outfilenameeval + '"']
            elif "robust" in xp:
                print "ici"
                table = ["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/trec_eval.9.0/trec_eval", "-M50", "-q",
                         "/osirim/sig/PROJET/PRINCESS/qrels/robust2004/qrels.txt", '"' + outfilename + '"',
                         ">",
                         '"' + outfilenameeval + '"']
            else :
                #TODO
                table = ["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/trec_eval.9.0/trec_eval", "-M50", "-q",
                         "/osirim/sig/PROJET/PRINCESS/qrels/"+dataset+"/qrels.txt", '"' + outfilename + '"',
                         ">",
                         '"' + outfilenameeval + '"']
            print "command", " ".join(table)
            os.system(" ".join(table))

        with open(outfilenameeval, 'r') as myFile:
            for line in myFile:
                if "all" in line:
                    for i in re.finditer(regex, line):
                        # feat = i.group(2)
                        maps[fold][xp] = float(i.group(3))
                        # print maps


def runTest(el, best, i):
    fold = el[0]
    idfold = fold.split("/")[-3]
    header = "#!/bin/sh\n#SBATCH --job-name=best" + str(
        i) + "\n#SBATCH --mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=best" + str(
        i) + ".out\n#SBATCH --error=best" + str(i) + ".err \n#SBATCH -c " + str(
        nbProc + 1) + "\n "
    command = "srun /logiciels/Python-2.7/bin/python2.7 " \
              "/projets/sig/PROJET/PRINCESS/code/princess_git/princess.py -p " + str(nbProc) + " -x " + idfold
    t = best.split("-")
    for param in t:
        tparam = param.split(":")
        print tparam
        if tparam[0] != "a":
            command += " -" + tparam[0] + " " + tparam[1]
        else:
            command += " -" + tparam[0]

    # print command
    with open("scriptBest_" + str(i) + ".sh", "w") as fout:
        fout.write(header)
        fout.write(command + "\n")

    with open("srunBest.sh", "a") as fout:
        fout.write(command + "\n")


        # os.system("chmod a+x scriptBest_" + str(i) + ".sh")
        # os.system("sbatch scriptBest_" + str(i) + ".sh")


def findBestConfig(el):
    print "el=>", el
    fold = el[0]
    listResults = {}
    listResults = maps[fold]
    print "listResults:",listResults
    sorted_x = sorted(listResults.items(), key=operator.itemgetter(1), reverse=True)
    best = sorted_x[0][0]
    #print sorted_x[0]
    return best


startTime = time.time()

l = checkDoneXp()

os.system("rm srunBest.sh")

if len(l) > 0:
    print "Au moins une expé est finie !!!"
    # sys.exit()
    for i, fold in enumerate(l):
        print"FOLD:",fold
        extractMapXp(fold)
        best = findBestConfig(fold)
        runTest(fold, best, i)
        #analyzedXp.append(fold)
            # time.sleep()

os.system("chmod a+x srunBest.sh")
os.system('./srunBest.sh')
