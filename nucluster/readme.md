
# Submission workflow on the NU cluster 'Quest'

The COVID-19 project files are located in `/projects/p30781/covidproject/covid-chicago/`.

1. Navigate to the project folder: 
	`cd /projects/p30781/covidproject`

2. Prepare simulation input files or copy simulation files (optional):
  - relevant files to edit are the yaml and emodl files
  - when done a useful command is `git reset --hard HEAD` to remove all changes done on the git repository on quest ! 
  Be sure to commit edits if needed before running that. However commiting files on the main repository under `/projects/p30781/covidproject/covid-chicago/` is not recommended, as it commits to upstream and not the forked repository.
  
  
3. Submit runScenarios.py : 
	`python runScenarios.py -rl NUCLUSTER -r EMS_1 -c EMSspecific_sample_parameters.yaml -e extendedmodel.emodl  -n "testrun"`
	
4. Submit postprocessing jobs
	`cd /projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/<exp_name>/sh"`
	`sbatch 2_runDataComparison.sh"`

5. Copy final files to Box
 - Recommended to zip before copying using `python cleanup_and_zip_simFiles.py --stem "<exp_name>"  --Location "NUCLUSTER" --zip_dir`
 - Via Box sync `lftp -p 990 -u  <useremail> ftps://box.com -e "mirror -R /projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/<exp_name> NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/<exp_name>; exit"`
 
## Files in this folder
- cleanup.py: moves simulation folder from  `/projects/p30781/covidproject/covid-chicago/_temp/<exp_name>` to Box on quest (`/projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/<exp_name>`), runs automatically after runScenarios.py
- cleanup_and_zip_simFiles.py zips and optionally deletes simulation folder in Box on quest (i.e. before transferring) and per default (!) deletes single trajectories and simulation files.

Example shell job submission files (experiment specific shell files generated in simulation folder)
- submit_cleanup.sh
- submit_combineTrajectories.sh
- submit_compareToData.sh

 
## Useful commands

Check status of submitted jobs 
`squeue -u <username>`

Cancel job
`scancel <jobid>`
`scancel -u <username> ` # all jobs for that user 

Hold and release job
`scontrol hold  <jobid>`
`scontrol release  <jobid>`

Wine error, if the wine container causes issues it may help to copy a new container like below
`mv ~/.wine ~/.wine.old99`

Reset git directory- quick way to discard all changes made and return to last PR (i.e. discard experiment specific edits in the yaml)
`git reset --hard HEAD`

Count csv files in folder 
`ls *.csv | wc -l`

Load python module
`module load python/anaconda3.6`

Load virtual environment module
``` 
module purge all
module load python/anaconda3.6
source activate /projects/p30781/anaconda3/envs/team-test-py37  
``` 
  
  