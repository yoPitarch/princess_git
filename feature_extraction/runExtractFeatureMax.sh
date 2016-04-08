#!/bin/sh
#SBATCH --job-name=Max
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hubert@irit.fr
#SBATCH --output=max.out
#SBATCH --error=max.err
#SBATCH -n 1
#SBATCH -N 1
srun -n 1 python extract_feature.py ../../param/config_features max
