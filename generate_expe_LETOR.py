# -*- coding: utf-8 -*-
import os, glob

listType = ['robin', 'grouprobin','swiss','groupswiss' ]
listFeature = ['']
listImpact = ['0','1']
listRound = ['10','20']
listCollection = ["HP2003_Fold1","HP2003_Fold2","HP2003_Fold3","HP2003_Fold4","HP2003_Fold5"]
listLife = ['0','2','5','10']
listStrategy = ['1']
listGroup = ['5','10','20']

count = 0 

#nbExp = len(glob.glob('./Experiment*')) + 1
dirname = './Experiment-LETOR-HP2003'
print dirname
os.mkdir(dirname)
with open(dirname+'/run.sh','w') as script_file:
	for elType in listType:
		for elFeature in listFeature:
			for elImpact in listImpact:
				for elRound in listRound:
					for elCollection in listCollection:
						for elLife in listLife:
							for elStrategy in listStrategy:
								for elGroup in listGroup:
									if "group" in elType:
										count += 1
										sbatch_filename = 'osirim_battle-t:'+elType+'-r:'+elRound+'-b:0.2-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-g:'+elGroup+'-s:'+elStrategy+'-a-f:'+elFeature+'.sh'
										with open(dirname+'/'+sbatch_filename, 'w') as the_file:
											the_file.write("#!/bin/sh\n#SBATCH --job-name=sigir\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=lea.laporte@insa-lyon.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n")
											
											if elFeature == '' : the_file.write('srun python /projets/sig/PROJET/PRINCESS/code/princess/princess_version_lea.py -t '+elType+' -r '+elRound+' -b 0.2 -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g '+elGroup+' -n 0 -s '+elStrategy+"\n")
											else : the_file.write('srun python /projets/sig/PROJET/PRINCESS/code/princess/princess_version_lea.py -t '+elType+' -r '+elRound+' -b 0.2 -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g '+elGroup+' -n 0 -s '+elStrategy+' -a -f '+elFeature+"\n")

										script_file.write("sbatch "+sbatch_filename+"\n")
									else:
										count += 1
										sbatch_filename = 'osirim_battle-t:'+elType+'-r:'+elRound+'-b:0.2-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-g:'+elGroup+'-s:'+elStrategy+'-a-f:'+elFeature+'.sh'
										with open(dirname+'/'+sbatch_filename, 'w') as the_file:
											the_file.write("#!/bin/sh\n#SBATCH --job-name=sigir\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=lea.laporte@insa-lyon.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n")
											if elFeature == '' : the_file.write('srun python /projets/sig/PROJET/PRINCESS/code/princess/princess_version_lea.py -t '+elType+' -r '+elRound+' -b 0.2 -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g '+elGroup+' -n 0 -s '+elStrategy+"\n")
											else : the_file.write('srun python /projets/sig/PROJET/PRINCESS/code/princess/princess_version_lea.py -t '+elType+' -r '+elRound+' -b 0.2 -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g '+elGroup+' -n 0 -s '+elStrategy+' -a -f '+elFeature+"\n")
										script_file.write("sbatch "+sbatch_filename+"\n")

print count
