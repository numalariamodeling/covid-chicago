
# IEMS_surveillance

new model steps:
scripts up to step 5 are fully tested  
need new .sh to run all code successively (all_run.sh is for old model, but can be used as a referenced for new .sh)   

- 1 run covid model with/without mitigation (no script here)
- 2 grab data series: daily new mild symptomatics  
run: python3 iems_step2_example.py -exp "insert simulation folder name" -loc "NUCLUSTER"  
output: new_symp_mild.csv in the simulation output folder
- 3 downsample to generate survaillance data  
run: module load R/4.0.0  
     R --vanilla -f Step3.R --args "insert simulation folder name"   
output: downsampled_cases.csv in simulation output folder. 
- 4 evaluate Rt & 5 calculate mitigation probability: these two steps are done in the same script
run: python3 final_stage4.py "insert simulation folder name"
- 6 combine death count results
trajectories_death_total.R
combine_death.R
- 7 plot deaths
