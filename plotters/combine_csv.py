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

    adf = pd.DataFrame()
    for d, exp_name in enumerate(exp_names):

        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        ems = int(exp_name.split('_')[2])
        df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))

        first_day = datetime.strptime(cdf['first_day'].unique()[0], '%Y-%m-%d')

        df['ems'] = ems
        df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
        adf = pd.concat([adf, df])

    if scen == 'scenario1' :
        filename = 'EMS_trajectories_separate_endsip_20200419.csv'
    if scen == 'scenario2':
        filename = 'EMS_trajectories_neversip_20200419.csv'
    if scen == 'scenario3':
        filename = 'EMS_trajectories_baseline_20200419.csv'

    adf.to_csv(os.path.join(wdir,'simulation_output/_csv', filename), index=False)
