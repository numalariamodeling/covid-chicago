#!/bin/bash
#SBATCH --job-name="custom_combine1"       # Name of job
#SBATCH -A b1139               # Allocation
#SBATCH -p b1139                # Queue
#SBATCH -t 02:00:00             # Walltime/duration of the job
#SBATCH -N 1                    # Number of Nodes
#SBATCH --mem=64GB              # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --ntasks-per-node=1     # Number of Cores (Processors)
#SBATCH --mail-user=manuela.runge@northwestern.edu  # Designate email address for job communications
#SBATCH --mail-type=FAIL     # Events options are job BEGIN, END, NONE, FAIL, REQUEUE
#SBATCH --output=/home/mrm9534/jobs/outputs/custom_combine-%A_%a.out    # Path for output must already exist
#SBATCH --error=/home/mrm9534/jobs/errors/custom_combine-%A_%a.err      # Path for errors must already exist
#SBATCH --array=1


# load modules you need to use
module load R/4.0.0

# R --vanilla -f "/home/mrm9534/jobs/split_csvs_by_region.R" 

#R --vanilla -f /projects/p30781/covidproject/covid-chicago/nucluster/split_csvs_by_region.R
#R --vanilla -f /projects/p30781/covidproject/covid-chicago/Rfiles/simulation_plotter/Ki_dat.R
#R --vanilla -f /home/mrm9534/gitrepos/covid-chicago/nucluster/combine_trajectory_chunks.R 
#R --vanilla -f /home/mrm9534/gitrepos/covid-chicago/nucluster/filter_trigger_activated.R 
#cd /home/mrm9534/gitrepos/covid-chicago/nucluster/
#R --vanilla -f /home/mrm9534/gitrepos/covid-chicago/Rfiles/Fig04_combine.R

#R --vanilla -f /home/mrm9534/gitrepos/covid-chicago/Rfiles/Fig5B.R

R --vanilla -f iems_surveillance/Step3-1.R --args 20210531_IL_localeEMS_11_jg_with_mitigation_mitigation






