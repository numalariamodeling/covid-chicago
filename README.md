# Modelling the COVID-19 pandemic in Chicago

- Modified SEIR model using Institute for Disease Modeling (IDM's) [Compartmental Modeling Software (CMS)](https://idmod.org/docs/cms/index.html)

- For more information on Covid in Chicago visit the (Chicago Covid Coalition website)[https://sites.google.com/view/nu-covid19-landing-page/home?authuser=0]

## CMS software
- [input](https://idmod.org/docs/cms/input-files.html) configuration file (cfg)
- [input](https://idmod.org/docs/cms/input-files.html)  model file (emodl)
- [output](https://idmod.org/docs/cms/output.html?searchText=output): trajectories.csv (optionally define prefix or suffix)

## Compartmental model 
### Simple model
The "simplemodel" includes only the basic S-E-I-R compartments. 
Go to the related [emodl file here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/simplemodel_testing.emodl)

### Extended model
The "extendedmodel" imclides additional compartments for asymptomatics, symptomatics, hospitalization, progression to critical and deaths. In addition the detections are tracked as a sum of detected asymptomatics, symptomatics,hospitalized, critical and deaths with group specific detection rates. 
Go to the related [emodl file here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_covid.emodl)

### "Extended_cobey" model
Latest version of the model, including modifications in alignment with the Covid model developed by Sarah Cobeys Team at University of Chicago. 
Go to the related [emodl file here](https://github.com/numalariamodeling/covid-chicago/blob/master/emodl/extendedmodel_cobey.emodl)


## Model types
## Base model
Assumes one well mixed homogeneous population 

## Age-structured model 
The "age_model" duplicates each compartment of the simple or the extended model for n age groups. To allow the age groups to get in contact with each other at different rates, the Ki (contact rate * probability of transmission) needs to be specified for a all age-combinations. 

## Spatial model
The "spatial_model" uses a special syntax as described [here](https://idmod.org/docs/cms/create-spatial-model.html?searchText=spatial). 

## Spatial age-structured model
A test verion is available under [spatial_age_model](https://github.com/numalariamodeling/covid-chicago/blob/master/spatial_age_model)
and the [emodl file](https://github.com/numalariamodeling/covid-chicago/blob/master/spatial_age_model/emodl/extendedmodel_cobey_locale_EMS_2grptest1.emodl)

## Running simulations

### Run single simulations
To run a single simulation: 
- Via termianl /bat
On Windows a single simulation can be run in the terminal or via batch file (i.e. as in [here](https://github.com/numalariamodeling/covid-chicago/blob/master/runModel_testing.bat)
- Via python (including plotting)
The [run_and_plot_testing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/run_and_plot_testing.py) file runs the emodl simulations and prododuces a simple plot of the observed channels. 

### Run scenarios (multiple simulations)
The [extendedmodel_runScenarios.py](https://github.com/numalariamodeling/covid-chicago/blob/master/extendedmodel_runScenarios.py) 
- takes one emodl, 
- optionally replaces parameters if @param@ placeholders are found, 
- optionally runs for multiple samples per parameter
- combines multiple trajectories.csv files produced into a trajectoriesDat.csv, that is used for postprocessing. 

## Postprocessing and visualizing results
- latest postprocessing file that calculates incidences for extended SEIR model [extended_model_postprocessing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/extended_model_postprocessing.py)

## Fitting to data
The [NMH_catchment_comparison.py](https://github.com/numalariamodeling/covid-chicago/blob/master/NMH_catchment_comparison.py) compares the predicted number of new detected hospitalized cases, cumulative detections of hospitalized cases, total number of case hospitalizations and number of critical cases to hospital data and case reports 


## Data sources
- IDPH
- NMH
- City of Chicago
- ...







