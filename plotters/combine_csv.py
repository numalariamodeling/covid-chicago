import os
import pandas as pd
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime
from processing_helpers import *
from simulation_setup import *
from data_comparison import load_sim_data

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()


for scen in ['scenario1', 'scenario2', 'scenario3']:
    stem = scen
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    channels = ['date', 'infected_median', 'infected_95CI_lower', 'infected_95CI_upper', 'deaths_median', 'deaths_95CI_lower',
                'deaths_95CI_upper', 'hospitalized_median', 'hospitalized_95CI_lower', 'critical_median', 'critical_95CI_lower',
                'critical_95CI_upper','ventilators_median','ventilators_95CI_lower', 'ventilators_95CI_upper']


    adf = pd.DataFrame()
    for d, exp_name in enumerate(exp_names):

        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        ems = int(exp_name.split('_')[2])
        df = pd.read_csv(os.path.join(sim_output_path, 'projection_for_civis.csv'))
        df['ems'] = ems
        adf = pd.concat([adf, df[channels + ['ems']]])

    if scen == 'scenario1' :
        filename = 'nu_EMS_endsip_20200418.csv'
    if scen == 'scenario2':
        filename = 'nu_EMS_baseline_20200418.csv'
    if scen == 'scenario3':
        filename = 'nu_EMS_neversip_20200418.csv'

    adf.to_csv(os.path.join(wdir,'simulation_output/_csv', filename), index=False)
