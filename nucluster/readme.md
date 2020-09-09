
# Submission workflow on the NU cluster 'Quest'

The covid files are located within a project under '/projects/p30781/'.
The directory '/projects/p30781/' includes also non-covid projects, hence '/projects/p30781/covidproject' is treated as the home directory with separate data and project folders to assemble the directory structure that exists locally,

1. Navigate to the project folder: 
	cd  /projects/p30781/covidproject

2. Prepare simulations or copy simulation files (optional):
  - However when doing this, do not forget to reset the git repository or ignore the new files or commit if relevant to keep the git repo clean while avoiing PR conflicts)
  - relevant files to edit are the yaml and emodl files
  
3. Submit python job (example) : 
	python runScenarios.py -rl NUCLUSTER -r EMS_1 -c EMSspecific_sample_parameters.yaml -e extendedmodel.emodl  -n "testrun"
	
4. Submit depdenent jobs
 Either submit sh files from experiment folder, or use templates in /projects/p30781/covidproject/covid-chicago/nucluster/
  ------ required
  a) run simulations (automatically submitted)
  ------ required
  b) combineTrajectories 
  c) cleanup
  ------ optional
  d) datacomparison
  e) Rt estimation
  f) processForCivis 
  g) ... any other analysis script to run


	Example 
	cd /projects/p30781/covidproject/covid-chicago/_temp/20200908_EMS_1_test6/trajectories/
	dos2unix runSimulations.sh
	sbatch runSimulations.sh
	
	cd /projects/p30781/covidproject/covid-chicago/_temp/20200908_EMS_1_test6
	
	###Submit after simulation are finished using job id
	sbatch --dependency=afterok:1026135 combineSimulations.sh
	
	###Submit after combineSimulations using job id
	sbatch --dependency=afterok:1026154 cleanupSimulations.sh
	
	###Submit after cleanupSimulations using job id
	sbatch --dependency=afterok:1026155 compareToData.sh
	
	###Submit after cleanupSimulations using job id
	sbatch --dependency=afterok:1026155 processForCivis.sh


5. Copy final files to Box
 - Either using automatic syncronization or copy relevant experiment files.
 
 
## Troubleshooting/ useful commands

Check status of submitted jobs 
squeue -u <username>

Cancel job
scancel <jobid>
scancel -u <username>  # all jobs for that user 

Hold and release job
scontrol hold  <jobid>
scontrol release  <jobid>

Load R module
  module load R/4.0.0

Wine error, if the wine container causes issues it may help to just copy a new container like below
  mv ~/.wine ~/.wine.old99

Reset git directory- quick way to discard all changes made and return to last PR (i.e. discard experiment specific edits in the yaml)
  git reset --hard HEAD

Count csv files in folder 
  ls *.csv | wc -l
  
  
  
  