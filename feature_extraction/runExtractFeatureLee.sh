#!/bin/sh
#SBATCH --job-name=Lee
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hubert@irit.fr
#SBATCH --output=lee.out
#SBATCH --error=lee.err
#SBATCH -n 1
#SBATCH -N 1
srun -n 1 python extract_feature.py ../../param/config_features lee
