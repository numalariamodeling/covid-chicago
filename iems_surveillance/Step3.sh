#!/bin/bash#SBATCH -A b1139#SBATCH -p b1139#SBATCH -t 00:45:00#SBATCH -N 1#SBATCH --ntasks-per-node=1#SBATCH --mem=18G#SBATCH --job-name=“step3”
#SBATCH --mail-user=LaithKassisieh2022@u.northwestern.edu
#SBATCH --mail-type=BEGIN,END,FAIL #SBATCH --error=log/arrayJob_%A_%a.err#SBATCH --output=log/arrayJob_%A_%a.out

module load R/4.0.0

R --vanilla -f Step3-1.R --args 20210531_IL_localeEMS_11_jg_with_mitigation_mitigation
