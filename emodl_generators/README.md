
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