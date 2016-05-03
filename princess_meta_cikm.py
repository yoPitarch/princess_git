# -*- coding: utf-8 -*-
import operator
import os
import re
import sys
import time
from os.path import join

dirname = '/osirim/sig/PROJET/PRINCESS/code/script_experiments_cikm/'
dirResult = '/osirim/sig/PROJET/PRINCESS/results/princess_cikm/'

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
# listFold = ["3", "4", "5"]
listType = ['robin', 'grouprobinoptim', 'swiss', 'groupswissoptim']
listFeatureLetor = ['']
listFeature = ['', ','.join(['f' + str(x) for x in range(3, 52, 3)]),
               ','.join(['f' + str(x) for x in range(28, 46)])]

listImpact = ['0', '1']
listRound = ['10', '20', '30']
# listCollection = ['indri_web2014clueweb12_adhoc_max50', 'indri_robust2004_max50']
listCollection = ['indri_web2014clueweb12_adhoc_max50', 'indri_robust2004_max50', "NP2003", "NP2004", "OHSUMED",
                  "TD2003", "TD2004", "HP2003", "HP2004"]
# listCollection = ['indri_web2014clueweb12_adhoc_max50']
# listCollectionDir = ["web2014", 'robust2004']
listCollectionDir = ["web2014", 'robust2004', "NP2003", "NP2004", "OHSUMED", "TD2003", "TD2004", "HP2003", "HP2004"]
# listCollectionDir = ["web2014"]


listLife = ['0', '2', '5', '10', '20']
listStrategy = ['0']
listGroup = ['5','2']
listBest = ['0.1', '0.2']
listBoost = ["undifferentiated", "upper", "seed"]
listAlpha = ['3', '5']
listTopX = ['10', '20']

regex = '^(map)\s+([\w\d]{3})(.*)'
analyzedXp = []
maps = {}
xpNb = 0


def get_running_jobs():
    command = "squeue -u quaesig |wc -l > nbProc.txt"
    os.system(command)
    runningJobs = 0
    with open("nbProc.txt", "r") as f:
        for l in f:
            runningJobs = int(l.strip()) - 1
            # print "line: ", l, "/ jobs:", runningJobs
    return runningJobs


def generate_script():
    count = 0
    global xpNb
    global listFeature

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
            count = 0
            for elType in listType:
                if "robin" in elType:
                    nbProc = 10
                else:
                    nbProc = 1
                for elCollection in listCollection:
                    if "web" not in elCollection and "robust" not in elCollection:  listFeature = ['']
                    for elImpact in listImpact:
                        for elFeature in listFeature:
                            for elLife in listLife:
                                for elStrategy in listStrategy:
                                    for elBoost in listBoost:
                                        if elBoost == "undifferentiated":
                                            if "group" in elType:  # group
                                                for elGroup in listGroup:
                                                    for elBest in listBest:
                                                        if "swiss" in elType:  # groupswiss
                                                            for elRound in listRound:
                                                                count += 1
                                                                sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-b:' + elBest + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                                  '-g:' + elGroup + '-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                                                                with open(dirname + '/' + sbatch_filename,
                                                                          'w') as the_file:
                                                                    the_file.write(
                                                                        "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                            count) + "\n#SBATCH --mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                            count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                            count) + ".err \n#SBATCH -c " + str(
                                                                            nbProc + 1) + "\n ")

                                                                    if elFeature == '':
                                                                        the_file.write(
                                                                            'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + \
                                                                            ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + "\n")
                                                                    else:
                                                                        the_file.write(
                                                                            'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")

                                                                script_file.write(
                                                                    "sbatch " + dirname + sbatch_filename + "\n")


                                                        else:  # grouprobin
                                                            count += 1
                                                            sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-b:' + elBest + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                              '-g:' + elGroup + '-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                                                            with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                                the_file.write(
                                                                    "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                        count) + "\n#SBATCH --mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                        count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                        count) + ".err \n#SBATCH -c " + str(
                                                                        nbProc + 1) + "\n ")

                                                                if elFeature == '':
                                                                    the_file.write(
                                                                        'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                            nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -b ' + elBest + ' -c ' + elCollection + \
                                                                        ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + "\n")
                                                                else:
                                                                    the_file.write(
                                                                        'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                            nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -b ' + elBest + ' -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")

                                                            script_file.write(
                                                                "sbatch " + dirname + sbatch_filename + "\n")

                                            else:  # non group
                                                if "swiss" in elType:  # swiss
                                                    for elRound in listRound:
                                                        count += 1
                                                        sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                          '-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                                                        with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                            the_file.write(
                                                                "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                    count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                    count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                    count) + ".err \n#SBATCH -c " + str(
                                                                    nbProc + 1) + "\n ")

                                                            if elFeature == '':
                                                                the_file.write(
                                                                    'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                        nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -c ' + elCollection + \
                                                                    ' -l ' + elLife + ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + "\n")
                                                            else:
                                                                the_file.write(
                                                                    'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                        nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")

                                                        script_file.write("sbatch " + dirname + sbatch_filename + "\n")


                                                else:  # robin
                                                    count += 1
                                                    sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                      '-s:' + elStrategy + '-a-f:' + elFeature + '.sh'
                                                    with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                        the_file.write(
                                                            "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                count) + ".err \n#SBATCH -c " + str(
                                                                nbProc + 1) + "\n ")

                                                        if elFeature == '':
                                                            the_file.write(
                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -c ' + elCollection + \
                                                                ' -l ' + elLife + ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + "\n")
                                                        else:
                                                            the_file.write(
                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -c ' + elCollection + ' -l ' + elLife + ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + "\n")

                                                    script_file.write("sbatch " + dirname + sbatch_filename + "\n")
                                        elif elBoost == "upper":
                                            for elAlpha in listAlpha:
                                                if "group" in elType:  # group
                                                    for elGroup in listGroup:
                                                        for elBest in listBest:
                                                            if "swiss" in elType:  # groupswiss
                                                                for elRound in listRound:
                                                                    count += 1
                                                                    sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-b:' + elBest + '-c:' + elCollection + '-l:' \
                                                                                      + elLife + '-i:' + elImpact + \
                                                                                      '-g:' + elGroup + '-s:' + elStrategy + '-a-f:' + elFeature + '-w:' + elBoost + '-y:' + elAlpha + '.sh'
                                                                    with open(dirname + '/' + sbatch_filename,
                                                                              'w') as the_file:
                                                                        the_file.write(
                                                                            "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                                count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                                count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                                count) + ".err \n#SBATCH -c " + str(
                                                                                nbProc + 1) + "\n ")

                                                                        if elFeature == '':
                                                                            the_file.write(
                                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + \
                                                                                ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -w ' + elBoost + ' -y ' + elAlpha + "\n")
                                                                        else:
                                                                            the_file.write(
                                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + ' -l ' + elLife +
                                                                                ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + ' -w ' + elBoost + ' -y ' + elAlpha + "\n")

                                                                    script_file.write(
                                                                        "sbatch " + dirname + sbatch_filename + "\n")


                                                            else:  # grouprobin
                                                                count += 1
                                                                sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-b:' + elBest + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                                  '-g:' + elGroup + '-s:' + elStrategy + '-a-f:' + elFeature + '-w:' + elBoost + '-y:' + elAlpha + '.sh'
                                                                with open(dirname + '/' + sbatch_filename,
                                                                          'w') as the_file:
                                                                    the_file.write(
                                                                        "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                            count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                            count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                            count) + ".err \n#SBATCH -c " + str(
                                                                            nbProc + 1) + "\n ")

                                                                    if elFeature == '':
                                                                        the_file.write(
                                                                            'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -b ' + elBest + ' -c ' + elCollection + \
                                                                            ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -w ' + elBoost + ' -y ' + elAlpha + "\n")
                                                                    else:
                                                                        the_file.write(
                                                                            'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -b ' + elBest + ' -c ' + elCollection + ' -l ' + elLife +
                                                                            ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + ' -w ' + elBoost + ' -y ' + elAlpha + "\n")

                                                                script_file.write(
                                                                    "sbatch " + dirname + sbatch_filename + "\n")

                                                else:  # non group
                                                    if "swiss" in elType:  # swiss
                                                        for elRound in listRound:
                                                            count += 1
                                                            sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                              '-s:' + elStrategy + '-a-f:' + elFeature + '-w:' + elBoost + '-y:' + elAlpha + '.sh'
                                                            with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                                the_file.write(
                                                                    "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                        count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                        count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                        count) + ".err \n#SBATCH -c " + str(
                                                                        nbProc + 1) + "\n ")

                                                                if elFeature == '':
                                                                    the_file.write(
                                                                        'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                            nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -c ' + elCollection + \
                                                                        ' -l ' + elLife + ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -w ' + elBoost + ' -y ' + elAlpha + "\n")
                                                                else:
                                                                    the_file.write(
                                                                        'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                            nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -c ' + elCollection + ' -l ' + elLife +
                                                                        ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + ' -w ' + elBoost + ' -y ' + elAlpha + "\n")

                                                            script_file.write(
                                                                "sbatch " + dirname + sbatch_filename + "\n")


                                                    else:  # robin
                                                        count += 1
                                                        sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                          '-s:' + elStrategy + '-a-f:' + elFeature + '-w:' + elBoost + '-y:' + elAlpha + '.sh'
                                                        with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                            the_file.write(
                                                                "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                    count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                    count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                    count) + ".err \n#SBATCH -c " + str(
                                                                    nbProc + 1) + "\n ")

                                                            if elFeature == '':
                                                                the_file.write(
                                                                    'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                        nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -c ' + elCollection + \
                                                                    ' -l ' + elLife + ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -w ' + elBoost + ' -y ' + elAlpha + "\n")
                                                            else:
                                                                the_file.write(
                                                                    'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                        nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -c ' + elCollection + ' -l ' + elLife +
                                                                    ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + ' -w ' + elBoost + ' -y ' + elAlpha + "\n")

                                                        script_file.write("sbatch " + dirname + sbatch_filename + "\n")

                                        else:
                                            for elAlpha in listAlpha:
                                                for elTopX in listTopX:
                                                    if "group" in elType:  # group
                                                        for elGroup in listGroup:
                                                            for elBest in listBest:
                                                                if "swiss" in elType:  # groupswiss
                                                                    for elRound in listRound:
                                                                        count += 1
                                                                        sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-b:' + elBest + '-c:' + elCollection + '-l:' \
                                                                                          + elLife + '-i:' + elImpact + \
                                                                                          '-g:' + elGroup + '-s:' + elStrategy + '-a-f:' + elFeature + '-w:' + elBoost + '-y:' + elAlpha + '-z:' + elTopX + '.sh'
                                                                        with open(dirname + '/' + sbatch_filename,
                                                                                  'w') as the_file:
                                                                            the_file.write(
                                                                                "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                                    count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                                    count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                                    count) + ".err \n#SBATCH -c " + str(
                                                                                    nbProc + 1) + "\n ")

                                                                            if elFeature == '':
                                                                                the_file.write(
                                                                                    'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                        nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + \
                                                                                    ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -w ' + elBoost + ' -y ' + elAlpha + ' -z ' + elTopX + "\n")
                                                                            else:
                                                                                the_file.write(
                                                                                    'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                        nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -b ' + elBest + ' -c ' + elCollection + ' -l ' + elLife +
                                                                                    ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + ' -w ' + elBoost + ' -y ' + elAlpha + ' -z ' + elTopX + "\n")

                                                                        script_file.write(
                                                                            "sbatch " + dirname + sbatch_filename + "\n")


                                                                else:  # grouprobin
                                                                    count += 1
                                                                    sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-b:' + elBest + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                                      '-g:' + elGroup + '-s:' + elStrategy + '-a-f:' + elFeature + '-w:' + elBoost + '-y:' + elAlpha + '-z:' + elTopX + '.sh'
                                                                    with open(dirname + '/' + sbatch_filename,
                                                                              'w') as the_file:
                                                                        the_file.write(
                                                                            "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                                count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                                count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                                count) + ".err \n#SBATCH -c " + str(
                                                                                nbProc + 1) + "\n ")

                                                                        if elFeature == '':
                                                                            the_file.write(
                                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -b ' + elBest + ' -c ' + elCollection + \
                                                                                ' -l ' + elLife + ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -w ' + elBoost + ' -y ' + elAlpha + ' -z ' + elTopX + "\n")
                                                                        else:
                                                                            the_file.write(
                                                                                'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                    nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -b ' + elBest + ' -c ' + elCollection + ' -l ' + elLife +
                                                                                ' -i ' + elImpact + ' -g ' + elGroup + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + ' -w ' + elBoost + ' -y ' + elAlpha + ' -z ' + elTopX + "\n")

                                                                    script_file.write(
                                                                        "sbatch " + dirname + sbatch_filename + "\n")

                                                    else:  # non group
                                                        if "swiss" in elType:  # swiss
                                                            for elRound in listRound:
                                                                count += 1
                                                                sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-r:' + elRound + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                                  '-s:' + elStrategy + '-a-f:' + elFeature + '-w:' + elBoost + '-y:' + elAlpha + '-z:' + elTopX + '.sh'
                                                                with open(dirname + '/' + sbatch_filename,
                                                                          'w') as the_file:
                                                                    the_file.write(
                                                                        "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                            count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                            count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                            count) + ".err \n#SBATCH -c " + str(
                                                                            nbProc + 1) + "\n ")

                                                                    if elFeature == '':
                                                                        the_file.write(
                                                                            'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -c ' + elCollection + \
                                                                            ' -l ' + elLife + ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -w ' + elBoost + ' -y ' + elAlpha + ' -z ' + elTopX + "\n")
                                                                    else:
                                                                        the_file.write(
                                                                            'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                                nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -r ' + elRound + ' -c ' + elCollection + ' -l ' + elLife +
                                                                            ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + ' -w ' + elBoost + ' -y ' + elAlpha + ' -z ' + elTopX + "\n")

                                                                script_file.write(
                                                                    "sbatch " + dirname + sbatch_filename + "\n")


                                                        else:  # robin
                                                            count += 1
                                                            sbatch_filename = 'osirim_battle-t:' + elType + '-x:' + elFold + '-c:' + elCollection + '-l:' + elLife + '-i:' + elImpact + \
                                                                              '-s:' + elStrategy + '-a-f:' + elFeature + '-w:' + elBoost + '-y:' + elAlpha + '-z:' + elTopX + '.sh'
                                                            with open(dirname + '/' + sbatch_filename, 'w') as the_file:
                                                                the_file.write(
                                                                    "#!/bin/sh\n#SBATCH --job-name=" + elFold + "_" + str(
                                                                        count) + "\n#SBATCH --exclude=co2-nc08,co2-nc09\n--mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=logs/" + elFold + "_" + str(
                                                                        count) + ".out\n#SBATCH --error=logs/" + elFold + "_" + str(
                                                                        count) + ".err \n#SBATCH -c " + str(
                                                                        nbProc + 1) + "\n ")

                                                                if elFeature == '':
                                                                    the_file.write(
                                                                        'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                            nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -c ' + elCollection + \
                                                                        ' -l ' + elLife + ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -w ' + elBoost + ' -y ' + elAlpha + ' -z ' + elTopX + "\n")
                                                                else:
                                                                    the_file.write(
                                                                        'srun /logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p  ' + str(
                                                                            nbProc) + ' -t ' + elType + ' -x -' + elFold + ' -c ' + elCollection + ' -l ' + elLife +
                                                                        ' -i ' + elImpact + ' -n 0 -s ' + elStrategy + ' -a -f ' + elFeature + ' -w ' + elBoost + ' -y ' + elAlpha + ' -z ' + elTopX + "\n")

                                                            script_file.write(
                                                                "sbatch " + dirname + sbatch_filename + "\n")

            xpNb = count

    print "[Nb expe per folfd:", xpNb, "]"
    print "[Nb expe launched:", xpNb * len(listFold), "]"


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

        if not (os.path.exists(outfilenameeval)):

            # print "\t\t outfilename:", outfilename
            # print "\t\t outfilenameeval:", outfilenameeval
            if "web2014" in xp:
                table = ["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/trec_eval.9.0/trec_eval", '-M50', "-q",
                         "/osirim/sig/PROJET/PRINCESS/qrels/web2014/qrels.all.web2014dedup.txt",
                         '"' + outfilename + '"',
                         ">",
                         '"' + outfilenameeval + '"']
            elif "robust" in xp:
                table = ["/osirim/sig/CORPUS-TRAV/TREC-ADHOC/trec_eval.9.0/trec_eval", "-M50", "-q",
                         "/osirim/sig/PROJET/PRINCESS/qrels/robust2004/qrels.robust2004.txt", '"' + outfilename + '"',
                         ">",
                         '"' + outfilenameeval + '"']
            # print "command", " ".join(table)
            os.system(" ".join(table))

        with open(outfilenameeval, 'r') as myFile:
            for line in myFile:
                if "all" in line:
                    for i in re.finditer(regex, line):
                        # feat = i.group(2)
                        maps[fold][xp] = float(i.group(3))
                        # print maps


def runTest(fold, best):
    idfold = fold.split("/")[-3]
    header = "#!/bin/sh\n#SBATCH --job-name=best" + str(len(
        analyzedXp)) + "\n#SBATCH --mail-type=FAIL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=best" + str(
        len(analyzedXp)) + ".out\n#SBATCH --error=best" + str(len(analyzedXp)) + ".err \n#SBATCH -n " + str(
        nbProc + 1) + "\n "
    command = "/logiciels/Python-2.7/bin/python2.7 " \
              "/projets/sig/PROJET/PRINCESS/code/princess_git/princess_cikm.py -p " + str(nbProc) + " -x " + idfold
    t = best.split("-")
    for param in t:
        tparam = param.split(":")
        print tparam
        if tparam[0] != "a":
            command += " -" + tparam[0] + " " + tparam[1]
        else:
            command += " -" + tparam[0]

    # print command
    with open("scriptBest.sh", "w") as fout:
        fout.write(header)
        fout.write(command)

    os.system("sbatch scriptBest.sh")


def findBestConfig(fold):
    listResults = {}
    listResults = maps[fold]
    sorted_x = sorted(listResults.items(), key=operator.itemgetter(1), reverse=True)
    best = sorted_x[0][0]
    # print sorted_x[0]
    return best


# Expe generation
generate_script()

# Script execution
os.system("scancel -u quaesig")
os.system("chmod a+x " + dirname + "run.sh")
sys.exit()
os.system(dirname + "run.sh")

interval = 1000
startTime = time.time()
isCheckDone = False
while get_running_jobs() > 0:
    t = time.time() - startTime
    # print int(t)
    if t > 0 and int(t) % interval == 0 and not isCheckDone:
        print "[Start check procedure]"
        isCheckDone = True
        l = checkDoneXp()
        if len(l) > 0:
            for fold in l:
                if fold not in analyzedXp:
                    extractMapXp(fold)
                    best = findBestConfig(fold)
                    runTest(fold, best)
                    analyzedXp.append(fold)
                    # time.sleep()
    if int(t) % interval > 0: isCheckDone = False

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
