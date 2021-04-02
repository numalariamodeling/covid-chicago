
### Plotters  - Visualization and analysis of model outcomes and input
List and description of main scripts used.

#### Compare simulations to data 
- [data_comparison.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/data_comparison.py) 
compares the predicted number of new detected hospitalized cases, cumulative detections of hospitalized cases, total number of case hospitalizations and number of critical cases to hospital data and case reports for specified EMS region as included in exp_name (using base or age emodl)
- [data_comparison_spatial.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/data_comparison_spatial.py) 
compares the predicted number of new detected hospitalized cases, cumulative detections of hospitalized cases, total number of case hospitalizations and number of critical cases to hospital data and case reports for all EMS regions (using locale emodl) 
- [data_comparison_spatial2.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/data_comparison_spatial2.py) 
same as data_comparison_spatial.py, for comparing two or more experiments (runs slow)
- [data_comparison_spatial3.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/data_comparison_spatial3.py) 
same as data_comparison_spatial.py, for plotting trends by a specified paramter

#### Comparison multiple simulation experiments 
- [plot_split_by_param](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_split_by_param.py)
Takes two experiment simulations and compares generates a plot comparing the trajectories of both
- [plot_by_param_ICU_nonICU](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_by_param_ICU_nonICU.py)
Plots the most recent trend in EMresource data for ICU and non-ICU and compares the next 2-3 weeks forward predictions, either with one or two exp_names
- [plot_exp_by_varying_param.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_exp_by_varying_param.py)
Plot to show trends by varying sample parameter (i.e. for intervention scenarios) within one simulation.
- [bar_timeline_plotter.py](https://github.com/numalariamodeling/covid-chicago/blob/master/data_plotters/bar_timeline_plotter.py)
Often used for civis slides, generates timeline comparing outcome channelf across multiple simulation experiments and cumulative barplot

### Compare parameter or channels within one simulation experiment
- [aggregate_by_param.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/aggregate_by_param.py)
Aggregate custom specified channels by defined parameter and generate plot for 1 channel across all groups compared by that parameter. Saved a csv with aggregated trajectores (large if too many channels selected!)
- [plot_split_by_param_trajectories](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_split_by_param_trajectories.py)
Simple plot per outcome channel for one experiment, instead of aggregating trajectories, show single trajectories
- [plot_split_by_channel](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_split_by_channel.py)
Plotter for comparing 2 channels in one panel for example used to plot vaccinations or detections (i.e. all vs detected, all vs vaccinated ...)
- [plot_single_trajectories.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_single_trajectories.py)


#### Stacked and grouped timeline plots
- [EMS_combo_plotter.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/EMS_combo_plotter.py)
Generates a plot showing the trajectories for all EMS together.
- [locale_age_postprocessing.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/locale_age_postprocessing.py)
Generates a plot showing the trajectories for any group, either EMS or Age, separate plots per group and stacked plot. 


#### Process-for-civis scripts
(see description in main readme)
- [trace_selection.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/trace_selection.py) calculating the negative log-likelihood per simulated trajectory, used for thinning predictions and parameter estimation (see paragraph below)
- [data_comparison_spatial.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/data_comparison_spatial.py) comparing model predictions to data per region over time
- [process_for_civis_EMSgrp.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/process_for_civis_EMSgrp.py) generates the result csv dataframe (i.e. nu_20201005.csv) and generates descriptive trajectories per channel and region
- [estimate_Rt_forCivisOutputs.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/estimate_Rt_forCivisOutputs.py)  that  runs the Rt estimation, the Rt columns are added to the result csv dataframe (i.e. nu_20201005.csv), produces descriptive plots
- [overflow_probabilities.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/overflow_probabilities.py) calculates the probability of hospital overflow and produces the  (i.e. nu_hospitaloverflow_20201005.csv), also adds total number of beds [additional script](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/overflow_numbers.py)
- [plot_prevalence.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_prevalence.py)
- [plot_by_param_ICU_nonICU.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/plot_by_param_ICU_nonICU.py)
- [hosp_icu_deaths_forecast_plotter.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/hosp_icu_deaths_forecast_plotter.py)
- [NUcivis_filecopy.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/NUcivis_filecopy.py) that generates the NU_civis_outputs subfolder and copies all relevant files and adds the changelog.txt. Note: the changelog.txt will need manual editing to reflect new changes per week. 
- [iteration_comparison.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/iteration_comparison.py) that  generates the iteration comparison plot (last 3 weeks)

#### Parameter fitting and selection of best fitting trajectories 
Building on [trace_selection.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/trace_selection.py), which ranks the simulated trajectories based on negative log-likelihood , the 
 [simulate_traces.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/simulate_traces.py) script extracts the a) single best fitting parameter set or b) n best fitting parameter sets, 
 and combines these now region specific fitted parameters with sample parameters. Next to the csv files the script generates bat/sh submission script to run a follow up simulation with fitted parameters. 
The script also uses functions from [sample_parameters.py](https://github.com/numalariamodeling/covid-chicago/blob/master/sample_parameters.py).

#### Further scripts 
- [extract_sample_param.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/extract_sample_param.py) 
Extract and visualize sample parameters that successfully ran in a simulation. Can be used to generate csv files that can be used as inpput in another simulation.
- [emresource_cli_per_covidregion.py](https://github.com/numalariamodeling/covid-chicago/blob/master/data_plotters/emresource_cli_per_covidregion.py) (data_plotters folder)
- [bar_plotter.py](https://github.com/numalariamodeling/covid-chicago/blob/master/data_plotters/bar_plotter.py)
Note: extended version in [bar_timeline_plotter.py](https://github.com/numalariamodeling/covid-chicago/blob/master/data_plotters/bar_timeline_plotter.py)
- [Ki_plotter.py](https://github.com/numalariamodeling/covid-chicago/blob/master/plotters/Ki_plotter.py)



