### Emodl file format  
The emodl file contains all information that defines the mathematical model itself. 
For example, it defines the species, the transition rates, incubation time, daily recovery rate, and many other parameters specific to the disease being modeled. 
The model file is in EMODL format; the syntax and available parameters are described in [Model file syntax](https://idmod.org/docs/cms/model-file.html).

### Emodl spcified for COVID-19 modelling in Illinois 
There are 5 types of models: 1) base, 2) age (testing), 3) locale (spatial), 4) age-locale (testing), and 5) specified long-term care facility model (LTCF) (not in active use). 
Different ["emodl-generators"](https://github.com/numalariamodeling/covid-chicago/tree/master/emodl_generators) are available to generate the specific emodl file. 

File name convention: 
`exp_name = f"{today.strftime('%Y%m%d')}_{region}_{model}_{args.name_suffix}_{scenario}"`


### Emodl folder 
As of Feb 4th, the 'emodl generators' have been linked to runScenarios. 
When running `runScenarios.py`, the simulation specific emodl is generated and copied into this folder (not version controlled), so that each user can collect, generate as many emodls as they want. 
The `runScenarios.py` still allows to provide the name of the emodl file, in which case the existing emodl is taken and not re-generated. 
Each emodl file is copied into the respective simulation folder and can be retrieved from there. 


