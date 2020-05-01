import os
import pandas as pd
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime
from processing_helpers import *
from data_comparison import load_sim_data

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

input_dir = os.path.join(wdir, 'simulation_output/')
output_dir = os.path.join(projectpath,'NU_civis_outputs','20200429','trajectories')

for scen in ['scenario1', 'scenario2', 'scenario3']:
    stem = scen
    exp_names = [x for x in os.listdir(input_dir) if stem in x]

    adf = pd.DataFrame()
    for d, exp_name in enumerate(exp_names):

        sim_output_path = os.path.join(input_dir, exp_name)
        ems = int(exp_name.split('_')[2])
        df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat_test.csv'))

        first_day = datetime.strptime(df['first_day'].unique()[0], '%Y-%m-%d')

        df['ems'] = ems
        df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))

        df = df.groupby(['ems','date','time','sample_num','scen_num']).agg(np.mean).reset_index()

        adf = pd.concat([adf, df])

    if scen == 'scenario1' :
        filename = 'Trajectories_endsip.csv'
    if scen == 'scenario2':
        filename = 'Trajectories_neversip.csv'
    if scen == 'scenario3':
        filename = 'Trajectories_baseline.csv'

    adf.to_csv(os.path.join(output_dir, filename), index=False)

