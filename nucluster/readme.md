# Using COVID-19 CMS modelling workflow on the NU cluster 'Quest'


## Directories
The COVID-19 project files are located in `/projects/p30781/covidproject/covid-chicago/`.
A cloned version of the git repository can be found under `/projects/p30781/covidproject/covid-chicago/`.

##Requirements:
All the modules need to be installed on the personal quest environment 
- use pip install ... in your terminal 
- install `dotenv` and `yamlordereddictloader`
`conda create --name dotenv-py37 -c conda-forge python-yamlordereddictloader python=3.7 --yes`
`source activate dotenv-py37`
`conda install -c conda-forge yamlordereddictloader`

### Virtual environment
Alternatively, a virtual environment can be activated using:
i.e. add a `set-covid-chicago` command in the `bash.profile` file in the home directory

	set-covid-chicago(){
		module purge all
		module load python/anaconda3.6
		source activate /projects/p30781/anaconda3/envs/team-test-py37
	}
  
### Syncing files between Box and Quest 
[Box syncing](https://kb.northwestern.edu/page.php?id=70521):

	mirror-box-covid(){
		lftp -p 990 -u <useremail> ftps://ftp.box.com -e "mirror NU-malaria-team/data/covid_IDPH/Cleaned\ Data/ /projects/p30781/covidproject/data/covid_IDPH/Cleaned\ Data/; exit"
		lftp -p 990 -u <useremail> ftps://ftp.box.com -e "mirror NU-malaria-team/data/covid_IDPH/Corona\ virus\ reports/ /projects/p30781/covidproject/data/covid_IDPH/Corona\ virus\ reports/; exit"
	}
 

### Run simulations 
On Quest jobs are submitted using the SLURM workload manager and syntax ([SLURM on quest](https://kb.northwestern.edu/page.php?id=89456))
`cd /projects/p30781/covidproject/covid-chicago/`
`- python runScenarios.py -rl NUCLUSTER --model "base" -r IL --scenario "baseline"  -n "userinitials"`

The experiments will go to the `_temp` folder on the quest gitrepository. 
To avoid confusion on owner of the simulations it is recommended to include the initials in the experiment name using the name_suffix argument
The `python runScenarios.py` will automatically submit two jobs, one for running simulations and one for the postprocessing, which starts automatically after the first finishes (or is cancelled).
The status of the job submission can be called via `squeue -u <username>`

The single steps are:
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
 - Recommended to zip before copying using `python cleanup_and_zip_simFiles.py --stem "<exp_name>"  --Location "NUCLUSTER" --zip_dir` (--del_trajectories to reduce folder size!)
 - Via Box sync `lftp -p 990 -u  <useremail> ftps://ftp.box.com  -e "mirror -R /projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/<exp_name> NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/<exp_name>; exit"`
 
### Postprocessing
### Postprocessing on the NU cluster 'Quest'
On Quest shell instead of batch files are generated for the same python files as shown above.
For a detailed descripton of the shell files and processing steps, expand below:


The time limit for each single simulation was set to 30 min per default.
Simulation run in the `_temp` folder (`/projects/p30781/covidproject/covid-chicago/_temp/`) in the git repository.
After all simulations ran, they are automatically combined and moved to the Box folder on Quest, located in 
`simulation_output` (`/projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/`)

Wrapper shell script:
- `run_postprocessing.sh` runs automatically after simulation finish, it includes scripts from the list below.

Run from `/projects/p30781/covidproject/covid-chicago/_temp/<exp_name>`
- `0_runCombineAndTrimTrajectories.sh` 
- `0_cleanupSimulations.sh`  calls  [cleanup.py](https://github.com/numalariamodeling/covid-chicago/blob/master/nucluster/cleanup.py) and transfers files from temp to Box (on Quest)

Run from `/projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/<exp_name>`
- `0_locale_age_postprocessing.sh`
- `1_runTraceSelection.sh` 
- (`1_runSimulateTraces.sh` )
- `2_runDataComparison.sh` 
- `3_runProcessTrajectories.sh`
- `4_runRtEstimation.sh` 
- `5_runOverflowProbabilities.sh` 
- `6_runPrevalenceIFR.sh` 
- `7_runICUnonICU.sh` 
- `8_runHospICUDeathsForecast.sh` 
- `9_runCopyDeliverables.sh`
- `10_runIterationComparison.sh` 
- `11_runCleanUpAndZip.sh` 


# Files in this folder
- cleanup.py: moves simulation folder from  `/projects/p30781/covidproject/covid-chicago/_temp/<exp_name>` to Box on quest (`/projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/<exp_name>`), runs automatically after runScenarios.py
- cleanup_and_zip_simFiles.py zips and optionally deletes simulation folder in Box on quest (i.e. before transferring) and per default (!) deletes single trajectories and simulation files.

Example shell job submission files (experiment specific shell files generated in simulation folder)
- submit_cleanup.sh
- submit_combineTrajectories.sh
- submit_compareToData.sh

 
# Useful 'Quest commands'

- Check storage
	`checkproject p30781` for project directory
	`homedu` for home directory

- Check status of submitted jobs 
	`squeue -u <username>`

- Cancel job
	`scancel <jobid>`
	`scancel -u <username> ` # all jobs for that user 
	Note, if simulations runs for too long (some will never finish), it is ok to cancel if enough trajectories have been processed.

- Hold and release job
	`scontrol hold  <jobid>`
	`scontrol release  <jobid>`

- Reset git directory- quick way to discard all changes made and return to last PR (i.e. discard experiment specific edits in the yaml)
	`git reset --hard HEAD`

- Count csv files in folder 
	`ls *.csv | wc -l`

- Load python module
	`module load python/anaconda3.6`

- Load virtual environment module
	``` 
	module purge all
	module load python/anaconda3.6
	source activate /projects/p30781/anaconda3/envs/team-test-py37  
	``` 
	Note, this can be put into a function into the `~/.bash_profile`
  
- Box sync
	`lftp -p 990 -u <useremail> ftps://ftp.box.com -e "mirror <from_dir> <to_dir>; exit"`
  
## Troubleshooting

#### ValueError: cannot cast unit days
1) Load virtual environment  
either with `source activate /projects/p30781/anaconda3/envs/team-test-py37` 
or using 
`source ~/.bash_profile`
`set-covid-chicago`

#### wine: Bad EXE format for Z:\projects\p30781\Box\NU-malaria-team\projects\binaries\compartments\compartments.exe.
1) Check storage and if needed delete/move simulations
2) Backup wine cntainer, i.e. `mv ~/.wine ~/.wine.old99`
3) Check/copy again the `compartments.exe` from Box to Quest
4) Re-configure wine using 
  - `singularity shell -B /projects:/projects /software/singularity/images/singwine-v1.img`
  - `winecfg`



