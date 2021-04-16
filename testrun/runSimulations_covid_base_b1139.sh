#!/bin/bash
#SBATCH -A b1139
#SBATCH -p b1139
#SBATCH -t 00:30:00
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=4G
#SBATCH --job-name="testrun_base"
#SBATCH --error=testrun_base.err
#SBATCH --output=testrun_base.out



module load singularity

singularity exec -B /projects:/projects/ /software/singularity/images/singwine-v1.img wine /projects/b1139/covidproject/binaries/compartments/compartments.exe -c $PWD/simplemodel.cfg -m $PWD/covidmodel_base.emodl