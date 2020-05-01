
### Plotters  - Visualization and exporting of model outcomes

-  [process_for_civis.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/process_for_civis.py)
The stem argument allows to process only experiments that contain this string in the name.
`python plotters/process_for_civis.py --stem 'test'`

- [extended_model_postprocessing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/archive_not_used/extended_model_postprocessing.py) (deprecated)
Postprocessing file that calculates incidences for extended SEIR model 

- [data_comparison.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/data_comparison.py) 
compares the predicted number of new detected hospitalized cases, cumulative detections of hospitalized cases, total number of case hospitalizations and number of critical cases to hospital data and case reports.  

- [plot_split_by_param](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_split_by_param.py)
Takes two experiment simulations and compares generates a plot comparing the trajectories of both

- [combineEMS_process_for_civis.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/combineEMS_process_for_civis.py)
Reads in several EMS specific simulation experiments and sums the trajectores to be representative for the total area.
Initially designed to produce one trajectoriesDat for IL for 3 defined scenarios.

- [combine_csv.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/combine_csv.py)
Reads in trajectoriesDat from several simulation experiments and appends the dataframe without aggregating them. 

- [EMS_combo_plotter.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/EMS_combo_plotter.py)
Generates a plot showing the trajectories for all EMS together.

