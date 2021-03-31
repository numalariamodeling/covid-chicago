
## Emodl generators
The python files in this sub-directory create the model structure in the format of `emodl` files.
When running the `runScenarios.py` a new `emodl` file is generated, if no `emodl` file is specified via the `--emodl flag`.
Using the  `--emodl flag` allows to run custom model structures for which no emodl generator exists.

#### emodl_generator_locale.py (main model in active use)
- Generates emodl using the `locales` syntax in `CMS`, referred to as spatial or locale model. 
- The locale model is customized for the eleven COVID-19 regions in Illinois and combines separate compartments for each region.
- via `python runScenarios.py -r IL`  all 11 regions are run 
- via `python runScenarios.py -r IL -sr EMS_1 EMS_2 ` selected sub-regions or single regions can be run
- additional parameters are specified (required) in a separate yaml file using the format as in [spatial_EMS_experiment.yaml](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/spatial_EMS_experiment.yaml)


#### emodl_generator_base.py (not maintained)
- Generates emodl files without any groups 
- previously used to run single regions, however as of March 31st, single regions are run using the locale model
- additional parameters can (optional depending on emodl) be specified in a separate yaml file using the format as in [EMSspecific_sample_parameters.yaml](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/EMSspecific_sample_parameters.yaml)

#### emodl_generator_age.py  (not maintained)
- Generates emodl files for different age groups, "8grp" with age specific transmission and disease parameter

#### emodl_generator_age_locale.py (testing)
- Generates emodl files with age groups per EMS (testing, not up to date) 


## Structure
The emodl generators specify separate functions for each text structure of the emodl file (species, parameter, observe, functions, and reactions)

#### write_species
Defines the compartments of the transmission model 
Example: 

-[ Base model](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_base.py#L13)
```
(species S 1000)
(species As 0)
(species E 0)
```

- [Grouped model (i.e. age)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_age.py#L15)
```
(species S_{grp} 1000)
(species As_{grp} 0)
(species E_{grp} 0)
```

- [Spatial model (using locale syntax)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_locale.py#L13)
```
(species S::{grp} 1000)
(species As::{grp} 0)
(species E::{grp} 0)
```

- Spatial age-grouped model 
```
(species S_{age}::{region} 1000)
(species E_{age}::{region} 0)
(species As_{age}::{region} 0)
```

#### write_observe (required)

A complete list of the available channels to observe is included in the main readme file.

##### Selection of channels to observe
With

 `observeLevel='primary'`

in the emodl generator function is it possible to select between three priority levels to observe.
Primary are the essential outcomes required for the weekly deliverables and standard plots.
Secondary are related additional channels.
Tertiary are channels rarely used or those that can be easily calculated during postprocessing.

##### Structure per model type
Defines the compartments, parameters and aggregated compartments that are written into output files
Example: 

- [Base model](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_base.py#L76)
```
(observe susceptible S)
(observe exposed E)
(observe asymptomatic asymptomatic)
```

- [Grouped model (i.e. age)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_age.py#L77)
```
(observe susceptible_{grp} S_{grp})
(observe exposed_{grp} E_{grp})
(observe asymptomatic_{grp} asymptomatic_{grp})
```

- [Spatial model (using locale syntax)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_locale.py#L80)
```
(observe susceptible_{grp} S::{grp})
(observe exposed_{grp} E::{grp})
(observe asymptomatic_{grp} asymptomatic_{grp})
```

- Spatial age-grouped model 
```
(observe susceptible_{age}_{grpout} S_{age}::{region})
(observe exposed_{age}_{grpout} E_{age}::{region})
(observe asymptomatic_{age}_{grpout} asymptomatic_{age}_{region})
```
Note, 'asymptomatic' is a function and not a compartment see write_functions

### write_functions (optional/required for present simulation models)
Defines custom functions to here mainly to sum compartments.
Functions are not required for an emodl simulation to run, however in the simulation framework in this repository functions are used in the observed text chunk, hence required. 

Examples: 
- [Base model](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_base.py#L117)
```
(func asymptomatic  (+ As As_det1))
(func infectious_undet (+ As P Sym Sys H1 H2 H3 C2 C3))
(func infected (+ infectious_det infectious_undet H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))
```

- [Grouped model (i.e. age)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_age.py#L118)
```
(func asymptomatic_{grp}  (+ As_{grp} As_det1_{grp}))
(func infectious_undet_{grp} (+ As_{grp} P_{grp} Sym_{grp} Sys_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))
```

- [Spatial model (using locale syntax)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_locale.py#L146)
```
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym::{grp} Sys::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
```

- Spatial age-grouped model 
```
(func asymptomatic_{age}_{region}  (+ As_preD_{age}::{region} As_{age}::{region} As_det1_{age}::{region}))
(func infectious_undet_{age}_{region} (+ As_preD_{age}::{region} As_{age}::{region} P_{age}::{region} Sym_{age}::{region} Sym_preD_{age}::{region} Sys_{age}::{region} Sys_preD_{age}::{region} H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} C2_{age}::{region} C3_{age}::{region}))
(func infected_{age}_{region} (+ infectious_det_{age}_{region} infectious_undet_{age}_{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
```
Note, 'infectious_undet' is a function included in another function  infected
The operator comes first, then the operands, in this case the compartments or functions. 

### write_params (required)
Defines the transition parameters to move from one to another compartment

Examples:
- [Universal parameters](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_base.py#L184)
```
(param time_to_infectious @time_to_infectious@)
(param fraction_symptomatic @fraction_symptomatic@)
(param Kl (/ (- 1 fraction_symptomatic ) time_to_infectious))
```
- [Group (i.e. age) specific parameters](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_age.py#L308)

Note, parameters are replaced in python using the @ pattern as identifier, and parameters can be calculated using basic mathematical operators
As seen in the functions, the operator comes first, then the operands.

### write_reactions (required)
Defines the 'reaction equations' to move from one to the next compartment. 

Examples: 

- [Base model](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_base.py#L315)
```
(reaction exposure   (S) (E) (* Ki S (/  (+ infectious_undet (* infectious_det_symp reduced_inf_of_det_cases) (* infectious_det_AsP reduced_inf_of_det_cases_ct)) N )))
(reaction presymptomatic (E)   (P)   (* Ks E (- 1 d_P)))
(reaction infection_asymp  (E)   (As_preD)   (* Kl E))
```

- [Grouped model (i.e. age)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_age.py#L495)
```
(reaction exposure_{grp}   (S_{grp}) (E_{grp}) (* Ki_{grp} S_{grp} (/  (+ infectious_undet_{grp} (* infectious_det_symp_{grp} reduced_inf_of_det_cases) (* infectious_det_AsP_{grp} reduced_inf_of_det_cases_ct)) N_{grp} )))
(reaction presymptomatic_{grp} (E_{grp})   (P_{grp})   (* Ks E_{grp} (- 1 d_P)))
(reaction infection_asymp_{grp}  (E_{grp})   (As_preD_{grp})   (* Kl E_{grp}))
```

- [contact matrix between groups] (https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_age.py#L481)


- [Spatial model (using locale syntax)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_locale.py#L439)
```
(reaction exposure_{grp}   (S::{grp}) (E::{grp}) (* Ki_{grp} S::{grp} (/  (+ infectious_undet_{grp} (* infectious_det_symp_{grp} reduced_inf_of_det_cases) (* infectious_det_AsP_{grp} reduced_inf_of_det_cases_ct)) N_{grp} )))
(reaction presymptomatic_{grp} (E::{grp})   (P::{grp})   (* Ks E::{grp} (- 1 d_P)))
(reaction infection_asymp_{grp}  (E::{grp})   (As_preD::{grp})   (* Kl E::{grp}))
```
- [migration between areas] (https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_locale.py#L351)


### write_interventions  (optional)
Defines custom time events to change specific parameter that reflect interventions (i.e. increase in testing, reduced transmission rates)

Examples:

- Universal intervention and parameter
```
(param Ki_red1 (* Ki @social_multiplier_1@))
(time-event socialDistance_no_large_events_start @socialDistance_time1@ (Ki Ki_red1))
```

- Universal intervention and with group specific parameter
```
(param Ki_red1_{grp} (* Ki_{grp} @social_multiplier_1_{grp}@))
(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki_{grp} Ki_red1_{grp})))
```

Where `@socialDistance_time1@` defines the time in days after start of simulation (i.e. 10)
And `(Ki Ki_red1)` specifes the replacement of the Ki parameter with Ki_red1
Note; the parameter is overwritten and stays constant unless a stop time event is specified, resetting the overwritten parameter to the initial value.

### generate_emodl 
Function that combines the functions described above to write the text chunks and saving it into an emodl file.
The function is called at the end of the emodl generator, specifying different options for model type, extension and intervention.

Examples:
```
generate_emodl(grpList=ems_grp, expandModel=None,  add_interventions='continuedSIP', add_migration=False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_noTD.emodl'))
```

Arguments
- grpList: list of the group names 
- expandModel: whether to add test delay to pre-defined compartments (As, Sym, Sys)
	- None 
	- 'testDelay_SymSys'
	- 'testDelay_AsSym'	
	- 'testDelay_AsSymSys'	
- add_interventions
	- None 
	- 'continuedSIP'
	- 'interventionStop' (not used, use interventionSTOP_adj instead)
	- 'interventionSTOP_adj'	
	- 'gradual_reopening'
	- 'contactTracing' ( needs to be manually defined whether to run in combination with immediate or gradual intervention stop)
- change_testDelay
	- 'AsSym'
	- 'SymSys'
	- 'AsSymSys'
- [add_migration](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_locale.py#L339) whether to allow for movement between groups or not, currently boolean only

Note [migration](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_locale.py#L339) is optional in the spatial model, whereas contact matrix in the age model is integrated per default.


