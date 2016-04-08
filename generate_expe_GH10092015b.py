# -*- coding: utf-8 -*-
import os, glob

listType = ['robin', 'grouprobin', 'return']
listFeature = ['f9,f24,f27,f30,f33,f45']
listImpact = ['0','1']
listGroup = ['10']
listRound = ['20']
listBest = ['0.1','0.3']
listCollection = ['trec8_adhoc_max100','trec8_adhoc_stdz100','trec8_adhoc_discWidth100','trec8_adhoc_lee100', 'trec8_adhoc_discFreq100']
listLife = ['0','20']
listNbFeats = ['0','2']
listStrategy = ['0','1']

count = 0 

#nbExp = len(glob.glob('./Experiment*')) + 1
dirname = './Experiment-GH10092015b'
print dirname
os.mkdir(dirname)
with open(dirname+'/run.sh','w') as script_file:
	for elCollection in listCollection:
		for elImpact in listImpact:
			for elStrategy in listStrategy:
				for elRound in listRound:
					for elLife in listLife:
						for elNbFeats in listNbFeats:
							for elFeature in listFeature:
								for elType in listType:
									if elType == 'grouprobin' or elType == 'groupswiss' or elType == 'grouprobinoptim' or elType == 'groupswissoptim':
										for elGroup in listGroup:
											for elBest in listBest:
												count += 1
												sbatch_filename = 'osirim_battle-t:'+elType+'-r:'+elRound+'-b:'+elBest+'-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-g:'+elGroup+'-n:'+elNbFeats+'-s:'+elStrategy+'-d-a-f:'+elFeature+'.sh'
												with open(dirname+'/'+sbatch_filename, 'w') as the_file:
													the_file.write("#!/bin/sh\n#SBATCH --job-name=battle_group\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=hubert@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n#SBATCH -n 1\n#SBATCH -N 1\n")
													the_file.write('srun -n 1 python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t '+elType+' -r '+elRound+' -b '+elBest+' -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g '+elGroup+' -n '+elNbFeats+' -s '+elStrategy+' -d -a -f '+elFeature+"\n")
												script_file.write("sbatch "+sbatch_filename+"\n")
									else:
										count += 1
										sbatch_filename = 'osirim_battle-t:'+elType+'-r:'+elRound+'-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-n:'+elNbFeats+'-s:'+elStrategy+'-d-a-f:'+elFeature+'.sh'
										with open(dirname+'/'+sbatch_filename, 'w') as the_file:
											the_file.write("#!/bin/sh\n#SBATCH --job-name=battle_group\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=hubert@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n#SBATCH -n 1\n#SBATCH -N 1\n")
											the_file.write("srun -n 1 python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t "+elType+" -r "+elRound+" -c "+elCollection+" -l "+elLife+" -i "+elImpact+" -n "+elNbFeats+" -s "+elStrategy+" -d -a -f "+elFeature+"\n")
										script_file.write("sbatch "+sbatch_filename+"\n")

print count
