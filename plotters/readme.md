
### Plotters  - Visualization and analysis of model outcomes and input data


#### Compare simulations to data 
- [data_comparison.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/data_comparison.py) 
compares the predicted number of new detected hospitalized cases, cumulative detections of hospitalized cases, total number of case hospitalizations and number of critical cases to hospital data and case reports.  

- [data_comparison_spatial.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/data_comparison_spatial.py) 

#### Comparison multiple simulation experiments 
- [plot_split_by_param](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_split_by_param.py)
Takes two experiment simulations and compares generates a plot comparing the trajectories of both

- [scenario_comparison.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/scenario_comparison.py)
Similar to [plot_split_by_param](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_split_by_param.py), but takes multiple scenarios from a subfolder.
Can be modified with improved analysis and comparison of varing scenarios (per EMS or combined). 

- [combine_csv.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/combine_csv.py)
Reads in trajectoriesDat from several simulation experiments and appends the dataframe without aggregating them. 



#### Stacked and grouped timeline plots
- [EMS_combo_plotter.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/EMS_combo_plotter.py)
Generates a plot showing the trajectories for all EMS together.

- [locale_age_postprocessing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/locale_age_postprocessing.py)


#### Generate "process-for-civis-like" timelines for selected channels
-  [process_for_civis.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/process_for_civis.py)
The stem argument allows to process only experiments that contain this string in the name.
`python plotters/process_for_civis.py --stem 'test'`


#### Process-for-civis scripts that generate custom outputs in the format requested by civis
- [combine_process_for_civis_csv.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/combine_process_for_civis_csv.py)
Reads in several EMS specific simulation experiments and sums the trajectores to be representative for the total area.

- [add_ems_to_IL.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/add_ems_to_IL.py)


#### rocess-for-civis scripts that generate custom outputs in the format requested by civis - using EMS grouped model 
-  [process_for_civis_EMSgrp.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/process_for_civis_EMSgrp.py)


#### Further scripts 
- county_estimation.py
- generate_trajectories_for_dash.py
- Ki_map.py and  ki_red_map.py
- scenario_sets.py and mixed_reopening_scenarios.py
- safegrafe_awaytime_map.py



