#!/bin/sh
#SBATCH --job-name=Stdz
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hubert@irit.fr
#SBATCH --output=stdz.out
#SBATCH --error=stdz.err
#SBATCH -n 1
#SBATCH -N 1
#SBATCH --exclusive
srun -n 1 python extract_featureIndri.py ../../param/config_featuresIndri stdz
