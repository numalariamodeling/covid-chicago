import os
import pandas as pd
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime
from processing_helpers import *
from scenario_sets import *
from data_comparison import load_sim_data

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

mixed_scenarios = True
simdate = "20200506"
output_dir = os.path.join(projectpath, 'NU_civis_outputs', simdate, 'trajectories')

if mixed_scenarios == False :
    input_dir = os.path.join(wdir, 'simulation_output')
    stem = 'scenario3'
    sim_scenarios = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

if mixed_scenarios == True :
    input_dir = os.path.join(wdir, 'simulation_output', simdate + '_mixed_reopening', 'simulations')
    sim_scenarios, sim_label, intervention_label = def_scenario_set(simdate)
    nsets = len(sim_scenarios)
    filenames = []
    for i in range(1, nsets) :
        filenames = filenames + ['Trajectories_set' + str(i) + '.csv']

for num, exp_names in enumerate(sim_scenarios):

    adf = pd.DataFrame()
    for d, exp_name in enumerate(exp_names):

        sim_output_path = os.path.join(input_dir, exp_name)
        ems = int(exp_name.split('_')[2])
        df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))

        first_day = datetime.strptime(df['first_day'].unique()[0], '%Y-%m-%d')

        df['ems'] = ems
        df['exp_name'] = exp_name
        df['scenario'] = exp_name.split("_")[-1]
        df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
        del df['Unnamed: 0']
        df = df.groupby(['ems','date','time','sample_num','scen_num','exp_name','scenario']).agg(np.mean).reset_index()

        adf = pd.concat([adf, df])

    filename = filenames[num]

    adf.to_csv(os.path.join(output_dir, filename), index=False)

