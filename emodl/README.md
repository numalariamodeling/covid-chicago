### Description 
The emodl file contains all information that defines the mathematical model itself. 
For example, it defines the species, the transition rates, incubation time, daily recovery rate, and many other parameters specific to the disease being modeled. 
The model file is in EMODL format; the syntax and available parameters are described in [Model file syntax](https://idmod.org/docs/cms/model-file.html).

There are 4 types of models: 1) base, 2) age, 3) spatial, and 4) spatial-age. 
The base emodl file is edited per hand, whereas for the other types so called "emodl-generator" scripts are availabble. 
Note the term 'cobey' was removed from age and spatial file names to shorten the filename. 

The simple SEIR model was extended with additional compartments i.e. Hospitalized, detected and undetected cases, 
the model was further improved inspired from the compartmental model used at the University of Chicago and Sarah Cobeys group, hence the "cobey" term in the filename. 

## Master file

### extendedmodel_cobey.emodl 
- master emodl file (base)

Note: the master file includes per default social distancing time events:
(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki Ki_red1)))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki Ki_red2)))
(time-event socialDistance_start @socialDistance_time3@ ((Ki Ki_red3)))

#### extendedmodel_cobey_interventionStop.emodl  
- base with intervention stop 
Same file as the master file including intervention stop
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki Ki_back)))

### extendedmodel_cobey_noSIP.emodl
base without intervention 

### extendedmodel_cobey_changeDetection.emodl
base with additional change in detection rates 

## Age grp 4 
- corresponding yaml for all age8 grp emodls: age4grp_experiment.yaml

### extendedmodel_age4_homogeneous.emodl
- assuming well mixed population 

### extendedmodel_age4.emodl
- includes contact matrix for 'all locations'
- assuming same disease and transmission parameter for all age groups

### extendedmodel_age4_param.emodl
- includes contact matrix for 'all locations'
- includes age specific parameter 


## Age grp 8 
- corresponding yaml for all age8 grp emodls: age8grp_experiment.yaml

### extendedmodel_age8.emodl
- includes contact matrix for 'all locations'
- assuming same disease and transmission parameter for all age groups

### extendedmodel_age8_param.emodl
- includes contact matrix for 'all locations'
- includes age specific parameter 

## Spatial 

###  extendedmodel_locale_EMS.emodl
- model for all EMS regions
- corresponding yaml: spatial_EMS_experiment.yaml 

## Test 

### Not used / not updated
- simplemodel_testing.emodl
- extendedmodel_cobey_changeDetection.emodl
- extendedmodel_cobey_cfr.emodl
- extendedmodel_cobey_locale_EMS_2grptest1.emodl  (testing in process)

### Test emodls
- locale_covid.emodl
- locale_covid_test.EMODL
- example_locale.emodl
- GE_county_model1.emodl
- GE_generated_test2.emodl
- county_model_covid.emodl

