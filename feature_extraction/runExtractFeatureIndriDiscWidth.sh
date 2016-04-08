#!/bin/sh
#SBATCH --job-name=discWidth
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hubert@irit.fr
#SBATCH --output=dw.out
#SBATCH --error=dw.err
#SBATCH -n 1
#SBATCH -N 1
srun -n 1 python extract_featureIndri.py ../../param/config_featuresIndri discWidth
