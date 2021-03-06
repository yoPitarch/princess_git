#!/bin/sh
#SBATCH --job-name=discFreq
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hubert@irit.fr
#SBATCH --output=df.out
#SBATCH --error=df.err
#SBATCH -n 1
#SBATCH -N 1
srun -n 1 python extract_featureIndri.py ../../param/config_featuresIndri discFreq
