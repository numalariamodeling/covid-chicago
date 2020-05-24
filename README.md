# Modelling the COVID-19 pandemic in Chicago


## 1. Project organization
In general we keep code on GitHub, files on [Box](https://northwestern.app.box.com/folder/106928919503), and use [slack](https://slack.com/) to communicate with each other. 

### 1.1. Data and documents (Box) 
The Box has a one project folder  "covid-chicago" and two data folders "covid-chicago" and "covid_IDPH". 
Some folder locations to point out: 
- `covid_chicago\cms_sim` includes files related to the modelling input and output (note the project covid-chicago folder) 
- `covid_chicago\project_notes` includes a description of the simulation, a collection of shared slide decks and figures
- `covid_IDPH`  includes data files used for fitting the EMS areas and is almost daily updated
- `covid_chicago\civis` includes files related to deliverables and requests of the model 
- `covid_chicago\Plots + Graphs` from data analysis

### 1.2. Code (GitHub)
- All the code is included in this gitrepository.  
To contribute to the gitrepository, you need a git account and then fork the git repository to your personal git account. 
Then clone the repository using https://github.com/numalariamodeling/covid-chicago.git to your local machine or your home directory on quest. 
To upload code, push to the cloned repository, and create a pull request to include your changes to the main repository. 
This documentation includes a description of the files used in this gitrepository. 

### 1.3. Communication (Slack)
There are two main channels on slack: 
- `covid-chicago`: is used for the day to day updates on the workflow, technical details, managing modelling taks and sharing updates and issues.
-  `w7-epidemiological modelling`: is used for 'higher level' communication around modelling and the data requirements from collaborators. 

## 1.4. Software used
- Modified SEIR model using Institute for Disease Modeling (IDM's)
[Compartmental Modeling Software (CMS)](https://idmod.org/docs/cms/index.html)
- [input](https://idmod.org/docs/cms/input-files.html) configuration file (cfg)
- [input](https://idmod.org/docs/cms/input-files.html)  model file (emodl)
- [output](https://idmod.org/docs/cms/output.html?searchText=output): trajectories.csv (optionally define prefix or suffix)


## 1.5. Updates 

### Key updates in base model structure and parameters
- 20200523 added d_Sys_incr4 and d_Sys_incr5, parameter fitting, including test delay per default
- 20200521 added s_m_4, parameter fitting
- 20200515 parameter fitting (also 20200512, 20200501)
- 20200428 Model disease and transmission parameters (previously 20200421, 20200419)
- 20200428 added d_Sys_incr1-3  
- 20200421 adding scale-invariant Ki
- 20200407 add more detected observables
- 20200402 cobey model implementation (including presymptomatic)

### Compartmental model structure (emodl file)
The "simplemodel" includes only the basic S-E-I-R compartments. 
Go to the related [emodl file here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/simplemodel_testing.emodl)
Latest version of the model, including modifications in alignment with the Covid model developed by Sarah Cobeys Team at University of Chicago. 
Go to the related [emodl file here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_cobey.emodl)
Or for more details read the [published paper](https://link.springer.com/chapter/10.1007/978-3-030-31304-3_18)

### Resources 
For more information on Covid in Chicago visit the [Chicago Covid Coalition website](https://sites.google.com/view/nu-covid19-landing-page/home?authuser=0)
Or watch the IPHAM Webinar from the 7th May on [youtube](https://www.youtube.com/watch?v=DV1l7RDOCEc&feature=youtu.be)

## 3. Model 

### 3.1. Base model
A basic SEIR model was extended to include symptom status (asymptomatic, presymptomatic, mild and severe symptoms), hospitalization, critical illness, and deaths, while allowing to track detected and undetected cases separately.
![model](https://github.com/numalariamodeling/covid-chicago/blob/master/SEIR_base_model_structure_testDelay.png)


For the contact tracing scenario an additional compartment for detection of presymptomatic cases is added. The option for quarantine of susceptibles is currently disabled. 
![model](https://github.com/numalariamodeling/covid-chicago/blob/master/SEIR_base_model_structure_Pdet_TestDelay_withParameter.png)


#### Model parameters
The starting date and intervention effect size are fixed and the transmission parameter "Ki"are fitted to the data.
All other parameters are derived from literature, local hospital data as well as doublechecked with other models used in Illinois (i.e. model from [UChicago](https://github.com/cobeylab/covid_IL))
To account for uncertainity and heterogeneity in transmission and disease parameters, all the parameters are sampled from a distribution informed by literature. 

#### 'reaction paramaters'

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


#### Time parameters (in days)

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


#### Intervention scenarios and time-varying parameters
The [time-event](https://idmod.org/docs/cms/model-file.html?searchText=time-event) option in cms allows to change a paramter at a given time point (days) (which will stay constant afterwards if not resetted using a second time-event).
Time-event are used to define reduction in the transmission rate, reflecting a decrease in contact rates due to social distancing interventions (i.e. stay-at-home order). 
The time event can also be used to reflect increasing testing rates by increasing the detection of cases (i.e. dSym and dSys for increased testing at health facilities, or dAs and dSym for contact tracing)

###### Intervention scenarios
Current scenarios include:
- No stay-at-home (counterfactual)
- Continue stay-at-home
- Stop stay-at-home order - immediately
- Stop stay-at-home order - step-wise 


### 3.2. Age-structured model 
The "age_model" duplicates each compartment of the simple or the extended model for n age groups. To allow the age groups to get in contact with each other at different rates, the Ki (contact rate * probability of transmission) needs to be specified for a all age-combinations. 

### 3.2.1. Age groups
- Four age groups: "0to19", "20to39", "40to59", "60to100" 
[look at the 4grp emodl here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_age4.emodl)
-  Eight age groups: "0to9", "10to19", "20to29", "30to39", "40to49", "50to59", "60to69", "70to100" 
[look at the 8grp emodl here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_age8.emodl)
To generate or modify the emodl files use the [age specific emodl generator](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_cobey_contact_mix.py) 

### 3.2.2. Contact matrix
The contacts between age groups were previously extracted for running an [EMOD model](https://idmod.org/documentation) from [Prem et al 2017](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005697). [Script that extracts the contact matrix values](https://github.com/numalariamodeling/covid-chicago/blob/master/age_model/age_contact/age_matrix_reducer.py). 

## 3.3. Spatial model
The "spatial_model" uses a special syntax as described [here](https://idmod.org/docs/cms/create-spatial-model.html?searchText=spatial). 
To generate or modify the emodl files use the [locale specific emmodl generator](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/locale_emodl_generator_extendedModel.py )
- View the [EMS specific emodl](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_cobey_locale_EMS.emodl)

### 3.3.1. Movement between areas
[...]

## 3.4. Spatial age-structured model
A test verion is available under [emodl file](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_cobey_locale_age_test.emodl).
To generate or modify the emodl files use the [locale-age specific emmodl generator](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/extended_cobey_age_locale_emodl_generator.py )

## 4 Run simulations 
[runScenarios.py](runScenarios.py) is used to run multiple simulations
given a configuration file with the parameters. The script builds off
a default configuration file [extendedcobey.yaml](extendedcobey.yaml)
and substitutes parameters with the values/functions in the
user-provided configuration file using the `@param@` placeholder. As with
[extendedcobey_runScenarios.py](extendedcobey_runScenarios.py), it combines multiple trajectories.csv files produced into a trajectoriesDat.csv, that is used for postprocessing.


### 4.1 Configuration file:
The configuration file is in YAML format and is divided into 5
blocks: `experiment_setup_parameters`,
`fixed_parameters_region_specific`, `fixed_parameters_global`,
`sampled_parameters`, `fitted_parameters`. The sampled parameters need
the sampling function as well as the arguments to pass into that
function (`function_kwargs`). Currently, only a few
sampling/calculation functions are supported. More can be added by
allowing for more libraries in `generateParameterSamples` of [runScenarios.py](runScenarios.py).

Note that the user-supplied configuration file is used to provide
*additional* or *updated* parameters from the base configutation file.

### 4.2 Inputs:
- Running location: Where the simulation is being run (either `Local`
  or `NUCLUSTER`)
- Region: The region of interest. (e.g. `EMS_1`)
- Configuration file: The configuration file with the parameters to
  use for the simulation. If a parameter is not provided, the value in
  the default configuration will be used. (e.g. [sample_experiment.yaml](sample_experiment.yaml))
- Emodl template (optional): The template emodl file to substitute in
  parameter values. The default is [extendedmodel_cobey.emodl](extendedmodel_cobey.emodl). emodl
  files are in the `./emodl` directory.
- Suffix for experiment name added as name_suffix (optional): The template emodl file to substitute in
  parameter values. The default is test_randomnumber (e.g. `20200417_EMS_10_test_rn29`)
  
### 4.3 Usage examples:
- Using the default emodl template: `python runScenarios.py
  --running_location Local --region IL  --experiment_config sample_experiment.yaml`
- Using a different emodl template: `python runScenarios.py
  --running_location Local  --region IL  --experiment_config sample_experiment.yaml --emodl_template simplemodel_testing.emodl`
- Specifying experiment name suffix and changing running_location : `python runScenarios.py
  --running_location NUCLUSTER --region IL --experiment_config extendedcobey.yaml --emodl_template simplemodel_testing.emodl --name_suffix "testrun_userinitials"`
- Specifiying cms configuration file and solver:`python runScenarios.py
  --running_location Local --region IL  --experiment_config sample_experiment.yaml --emodl_template simplemodel_testing.emodl --cfg_template model_Tau.cfg`

#### Specifiy solver 
If not specified the [Tau leaping](https://idmod.org/docs/cms/tau-leaping.html) will be used as default. 
CMS configuration files are in the [cfg](https://github.com/numalariamodeling/covid-chicago/tree/master/cfg) folder. 

### 4.4 Define age or region specific inputs 
View [EMSscenario_submission_template.txt](https://github.com/numalariamodeling/covid-chicago/blob/master/EMSscenario_submission_template.txt) for current custom scenarios that are being used. 

#### Region specific sample parameters (i.e. using estimates parameters per EMS regions)
-  `EMSspecific_sample_parameters.yaml`  (needs to be updated with fitted parameter estimates)

####  Age extension and age specific parameters 
- `sample_age4grp_experiment.yaml` and  `sample_age8grp_experiment.yaml`


### 4.5. Local environment setup
Use a `.env` file in the same directory as your `runScenarios` script to define paths to directories and files on your own computer.
Copy the `sample.env` file to `.env` and edit so that paths point as needed for your system.

### 4.6. Running on OS X or Linux
The CMS software is provided as a compiled Windows executable, but can be run on Unix-like systems via [`wine`](https://www.winehq.org/).
If you do not have `wine` installed on your system, you can use the provided [Dockerfile](Dockerfile), which has `wine` baked in.
To build the Docker image, run `docker build -t cms`. Set `DOCKER_IMAGE=cms` in your environment or your `.env` file to use it.

### 4.7 Running on Quest (NUCLUSTER) 
A cloned version of the git repository can be found under `/projects/p30781/covidproject/covid-chicago/`.

#### Requirements on quest 
All the modules need to be installed on the personal quest environment 
- use pip install ... in your terminal 
- install `dotenv` and `yamlordereddictloader`
`conda create --name dotenv-py37 -c conda-forge python-yamlordereddictloader python=3.7 --yes`
`source activate dotenv-py37`
`conda install -c conda-forge yamlordereddictloader`

The `source activate dotenv-py37` needs to be run before runnung the `runScenarios.py`

#### Submit job 
`cd /projects/p30781/covidproject/covid-chicago/`
`python runScenarios.py --running_location NUCLUSTER --region EMS_11 --experiment_config extendedcobey_200428.yaml --emodl_template extendedmodel_cobey.emodl --name_suffix "quest_run_<your initial>"`

The experiments will go to the _temp folder on the quest gitrepository. To avoid confusion on owner of the simulations it is recommended to include the initials in the experiment name using the name_suffix argument

Next step copy the content of the submit_runSimulations.sh (should be a simple txt file) to the terminal to run:
- `cd /projects/p30781/covidproject/covid-chicago/_temp/<exp_name>/trajectories/`
- `dos2unix runSimulations.sh`  # converts windows format to linux format
- `sbatch runSimulations.sh`  # submits the simulations as an array job , note maximum array <5000 scenarios. 

### 5 Visualizing and analyzing results
- see [plotters folder](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/)

