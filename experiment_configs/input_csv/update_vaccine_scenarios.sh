#!/bin/bash
#SBATCH -A p30781
#SBATCH -p short
#SBATCH -t 00:20:00
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=12G
#SBATCH --job-name="update_vacc_scen"
#SBATCH --error=_temp/vaccine_scenarios.%j.err
#SBATCH --output=_temp/vaccine_scenarios.%j.out


module purge all
module load python/anaconda3.6
source activate /projects/p30781/anaconda3/envs/team-test-py37

cd /home/mrm9534/gitrepos/covid-chicago/data_processing/
python vaccinations_by_age.py
python vaccinations_by_covidregion.py

cd /home/mrm9534/gitrepos/covid-chicago/
module load R/4.0.0
R --vanilla -f  "Rfiles/vaccine_scenarios.R"
R --vanilla -f  "Rfiles/vaccine_scenario_fracSevere.R"


