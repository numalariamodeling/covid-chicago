
### Emodl generators
The python files in this sub-directory allow to create .emodl files using python!
To avoid having to edit the experiment_config (yaml) files, different emodl files are generated per simulation scenario. 
Currently the emodl files are generated independently of the runScenarios and emodls exist for all scenarios regardless of being needed or not, leading to a high number of emodl files in the emod-sub-directory.
One future improvement will be to have 1 master file per model type and structural differences, and adding the additonal interventions from the runScenarios.py file (i.e. additional argument). 
Some interventions, such as contact tracing require a different compartmental structure as the current master file (i.e. additinal P_det compartment), this is also true for testDelay, currently only added in the base model.

Currently added interventions: 
- neverSIP
- continuedSIP 
- continuedSIP + interventionStop 
- continuedSIP + gradual_reopen
- continuedSIP + gradual_reopen + contact_tracing 
  (emodl needs additional compartments, and manually edited emodls are in emodl sub folder)

Optional compartment + parameter additions 
- none (base model)
- P_det, d_P (required for contact tracing)
- Sym_preD, Sys_preD, time_D, Ksys_D,Ksym_D  Kh1_D, Kh2_D, Kh3_D Kr_m_D (required for test delay)


#### emodl_generator_base.py
- Generates emodl files without any age groups 

#### emodl_generator_cobey_age.py
- Generates emodl files for different age groups, currently "4grp" and "8grp" with age specific transmission and disease parameter
- Eventually could be combined with  emodl_generator_cobey_contact_mix.py and having an option "age_specific=T"

#### emodl_generator_locale.py
- Generates emodl files without 'locales' per EMS , referred to as spatial model or 'EMS locale'

#### emodl_generator_age_locale.py (testing)
- Generates emodl files with age groups per EMS (testing, not up to date) 


### Structure
The emodl generators specify separate functions for each text structure of the emodl file (species, parameter, observe, functions, and reactions)

#### write_species
Defines the compartments of the transmission model 
Example: 

- Base model 
(species S 1000)
(species As 0)
(species E 0)

- Grouped model (i.e. age)
(species S_{grp} 1000)
(species As_{grp} 0)
(species E_{grp} 0)

- Spatial model (using locale syntax)
(species S::{grp} 1000)
(species As::{grp} 0)
(species E::{grp} 0)

- Spatial age-grouped model 
(species S_{age}::{region} 1000)
(species E_{age}::{region} 0)
(species As_{age}::{region} 0)


#### write_observe (required)
Defines the compartments, parameters and aggregated compartments that are written into output files
Example: 

- Base model 
(observe susceptible S)
(observe exposed E)
(observe asymptomatic asymptomatic)

- Grouped model (i.e. age)
(observe susceptible_{grp} S_{grp})
(observe exposed_{grp} E_{grp})
(observe asymptomatic_{grp} asymptomatic_{grp})

- Spatial model (using locale syntax)
(observe susceptible_{grp} S::{grp})
(observe exposed_{grp} E::{grp})
(observe asymptomatic_{grp} asymptomatic_{grp})

- Spatial age-grouped model 
(observe susceptible_{age}_{grpout} S_{age}::{region})
(observe exposed_{age}_{grpout} E_{age}::{region})
(observe asymptomatic_{age}_{grpout} asymptomatic_{age}_{region})


Note, 'asymptomatic' is a function and not a compartment see write_functions

### write_functions (optional/required for present simulation models)
Defines custom functions to here mainly to sum compartments.
Functions are not required for an emodl simulation to run, however in the simulation framework in this repository functions are used in the observed text chunk, hence required. 

Examples: 
- Base model (i.e. age)
(func asymptomatic  (+ As As_det1))
(func infectious_undet (+ As P Sym Sys H1 H2 H3 C2 C3))
(func infected (+ infectious_det infectious_undet H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))

- Grouped model (i.e. age)
(func asymptomatic_{grp}  (+ As_{grp} As_det1_{grp}))
(func infectious_undet_{grp} (+ As_{grp} P_{grp} Sym_{grp} Sys_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))

- Spatial model (using locale syntax)
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym::{grp} Sys::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))

- Spatial age-grouped model 
(func asymptomatic_{age}_{region}  (+ As_preD_{age}::{region} As_{age}::{region} As_det1_{age}::{region}))
(func infectious_undet_{age}_{region} (+ As_preD_{age}::{region} As_{age}::{region} P_{age}::{region} Sym_{age}::{region} Sym_preD_{age}::{region} Sys_{age}::{region} Sys_preD_{age}::{region} H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} C2_{age}::{region} C3_{age}::{region}))
(func infected_{age}_{region} (+ infectious_det_{age}_{region} infectious_undet_{age}_{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))


Note, 'infectious_undet' is a function included in another function  infected
The operator comes first, then the operands, in this case the compartments or functions. 

### write_params (required)
Defines the transition parameters to move from one to another compartment

Examples:
- Universal parameters 
(param time_to_infectious @time_to_infectious@)
(param fraction_symptomatic @fraction_symptomatic@)
(param Kl (/ (- 1 fraction_symptomatic ) time_to_infectious))

Note, parameters are replaced in python using the @ pattern as identifier, and parameters can be calculated using basic mathematical operators
As seen in the functions, the operator comes first, then the operands.

### write_reactions (required)
Defines the 'reaction equations' to move from one to the next compartment. 

Examples: 

- Base model
(reaction exposure   (S) (E) (* Ki S (/  (+ infectious_undet (* infectious_det_symp reduced_inf_of_det_cases) (* infectious_det_AsP reduced_inf_of_det_cases_ct)) N )))
(reaction presymptomatic (E)   (P)   (* Ks E (- 1 d_P)))
(reaction infection_asymp  (E)   (As_preD)   (* Kl E))

- Grouped model (i.e. age)
(reaction exposure_{grp}   (S_{grp}) (E_{grp}) (* Ki_{grp} S_{grp} (/  (+ infectious_undet_{grp} (* infectious_det_symp_{grp} reduced_inf_of_det_cases) (* infectious_det_AsP_{grp} reduced_inf_of_det_cases_ct)) N_{grp} )))
(reaction presymptomatic_{grp} (E_{grp})   (P_{grp})   (* Ks E_{grp} (- 1 d_P)))
(reaction infection_asymp_{grp}  (E_{grp})   (As_preD_{grp})   (* Kl E_{grp}))


- Spatial model (using locale syntax)
(reaction exposure_{grp}   (S::{grp}) (E::{grp}) (* Ki_{grp} S::{grp} (/  (+ infectious_undet_{grp} (* infectious_det_symp_{grp} reduced_inf_of_det_cases) (* infectious_det_AsP_{grp} reduced_inf_of_det_cases_ct)) N_{grp} )))
(reaction presymptomatic_{grp} (E::{grp})   (P::{grp})   (* Ks E::{grp} (- 1 d_P)))
(reaction infection_asymp_{grp}  (E::{grp})   (As_preD::{grp})   (* Kl E::{grp}))


### write_interventions  (optional)
Defines custom time events to change specific parameter that reflect interventions (i.e. increase in testing, reduced transmission rates)

Examples:

- Universal intervention and parameter
(param Ki_red1 (* Ki @social_multiplier_1@))
(time-event socialDistance_no_large_events_start @socialDistance_time1@ (Ki Ki_red1))


- Universal intervention and with group specific parameter
(param Ki_red1_{grp} (* Ki_{grp} @social_multiplier_1_{grp}@))
(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki_{grp} Ki_red1_{grp})))


Where '@socialDistance_time1@' defines the time in days after start of simulation (i.e. 10)
And '(Ki Ki_red1)' specifes the replacement of the Ki parameter with Ki_red1
Note; the parameter is overwritten and stays constant unless a stop time event is specified, resetting the overwritten parameter to the initial value.


### generate_emodl 
Function that combines the functions described above to write the text chunks and saving it into an emodl file.
The function is called at the end of the emodl generator, specifying different options for model type, extension and intervention.

Examples:
generate_emodl(grpList=ems_grp, expandModel=None,  add_interventions='continuedSIP', add_migration=False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_noTD.emodl'))

Arguments
- grpList: list of the group names 
- expandModel: whether to add test delay to pre-defined compartments (As, Sym, Sys)
	- None 
	- "testDelay_SymSys"
	- "testDelay_AsSym"	
	- "testDelay_AsSymSys"	
- add_interventions
	- None 
	- 'continuedSIP'
	- 'interventionStop' (not used, use interventionSTOP_adj instead)
	- 'interventionSTOP_adj'	
	- 'gradual_reopening'
	- 'contactTracing' ( needs to be manually defined whether to run in combination with immediate or gradual intervention stop)
- add_migration whether to allow for movement between groups or not, currently boolean only

Note migration is optional in the spatial model, whereas contact matrix in the age model is integrated per default.

