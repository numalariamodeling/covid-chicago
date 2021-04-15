# Using COVID-19 CMS modelling workflow on the NU cluster 'Quest'


## Directories
The COVID-19 project files are located in `/projects/p30781/covidproject/covid-chicago/` as well as `/projects/b1139/covidproject/`.
A cloned version of the git repository can be found under `/projects/p30781/covidproject/covid-chicago/` (or b1139) 

## Connecting to the NUCLUSTER
See Northwestern Knowledge database [Quest User Guide](https://kb.northwestern.edu/72406)
On Quest jobs are submitted using the SLURM workload manager and syntax ([SLURM on quest](https://kb.northwestern.edu/page.php?id=89456))

## Requirements:

### Wine installation
The [CMS](https://docs.idmod.org/projects/cms/en/latest/index.html) is a windows software, hence we are using [wine](https://www.winehq.org/) for running CMS on the NUCLUSTER (unix). 
To use wine, one must be connected to Quest with X11 forwarding enabled. 
Some applications like [FastX](https://www.starnet.com/fastx/) or [MobaXterm](https://mobaxterm.mobatek.net/) have these connection turned on by default. 

##### Using FastX or MobaXterm
When using FastX or MobaXterm, the wine installation usually pop's up automatically when running simulation for the first time.
If the 'Wine Mono not installed' error appears run

`module load singularity`
`rm -rf ~/.wine`
`singularity shell -B /projects:/projects /software/singularity/images/singwine-v1.img winecfg`

And click *ok* on the configuration window that pops up. 
![model](https://github.com/numalariamodeling/covid-chicago/blob/nucluster/wine_installation.png)


##### Using other ways to connect
For a normal terminal based connection, one must add -X to the ssh command. 
`ssh -X netid@quest.northwestern.edu`


### Git on Quest 

#### Working from shared project folder p30781 or b1139
When having access to the `p30781` or `b1139` allocation, the repository was already cloned.
The directories  `/projects/p30781/covidproject/` are shared folders, and multiple people may work on the same files at the same time!
Therefore it is not recommended to make many edits or commits from that location, except you know what you are doing, who else is using it, or work from a different branch.
A useful command is `git reset --hard HEAD` to remove all changes done on the git repository on quest!
Be sure to commit edits if needed before running that. 
Edits should only be temporary parameter changes in the yaml files if needed, or alternatively add new yaml files that you also have backed-up locally.


#### Working from personal home directory home/<netid>
When using Quest for workflow editing, an advanced (better) option would be to clone your forked repository to your home directory on quest.
The only change required when working from the home directory is to update your paths in the load_paths.py under the if statement for NUCLUSTER. 

### Python packages and virtual environment
A python virtual environment can be activated using:
		module purge all
		module load python/anaconda3.6
		source activate /projects/p30781/anaconda3/envs/team-test-py37
		
For convenience one can define a`set-covid-chicago` command in the `bash.profile` file in the home directory

	set-covid-chicago(){
		module purge all
		module load python/anaconda3.6
		source activate /projects/p30781/anaconda3/envs/team-test-py37
	}
  
and then run `source ~/.bash_profile` followed by `set-covid-chicago` in the terminal, prior to the simulations.
  
Manual package installation is not recommended, but if necessary can be done via pip install from the termianl. Using the requirements.txt.
dotenv and yamlordereddictloader are known to cause issues, and yamlordereddictloader is not required although recommended for save loading of yaml files.
If pip install does not work, the commands below might be useful. 
`conda create --name dotenv-py37 -c conda-forge` 
`source activate dotenv-py37`  
`conda install -c conda-forge yamlordereddictloader` 


## Syncing files between Box and Quest 
[Box syncing](https://kb.northwestern.edu/page.php?id=70521):

	mirror-box-covid(){
		lftp -p 990 -u <useremail> ftps://ftp.box.com -e "mirror NU-malaria-team/data/covid_IDPH/Cleaned\ Data/ /projects/p30781/covidproject/data/covid_IDPH/Cleaned\ Data/; exit"
		lftp -p 990 -u <useremail> ftps://ftp.box.com -e "mirror NU-malaria-team/data/covid_IDPH/Corona\ virus\ reports/ /projects/p30781/covidproject/data/covid_IDPH/Corona\ virus\ reports/; exit"
	}
 
## Run simulations

## Testrun CMS/wine 
To check whether CMS runs on quest run a single simulation via:

`cd /projects/p30781/covidproject/covid-chicago/testrun/`
`dos2unix runSimulations_covid_base_p30781.sh`  
`bash runSimulations_covid_base_p30781.sh` 
(or b1137)

### Full workflow 
In the full workflow multiple simulations submitted as array job to Quest via:
`cd /projects/p30781/covidproject/covid-chicago/`
`python runScenarios.py -r IL -sr EMS_11 --model "locale" --scenario "baseline"  -n "userinitials"`
The running location does not need to be specified (optionally via -rl 'NUCLUSTER') as identified automatically based on the system environment.

The experiments will go to the `_temp` folder on the quest gitrepository. 
To avoid confusion on owner of the simulations it is recommended to include the initials in the experiment name using the name_suffix argument.

The `python runScenarios.py` will automatically submit two jobs, one for running simulations and one for the postprocessing, which starts automatically after the first finishes (or is cancelled).
The status of the job submission can be called via `squeue -u <username>`


The single steps are:
1. Navigate to the project folder: 
	`cd /projects/p30781/covidproject`

2. Prepare simulation input files or copy simulation files (optional):
  - relevant files to edit are the yaml files.
  
3. Submit runScenarios.py : 
	`python runScenarios.py -r IL -sr EMS_11 --model "locale" --scenario "baseline"  -n "userinitials"`
	
4. Submit postprocessing jobs (most run automatically, if not single sbatch files can be submitted as below)
	`cd /projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/<exp_name>/sh"`
	`sbatch 2_runDataComparison.sh"`
	
	 or interactively to see output directly in terminal (for testing)
	`bash 2_runDataComparison.sh"`
	
5. Copy final files to Box
 - Recommended to zip before copying using `python cleanup_and_zip_simFiles.py --stem "<exp_name>"  --Location "NUCLUSTER" --zip_dir` (--del_trajectories to reduce folder size!)
 - Via Box sync `lftp -p 990 -u  <useremail> ftps://ftp.box.com  -e "mirror -R /projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/<exp_name> NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/<exp_name>; exit"`
 
The time limit for each single simulation was set to 2 hours per default.
Simulations run in the `_temp` folder (`/projects/p30781/covidproject/covid-chicago/_temp/`) in the git repository.
After all simulations ran (regardless of being successful), the folder is automatically moved to the Box folder on Quest, located in 
`simulation_output` (`/projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/`)


#### Shell submission scripts 

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


#### No trajectoriesDat.csv
The simulations did not run successfully. Check the log folder within <exp_name>/trajectories/temp.
<!-- future step will prevent simulations from copying if no trajectories there-->

#### ValueError: cannot cast unit days
1) Load virtual environment  
either with `source activate /projects/p30781/anaconda3/envs/team-test-py37` 
or using 
`source ~/.bash_profile`
`set-covid-chicago`

#### Wine Mono not installed 
Reinstall wine
`module load singularity`
`rm -rf ~/.wine`
`singularity shell -B /projects:/projects /software/singularity/images/singwine-v1.img winecfg`

#### wine: Bad EXE format for Z:\projects\p30781\Box\NU-malaria-team\projects\binaries\compartments\compartments.exe.
1) Check storage and if needed delete/move simulations
2) Backup wine cntainer, i.e. `mv ~/.wine ~/.wine.old99`
3) Check/copy again the `compartments.exe` from Box to Quest
4) Re-configure wine using 
  - `singularity shell -B /projects:/projects /software/singularity/images/singwine-v1.img`
  - `winecfg`

#### wine: cannot find '~binaries/compartments/compartments.exe'
Check if compartments.exe exit and if the paths in [load_paths.py](https://github.com/numalariamodeling/covid-chicago/blob/master/load_paths.py) are correctly set!

#### sbatch: error: This does not look like a batch script. 
In some instances, when shell submission files are generated on a local windows machine and copied to quest this error occurs.
Then the sh file needs to be converted via `dos2unix <name_of_sh_file.sh>`


