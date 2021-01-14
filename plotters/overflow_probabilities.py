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

def get_latest_filedate(file_path=os.path.join(datapath, 'covid_IDPH', 'Corona virus reports',
                                               'hospital_capacity_thresholds'), extraThresholds=False):
    files = os.listdir(file_path)
    files = sorted(files, key=len)
    if extraThresholds == False:
        files = [name for name in files if not 'extra_thresholds' in name]
    if extraThresholds ==True:
        files = [name for name in files if 'extra_thresholds' in name]

    filedates = [item.replace('capacity_weekday_average_', '') for item in files]
    filedates = [item.replace('.csv', '') for item in filedates]
    latest_filedate = max( [int(x) for x in filedates])
    fname = f'capacity_weekday_average_{latest_filedate}.csv'
    if extraThresholds == True :
        fname = f'capacity_weekday_average_{latest_filedate}__extra_thresholds.csv'
    return fname


def get_probs(exp_name):    
    trajectories = load_sim_data(exp_name, column_list=column_list) #pd.read_csv('trajectoriesDat_200814_1.csv', usecols=column_list)
    trajectories = trajectories.dropna()
    fname = get_latest_filedate()
    civis_template = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'hospital_capacity_thresholds', fname))
    civis_template = civis_template.drop_duplicates()

    civis_template['date_window_upper_bound'] = pd.to_datetime(civis_template['date_window_upper_bound'])
    
    for ems_region in range(1,12):
        trajectories['total_hosp_census_EMS-' + str(ems_region)] = trajectories['hosp_det_EMS-'+str(ems_region)]+trajectories['crit_det_EMS-'+str(ems_region)]


    lower_limit = 170
    unique_scen = np.array(list(set(trajectories['scen_num'].values)))
    
    for index, row in civis_template.iterrows():
        upper_limit = (row['date_window_upper_bound'] - dt.datetime(month=2, day=13, year=2020)).days
        if row['resource_type'] == 'hb_availforcovid':
            metric_root = 'total_hosp_census_EMS-'
        if row['resource_type'] == 'icu_availforcovid':
            metric_root = 'crit_det_EMS-'
        elif row['resource_type'] == 'vent_availforcovid':
            metric_root = 'vent_EMS-'
        thresh = row['avg_resource_available']
        region = int(re.sub('[^0-9]','', row['geography_modeled']))
        prob = 0
        for scen in unique_scen:
            new = trajectories[(trajectories['scen_num'] == scen)].reset_index()
            if row['resource_type'] == 'vent_availforcovid':
                new[metric_root + str(region)] = get_vents(new['crit_det_EMS-' + str(region)])
            if exceeds(new, metric_root + str(region), lower_limit, upper_limit, thresh):
                prob += 1/len(unique_scen)
        civis_template.loc[index, 'percent_of_simulations_that_exceed'] = prob
        
    civis_template['scenario_name'] = 'baseline'
    file_str = 'nu_hospitaloverflow_' + str(exp_name[:8]) + '.csv'
    civis_template.to_csv(os.path.join(wdir, 'simulation_output', exp_name, file_str), index=False)

def plot_probs(exp_name, show_75=True) :
    simdate = str(exp_name[:8])
    file_str = 'nu_hospitaloverflow_' + simdate + '.csv'
    df = pd.read_csv(os.path.join(wdir, 'simulation_output', exp_name, file_str))
    df['date'] = pd.to_datetime(df['date_window_upper_bound'])
    df['date_md'] = df['date'].dt.strftime('%m-%d\n%Y')

    covidregionlist = list(df.geography_modeled.unique())

    fig = plt.figure(figsize=(14, 12))
    fig.subplots_adjust(right=0.98, wspace=0.4, left=0.1, hspace=0.4, top=0.88, bottom=0.07)
    palette = sns.color_palette('Set1', len(df.resource_type.unique()))
    axes = [fig.add_subplot(4, 3, x + 1) for x in range(len(covidregionlist))]

    for c, region_suffix in enumerate(covidregionlist) :
        region_label = region_suffix.replace('_', ' ')
        mdf = df[df['geography_modeled'] == region_suffix]
        ax = axes[c]
        ax.set_ylim(0, 1)
        ax.set_title(region_label)
        ax.set_ylabel(f'Probability of overflow')

        for e, t in enumerate(list(df.resource_type.unique())) :
            adf = mdf[mdf['resource_type'] == t]
            adf1 = adf[adf['overflow_threshold_percent']== 1]
            adf2 = adf[adf['overflow_threshold_percent']!= 1]
            ax.plot(adf1['date_md'], adf1['percent_of_simulations_that_exceed'], linestyle='-', color=palette[e], label=t)
            if show_75 :
                ax.plot(adf2['date_md'], adf2['percent_of_simulations_that_exceed'], linestyle='--', color=palette[e], label='', alpha=0.5)

    axes[-1].legend()

    plt.savefig(os.path.join(wdir, 'simulation_output', exp_name, '_plots','overflow_probabilities.png'))
    plt.savefig(os.path.join(wdir, 'simulation_output', exp_name, '_plots', 'pdf', 'overflow_probabilities.pdf'))


if __name__ == '__main__':
    stem = sys.argv[1]
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    for exp_name in exp_names:
        get_probs(exp_name)
        plot_probs(exp_name)
