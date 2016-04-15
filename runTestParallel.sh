#!/bin/bash
#
#SBATCH -n 1                      # number of cores
#SBATCH -o testParallgro.out        # STDOUT
#SBATCH -e testParallgro.err        # STDERR
#SBATCH --mail-type=ALL      # notifications for job done & fail
#SBATCH --mail-user=pitarch@irit.fr # send-to address

/logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess.py -t grouprobinoptim -r 20 -b 0.2 -c indri_web2014clueweb12_adhoc_max50 -l 5 -i 1 -g 5 -n 0 -s 0 -p 1
