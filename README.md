# Modelling the COVID-19 pandemic in Illinois

This repository includes simulation model and analysis scripts for modelling the COVID-19 pandemic in Illinois per covidregion.  

[1. Model overview](https://github.com/numalariamodeling/covid-chicago#1-model-overview)  
[2. Software used](https://github.com/numalariamodeling/covid-chicago#2-software-used)  
[3. Postprocess and analyse simulation outputs](https://github.com/numalariamodeling/covid-chicago#3-postprocess-and-analyse-simulation-outputs)  
[4. Data sources](https://github.com/numalariamodeling/covid-chicago#4-data-sources)  
[5. Model updates](https://github.com/numalariamodeling/covid-chicago#5-model-updates)  
[6. Resources](https://github.com/numalariamodeling/covid-chicago#6-resources)  

# 1. Model overview

### 1.1 Compartmental model structure (emodl file)
A basic SEIR model was extended to include symptom status (asymptomatic, presymptomatic, mild and severe symptoms), hospitalization, critical illness, and deaths, while allowing to track detected and undetected cases separately. In the model, the susceptible population is exposed (infected) at a constant rate described by the transmission probability and contact rate with the infectious population. After latent period of few days, the exposed population becomes infectious and moves either to the asymptomatic or pre-symptomatic compartments. At the end of the incubation period pre-symptomatic population develops either mild or severe symptoms. Mild symptomatic cases recover at a similar rate as asymptomatic cases, while all severe symptomatic cases that ‘should’ need professional care move to the hospitalization compartment. Hospitalized cases either recover or develop critical illness and then recover, or die. Once recovered, we assume that the population stays immune throughout the simulation period. The asymptomatic presymptomatic, mild symptomatic, severe symptomatic infections, undetected hospitalized are the infectious compartments with reduced infectiousness for the detected sub-compartments due to self-isolation. We assume that hospitalized cases that are detected are not infectious. 
![model](https://github.com/numalariamodeling/covid-chicago/blob/master/SEIR_base_model_structure.png)
Simulations run per [Emergency Medical Service Area (EMS)](https://www.dph.illinois.gov/sites/default/files/publications/emsjuly2016small.pdf) and are aggregated for [restore regions](https://coronavirus.illinois.gov/s/restore-illinois-regional-dashboard), and for Illinois. As of the 22nd of July, the ['covid regions'](http://dph.illinois.gov/regionmetrics?regionID=1) are used. For simplicity, the term 'EMS' is kept in the modelling files. 

## 1.2. Model parameters
Most of the parameters are derived from literature, local hospital data as well as doublechecked with other models used in Illinois (i.e. [UChicago](https://github.com/cobeylab/covid_IL/tree/master/Parameters)).
The starting date, intervention effect size, and the transmission parameter "Ki"are fitted to death data.

<details><summary>Show parameter tables</summary>
<p>

### 1.2.1 'reaction paramaters'
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


### 1.2.2  Transmission and disease parameters 

| Parameter                                                               | Description                                                                                                                                                                                   | Value             | Unit                                                                           | Source                                                                      |
|-------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| Initial   infectious population                                         | Number of infectious population   that initiates the local transmission                                                                                                                       | 10                | N                                                                              | Assumed                                                                       |
| Ki   (transmission rate)                                                | Rate at which susceptible become   infectious (contact rate * probability of infection).                                                                                                      |                   | rate                                                                           | Fited   to data from pre March 21 (EMResource and Line List data)                    |
| Ki   multiplier (transmission rate multiplier)                          | This parameter adjusts the   initial transmission rate over time to reflect changes in mitigation policies, lockdowns and mask wearing as well as other factors that affect   transmission. |                   |                                                                                | Fited to data every week using  monthly time events for change in transmission.  |
| Date of   imported infection                                            | Date when local transmission   started                                                                                                                                                        | Feb   13 - Feb 27 | date                                                                           | Fit   to data from pre March 21 (EMResource and line list)                    |
| time_to_infectious                                                      | Time   from being exposed to become infectious                                                                                                                                                | (2.4 , 3.5)       | days                                                                           |  [Li et al 2020](https://science.sciencemag.org/content/368/6490/489)                                                                             |
| time_to_symptomatic                                                     | Time from   becoming infectious to onset of symptoms                                                                                                                                          | (3.0, 4.5)        | days                                                                           |  [Li et al 2020](https://science.sciencemag.org/content/368/6490/489) and [Jing et al 2020](https://www.medrxiv.org/content/10.1101/2020.03.06.20032417v1)                                                                            |
| time_to_hospitalization                                                 | Time from   possible detection to hospitalization                                                                                                                                             | (3, 6)            | days                                                                           | [Huang et al 2020](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(20)30183-5/fulltext)        |
| Time to   critical                                                      | Time between hospitalization and   critical illness                                                                                                                                           | (4,   6)          | days                                                                           | NMH,  [Huang et al 2020](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(20)30183-5/fulltext)                                                                      |
| Time to   death                                                         | Time between critical illness   and deaths                                                                                                                                                    | (4,   6)          | days                                                                           |  [Yang et al 2020](https://pubmed.ncbi.nlm.nih.gov/32105632/)                                                                             |
| Recovery time asymptomatic                                              | Time   until an asymptomatic infection is cleared                                                                                                                                             | 9                 | days                                                                           | [Cevik et al 2020](https://www.thelancet.com/journals/lanmic/article/PIIS2666-5247(20)30172-5/fulltext)                                            |
| Recovery   time mild symptomatic                                        | Time until mildly symptomatic   case recovers                                                                                                                                                 | 9                 | days                                                                           | [Cevik et al 2020](https://www.thelancet.com/journals/lanmic/article/PIIS2666-5247(20)30172-5/fulltext)                                                                           |
| Recovery time hospitalized                                              | Time   until hospitalized cases (severe symptomatic) recover                                                                                                                                  | (4, 6)            | days                                                                           | NMH, [Lewnard et al 2020](https://pubmed.ncbi.nlm.nih.gov/32444358/) and  [Wang et al 2020](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7042881/)                                                   |
| Recovery   time critical   (time varying)                               | Time until   critical cases (severe symptomatic) recover                                                                                                                                      | (8,10)            |                                                                                | [Bi et al 2020](https://www.thelancet.com/journals/laninf/article/PIIS1473-3099(20)30287-5/fulltext)                                                                             |
| Fraction   symptomatic                                                  | Fraction of infections that   develop either mild or severe symptoms                                                                                                                          | (0.5,   0.7)      |                                                                                | [Oran and Topol et al 2020](https://www.scripps.edu/science-and-medicine/translational-institute/about/news/sarc-cov-2-infection/)                                                                              |
| Fraction   severe symptomatic                                           | Fraction of symptomatic that   develop severe symptoms                                                                                                                                        | (0.02,   0.1)     |                                                                                | [Salje et al 2020](https://www.medrxiv.org/content/10.1101/2020.04.20.20072413v2)                                                                             |
| Fraction critical     (time varying)                                    | Fraction   of severe symptomatic infections that require intensive care                                                                                                                       | (0.2, 0.35)       |                                                                                | [Lewnard et al 2020](https://pubmed.ncbi.nlm.nih.gov/32444358/)                                                                             |
| CFR       (time varying)                                                | Case fatality rate                                                                                                                                                                            | (0.01, 0.04)      |                                                                                | [Wang et al 2020](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7042881/)                                                                              |
| Reduced   infectiousness of detected cases                              | Fraction of detected cases that   isolate and are removed from the infectious population                                                                                                      | (0,   0.3)        |                                                                                | Assumed                                                                       |
| Detection   probability of asymptomatic case                            | Used for contact tracing   simulations, per default asymtomatic cases are not detected                                                                                                        | (0,   0)          |                                                                                | Assumed   initial value, increase informed from Illinois specific data                                                                       |
| Detection   probability of mild symptomatic case   (time varying)       | Initial value of the detection   rate, which is increasing over time                                                                                                                          | (0.05,   0.2)     |                                                                                | Assumed   initial value, increase informed from Illinois specific data        |
| Detection   probability of severe symptomatic case  (time varying)      | Initial value of the detection   rate, which is increasing over time                                                                                                                          | (0.2,   0.5)      |                                                                                | Calculated from IL data                                        |
| Impact of transmission mitigation policies, lockdown and   mask-wearing | reflected in transmission rate parameter                                                                                                                                                      |                   | Fiteed to data and updated every week using monthly 'transmission changepoints' |                                                                               |

Note: List also on [Box](https://northwestern.app.box.com/file/656414061983)!

### 1.2.3  time-varying parameters (intervention scenarios)
The [time-event](https://idmod.org/docs/cms/model-file.html?searchText=time-event) option in cms allows to change a paramter at a given time point (days) (which will stay constant afterwards if not resetted using a stop time-event).
Time-event are used to define reduction in the transmission rate, reflecting a decrease in contact rates due to social distancing interventions (i.e. stay-at-home order). 
The time event can also be used to reflect increasing testing rates by increasing the detection of cases (i.e. dSym and dSys for increased testing at health facilities, or dAs and dSym for contact tracing)

Current scenarios include:
- No stay-at-home 
- Continued stay-at-home
- Stop stay-at-home order - immediately
- Stop stay-at-home order - step-wise 
- Contact tracing - immediately
- Contact tracing - step-wise

For details, see the [cms implementation in one of the emodl generators](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_base.py#L514)

</p>
</details>

## 1.3. Model outcomes

Currently the model includes 28 compartments of which 43 outcome variables are generated.
The outcome variables or channels, as referred to in the py plotters, are different aggregates of the main compartments by type (i.e. all detected, all severe symptomatic) and includes cumulative counts for the calculation of incidences during postprocessing. 
A ranking 'observeLevel' was introduced to select subsets of the outcomes. The primary outcomes are those required for the weekly deliverables, the secondary are the related outcomes that are not required for the standard outputs and tertiary are those that can easily be calculated outside the model, such as prevalence, or outcomes rarely used such as infectiousness by symptomatic type and detection level. 

<details><summary>Show table</summary>
<p>

| alphabet.   No | name                   | description                                                                            | observeLevel | compartments  included                                                                                                   |
|----------------|------------------------|----------------------------------------------------------------------------------------|--------------|------------------------------------------------------------------------------------------------------------------------|
| 1              | asymp_cumul            | Number of all asymptomatic infections that happened (cumulative)                       | primary      | asymptomatic, RA, RAs_det1                                                                                             |
| 2              | asymp_det_cumul        | Number of all detected asymptomatic infections that happened (cumulative)              | secondary    | As_det1, RAs_det1                                                                                                      |
| 3              | asymptomatic           | Number of asymptomatic infections                                                      | secondary    | As                                                                                                                     |
| 4              | asymptomatic_det       | Number of  detected asymptomatic   infections                                          | secondary    | As_det1                                                                                                                |
| 5              | crit_cumul             | Number of all critical cases that happened (cumulative)                                | primary      | deaths, critical, RC2,RC2_det3                                                                                         |
| 6              | crit_det               | Number of critical cases that are detected                                             | primary      | C2_det3, C3_det3                                                                                                       |
| 7              | crit_det_cumul         | Number of all detected critical cases that happened (cumulative)                       | primary      | C2_det3, C3_det3, D3_det3, RC2_det3                                                                                    |
| 8              | critical               | Number of severe symptomatic infections that are hospitalized that are   critical      | primary      | C2, C3,  C2_det3,  C3_det3                                                                                             |
| 9              | death                  | Number of COVID-19 deaths in the population                                            | primary      | D3, D3_det3                                                                                                            |
| 11             | death_det_cumul        | Number of all detected COVID-19 deaths in the population that happened                 | primary      | D3_det3                                                                                                                |
| 12             | detected               | Number of detected COVID-19 infections regardless of symptomaticity                    | primary      |  As_det1, Sym_det2, Sys_det3,   H1_det3, H2_det3, H3_det3, C2_det3, C3_det3                                            |
| 13             | detected_cumul         | Number of all detected COVID-19 infections regardless of symptomaticity   (cumulative) | primary      | As_det1, Sym_det2, Sys_det3, H1_det3, H2_det3, C2_det3, C3_det3,   RAs_det1, RSym_det2, RH1_det3, RC2_det3,    D3_det3 |
| 14             | exposed                | Number of exposed (infected not yet infectious) in the population                      | secondary    | E                                                                                                                      |
| 15             | hosp_cumul             | Number of all hospitalizations due to COVID-19 that happened (cumulative)              | primary      | hospitalized,  critical,  deaths,    RH1,  RC2,  RH1_det3,    RC2_det3                                                 |
| 16             | hosp_det               | Number of detected COVID-19 hospitalizations                                           | primary      | H1_det3,  H2_det3,  H3_det3                                                                                            |
| 17             | hosp_det_cumul         | Number of all detected COVID-19 hospitalizations that happened   (cumulative)          | primary      | H1_det3, H2_det3, H3_det3, C2_det3, C3_det3, D3_det3, RH1_det3,   RC2_det3                                             |
| 18             | hospitalized           | Number of severe symptomatic infections that are hospitalized                          | primary      | H1,  H2,   H3,     H1_det3,  H2_det3,  H3_det3                                                                         |
| 19             | infected               | Number of all infected in the population                                               | primary      | all except susceptibles                                                                                                |
| 20             | infected_cumul         | Number of all that were infected (cumulative)                                          | secondary    | infected, recovered, deaths                                                                                            |
| 21             | infected_det           | Number of all  infected that are   detected                                            | secondary    | infectious_det,  H1_det3,  H2_det3,    H3_det3,  C2_det3, C3_det3                                                      |
| 23             | infectious_det         | Number of all infectious that are detected                                             | tertiary     | As_det1, P_det , Sym_det2, Sys_det3                                                                                    |
| 24             | infectious_det_AsP     | Number of all non-symptomatic that are infectious and detected                         | tertiary     | As_det1, P_det                                                                                                         |
| 25             | infectious_det_symp    | Number of all  symptomatic that are   infectious and detected                          | tertiary     | Sym_det2,  Sys_det3                                                                                                    |
| 26             | infectious_undet       | Number of infectious that are not detected                                             | tertiary     | As, P, Sym, Sys, H1, H2, H3, C2, C3                                                                                    |
| 27             | presymptomatic         | Number of presymptomatic infections                                                    | primary      | P, Pdet                                                                                                                |
| 28             | presymptomatic_det     | Number of all detected presymptomatic infections                                       | secondary    | Pdet                                                                                                                   |
| 29             | prevalence             | Number of infected (cumul) over total population                                       | tertiary     | infected /  N                                                                                                          |
| 30             | prevalence_det         | Number of detected infected (cumul) over total population                              | tertiary     | infected_det /  N                                                                                                      |
| 31             | recovered              | Number of recovered COVID-19 cases    in the population                                | primary      | RAs,RSym, RH1,  RC2, RAs_det1,   RSym_det2, RH1_det3, RC2_det3                                                         |
| 32             | recovered_det          | Number of detected recovered COVID-19 cases in the population                          | primary      | RAs_det1, RSym_det2, RH1_det3, RC2_det3                                                                                |
| 33             | seroprevalence         | Number of recovered (cumul) over total population                                      | tertiary     | (infected + recovered) /  N                                                                                            |
| 34             | seroprevalence_det     | Number of detected recovered (cumul) over total population                             | tertiary     | (infected_det + recovered_det) /  N                                                                                    |
| 35             | susceptible            | Number of susceptibles in the population                                               | primary      | S                                                                                                                      |
| 36             | symp_mild_cumul        | Number of all mild symptomatic infections that happened (cumulative)                   | primary      | symptomatic_mild, RSym,  RSym_det2                                                                                     |
| 37             | symp_mild_det_cumul    | Number of all detected mild symptomatic infections that happened   (cumulative)        | primary      | symptomatic_mild_det, RSym_det2                                                                                        |
| 38             | symp_severe_cumul      | Number of all severe symptomatic infections that happened (cumulative)                 | primary      | symptomatic_severe, hospitalized,    critical,  deaths,  RH1,    RC2,  RH1_det3,  RC2_det3                             |
| 39             | symp_severe_det_cumul  | Number of all detected severe symptomatic infections that happened   (cumulative)      | primary      | symptomatic_severe_det, hosp_det,    crit_det,  deaths_det                                                             |
| 40             | symptomatic_mild       | Number of  mild symptomatic   infections                                               | primary      | Sym,  Sym_det2; Sym,  Sym_preD, Sym_det2 ;  Sym,    Sym_preD, Sym_det2a, Sym_det2b                                     |
| 41             | symptomatic_mild_det   | Number of detected mild infections in the population                                   | secondary    | symptomatic_mild_det                                                                                                   |
| 42             | symptomatic_severe     | Number of severe symptomatic infections                                                | secondary    | Sys, Sys_det3; Sys, Sys_preD, Sys_det3 ; Sys, Sys_preD, Sys_det3a,   Sys_det3b                                         |
| 43             | symptomatic_severe_det | Number of detected severe symptomatic infections                                       | secondary    | symptomatic_severe_det                                                                                                 |
 
</p>
</details>

## 1.4. Age and spatial model structures

### 1.4.1. Age-structured model 
The "age_model" duplicates each compartment of the simple or the extended model for n age groups. To allow the age groups to get in contact with each other at different rates, the Ki (contact rate * probability of transmission) needs to be specified for a all age-combinations. 

-  Age groups: "0to9", "10to19", "20to29", "30to39", "40to49", "50to59", "60to69", "70to100" 
[(emodl)](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_age8.emodl)
To generate or modify the emodl files use the [age specific emodl generator](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/emodl_generator_cobey_contact_mix.py) 

#### Contact matrix
The contacts between age groups were previously extracted for running an [EMOD model](https://idmod.org/documentation) from [Prem et al 2017](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005697). [Script that extracts the contact matrix values](https://github.com/numalariamodeling/covid-chicago/blob/master/age_model/age_contact/age_matrix_reducer.py). 

### 1.4.2. Spatial model
The "spatial_model" uses a special syntax as described [here](https://idmod.org/docs/cms/create-spatial-model.html?searchText=spatial). 
To generate or modify the emodl files use the [locale specific emmodl generator](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/locale_emodl_generator_extendedModel.py )
- View the [EMS specific emodl](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_EMS.emodl)


### 1.4.3. Spatial age-structured model
A test verion is available under [emodl file](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_agelocale_scen3.emodl).
To generate or modify the emodl files use the [locale-age specific emmodl generator](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl_generators/extended_cobey_age_locale_emodl_generator.py )


# 2. Software used
The [Compartmental Modeling Software (CMS)](https://idmod.org/docs/cms/index.html) is used to simulate the COVID-19 transmission and disease progression. The CMS language defines 5 main type: species, observations, reactions, parameters and functions, in addition time-events can be added as well as state-events. Multiple compartments, called ‘species’ can be defined. The movement of populations between compartments is called reaction. The model runs with different solvers, including spatial solvers. The model is written in ['emodl' files](https://idmod.org/docs/cms/input-files.html) and model configurations are written in ['cfg' files](https://idmod.org/docs/cms/input-files.html). The output is written into [trajectories.csv files](https://idmod.org/docs/cms/output.html?searchText=output).

The latest model description in emodl format is written in the [extendedmodel.emodl](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel.emodl) file (note original emodl with history in [extendedmodel_cobey.emodl](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_cobey.emodl). 

## 2.1 Run simulations 
The [runScenarios.py](runScenarios.py) is used to run multiple simulations
given a configuration file with the parameters. The script builds off
a default configuration file [extendedcobey.yaml](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/extendedcobey_200428.yaml)
and substitutes parameters with the values/functions in the
user-provided configuration file using the `@param@` placeholder. Multiple trajectories.csv that are produced per single simulation are combined into a trajectoriesDat.csv, used for postprocessing and plotting.

## 2.2 [Configuration file](https://github.com/numalariamodeling/covid-chicago/tree/master/experiment_configs):
The configuration file is in [YAML](https://yaml.org/) format and is divided into 5
blocks: `experiment_setup_parameters`,
`fixed_parameters_region_specific`, `fixed_parameters_global`,
`sampled_parameters`, `fitted_parameters`. The sampled parameters need
the sampling function as well as the arguments to pass into that
function (`function_kwargs`). Currently, only a few
sampling/calculation functions are supported. More can be added by
allowing for more libraries in `generateParameterSamples` of [runScenarios.py](runScenarios.py).

Note that the user-supplied configuration file is used to provide
*additional* or *updated* parameters from the base configuration file.

## 2.3 Inputs:
- Master configuration: YAML file that defines the parameter input values for the model (if not specified uses the default `extendedcobey_200428.yaml`)
- Running location: Where the simulation is being run (either `Local`
  or `NUCLUSTER`)
- Region: The region of interest. (e.g. `EMS_1`, or `IL` for all EMS 1-11 inclued in the same model)
- Configuration file: The configuration file with the parameters to
  use for the simulation. If a parameter is not provided, the value in
  the default configuration will be used. (e.g. [sample_experiment.yaml](sample_experiment.yaml))
- Emodl template (optional): The template emodl file to substitute in
  parameter values. The default is [extendedmodel.emodl](extendedmodel.emodl). emodl
  files are in the `./emodl` directory.
- cfg template (optional): The default cfg file uses the [Tau leaping](https://idmod.org/docs/cms/tau-leaping.html) solver (recommended B solver).
- Suffix for experiment name added as name_suffix (optional): The template emodl file to substitute in
  parameter values. The default is test_randomnumber (e.g. `20200417_EMS_10_test_rn29`)

### Region specific sample parameters (i.e. using estimates parameters per regions)
- [`EMSspecific_sample_parameters.yaml`](https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/EMSspecific_sample_parameters.yaml)

###  Age extension and age specific parameters 
- `sample_age4grp_experiment.yaml `(https://github.com/numalariamodeling/covid-chicago/blob/master/experiment_configs/sample_age4grp_experiment.yaml) 
Note: this extension works for any sub-group as it duplicates the parameter names for the defined group names, which need to be defined in the same way in the corresponding emodl file.

The [simulation_submission_template.txt](https://github.com/numalariamodeling/covid-chicago/blob/master/simulation_submission_template.txt) shows example command lines and scenarios that are currently being used. 

<details><summary>Show examples</summary>
<p>  


####  Usage examples:  
- Using the default emodl template: `python runScenarios.py
  --running_location Local --region IL  --experiment_config sample_experiment.yaml`
- Using a different emodl template: `python runScenarios.py
  --running_location Local  --region IL  --experiment_config sample_experiment.yaml --emodl_template simplemodel_testing.emodl`
- Specifying experiment name suffix and changing running_location : `python runScenarios.py
  --running_location NUCLUSTER --region IL --experiment_config sample_experiment.yaml --emodl_template simplemodel_testing.emodl --name_suffix "testrun_userinitials"`
- Specifiying cms configuration file and solver:`python runScenarios.py
  --running_location Local --region IL  --experiment_config sample_experiment.yaml --emodl_template simplemodel_testing.emodl --cfg_template model_Tau.cfg`
- Specifiying master configuration file and using short form of arguments:`python runScenarios.py 
  -mc config_param_delay7.yaml -rl Local -r IL -c spatial_EMS_experiment.yaml -e extendedmodel_EMS_criticaldet_triggeredrollbackdelay.emodl -cfg model_B.cfg
</p>
</details>

## 2.4 Sampled parameters 
As described in 2.1. and 2.2 parameters are sampled from the base configuration files when running `python runScenarios.py`.
The [sample_parameters.py](sample_parameters.py) script handles only the sampled_parameters.csv, it allows to: 
(1) generate csv file from configuration files without running simulations
(2) load and modify an existing sampled_parameters.csv (change or add single or multiple parameter) (default location `experiment_configs\input_csv`)
(3) replace single values for one or more parameter use python dictionary  `--param_dic  {\"capacity_multiplier\":\"0.5\"}`
(4) combine with multiple values for one or more parameters define additional csv file   `--csv_name_combo startdate_Ki_sets.csv`

<details><summary>Show examples</summary>
<p>  

Running examples:  
- nsamples: optional, if specified if overwrites the nsamples in the base configuration, if loading an existing csv the first n samples will be selected (i.e. when selecting samples from an excisting csv file, could be modified to be random if needed)
- emodl_template: the emodl template is required to test whether the parameter csv table includes all required parameters defined in the desired emodl file to run
- example 1: `python sample_parameters.py -rl Local -r IL --experiment_config spatial_EMS_experiment.yaml --emodl_template extendedmodel_EMS.emodl  -save sampled_parameters2.csv`
- example 2: `python sample_parameters.py -rl Local -save sampled_parameters_1000.csv --nsamples 1000`
- example 3: `python sample_parameters.py -rl Local -load sampled_parameters_1000.csv -save sampled_parameters_1000_v2.csv  --param_dic  {\"capacity_multiplier\":\"0.5\"} `
- example 4: `python sample_parameters.py   --csv_name_combo  sampled_parameters_sm7.csv   -save sampled_parameters_sm7_combo.csv`
   -(sampled_parameters_sm7.csv not under version control, but would for example include 10 values for social multiplier 7 for all 11 regions, the base sample parameters are repeated for each of the 10 rows of the additional csv)

When running simulations with an pre-existing csv file, specify 
- `--load_sample_parameters` (boolean) and 
- `--sample_csv` (name of csv file in `experiment_configs\input_csv` ).

Note: except the loaded "sampled_parameters.csv" and "sampled_parameters_1000.csv", csv files should not be added to version control on git. 
</p>
</details>

## 2.6. Setup 
Running simulation requires the CMS software and python. Additional software includes R and Rstudio for some of the postprocessing steps. 
The model runs on Windows and Linux as well as the Northwestern high performance computing cluster (Quest). 
The detailes are described below. 

<details><summary>Show setup description</summary>
<p> 

### Software requirements and packages
The [`requirements.txt`](https://github.com/numalariamodeling/covid-chicago/blob/master/requirements.txt) includes name and version of required python modules.

  
### Local environment setup  
Use a `.env` file in the same directory as your `runScenarios` script to define paths to directories and files on your own computer.
Copy the `sample.env` file to `.env` and edit so that paths point as needed for your system.

### Running on OS X or Linux
The CMS software is provided as a compiled Windows executable, but can be run on Unix-like systems via [`wine`](https://www.winehq.org/).
If you do not have `wine` installed on your system, you can use the provided [Dockerfile](Dockerfile), which has `wine` baked in.
To build the Docker image, run `docker build -t cms`. Set `DOCKER_IMAGE=cms` in your environment or your `.env` file to use it.

### Running on Quest (NUCLUSTER) 
A cloned version of the git repository can be found under `/projects/p30781/covidproject/covid-chicago/`.

Requirements:
All the modules need to be installed on the personal quest environment 
- use pip install ... in your terminal 
- install `dotenv` and `yamlordereddictloader`
`conda create --name dotenv-py37 -c conda-forge python-yamlordereddictloader python=3.7 --yes`
`source activate dotenv-py37`
`conda install -c conda-forge yamlordereddictloader`

Alternatively, a virtual environment can be activated using:
i.e. add a `set-covid-chicago` command in the `bash.profile` file in the home directory

	set-covid-chicago(){
		module purge all
		module load python/anaconda3.6
		source activate /projects/p30781/anaconda3/envs/team-test-py37
	}
  
[Box syncing](https://kb.northwestern.edu/page.php?id=70521):

	mirror-box-covid(){
		lftp -p 990 -u <useremail> ftps://box.com -e "mirror NU-malaria-team/data/covid_IDPH/Cleaned\ Data/ /projects/p30781/covidproject/data/covid_IDPH/Cleaned\ Data/; exit"
		lftp -p 990 -u  <useremail> ftps://box.com -e "mirror -R /projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/ NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/; exit"
	}
 

##### Submit job 
On Quest jobs are submitted using the SLURM workload manager and syntax ([SLURM on quest](https://kb.northwestern.edu/page.php?id=89456))
`cd /projects/p30781/covidproject/covid-chicago/`
`python runScenarios.py -rl NUCLUSTER --r EMS_11 -c extendedcobey_200428.yaml --emodl_template extendedmodel.emodl -n "quest_run"`

The experiments will go to the _temp folder on the quest gitrepository. 
To avoid confusion on owner of the simulations it is recommended to include the initials in the experiment name using the name_suffix argument

The status of the job submission can be called via `squeue -u <username>`

</p>
</details>

# 3 Postprocessing and visualization of simulation outputs
Via the `--post_process` argument in the runScenarios command additional scripts will run directly after simulations finished.
A sample plot (`master_sample_plot.png`) is generated for every simulation regardless of type (base, age, spatial) for all Illinois, which can be disabled via --noSamplePlot.
Batch files are generated for data comparison, process for civis steps and basic plotter (age, locale emodl regardless of the  `--post_process` argument.
Batch files are only generated for the most important postprocessing files and additional batch files or postprocesses may be linked to runScenarios of needed. 
To see all the available postprocessing scripts, go to the [plotters folder](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/) (see readme in folder for details).
When adding the flag `--post_process "processForCivis"` in the `runScenarios.py` submission command, the batch files related to the weekly deliverables are automatically executed. 

## Postprocessing on local machine
Locally, there are two main batch files:
- `run_postprocess.bat` is a wrapper batch file that runs postprocessing files from the list below (general postprocessing not for weekly deliverables)
- `run_postprocess_for_civis.bat` is a wrapper batch file that runs postprocessing from the list below (postprocessing for weekly deliverables)

The postprocessing includes the following steps below:

<details><summary>Show postprocessing scripts</summary>
<p> 

- `0_runCombineAndTrimTrajectories.bat` calls  [combine_and_trim.py](https://github.com/numalariamodeling/covid-chicago/blob/master/combine_and_trim.py) combines and trims the simulation output csv files (trajectories.csv files) 
- `0_locale_age_postprocessing.bat` calls  [locale_age_postprocessing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/locale_age_postprocessing.py) to plot trajectories for pre-specified outcome channels per age group.
- `1_runTraceSelection.bat`  calls [trace_selection.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/trace_selection.py) calculating the negative log-likelihood per simulated trajectory, used for thinning predictions and parameter estimation
- `2_runDataComparison.bat`  calls [data_comparison_spatial.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/data_comparison_spatial.py) comparing model predictions to data per region over time
- `3_runProcessTrajectories.bat`  calls [process_for_civis_EMSgrp.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/process_for_civis_EMSgrp.py) generates the result csv dataframe (i.e. nu_20201005.csv) and generates descriptive trajectories per channel and region
- `4_runRtEstimation.bat`  calls [estimate_Rt_forCivisOutputs.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/estimate_Rt_forCivisOutputs.py)  that  runs the Rt estimation, the Rt columns are added to the result csv dataframe (i.e. nu_20201005.csv), produces descriptive plots
- `5_runOverflowProbabilities.bat`  calls [overflow_probabilities.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/overflow_probabilities.py) calculates the probability of hospital overflow and produces the  (i.e. nu_hospitaloverflow_20201005.csv), also adds total number of beds [additional script](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/overflow_numbers.py)
- `6_runPrevalenceIFR.bat`  calls [plot_prevalence.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_prevalence.py)
- `7_runICUnonICU.bat`  calls [plot_by_param_ICU_nonICU.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_by_param_ICU_nonICU.py)
- `8_runHospICUDeathsForecast.bat`  calls  [hosp_icu_deaths_forecast_plotter.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/hosp_icu_deaths_forecast_plotter.py)
- `9_runCopyDeliverables.bat` calls [NUcivis_filecopy.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/NUcivis_filecopy.py) that generates the NU_civis_outputs subfolder and copies all relevant files and adds the changelog.txt. Note: the changelog.txt will need manual editing to reflect new changes per week. 
- `10_runIterationComparison.bat` calls [iteration_comparison.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/iteration_comparison.py) that  generates the iteration comparison plot (last 3 weeks)
Note: if `1_runTraceSelection.bat` was run and the output csv files are located in the experiment folder, all subsequent scripts and plotting scripts will per default filter the simulated trajectories, if not explicily set to False in the `load_sim_data` function call.

To clean up simulations (delete trajectories and optinally zip and delete simulation folder run  [cleanup_and_zip_simFiles.py](https://github.com/numalariamodeling/covid-chicago/blob/master/nucluster/cleanup_and_zip_simFiles.py))

</p>
</details>

## Postprocessing on the NU cluster 'Quest'
On Quest shell instead of batch files are generated for the same python files as shown above.
For a detailed descripton of the shell files and processing steps, expand below:

<details><summary>Detailed processing steps</summary>
<p> 

The time limit for each single simulation was set to 30 min per default.
Simulation run in the `_temp` folder (`/projects/p30781/covidproject/covid-chicago/_temp/`) in the git repository.
After all simulations ran, they are automatically combined and moved to the Box folder on Quest, located in 
`simulation_output` (`/projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/`)

Wrapper shell script:
- `run_postprocessing.sh` runs automatically after simulation finish, it includes scripts from the list below.

Run from `/projects/p30781/covidproject/covid-chicago/_temp/<exp_name>`
- `0_runCombineAndTrimTrajectories.sh` 
- `0_cleanupSimulations.sh`  calls  [cleanup.py](https://github.com/numalariamodeling/covid-chicago/blob/master/nucluster/cleanup.py) and transfers files from temp to Box (on Quest)

Run from `/projects/p30781/covidproject/projects/covid_chicago/cms_sim/simulation_output/<exp_name>`
- `0_locale_age_postprocessing.sh`
- `1_runTraceSelection.sh` 
- `2_runDataComparison.sh` 
- `3_runProcessTrajectories.sh
- `4_runRtEstimation.sh` 
- `5_runOverflowProbabilities.sh` 
- `6_runPrevalenceIFR.sh` 
- `7_runICUnonICU.sh` 
- `8_runHospICUDeathsForecast.sh` 
- `9_runCopyDeliverables.sh`
- `10_runIterationComparison.sh` 

To clean up simulations (delete trajectories and optinally zip and delete simulation folder run  [cleanup_and_zip_simFiles.py](https://github.com/numalariamodeling/covid-chicago/blob/master/nucluster/cleanup_and_zip_simFiles.py))
Zipping the simulation folder facilitiates copying file to Box or the local machine.

</p>
</details>


# 4 Data sources
- Populaton estimates per county (2019): [County Population Totals: 2010-2019](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-total.html#par_textimage_242301767)
- Region boundaries and operational units
  - Emergency Medical Service Areas (EMS) regions (not used anymore): https://www.dph.illinois.gov/sites/default/files/publications/emsjuly2016small.pdf  
  - Covid regions: http://dph.illinois.gov/regionmetrics?regionID=1 
  - Restore regions: https://coronavirus.illinois.gov/s/restore-illinois-regional-dashboard 
- Hospital census data: daily occupancy of intensive care unit (ICU) and non_ICU beds (EMResource)
- Hospital capacity limits for hospital and intensive care unit beds (from IDPH)
- Positive case line list data: Of each individual tested positive for COVID-19: age, sex, race, ethnicity, date of specimen collection, date of hospital admission (if admitted), date of death (if died)
- Covid like illness (CLI) admissions is obtained from IDPH and  included in weekly model calibration. 

# 5. Model updates

## Updates in model structure and fitted parameters

The model is updated every week to fit to latest hospitalisation and deaths reports. 
<details><summary>Show history of updates</summary>
<p>  

- 20210114 updated parameter fit, activated transmission multiplier 12 for Dec, updated region populations, reduced recovery time As
- 20210106 added region specific recovery time critical
- 20201216 updated parameter fit
- 20201204 updated parameter fit, use muliplier 11 for decrease in trend
- 20201201 updated parameter fit
- 20201130 added transmission multiplier 12
- 20201124 updated parameter fit
- 20201119 updated parameter fit, added transmission multiplier 11
- 20201110 updated parameter fit
- 20201104 updated parameter fit 
- 20201027 updated parameter fit, added transmission multiplier 10 (previously called social multiplier)
- 20201020 updated parameter fit 
- 20201015 updated parameter fit, reset fitting method
- 20201007 updated parameter fit
- 20200929 updated parameter fit, changed fitting method
- 20200922 updated parameter fit, changed d_Sym parameters (generic)
- 20200915 updated parameter fit, added social multiplier 7 (time event Aug 25)
- 20200909 updated parameter fit, updated evolution of CFR
- 20200825 updated parameter fit
- 20200818 updated parameter fit, updated evolution of dSys and region-specific evolution of dSym
- 20200812 updated parameter fit
- 20200807 updated parameter fit
- 20200804 updated parameter fit
- 20200729 updated parameter fit, added region-specific evolution of dSym over time
- 20200722 updated parameter fit, use covid regions instead of EMS regions for fitting (same numbering 1-11)
- 20200715 updated parameter fit, added fifth social distancing multiplier (time event June 21st)
- 20200706 added time-varying fraction_critical
- 20200624 updated parameter fit
- 20200622 adjusted increase in detection for severe and mild symptomatic cases 
- 20200622 updated model structure, added test delay in Asymptomatics and detections in presymptomatic 
- 20200616 updated parameter fit 
- 20200610 updated parameter fit 
- 20200609 separat time delay for dSym and dSys, added d_Sym_incr 1-5 proportional to d_Sys_incr
- 20200602 updated parameter fit 
- 20200523 added d_Sys_incr4 and d_Sys_incr5, parameter fitting, including test delay per default
- 20200521 added s_m_4, parameter fitting
- 20200515 parameter fitting (also 20200512, 20200501)
- 20200428 updated model disease and transmission parameters (previously 20200421, 20200419)
- 20200428 added d_Sys_incr1-3  
- 20200421 adding scale-invariant Ki
- 20200407 add more detected observables
- 20200402 [cobey](https://github.com/cobeylab/covid_IL) model alignment (including presymptomatic)
- 20200321 initial model development including (S,E, Sym, Sys, As, H, C, D, R)


</p>
</details>

# 6. Resources and publications
- [Illinois COVID-19 Modeling Website](https://illinoiscovid.org/)
- [CMS software publication](https://link.springer.com/chapter/10.1007/978-3-030-31304-3_18); [CMS online documentation](https://idmod.org/docs/cms/index.html)
- [Chicago Covid Coalition website](https://sites.google.com/view/nu-covid19-landing-page/home?authuser=0)
- [Modeling COVID 19 Transmission and Containment in Illinois (IPHAM Webinar)](https://www.youtube.com/watch?v=DV1l7RDOCEc&feature=youtu.be) by Dr Jaline Gerardin.
- [Modeling COVID-19 Transmission and Containment Efforts at Northwestern](https://news.feinberg.northwestern.edu/2020/05/modeling-covid-19-transmission-and-containment-efforts/)
- [Use of the model for demonstrating statistical data assimilation](https://arxiv.org/abs/2005.12441) by Dr Armstrong et al. 

