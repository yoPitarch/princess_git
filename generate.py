# -*- coding: utf-8 -*-
import os, stat, glob

listType = ['grouprobin']
listFeature = ['f37,f38,f39,f40,f41,f42,f46,f47,f48']
listImpact = ['0']
listGroup = ['5']
listRound = ['5']
listBest = ['0.1']
listCollection = ['trec_adhoc_max','trec_adhoc_lee','trec_adhoc_discWidth']
listLife = ['0','40']
listNbFeats = ['8','48']
listStrategy = ['0','5']

nbExp = len(glob.glob('./Experiment*')) + 1
dirname = './Experiment'+str(nbExp)
os.mkdir(dirname)
mainscript_filename = dirname+'/osirim_battle_Exp'+str(nbExp)+'.sh'
with open(mainscript_filename,'w') as script_file:
	os.chmod(mainscript_filename,stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH)
	for elCollection in listCollection:
		for elImpact in listImpact:
			for elStrategy in listStrategy:
				for elLife in listLife:
					for elNbFeats in listNbFeats:
						for elFeature in listFeature:
							for elType in listType:
								if elType == 'grouprobin' or elType == 'groupswiss':
									if elType == 'groupswiss':
										for elRound in listRound:
											for elGroup in listGroup:
												for elBest in listBest:
													sbatch_filename = 'osirim_battle-t:'+elType+'-r:'+elRound+'-b:'+elBest+'-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-g:'+elGroup+'-n:'+elNbFeats+'-s:'+elStrategy+'-d-f:'+elFeature+'.sh'
													sbatch_fullfilename = dirname+'/'+sbatch_filename
													with open(sbatch_fullfilename, 'w') as the_file:
														os.chmod(sbatch_fullfilename,stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH)
														the_file.write("#!/bin/sh\n#SBATCH --job-name=battle_group\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=hubert@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n#SBATCH -n 25\n#SBATCH -N 1\n")
														the_file.write('srun -n 1 python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t '+elType+' -r '+elRound+' -b '+elBest+' -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g '+elGroup+' -n '+elNbFeats+' -s '+elStrategy+' -d -f '+elFeature+"\n")
													script_file.write("sbatch "+sbatch_filename+"\n")
									else:
										for elGroup in listGroup:
											for elBest in listBest:
												sbatch_filename = 'osirim_battle-t:'+elType+'-b:'+elBest+'-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-g:'+elGroup+'-n:'+elNbFeats+'-s:'+elStrategy+'-d-f:'+elFeature+'.sh'
												sbatch_fullfilename = dirname+'/'+sbatch_filename
												with open(sbatch_fullfilename, 'w') as the_file:
													os.chmod(sbatch_fullfilename,stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH)
													the_file.write("#!/bin/sh\n#SBATCH --job-name=battle_group\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=hubert@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n#SBATCH -n 25\n#SBATCH -N 1\n")
													the_file.write('srun -n 1 python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t '+elType+' -b '+elBest+' -c '+elCollection+' -l '+elLife+' -i '+elImpact+' -g '+elGroup+' -n '+elNbFeats+' -s '+elStrategy+' -d -f '+elFeature+"\n")
												script_file.write("sbatch "+sbatch_filename+"\n")
								elif elType == 'swiss':
									for elRound in listRound:
										sbatch_filename = 'osirim_battle-t:'+elType+'-r:'+elRound+'-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-n:'+elNbFeats+'-s:'+elStrategy+'-d-f:'+elFeature+'.sh'
										sbatch_fullfilename = dirname+'/'+sbatch_filename
										with open(sbatch_fullfilename, 'w') as the_file:
											os.chmod(sbatch_fullfilename,stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH)
											the_file.write("#!/bin/sh\n#SBATCH --job-name=battle_group\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=hubert@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n#SBATCH -n 25\n#SBATCH -N 1\n")
											the_file.write("srun -n 1 python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t "+elType+" -r "+elRound+" -c "+elCollection+" -l "+elLife+" -i "+elImpact+" -n "+elNbFeats+" -s "+elStrategy+" -d -f "+elFeature)
										script_file.write("sbatch "+sbatch_filename+"\n")
								else:
									sbatch_filename = 'osirim_battle-t:'+elType+'-c:'+elCollection+'-l:'+elLife+'-i:'+elImpact+'-n:'+elNbFeats+'-s:'+elStrategy+'-d-f:'+elFeature+'.sh'
									sbatch_fullfilename = dirname+'/'+sbatch_filename
									with open(sbatch_fullfilename, 'w') as the_file:
										os.chmod(sbatch_fullfilename,stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH)
										the_file.write("#!/bin/sh\n#SBATCH --job-name=battle_group\n#SBATCH --mail-type=ALL\n#SBATCH --mail-user=hubert@irit.fr\n#SBATCH --output=group.out\n#SBATCH --error=group.err\n#SBATCH -n 25\n#SBATCH -N 1\n")
										the_file.write("srun -n 1 python /projets/sig/PROJET/PRINCESS/code/princess/princess.py -t "+elType+" -c "+elCollection+" -l "+elLife+" -i "+elImpact+" -n "+elNbFeats+" -s "+elStrategy+" -d -f "+elFeature)
									script_file.write("sbatch "+sbatch_filename+"\n")
