## Description 
The yaml file contains all input parameter and simulation settings.

## Master 

### extendedcobey_200421.yaml (current master file) 
- extendedmodel_cobey.emodl 
- extendedmodel_cobey_interventionStop.emodl  
- extendedmodel_cobey_noSIP.emodl
- extendedmodel_cobey_changeDetection.emodl

### extendedcobey.yaml (outdated)

## Extensions 

### EMSspecific_sample_parameters.yaml
Adds EMS specific sample parameters, such as effect of social distancing multipler.

### age4grp_experiment.yaml and age8grp_experiment.yaml 
Adds age specific parameter and contact matrix.
Runs with these emodl files:
- extendedmodel_age4_homogeneous.emodl
- extendedmodel_age4.emodl
- extendedmodel_age4_param.emodl
- extendedmodel_age8.emodl
- extendedmodel_age8_param.emodl


### spatial_EMS_experiment.yaml
Adds parameters for all EMS regions at once. 
Runs with these emodl file:
- extendedmodel_locale_EMS.emodl

### sample_age4grp_experiment.yaml
includes description on how to specifiy age and region specific sample parameters 

### sample_experiment.yaml



