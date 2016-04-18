# -*- coding: utf-8 -*-
import operator
import os
import re
import subprocess
import time
from os.path import join

dirname = '/osirim/sig/PROJET/PRINCESS/code/script_experiments/'
dirResult = '/osirim/sig/PROJET/PRINCESS/results/princess/'
listFold = ["1", "2", "3", "4", "5"]
listType = ['robin', 'grouprobin', 'swiss', 'groupswiss']
listFeature = ['', ','.join(['f' + str(x) for x in range(3, 52, 3)]),
               ','.join(['f' + str(x) for x in range(28, 46)])]
listImpact = ['0', '1']
listRound = ['10', '20', '30']
listCollection = ['web2014clueweb12_adhoc_max50']
listCollectionDir = ["web2014"]
listLife = ['0', '2', '5', '7', '10', '20']
listStrategy = ['0']
regex = '^(map)\s+([\w\d]{3})(.*)'
analyzedXp = []
maps = {}
xpNb = len(listType) * len(listFeature) * len(listImpact) * len(listRound) * len(listLife) * len(listStrategy)


def get_running_jobs():
    p = subprocess.Popen(['squeue', '-u', 'quaesig', '|', 'wc', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    runningJobs = int(out.strip()) - 1
    return runningJobs


def generate_script():
    count = 0

    # nbExp = len(glob.glob('./Experiment*')) + 1
    # dirname = './osirim+sig/PROJET/PRINCESS/code/script_experiments/'
    print dirname
    os.mkdir(dirname)
    with open(dirname + '/run.sh', 'w') as script_file:
        for elFold in listFold:
            for elType in listType:
                for elFeature in listFeature:
                    for elImpact in listImpact:
                        for elRound in listRound:
                            for elCollection in listCollection:
                                for elLife in listLife:
                                    for elStrategy in listStrategy:
                                        if "group" in elType:
                                            count += 1
                                            sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-b:0.2-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                              '-g:5-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                                            with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                the_file.write(
                                                    "#!/bin/sh\n#SBATCH --job-name=sigir\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n")

                                                if elFeature == '':
                                                    the_file.write(
                                                        'srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b 0.2 -c ' + elCollection + \
                                                        ' -l ' + elLife + ' -i ' + elImpact + ' -g 5 -n 0 -s ' + elStrategy + "\n")
                                                else:
                                                    the_file.write(
                                                        'srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b 0.2 -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g 5 -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")

                                            script_file.write("sbatch " + sbatch_filename + "\n")
                                        else:
                                            count += 1
                                            sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-b:0.2-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + '-g:5-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                                            with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                the_file.write(
                                                    "#!/bin/sh\n#SBATCH --job-name=sigir\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n")
                                                if elFeature == '':
                                                    the_file.write(
                                                        'srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b 0.2 -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g 5 -n 0 -s ' + elStrategy + "\n")
                                                else:
                                                    the_file.write(
                                                        'srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b 0.2 -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g 5 -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")
                                            script_file.write("sbatch " + sbatch_filename + "\n")

    print count


def checkDoneXp():
    def runOk(dirFold):

        listDirXp = os.listdir(dirFold)
        if len(listDirXp) < xpNb: return False

        for dir in listDirXp:
            dirExpe = join(dirFold, dir)
            filesInExpe = os.listdir(dirExpe)
            if "completed.txt" not in filesInExpe: return False
        return True

    listCompleted = []
    for el in listCollectionDir:
        dirResult = dirResult + el + "/"
        for fold in listFold:
            dirResult += fold + "/training/"
            if runOk(dirResult): listCompleted.append(dirResult)


    return listCompleted


def extractMapXp(fold):
    maps[fold] = {}
    table = []

    for xp in os.listdir(fold):
        outfilename = join(fold, xp) + "/results.txt"
        outfilenameeval = join(fold, xp) + "/results_trec.txt"
        if "web2014" in xp:
            table = ["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/trec_eval.9.0/trec_eval", '-M50', "-q",
                     "/osirim/sig/PROJET/PRINCESS/qrels/web2014/qrels.all.web2014dedup.txt", '"' + outfilename + '"',
                     ">",
                     '"' + outfilenameeval + '"']
        elif "robust" in xp:
            table = ["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/trec_eval.9.0/trec_eval", "-M50", "-q",
                     "/osirim/sig/PROJET/PRINCESS/qrels/robust2004/qrels.robust2004.txt", '"' + outfilename + '"', ">",
                     '"' + outfilenameeval + '"']
        # print " ".join(table)
        os.system(" ".join(table))


def writeScriptTest():
    with open(outfilenameeval, 'r') as myFile:
        for line in myFile:
            if "all" in line:
                for i in re.finditer(regex, line):
                    # feat = i.group(2)
                    maps[fold][xp] = float(i.group(3))

                    if "group" in elType:
                        count += 1
                        sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-b:0.2-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                          '-g:5-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                        with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                            the_file.write(
                                "#!/bin/sh\n#SBATCH --job-name=sigir\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n")

                            if elFeature == '':
                                the_file.write(
                                    'srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b 0.2 -c ' + elCollection + \
                                    ' -l ' + elLife + ' -i ' + elImpact + ' -g 5 -n 0 -s ' + elStrategy + "\n")
                            else:
                                the_file.write(
                                    'srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b 0.2 -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g 5 -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")

                        script_file.write("sbatch " + sbatch_filename + "\n")
                    else:
                        count += 1
                        sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-b:0.2-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + '-g:5-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                        with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                            the_file.write(
                                "#!/bin/sh\n#SBATCH --job-name=sigir\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n")
                            if elFeature == '':
                                the_file.write(
                                    'srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b 0.2 -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g 5 -n 0 -s ' + elStrategy + "\n")
                            else:
                                the_file.write(
                                    'srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b 0.2 -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g 5 -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")
                        script_file.write("sbatch " + sbatch_filename + "\n")


def findBestConfig(fold):
    listResults = maps[fold]
    sorted_x = sorted(x.items(), key=operator.itemgetter(1), reverse=True)
    best = sorted_x[0]








# Expe generation
generate_script()

# Script execution
os.system("chmod a+x " + dirname + "/run.sh")
os.system("./" + dirname + "/run.sh")

startTime = time.time()
while get_running_jobs() > 0:
    if time.time() - startTime % 7200 == 0:
        l = checkDoneXp()
        if len(l) > 0:
            for fold in l:
                extractMapXp(fold)
                findBestConfig(fold)
