#!/bin/bash
#SBATCH -A p30781               # Allocation
#SBATCH -p short                # Queue
#SBATCH -t 04:00:00             # Walltime/duration of the job
#SBATCH -N 1                    # Number of Nodes
#SBATCH --mem=18G               # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --ntasks-per-node=1     # Number of Cores (Processors)
#SBATCH --output=/projects/p30781/covidproject/covid-chicago/nucluster/outputs/processForCivis-%A_%a.out    # Path for output must already exist
#SBATCH --error=/projects/p30781/covidproject/covid-chicago/nucluster/errors/processForCivis-%A_%a.err      # Path for errors must already exist
#SBATCH --job-name="processForCivis"       # Name of job


# load modules you need to use
ml python/anaconda3.6

# A command you actually want to execute:
python /projects/p30781/covidproject/covid-chicago/plotters/process_for_civis_EMSgrp.py --stem "20200826_IL_baseline" --Location "NUCLUSTER"

