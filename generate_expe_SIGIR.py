# -*- coding: utf-8 -*-
import os, glob

listType = ['robin', 'grouprobin','swiss','groupswiss' ]
listFeature = ['',','.join(['f'+str(x) for x in range(3,52,3)]),','.join(['f'+str(x) for x in range(28,46)]) ]
listImpact = ['0','1']
listRound = ['10','20']
listCollection = ['trec_adhoc_max50','trec_adhoc_stdz50','trec_adhoc_discWidth50','trec_adhoc_lee50', 
				'trec_adhoc_discFreq50','trec8_adhoc_max50','trec8_adhoc_stdz50','trec8_adhoc_discWidth50',
				'trec8_adhoc_lee50', 'trec8_adhoc_discFreq50']
listLife = ['0','2','5','10']
listStrategy = ['0']

count = 0 

#nbExp = len(glob.glob('./Experiment*')) + 1
dirname = './Experiment-SIGIR'
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
								if "group" in elType:
									count += 1
									sbatch_filename = 'osirim_battle-t:'+elType+'-r:'+elRound+'-b:0.2-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-g:5-s:'+elStrategy+'-a-f:'+elFeature+'.sh'
									with open(dirname+'/'+sbatch_filename, 'w') as the_file:
										the_file.write("#!/bin/sh\n#SBATCH --job-name=sigir\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n")
										
										if elFeature == '' : the_file.write('srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t '+elType+' -r '+elRound+' -b 0.2 -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g 5 -n 0 -s '+elStrategy+"\n")
										else : the_file.write('srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t '+elType+' -r '+elRound+' -b 0.2 -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g 5 -n 0 -s '+elStrategy+' -a -f '+elFeature+"\n")

									script_file.write("sbatch "+sbatch_filename+"\n")
								else:
									count += 1
									sbatch_filename = 'osirim_battle-t:'+elType+'-r:'+elRound+'-b:0.2-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-g:5-s:'+elStrategy+'-a-f:'+elFeature+'.sh'
									with open(dirname+'/'+sbatch_filename, 'w') as the_file:
										the_file.write("#!/bin/sh\n#SBATCH --job-name=sigir\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=pitarch@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n")
										if elFeature == '' : the_file.write('srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t '+elType+' -r '+elRound+' -b 0.2 -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g 5 -n 0 -s '+elStrategy+"\n")
										else : the_file.write('srun python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t '+elType+' -r '+elRound+' -b 0.2 -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g 5 -n 0 -s '+elStrategy+' -a -f '+elFeature+"\n")
									script_file.write("sbatch "+sbatch_filename+"\n")

print count
