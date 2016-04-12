#!/bin/sh
#SBATCH --job-name=sigir
#SBATCH --mail-type=ALL
#SBATCH --mail-user=pitarch@irit.fr
#SBATCH --output=group.out
#SBATCH --error=group.err
srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t grouprobin -r 20 -b 0.2 -c trec8_adhoc_lee50 -l 10 -i 1 -g 5 -n 0 -s 0
