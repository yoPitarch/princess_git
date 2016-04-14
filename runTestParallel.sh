#!/bin/bash
#
#SBATCH -n 11                      # number of cores
#SBATCH -o testParall.out        # STDOUT
#SBATCH -e testParall.err        # STDERR
#SBATCH --mail-type=BEGIN,END,FAIL      # notifications for job done & fail
#SBATCH --mail-user=pitarch@irit.fr # send-to address

/logiciels/Python-2.7/bin/python2.7 /projets/sig/PROJET/PRINCESS/code/princess_git/princess.py -t robin -r 20 -b 0.2 -c indri_web2014clueweb12_adhoc_max50 -l 5 -i 1 -g 5 -n 0 -s 0