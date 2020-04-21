# Modelling the COVID-19 pandemic in Chicago

For more information on Covid in Chicago visit the (Chicago Covid Coalition website)[https://sites.google.com/view/nu-covid19-landing-page/home?authuser=0]

## 1. Software used
- Modified SEIR model using Institute for Disease Modeling (IDM's) [Compartmental Modeling Software (CMS)](https://idmod.org/docs/cms/index.html)

- [input](https://idmod.org/docs/cms/input-files.html) configuration file (cfg)
- [input](https://idmod.org/docs/cms/input-files.html)  model file (emodl)
- [output](https://idmod.org/docs/cms/output.html?searchText=output): trajectories.csv (optionally define prefix or suffix)

## 2. Compartmental model structure
### 2.1. Simple model
The "simplemodel" includes only the basic S-E-I-R compartments. 
Go to the related [emodl file here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/simplemodel_testing.emodl)

### 2.2. Extended model
The "extendedmodel" imclides additional compartments for asymptomatics, symptomatics, hospitalization, progression to critical and deaths. In addition the detections are tracked as a sum of detected asymptomatics, symptomatics,hospitalized, critical and deaths with group specific detection rates. 
Go to the related [emodl file here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_covid.emodl)

### 2.3. "Extended_cobey" model
Latest version of the model, including modifications in alignment with the Covid model developed by Sarah Cobeys Team at University of Chicago. 
Go to the related [emodl file here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_cobey.emodl)

## 3. Model types
## 3.1. Base model
Assumes one well mixed homogeneous population 

## 3.2. Age-structured model 
The "age_model" duplicates each compartment of the simple or the extended model for n age groups. To allow the age groups to get in contact with each other at different rates, the Ki (contact rate * probability of transmission) needs to be specified for a all age-combinations. 

### 3.2.1. Age groups
- Four age grouos: "0to19", "20to39", "40to59", "60to100" 
  
[run 4grp model here](https://github.com/numalariamodeling/covid-chicago/blob/master/age_model/extendedcobey_age_4grp_runScenarios.py)
or look at the  [emodl file](https://github.com/numalariamodeling/covid-chicago/blob/master/age_model/emodl/extendedmodel_cobey_age_4grp.emodl)
-  Eight age groups: "0to9", "10to19", "20to29", "30to39", "40to49", "50to59", "60to69", "70to100"
  
[run 8grp model here](https://github.com/numalariamodeling/covid-chicago/blob/master/age_model/extendedcobey_age_8grp_runScenarios.py)
or look at the [emodl file](https://github.com/numalariamodeling/covid-chicago/blob/master/age_model/emodl/extendedmodel_cobey_age_8grp.emodl)

### 3.2.2. Contact matrix
The contacts between age groups were previously extracted for running an [EMOD model](https://idmod.org/documentation) from [Prem et al 2017](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005697). [Script that extracts the contact matrix values](https://github.com/numalariamodeling/covid-chicago/blob/master/age_model/age_contact/age_matrix_reducer.py). 

## 3.3. Spatial model
The "spatial_model" uses a special syntax as described [here](https://idmod.org/docs/cms/create-spatial-model.html?searchText=spatial). 

## 3.4. Spatial age-structured model
A test verion is available under [spatial_age_model](https://github.com/numalariamodeling/covid-chicago/blob/master/spatial_age_model)
and the [emodl file](https://github.com/numalariamodeling/covid-chicago/blob/master/spatial_age_model/emodl/extendedmodel_cobey_locale_EMS_2grptest1.emodl).

## 4. Running simulations and analyzing predictions

### 4.1. Run single simulations
To run a single simulation: 
- Via termianl /bat
On Windows a single simulation can be run in the terminal or via batch file (i.e. as in [here](https://github.com/numalariamodeling/covid-chicago/blob/master/runModel_testing.bat)
- Via python (including plotting)
The [run_and_plot_testing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/run_and_plot_testing.py) file runs the emodl simulations and prododuces a simple plot of the observed channels. 

### 4.2.1. Run scenarios (multiple simulations)
The [extendedcobey_runScenarios.py](extendedcobey_runScenarios.py) 
- takes one emodl, 
- optionally replaces parameters if @param@ placeholders are found, 
- optionally runs for multiple samples per parameter
- combines multiple trajectories.csv files produced into a trajectoriesDat.csv, that is used for postprocessing. 

### 4.2.2. Run scenarios (generic)
[runScenarios.py](runScenarios.py) is used to run multiple simulations
given a configuration file with the parameters. The script builds off
a default configuration file [extendedcobey.yaml](extendedcobey.yaml)
and substitutes parameters with the values/functions in the
user-provided configuration file using the `@param@` placeholder. As with
[extendedcobey_runScenarios.py](extendedcobey_runScenarios.py), it combines multiple trajectories.csv files produced into a trajectoriesDat.csv, that is used for postprocessing.


#### Configuration file:
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

#### Inputs:
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
  parameter values. The default is test_randomnumber (e.g. `20200417_EMS_10__test_rn29`)
  
### Usage examples:
- Using the default emodl template: `python runScenarios.py
  --running_location Local --region IL  --experiment_config ./experiment_configs/sample_experiment.yaml`
- Using a different emodl template: `python runScenarios.py
  --running_location Local  --region IL  --experiment_config sample_experiment.yaml --emodl_template simplemodel_testing.emodl`
- Specifying experiment name suffix and changing running_location : `python runScenarios.py
  --running_location NUCLUSTER --region IL --experiment_config extendedcobey.yaml --emodl_template simplemodel_testing.emodl --name_suffix "testrun_userinitials"`

### 4.3. Postprocessing and visualizing results
- latest postprocessing file that calculates incidences for extended SEIR model [extended_model_postprocessing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/extended_model_postprocessing.py)

### 4.4. Fitting to data
The [NMH_catchment_comparison.py](https://github.com/numalariamodeling/covid-chicago/blob/master/NMH_catchment_comparison.py) compares the predicted number of new detected hospitalized cases, cumulative detections of hospitalized cases, total number of case hospitalizations and number of critical cases to hospital data and case reports. The starting date and intervention effect size are fixed and the transmission parameter beta, or in CMS called "Ki", in other words the contact rate * transmission probability is fitted to the data. 

### 4.5. Local environment setup
Use a `.env` file in the same directory as your `runScenarios` script to define paths to directories and files on your own computer.
Copy the `sample.env` file to `.env` and edit so that paths point as needed for your system.

### 4.6. Running on OS X or Linux
The CMS software is provided as a compiled Windows executable, but can be run on Unix-like systems via [`wine`](https://www.winehq.org/).
If you do not have `wine` installed on your system, you can use the provided [Dockerfile](Dockerfile), which has `wine` baked in.
To build the Docker image, run `docker build -t cms`. Set `DOCKER_IMAGE=cms` in your environment or your `.env` file to use it.

## 5. Data sources
- IDPH
- NMH
- City of Chicago
- ...

## 6. Model parameters and uncertainity
To account for uncertainity and heterogeneity in transmission and disease parameters, all the parameters are sampled from a distribution informed by literature. 

### 6.1. Parameter table of transmission and disease parameters

| Parameter                                       | value (lower) | value (higher) | Source                           |   |
|-------------------------------------------------|---------------|----------------|----------------------------------|---|
| Transmission   rate                             |               |                | Fitted to data                   |   |
|                                                 |               |                |                                  |   |
| Initial infections                              |  10           | fixed          |                                  |   |
| Latency period                                  | 1             | 5              |                                  |   |
| Incubation period                               | 4.2           | 6.63           |                                  |   |
| Time to hospitalization                         | 2             | 10             | [1]                              |   |
| Time to critical                                | 4             | 9              | [2]                              |   |
| Time to death                                   | 3             | 11             | [3]                              |   |
| Fraction hospitalized                           |               |                | Derived from critical and deaths |   |
| Fraction symptomatic                            | 0.5           | 0.8            |                                  |   |
| Fraction critical*                              | 0.049         | 0.115          |                                  |   |
| Reduced infectiousness of detected cases        | 0.5           | 0.9            |                                  |   |
| Case fatality rate*                             | 1.8           | 3.4            |                                  |   |
| Detection rate of mild symptomatic infections   | 0.2           | 0.3            |                                  |   |
| Detection rate of severe symptomatic infections | 0.7           | 0.9            |                                  |   |
| Detection rate of asymptomatic infections       | 0             | 0              |                                  |   |
| Recovery rate of asymptomatic infections        | 6             | 16             | [4]                              |   |
| Recovery rate mild symptomatic infections       | 19.4          | 21.3           | [4]                              |   |
| Recovery rate of hospitalized cases             | 19.5          | 21.1           | [4]                              |   |
| Recovery rate of critical cases                 | 25.3          | 31.6           | [4]                              |   |


[1] Report 8: Symptom progression of COVID-19
[2] Huang, C et al, 2020. Clinical features of patients infected with 2019 novel coronavirus in Wuhan, China. https://doi.org/10.1016/S0140-6736(20)30183-5
[3] Yang, X., et al 2020. Clinical course and outcomes of critically ill patients with SARS-CoV-2 pneumonia in Wuhan, China […]. https://doi.org/10.1016/S2213-2600(20)30079-5
[4] Bi, Q.  et al ., 2020. Epidemiology and Transmission of COVID-19 in Shenzhen China […] https://doi.org/10.1101/2020.03.03.20028423

### 6.1. Time-varying parameters
[...]

### 6.3. Intervention scenarios
[...]


## 7. List of assumptions made (and potential improvements)
- same case fatality rate for detected and not detected cases
- no waning of immunity, recovered individuals stay in the recovered compartment
- fixed effect size of social distancing using step function increase on 13, 17, and 21st of March
- fixed detection rate over time
- symmetric contacts between age groups
- no age-specific disease parameters (in process)
- homogeneous mixing in spatial model
- ...
[...]



