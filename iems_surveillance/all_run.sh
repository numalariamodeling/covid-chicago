#!/bin/sh
#Step 1
#enter arguments

region=$1
subregion=$2
scenario=$3
model=$4
name=$5

n_region=${region:3}
n_subregion=${subregion:4}
n_scenario=${scenario:11}
n_model=${model:8}
n_name=${name:3}
under="_"
module purge all
#module load python/anaconda3.6
#source activate /projects/b1139/anaconda3/envs/team-test-py37
#cd /projects/b1139/covidproject/covid-chicago

#python runScenarios.py $region $subregion $scenario $model $name

now="$(date +'%Y%m%d')"
fake="20210506"
listname=$fake$under$n_region$under$n_model$n_subregion$under$n_name$under$n_scenario
echo $listname
#wait for files to process
until [ -d /projects/b1139/covidproject/projects/covid_chicago/cms_sim/simulation_output/$listname ]
do
    sleep 5
done
echo "file found!"

#step 2
module load python/anaconda3.6
source activate /projects/b1139/anaconda3/envs/team-test-py37
cd /projects/b1139/covidproject/covid-chicago/iems_surveillance
python3 iems_step2_example.py -exp $listname -loc "NUCLUSTER"

#step 3



module load R/4.0.0
R --vanilla -f Step3.R --args $listname
echo "----Step 3----"


#step 4
module load python/anaconda3.6
source activate /projects/b1139/anaconda3/envs/team-test-py37
python3 stage4.py /projects/b1139/covidproject/projects/covid_chicago/cms_sim/simulation_output/$listname
echo "----Step 4----"

#Step 5
echo "----- Step 5 -----"
python3 step5_1.py 
