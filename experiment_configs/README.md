#  experiment_config
The yaml file contains all input parameter and simulation settings.

# 1. Config files and related scenario files

## [experiment_setup_parameters](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml#L1)
Takes single integer values. 

- number_of_samples: specifies the number of random samples drawn for 'sampled_parameters'
- number_of_runs: specifies the number of stochastic replications using cms software
- duration: Duration of simulation in days.
- monitoring_samples: Duration of monitoring time, i.e. when running burnin that does not need to be observed. 
- random_seed: Random seed for the parameter samples drawn in runScenarios.py
- initialAs: Number of initial (imported) infections, assumed to be asymptomatic per default.  

Of these values number_of_runs, duration, and monitoring_samples are replaced in the CMS configuration (cfg) file. 
The number_of_samples and random_seed are used in the runScenarios.py when generating the sampling parameters to be replaced in the emodl files.
The initialAs is added to the sample dataset and replaced in the emodl file. 

## [fixed_parameters_region_specific](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml#L8)
- populations: population size 
- startdate: startdate of the simulation, defins the date at which the first infections occur. 

## [fixed_parameters_global](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml#L42)

### [sampled_parameters](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml#L43)
- time_to_infectious
- time_to_symptoms
- time_to_hospitalization
- ...

These parameters take a random uniform distribution, but other np.random distributions could be defined as well.
The number of samples drawn is specified in the experiment_setup_parameters, and full factorial among sample parameters is disabled.
In order to repeat one of the sample parameters for all other variables, the parameter needs to be moved to the intervention_parameters.

    np.random: uniform
    function_kwargs: {'low': 3.4, 'high':4.5}
	
### [intervention_parameters](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml#L101)
Intervention parameters or also scenario parameter  are repeated for each sample, fitting parameter and startdate.
Most of the intervention parameter include time varying parameters to simulate an intervention put in place or being lifted at any time point. 
Since time in the cms model depends on the start date, the effect size parameter and time event parameter have been separated (see time_parameter below).
Below are some examples: 

Adding social distancing interventions
- social_multiplier_1
- social_multiplier_2
- social_multiplier_n

Increasing detection rates over time
- detection_time_1
- detection_time_2
- detection_time_n

Include testing of asymptomatic infections 
- d_As_ct1

- ...


The parameters here can take a random distribution as for the sample_parameters, or a for example an linspace format. 
  
     backtonormal_multiplier:
        np.random: uniform
        function_kwargs: {'low':0.10, 'high':0.30, 'size':2}

      reduced_inf_of_det_cases':
        np: linspace
        function_kwargs: {'start':0, 'stop':1, 'num':6}
	
### [time_parameters](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml#L164)
The time parameters are linked with the intervention parameters and specify the time of change, writtens time events in the emodl file. 

    detection_time_1:
      custom_function: DateToTimestep
      function_kwargs: {'dates': 2020-03-14}

It is also possible to define multiple dates

    detection_time_1:
      custom_function: DateToTimestep
      function_kwargs: {'dates': [2020-03-12, 2020-03-13]}

In contrast to the startdate, the dates here are taken ony by one and not as a range including all days inbetween. 	
	
## [fitted_parameters](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml#L227)

- Ki (transmission parameter)

In base model (running for specified EMS alone)

    'EMS_1':
      np: linspace
      function_kwargs: {'start': 0.589, 'stop': 0.589, 'num': 1}
     ...
	  
In spatial model (running for all EMS in one simulation using separate compartments)

    sampled_parameters:
      Ki:  
        IL:
          expand_by_age: True
          np.random: uniform
          function_kwargs:
            - {'low': 0.589, 'high': 0.589}
            - {'low': 0.654, 'high': 0.654}
            - {'low': 0.373, 'high': 0.373}
            - {'low': 0.571, 'high': 0.571}
            - {'low': 0.501, 'high': 0.501}
            - {'low': 0.501, 'high': 0.501}
            - {'low': 0.714, 'high': 0.714}
            - {'low': 0.897, 'high': 0.897}
            - {'low': 0.857, 'high': 0.857}
            - {'low': 0.754, 'high': 0.754}
            - {'low': 1.01, 'high': 1.01} 


### [expand_by_age](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/age8grp_experiment.yaml#L13)
The expand_by_age option means repeating compartments and parameters per sub-groups, either age or EMS, or any other group that seems relevant (i.e. residents and staff within a long-term health care facility).

# 2. Config files and related scenario files
- extendedcobey_200428.yaml (current master file) 

## 1.2. Model extensions (in addition to master yaml file)
- [sample_age4grp_experiment.yaml](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/sample_age4grp_experiment.yaml)
includes description on how to specifiy age and region specific sample parameters 
- [age_locale_experiment.yaml](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/age_locale_experiment.yaml) 

## 1.3 Long-term-care-facility (LTCF) simulations  
- [ltcf_experiment.yaml](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/ltcf_experiment.yaml)
- [extendedmodel_ltcf_homogeneous.emodl](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_ltcf_homogeneous.emodl)
- [ltcf_experiment_age.yaml](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/ltcf_experiment_age.yaml)
- [extendedmodel_ltcf_age.emodl](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_ltcf_age.emodl)
- [extendedmodel_ltcf_age_testDelay.emodl](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_ltcf_age_testDelay.emodl)


