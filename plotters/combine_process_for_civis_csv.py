import os
import pandas as pd
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime
from processing_helpers import *
from data_comparison import load_sim_data

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
today = datetime.today()

mixed_scenarios = True
simdate = "20200506"
plot_first_day = date(2020, 3, 1)
plot_last_day = date(2020, 8, 1)
channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']

if mixed_scenarios == False:
    sim_path = os.path.join(wdir, 'simulation_output')
    plotdir = os.path.join(sim_path, '_plots')
    out_dir = os.path.join(projectpath, 'NU_civis_outputs', today.strftime('%Y%m%d'), 'csv')

    plot_name = simdate + '_' + stem + '_test'
    sim_scenarios_1 =  [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if 'scenario1' in x]
    sim_scenarios_2 = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if 'scenario2' in x]
    sim_scenarios_3 =  [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if 'scenario3' in x]
    #sim_scenarios = sim_scenarios[2:] + sim_scenarios[:2]  ## workaround to get right order 1-11
    sim_scenarios = [sim_scenarios_1, sim_scenarios_2, sim_scenarios_3]
    filenames = [ 'nu_ems_endsip_'+ simdate +'.csv' ,  'nu_ems_neversip_'+ simdate +'.csv' ,  'nu_ems_baseline_'+ simdate +'.csv'  ]

if mixed_scenarios == True:
    sim_path = os.path.join(wdir, 'simulation_output', simdate + '_mixed_reopening', 'simulations')
    plotdir = os.path.join(wdir, 'simulation_output', simdate + '_mixed_reopening', 'plots')
    out_dir = os.path.join(wdir, 'simulation_output', simdate + '_mixed_reopening',  'csv')

    Northwest, Northeast, Central, Southern = loadEMSregions()
    exp_suffix = ['reopening_May15', 'reopening_June1', 'reopening_June15', 'reopening_July1', 'scenario3','reopening_gradual']
    sim_scenarios_1 = [get_exp_name(x, 1, simdate) for x in Northwest] + [get_exp_name(x, 2, simdate) for x in  Central] + [get_exp_name(x, 1, simdate) for x   in Northeast] + [ get_exp_name(x, 3, simdate) for x in Southern]
    sim_scenarios_2 = [get_exp_name(x, 5, simdate) for x in Northwest] + [get_exp_name(x, 5, simdate) for x in  Central] + [get_exp_name(x, 5, simdate) for x in Northeast] + [ get_exp_name(x, 5, simdate) for x in Southern]
    sim_scenarios_3 = [get_exp_name(x, 5, simdate) for x in Northwest] + [get_exp_name(x, 5, simdate) for x in  Central] + [get_exp_name(x, 5, simdate) for x in Northeast] + [ get_exp_name(x, 5, simdate) for x in Southern]
    # Combine multiple mixed scenarios if required
    sim_scenarios = [sim_scenarios_1, sim_scenarios_2, sim_scenarios_3]
    filenames = ['nu_ems_set1.csv', 'nu_ems_set2.csv', 'nu_ems_set3.csv']

for num, exp_names in enumerate(sim_scenarios):
#for scen in ['scenario1', 'scenario2', 'scenario3']:
#    stem = scen
#    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    adf = pd.DataFrame()
    for d, exp_name in enumerate(exp_names):

        sim_output_path = os.path.join(sim_path, exp_name)
        ems = int(exp_name.split('_')[2])
        df = pd.read_csv(os.path.join(sim_output_path, 'projection_for_civis.csv'))

        #first_day = datetime.strptime(df['first_day'].unique()[0], '%Y-%m-%d')
        df = df.rename(columns={"date": "Date",
                       "infected_median": "Number of Covid-19 infections",
                       "infected_95CI_lower": "Lower error bound of covid-19 infections",
                       "infected_95CI_upper": "Upper error bound of covid-19 infections",
                       "new_symptomatic_median": "Number of Covid-19 symptomatic",
                       "new_symptomatic_95CI_lower": "Lower error bound of covid-19 symptomatic",
                       "new_symptomatic_95CI_upper": "Upper error bound of covid-19 symptomatic",
                       "new_deaths_median": "Number of covid-19 deaths",
                       "new_deaths_95CI_lower": "Lower error bound of covid-19 deaths",
                       "new_deaths_95CI_upper": "Upper error bound of covid-19 deaths",
                       "hospitalized_median": "Number of hospital beds occupied",
                       "hospitalized_95CI_lower": "Lower error bound of number of hospital beds occupied",
                       "hospitalized_95CI_upper": "Upper error bound of number of hospital beds occupied",
                       "critical_median": "Number of ICU beds occupied",
                       "critical_95CI_lower": "Lower error bound of number of ICU beds occupied",
                       "critical_95CI_upper": "Upper error bound of number of ICU beds occupied",
                       "ventilators_median": "Number of ventilators used",
                       "ventilators_95CI_lower": "Lower error bound of number of ventilators used",
                       "ventilators_95CI_upper": "Upper error bound of number of ventilators used"})

        df['ems'] = ems
        df['Date'] = pd.to_datetime(df['Date'])

        plot_first_day = pd.to_datetime('2020/3/13')
        plot_last_day = pd.to_datetime('2020/8/1')
        df = df[(df['Date'] >= plot_first_day) & (df['Date'] <= plot_last_day)]

        adf = pd.concat([adf, df])

        filename = filenames[num]

    adf.to_csv(os.path.join(out_dir, filename), index=False)
