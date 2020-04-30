import os
import pandas as pd
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime
from processing_helpers import *
#from data_comparison import load_sim_data

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def load_sim_data(exp_name, input_wdir=None) :
    input_wdir = input_wdir or wdir
    sim_output_path = os.path.join(input_wdir,'simulation_output/EMS/20200429_scenarios/', exp_name)
    scen_df = pd.read_csv(os.path.join(sim_output_path, 'scenarios.csv'))

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat_test.csv'))
    if 'Ki' not in df.columns.values :
        df = pd.merge(left=df, right=scen_df[['scen_num', 'Ki']], on='scen_num', how='left')

    df = calculate_incidence(df)

    return df


for scen in ['scenario1', 'scenario2', 'scenario3']:
    stem = scen
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output/EMS/20200429_scenarios/')) if stem in x]

    adf = pd.DataFrame()
    for d, exp_name in enumerate(exp_names):

        sim_output_path = os.path.join(wdir, 'simulation_output/EMS/20200429_scenarios/', exp_name)
        ems = int(exp_name.split('_')[2])
        df = pd.read_csv(os.path.join(sim_output_path, 'projection_for_civis.csv'))

        #first_day = datetime.strptime(df['first_day'].unique()[0], '%Y-%m-%d')
        df = df.rename(columns={"date": "Date",
                       "infected_median": "Number of Covid-19 infections",
                       "infected_95CI_lower": "Lower error bound of covid-19 infections",
                       "infected_95CI_upper": "Upper error bound of covid-19 infections",
                       "new_deaths_median": "Number of new covid-19 deaths",
                       "new_deaths_95CI_lower": "Lower error bound of new covid-19 deaths",
                       "new_deaths_95CI_upper": "Upper error bound of new covid-19 deaths",
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

        plot_first_day = pd.to_datetime('2020/3/13')
        plot_last_day = pd.to_datetime('2020/8/1')
        df = df[(df['date'] >= plot_first_day) & (df['date'] <= plot_last_day)]

        adf = pd.concat([adf, df])

    if scen == 'scenario1' :
        filename = 'nu_ems_endsip_20200429.csv'
    if scen == 'scenario2':
        filename = 'nu_ems_neversip_20200429.csv'
    if scen == 'scenario3':
        filename = 'nu_ems_baseline_20200429.csv'

    adf.to_csv(os.path.join(projectpath,'NU_civis_outputs/20200429/csv/', filename), index=False)
