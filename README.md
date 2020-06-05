# Modelling the COVID-19 pandemic in Chicago



# 1. General 

### 1.1 Compartmental model structure (emodl file)
A basic SEIR model was extended to include symptom status (asymptomatic, presymptomatic, mild and severe symptoms), hospitalization, critical illness, and deaths, while allowing to track detected and undetected cases separately.
![model](https://github.com/numalariamodeling/covid-chicago/blob/master/SEIR_base_model_structure_testDelay.png)


## 1.2. Software used
The [Compartmental Modeling Software (CMS)](https://idmod.org/docs/cms/index.html) is used to simulate the COVID-19 transmission and disease progression. The CMS language defines 5 main type: species, observations, reactions, parameters and functions, in addition time-events can be added as well as state-events. Multiple compartments, called ‘species’ can be defined. The movement of populations between compartments is called reaction. The model runs with different solvers, including spatial solvers. The model is written in ['emodl' files](https://idmod.org/docs/cms/input-files.html) and model configurations are written in ['cfg' files](https://idmod.org/docs/cms/input-files.html). The output is written into [trajectories.csv files](https://idmod.org/docs/cms/output.html?searchText=output).

## 1.2. Updates 

### Main updates in model structure and fitted parameters
- 20200602 updated parameter fit 
- 20200523 added d_Sys_incr4 and d_Sys_incr5, parameter fitting, including test delay per default
- 20200521 added s_m_4, parameter fitting
- 20200515 parameter fitting (also 20200512, 20200501)
- 20200428 Model disease and transmission parameters (previously 20200421, 20200419)
- 20200428 added d_Sys_incr1-3  
- 20200421 adding scale-invariant Ki
- 20200407 add more detected observables
- 20200402 [cobey](https://github.com/cobeylab/covid_IL) model implementation (including presymptomatic)
- 20200402 [cobey](https://github.com/cobeylab/covid_IL) model implementation (including presymptomatic)


### Resources 
- CMS software publication [published paper](https://link.springer.com/chapter/10.1007/978-3-030-31304-3_18)
- [Chicago Covid Coalition website](https://sites.google.com/view/nu-covid19-landing-page/home?authuser=0)
- [Modeling COVID 19 Transmission and Containment in Illinois (IPHAM Webinar)](https://www.youtube.com/watch?v=DV1l7RDOCEc&feature=youtu.be) by Dr Jaline Gerardin.
- [Modeling COVID-19 Transmission and Containment Efforts at Northwestern](https://news.feinberg.northwestern.edu/2020/05/modeling-covid-19-transmission-and-containment-efforts/)

# 2. Model 
The latest model description in emodl format is written in the [extendedmodel_cobey.emodl](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_cobey.emodl) file. Since early April,, the model includes modifications added in alignment with the COVID model from [a modelling team at the University of Chicago](https://github.com/cobeylab/covid_IL). 

## 2.1. Model parameters
Most of the parameters are derived from literature, local hospital data as well as doublechecked with other models used in Illinois (i.e. model from [UChicago](https://github.com/cobeylab/covid_IL)).
The starting date, intervention effect size, and the transmission parameter "Ki"are fitted to the data.

### 2.1.1 'reaction paramaters'
All the parameters are sampled from a uniform distribution as specified in the [experiment config (yaml) file ](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml#L43)

| parameter | name                                                                         | 
|-----------|------------------------------------------------------------------------------|
| Ki        | Transmission rate (contact rate * infection  probability)                    | 
| Ks        | Progression to presymtomatic ( fraction_symptomatic /  time_to_infectious))       |  
| Kl        | Progression to asymptomatic ((1 - fraction_symptomatic ) /   time_to_infectious)) | 
| dAs       | detection rate of asymptomatic infections                                    |   
| dSym      | detection rate of mild symptomatic infections                                |  
| dSys      | Detection rate of severe symptomatic infections                              | 
| Ksym      | Progression to mild symptoms                                                 |  
| Ksys      | Progression to severe status ( fraction_severe * (1 / time_to_symptoms))     | 
| Kh        | Hospitalization rate                                                         |  
| Kh_D      | Hospitalization rate minus delay in detection                                | 
| Kr_a      | Recovery rate of asymptomatic infections                                     |  
| Kr_m      | Recovery rate mild symptomatic infections                                    |  
| Kr_m_D    | Recovery rate mild symptomatic infections  minus delay in detection          |  
| Kr_h      | Recovery rate of hospitalized cases                                          |  
| Kr_c      | Recovery rate of critical cases                                              |  
| Kc        | Progression to critical                                                      |  
| Km        | Deaths                                                                       |   


### 2.1.2  Time parameters (in days)

| parameter | name                                                                         | 
|---------------------------|--------------------------------------------------------------|
| time_to_infectious    	| Time from being exposed to become infectious                 |   
| time_to_symptomatic    	| Time from becoming infectious to onset of symptoms           |  
| time_D    				| Time from onset of symptoms to be detected (if detected)     |   
| time_to_hospitalization   | Time from possible detection to hospitalization              |  
| recovery_time_asymp       | Time until an asymptomatic infection is cleared              | 
| recovery_time_mild        | Time until mildly symptomatic case recovers                  | 
| recovery_time_hosp        | Time until hospitalized cases (severe symptomatic) recover   | 
| recovery_time_crit        | Time until critical cases (severe symptomatic) recover       | 
| time_to_critical        	| Time between hospitalization and critical illness            | 
| time_to_death        		| Time between critical illness and deaths                     | 

Note: Updated list on [Box](https://northwestern.app.box.com/file/656414061983)!

### 2.1.3  time-varying parameters (intervention scenarios)
The [time-event](https://idmod.org/docs/cms/model-file.html?searchText=time-event) option in cms allows to change a paramter at a given time point (days) (which will stay constant afterwards if not resetted using a second time-event).
Time-event are used to define reduction in the transmission rate, reflecting a decrease in contact rates due to social distancing interventions (i.e. stay-at-home order). 
The time event can also be used to reflect increasing testing rates by increasing the detection of cases (i.e. dSym and dSys for increased testing at health facilities, or dAs and dSym for contact tracing)

Current scenarios include:
- No stay-at-home (counterfactual)
- Continue stay-at-home
- Stop stay-at-home order - immediately
- Stop stay-at-home order - step-wise 
(- Contact tracing and increase in case detection (includes additional compartment for detection of presymptomatic cases))

For details, see the [cms implementation in one of the emodl generators](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_base.py#L514)

## 2.2. Age-structured model 
The "age_model" duplicates each compartment of the simple or the extended model for n age groups. To allow the age groups to get in contact with each other at different rates, the Ki (contact rate * probability of transmission) needs to be specified for a all age-combinations. 

![model](https://github.com/numalariamodeling/covid-chicago/blob/master/age_model_8grp.png)


### 2.2.1. Age groups
- Four age groups: "0to19", "20to39", "40to59", "60to100" 
[(4grp emodl)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_age4.emodl)
-  Eight age groups: "0to9", "10to19", "20to29", "30to39", "40to49", "50to59", "60to69", "70to100" 
[(8grp emodl)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_age8.emodl)
To generate or modify the emodl files use the [age specific emodl generator](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_cobey_contact_mix.py) 

### 2.2.2. Contact matrix
The contacts between age groups were previously extracted for running an [EMOD model](https://idmod.org/documentation) from [Prem et al 2017](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005697). [Script that extracts the contact matrix values](https://github.com/numalariamodeling/covid-chicago/blob/master/age_model/age_contact/age_matrix_reducer.py). 

## 2.3. Spatial model
The "spatial_model" uses a special syntax as described [here](https://idmod.org/docs/cms/create-spatial-model.html?searchText=spatial). 
To generate or modify the emodl files use the [locale specific emmodl generator](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/locale_emodl_generator_extendedModel.py )
- View the [EMS specific emodl](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_cobey_locale_EMS.emodl)

### 3.3.1. Movement between areas
[...]

## 2.4. Spatial age-structured model
A test verion is available under [emodl file](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_cobey_locale_age_test.emodl).
To generate or modify the emodl files use the [locale-age specific emmodl generator](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/extended_cobey_age_locale_emodl_generator.py )

# 3 Run simulations 
The [runScenarios.py](runScenarios.py) is used to run multiple simulations
given a configuration file with the parameters. The script builds off
a default configuration file [extendedcobey.yaml](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml)
and substitutes parameters with the values/functions in the
user-provided configuration file using the `@param@` placeholder. Multiple trajectories.csv that are produced per single simulation are combined into a trajectoriesDat.csv, used for postprocessing and plotting.


## 3.1 [Configuration file](https://github.com/numalariamodeling/covid-chicago/tree/master/experiment_configs):
The configuration file is in [YAML](https://yaml.org/) format and is divided into 5
blocks: `experiment_setup_parameters`,
`fixed_parameters_region_specific`, `fixed_parameters_global`,
`sampled_parameters`, `fitted_parameters`. The sampled parameters need
the sampling function as well as the arguments to pass into that
function (`function_kwargs`). Currently, only a few
sampling/calculation functions are supported. More can be added by
allowing for more libraries in `generateParameterSamples` of [runScenarios.py](runScenarios.py).

Note that the user-supplied configuration file is used to provide
*additional* or *updated* parameters from the base configutation file.

## 3.2 Inputs:
- Running location: Where the simulation is being run (either `Local`
  or `NUCLUSTER`)
- Region: The region of interest. (e.g. `EMS_1`, or `IL` for all EMS 1-11 inclued in the same model)
- Configuration file: The configuration file with the parameters to
  use for the simulation. If a parameter is not provided, the value in
  the default configuration will be used. (e.g. [sample_experiment.yaml](sample_experiment.yaml))
- Emodl template (optional): The template emodl file to substitute in
  parameter values. The default is [extendedmodel_cobey.emodl](extendedmodel_cobey.emodl). emodl
  files are in the `./emodl` directory.
- cfg template (optional): The default cfg file uses the [Tau leaping](https://idmod.org/docs/cms/tau-leaping.html) solver (recommended B solver).
- Suffix for experiment name added as name_suffix (optional): The template emodl file to substitute in
  parameter values. The default is test_randomnumber (e.g. `20200417_EMS_10_test_rn29`)
  
## 3.3 Usage examples:
- Using the default emodl template: `python runScenarios.py
  --running_location Local --region IL  --experiment_config sample_experiment.yaml`
- Using a different emodl template: `python runScenarios.py
  --running_location Local  --region IL  --experiment_config sample_experiment.yaml --emodl_template simplemodel_testing.emodl`
- Specifying experiment name suffix and changing running_location : `python runScenarios.py
  --running_location NUCLUSTER --region IL --experiment_config extendedcobey.yaml --emodl_template simplemodel_testing.emodl --name_suffix "testrun_userinitials"`
- Specifiying cms configuration file and solver:`python runScenarios.py
  --running_location Local --region IL  --experiment_config sample_experiment.yaml --emodl_template simplemodel_testing.emodl --cfg_template model_Tau.cfg`


## 3.4 Define age or region specific inputs 
The [EMSscenario_submission_template.txt](https://github.com/numalariamodeling/covid-chicago/blob/master/EMSscenario_submission_template.txt) shows example command lines and scenarios that are currently being used. 

### Region specific sample parameters (i.e. using estimates parameters per EMS regions)
- [`EMSspecific_sample_parameters.yaml`](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/EMSspecific_sample_parameters.yaml)

###  Age extension and age specific parameters 
- `sample_age4grp_experiment.yaml `(https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/sample_age4grp_experiment.yaml) 
Note: this extension works for any sub-group as it duplicates the parameter names for the defined group names, which need to be defined in the same way in the corresponding emodl file.

## 3.5. Local environment setup
Use a `.env` file in the same directory as your `runScenarios` script to define paths to directories and files on your own computer.
Copy the `sample.env` file to `.env` and edit so that paths point as needed for your system.

## 3.6. Running on OS X or Linux
The CMS software is provided as a compiled Windows executable, but can be run on Unix-like systems via [`wine`](https://www.winehq.org/).
If you do not have `wine` installed on your system, you can use the provided [Dockerfile](Dockerfile), which has `wine` baked in.
To build the Docker image, run `docker build -t cms`. Set `DOCKER_IMAGE=cms` in your environment or your `.env` file to use it.

## 3.7 Running on Quest (NUCLUSTER) 
A cloned version of the git repository can be found under `/projects/p30781/covidproject/covid-chicago/`.

### Requirements on quest 
All the modules need to be installed on the personal quest environment 
- use pip install ... in your terminal 
- install `dotenv` and `yamlordereddictloader`
`conda create --name dotenv-py37 -c conda-forge python-yamlordereddictloader python=3.7 --yes`
`source activate dotenv-py37`
`conda install -c conda-forge yamlordereddictloader`

The `source activate dotenv-py37` needs to be run before runnung the `runScenarios.py`

### Submit job 
`cd /projects/p30781/covidproject/covid-chicago/`
`python runScenarios.py --running_location NUCLUSTER --region EMS_11 --experiment_config extendedcobey_200428.yaml --emodl_template extendedmodel_cobey.emodl --name_suffix "quest_run_<your initial>"`

The experiments will go to the _temp folder on the quest gitrepository. To avoid confusion on owner of the simulations it is recommended to include the initials in the experiment name using the name_suffix argument

Next step copy the content of the submit_runSimulations.sh (should be a simple txt file) to the terminal to run:
- `cd /projects/p30781/covidproject/covid-chicago/_temp/<exp_name>/trajectories/`
- `dos2unix runSimulations.sh`  # converts windows format to linux format
- `sbatch runSimulations.sh`  # submits the simulations as an array job , note maximum array <5000 scenarios. 

# 4 Visualizing and analyzing results
- see [plotters folder](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/)

