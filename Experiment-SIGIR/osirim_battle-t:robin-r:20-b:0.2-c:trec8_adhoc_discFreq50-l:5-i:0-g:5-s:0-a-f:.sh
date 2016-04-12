#!/bin/sh
#SBATCH --job-name=sigir
#SBATCH --mail-type=ALL
#SBATCH --mail-user=pitarch@irit.fr
#SBATCH --output=group.out
#SBATCH --error=group.err
srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t robin -r 20 -b 0.2 -c trec8_adhoc_discFreq50 -l 5 -i 0 -g 5 -n 0 -s 0
