#!/bin/bash
#SBATCH --mail-user=LaithKassisieh2022@u.northwestern.edu
#SBATCH --mail-type=BEGIN,END,FAIL 

module load R/4.0.0

R --vanilla -f Step3-1.R --args 20210531_IL_localeEMS_11_jg_with_mitigation_mitigation