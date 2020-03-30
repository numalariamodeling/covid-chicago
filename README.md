# covid-chicago

- SEIR model using Institute for Disease Modeling (IDM's) [Compartmental Modeling Software (CMS)](https://idmod.org/docs/cms/index.html)

## CMS software
- [input](https://idmod.org/docs/cms/input-files.html) configuration file (cfg)
- [input](https://idmod.org/docs/cms/input-files.html)  model file (emodl)
- [output](https://idmod.org/docs/cms/output.html?searchText=output): trajectories.csv (optionally define prefix or suffix)

## Model types
### Simple SEIR model
The "simplemodel" includes only the basic S-E-I-R compartments. 

### Extended SEIR model
The "extendedmodel" imclides additional compartments for asymptomatics, symptomatics, hospitalization, progression to critical and deaths. In addition the detections are tracked as a sum of detected asymptomatics, symptomatics,hospitalized, critical and deaths with group specific detection rates. 

### Age model 
The "age_model" duplicates each compartment of the simple or the extended model for n age groups. To allow the age groups to get in contact with each other at different rates, the Ki (contact rate * probability of transmission) needs to be specified for a all age-combinations. In the format of:

- (reaction exposure1   (S1) (E1) (sum(* Ki1.1 S1  I1 ) (* Ki1.2 S1  I2) (* Ki1.3 S1  I3) ))
- (reaction exposure2   (S2) (E2) (sum (* Ki2.1 S2  I1 ) (* Ki2.2 S2  I2) (* Ki2.3 S2  I3) ))
- (reaction exposure3   (S3) (E3) (sum (* Ki3.1 S3  I1 ) (* Ki3.2 S3  I2) (* Ki3.3 S3  I3) ) )

(where Ki1.2 == Ki2.1  etc) 

### Spatial model 
The "spatial_model" uses a special syntax as described [here](https://idmod.org/docs/cms/create-spatial-model.html?searchText=spatial). 

## Running simulations

### Run single simulations
To run a single simulation is useful to test changes in the emodl syntax and to rule out technical issues.
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
- postprocessing for simple SEIR model [basic_output_processing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/basic_output_processing.py)
- latest postprocessing file that calculates incidences for extended SEIR model [extended_model_postprocessing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/extended_model_postprocessing.py)

## Fitting to data
[in process]

