# -*- coding: utf-8 -*-
import operator
import os
import re
import time
from os.path import join

dirname = '/osirim/sig/PROJET/PRINCESS/code/script_experiments/'
dirResult = '/osirim/sig/PROJET/PRINCESS/results/princess/'

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
# listFold = ["1", "2", "3", "4", "5"]
listFold = ["1", "2"]
listType = ['robin', 'grouprobinoptim', 'swiss', 'groupswissoptim']
listFeature = ['', ','.join(['f' + str(x) for x in range(3, 52, 3)]),
               ','.join(['f' + str(x) for x in range(28, 46)])]
listImpact = ['0', '1']
listRound = ['10', '20', '30']
# listCollection = ['indri_web2014clueweb12_adhoc_max50', 'indri_robust2004_max50']
listCollection = ['indri_web2014clueweb12_adhoc_max50']
# listCollectionDir = ["web2014", 'robust2004']
listCollectionDir = ["web2014"]
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


'''
def generate_script():
    count = 0

    # nbExp = len(glob.glob('./Experiment*')) + 1
    # dirname = './osirim+sig/PROJET/PRINCESS/code/script_experiments/'
    command = "rm -r " + dirname
    os.system(command)
    command = "mkdir " + dirname
    os.system(command)
    print dirname
    # os.mkdir(dirname)
    with open(dirname + '/run.sh', 'w') as script_file:
        for elFold in listFold:
            for elGroup in listGroup:
                for elBest in listBest:
                    for elType in listType:
                        for elFeature in listFeature:
                            for elImpact in listImpact:
                                for elRound in listRound:
                                    for elCollection in listCollection:
                                        for elLife in listLife:
                                            for elStrategy in listStrategy:
                                                if "group" in elType:
                                                    count += 1
                                                    sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-b:' + elBest + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                      '-g:' + elGroup + '-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                                                    with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                        the_file.write(
                                                            "#!/bin/sh\n#SBATCH --job-name=" + str(
                                                                count) + "\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + str(
                                                                count) + ".out\n#SBATCH --error=logs/" + str(
                                                                count) + ".err \n#SBATCH -c " + str(
                                                                nbProc + 1) + "\n ")

                                                        if elFeature == '':
                                                            the_file.write(
                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess.py -p  ' + str(
                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + \
                                                                ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + "\n")
                                                        else:
                                                            the_file.write(
                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess.py -p  ' + str(
                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")

                                                    script_file.write("sbatch " + dirname + sbatch_filename + "\n")
                                                else:
                                                    count += 1
                                                    sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-b:' + elBest + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + '-g:' + elGroup + '-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                                                    with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                        the_file.write(
                                                            "#!/bin/sh\n#SBATCH --job-name=" + str(
                                                                count) + "\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + str(
                                                                count) + ".out\n#SBATCH --error=logs/" + str(
                                                                count) + ".err\n#SBATCH -c " + str(
                                                                nbProc + 1) + "\n")
                                                        if elFeature == '':
                                                            the_file.write(
                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess.py -p  ' + str(
                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + "\n")
                                                        else:
                                                            the_file.write(
                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess.py -p  ' + str(
                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")
                                                    script_file.write("sbatch " + dirname + sbatch_filename + "\n")

    print count
'''


def checkDoneXp():
    def runOk(dirFold):
        # print '\tChecking if ', dirFold, "is over...."
        if not os.path.exists(dirFold): return False
        listDirXp = os.listdir(dirFold)
        print dirFold
        print '\t\t nb expe:', len(listDirXp), ' vs nbRequired expe:', xpNb

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
        # print "list dataset:", el
        for fold in listFold:
            dirResultRun = dirResult + el + "/" + fold + "/training/"
            if runOk(dirResultRun): listCompleted.append(dirResultRun)

    return listCompleted


def extractMapXp(fold):
    # print "[extractMapXp", fold, "]"
    maps[fold] = {}
    table = []

    for xp in os.listdir(fold):
        # print "\t xp:", xp
        outfilename = join(fold, xp) + "/results.txt"
        outfilenameeval = join(fold, xp) + "/results_trec.txt"
        print "\t\t outfilename:", outfilename
        print "\t\t outfilenameeval:", outfilenameeval
        if "web2014" in xp:
            table = ["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/trec_eval.9.0/trec_eval", '-M50', "-q",
                     "/osirim/sig/PROJET/PRINCESS/qrels/web2014/qrels.all.web2014dedup.txt", '"' + outfilename + '"',
                     ">",
                     '"' + outfilenameeval + '"']
        elif "robust" in xp:
            table = ["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/trec_eval.9.0/trec_eval", "-M50", "-q",
                     "/osirim/sig/PROJET/PRINCESS/qrels/robust2004/qrels.robust2004.txt", '"' + outfilename + '"', ">",
                     '"' + outfilenameeval + '"']
        print "command", " ".join(table)
        os.system(" ".join(table))

        with open(outfilenameeval, 'r') as myFile:
            for line in myFile:
                if "all" in line:
                    for i in re.finditer(regex, line):
                        # feat = i.group(2)
                        maps[fold][xp] = float(i.group(3))


def runTest(fold, best):
    idfold = fold.split("/")[-3]
    header = "#!/bin/sh\n#SBATCH --job-name=best" + str(len(
        analyzedXp)) + "\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=best" + str(
        len(analyzedXp)) + ".out\n#SBATCH --error=best" + str(len(analyzedXp)) + ".err \n#SBATCH -n " + str(
        nbProc + 1) + "\n "
    command = "/logiciels/Python-2.7/bin/python2.7 " \
              "/projets/sig/PROJET/PRINCESS/code/princess_git/princess.py -p " + str(nbProc) + " -x " + idfold
    t = best.split("-")
    for param in t:
        tparam = param.split(":")
        command += " " + tparam[0] + " " + tparam[1]

    print command
    with open("scriptBest.sh", "w") as fout:
        fout.write(header)
        fout.write(command)

    os.system("sbatch scriptBest.sh")


def findBestConfig(fold):
    listResults = {}
    listResults = maps[fold]
    sorted_x = sorted(listResults.items(), key=operator.itemgetter(1), reverse=True)
    best = sorted_x[0][0]
    return best


startTime = time.time()

l = checkDoneXp()

if len(l) > 0:
    print "Au moins une expé est finie !!!"
    # sys.exit()
    for fold in l:
        if fold not in analyzedXp:
            extractMapXp(fold)
            best = findBestConfig(fold)
            runTest(fold, best)
            analyzedXp.append(fold)
            # time.sleep()
