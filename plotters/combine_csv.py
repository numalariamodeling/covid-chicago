import os
import pandas as pd
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime
from processing_helpers import *
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

    Northwest, Northeast, Central, Southern = loadEMSregions()
    exp_suffix = ['reopening_May15', 'reopening_June1', 'reopening_June15', 'reopening_July1', 'scenario3','reopening_gradual', 'scenario2', 'reopening_gradual_ct80redinfect0', 'reopening_gradual_ct80', 'reopening_gradual_ct30']
    sim_scenarios_1 = [get_exp_name(x, 5, simdate) for x in Northwest] + [get_exp_name(x, 4, simdate) for x in Northeast] + [get_exp_name(x, 5, simdate) for x in Central] + [get_exp_name(x, 5, simdate) for x in Southern]
    sim_scenarios_2 = [get_exp_name(x, 4, simdate) for x in Northwest] + [get_exp_name(x, 4, simdate) for x in Northeast] + [get_exp_name(x, 5, simdate) for x in Central] + [get_exp_name(x, 5, simdate) for x in Southern]
    sim_scenarios_3 = [get_exp_name(x, 4, simdate) for x in Northwest] + [get_exp_name(x, 5, simdate) for x in Northeast] + [get_exp_name(x, 1, simdate) for x in Central] + [ get_exp_name(x, 5, simdate) for x in Southern]
    ### homogeneous scenario 2 or 3
    sim_scenarios_4 = [get_exp_name(x, 6, simdate) for x in Northwest] + [get_exp_name(x, 6, simdate) for x in Northeast] + [get_exp_name(x, 6, simdate) for x in Central] + [ get_exp_name(x, 6, simdate) for x in Southern]
    sim_scenarios_5 = [get_exp_name(x, 4, simdate) for x in Northwest] + [get_exp_name(x, 4, simdate) for x in Northeast] + [get_exp_name(x, 4, simdate) for x in Central] + [ get_exp_name(x, 4, simdate) for x in Southern]
    ### as in sim_scenarios_1 but with contact tracing
    sim_scenarios_6 = [get_exp_name(x, 7, simdate) for x in Northwest] + [get_exp_name(x, 4, simdate) for x in Northeast] + [get_exp_name(x, 7, simdate)  for x in Central] + [ get_exp_name(x, 7, simdate) for x in Southern]
    sim_scenarios_7 = [get_exp_name(x, 8, simdate) for x in Northwest] + [get_exp_name(x, 4, simdate) for x in Northeast] + [get_exp_name(x, 8, simdate)  for x in Central] + [ get_exp_name(x, 8, simdate) for x in Southern]
    sim_scenarios_8 = [get_exp_name(x, 9, simdate) for x in Northwest] + [get_exp_name(x, 4, simdate) for x in Northeast] + [get_exp_name(x, 9, simdate)  for x in Central] + [ get_exp_name(x, 9, simdate) for x in Southern]
    sim_scenarios_9 = [get_exp_name(x, 1, simdate) for x in Northwest] + [get_exp_name(x, 1, simdate) for x in Northeast] + [get_exp_name(x, 1, simdate)  for x in Central] + [get_exp_name(x, 1, simdate) for x in Southern]

    # Combine multiple mixed scenarios if required
    sim_scenarios = [sim_scenarios_1, sim_scenarios_2, sim_scenarios_3, sim_scenarios_4, sim_scenarios_5,  sim_scenarios_6, sim_scenarios_7, sim_scenarios_8, sim_scenarios_9]
    filenames = ['Trajectories_set1.csv', 'Trajectories_set2.csv', 'Trajectories_set3.csv', 'Trajectories_set4.csv', 'Trajectories_set5.csv', 'Trajectories_set6.csv', 'Trajectories_set7.csv', 'Trajectories_set8.csv', 'Trajectories_set9.csv']


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

