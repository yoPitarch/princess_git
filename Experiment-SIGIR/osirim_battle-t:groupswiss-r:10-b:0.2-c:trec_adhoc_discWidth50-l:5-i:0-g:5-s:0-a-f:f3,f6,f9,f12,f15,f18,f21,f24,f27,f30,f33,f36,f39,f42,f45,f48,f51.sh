#!/bin/sh
#SBATCH --job-name=sigir
#SBATCH --mail-type=ALL
#SBATCH --mail-user=pitarch@irit.fr
#SBATCH --output=group.out
#SBATCH --error=group.err
srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t groupswiss -r 10 -b 0.2 -c trec_adhoc_discWidth50 -l 5 -i 0 -g 5 -n 0 -s 0 -a -f f3,f6,f9,f12,f15,f18,f21,f24,f27,f30,f33,f36,f39,f42,f45,f48,f51
