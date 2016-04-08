#!/bin/sh
#SBATCH --job-name=indri-index
#SBATCH --mail-type=ALL
#SBATCH --mail-user=pitarch@irit.fr
#SBATCH --output=features.out
#SBATCH --error=features.err

date
python --version
cd /projets/sig/PROJET/PRINCESS/mongodb/mongodb-linux-x86_64-2.6.1/bin
#numactl --interleave=all ./mongod -f ../mongodb.conf
./mongo --port 28018 --host co2-ni01.irit.fr

cd /projets/sig/PROJET/PRINCESS/code/princess/feature_extraction
python extract_feature.py /projets/sig/PROJET/PRINCESS/code/param/config_features
date