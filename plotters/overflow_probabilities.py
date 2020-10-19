import os
import sys
sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
import numpy as np
import matplotlib.dates as mdates
import datetime
#sns.set(color_codes=True)
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42
import statistics as st
sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
from statsmodels.distributions.empirical_distribution import ECDF
import scipy
import gc
import sys
import re


datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()

def load_sim_data(exp_name, input_wdir=None, input_sim_output_path=None, column_list=None):
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'), usecols=column_list)
    return df


def exceeds(trajectory, metric, lower_limit, upper_limit, maximum):
    return (trajectory[metric].values[lower_limit:upper_limit] > maximum).any()

def when_exceeds(trajectory, metric, lower_limit, upper_limit, maximum):
    ii = lower_limit
    while trajectory[metric].values[ii] <= maximum:
        ii += 1
    return ii

column_list = ['scen_num',  'hosp_det_All', 'crit_det_All']  #'reopening_multiplier_4'
for ems_region in range(1,12):
    column_list.append('hosp_det_EMS-' + str(ems_region))
    column_list.append('crit_det_EMS-' + str(ems_region))
    #column_list.append('death_det_cumul_EMS-' + str(ems_region))

def get_latest_filedate(file_path=os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'hospital_capacity_thresholds')):
   files =  os.listdir(file_path)
   filedates = [item.replace('capacity_weekday_average_', '') for item in files]
   filedates = [item.replace('.csv', '') for item in filedates]
   latest_filedate = max( [int(x) for x in filedates])

   return latest_filedate


def get_probs(exp_name):    
    trajectories = load_sim_data(exp_name, column_list=column_list) #pd.read_csv('trajectoriesDat_200814_1.csv', usecols=column_list)
    filedate = get_latest_filedate()
    civis_template = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'hospital_capacity_thresholds', f'capacity_weekday_average_{filedate}.csv'))
    civis_template['date_window_upper_bound'] = pd.to_datetime(civis_template['date_window_upper_bound'])
    
    for ems_region in range(1,12):
        trajectories['total_hosp_census_EMS-' + str(ems_region)] = trajectories['hosp_det_EMS-'+str(ems_region)]+trajectories['crit_det_EMS-'+str(ems_region)]


    lower_limit = 170
    unique_scen = np.array(list(set(trajectories['scen_num'].values)))
    
    for index, row in civis_template.iterrows():
        upper_limit = (row['date_window_upper_bound'] - dt.datetime(month=2, day=13, year=2020)).days
        if row['resource_type'] == 'hb_availforcovid':
            metric_root = 'total_hosp_census_EMS-'
        elif row['resource_type'] == 'icu_availforcovid':
            metric_root = 'crit_det_EMS-'
        thresh = row['avg_resource_available']
        region = int(re.sub('[^0-9]','', row['geography_modeled']))
        prob = 0
        for scen in unique_scen:
            new = trajectories[(trajectories['scen_num'] == scen)].reset_index()
            if exceeds(new, metric_root + str(region), lower_limit, upper_limit, thresh):
                prob += 1/len(unique_scen)
        civis_template.loc[index, 'percent_of_simulations_that_exceed'] = prob
        
    civis_template['scenario_name'] = 'baseline'
    file_str = 'nu_hospitaloverflow_' + str(exp_name[:8]) + '.csv'
    civis_template.to_csv(os.path.join(wdir, 'simulation_output', exp_name, file_str), index=False)

    
if __name__ == '__main__':
    stem = sys.argv[1]
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    for exp_name in exp_names:
        get_probs(exp_name)
