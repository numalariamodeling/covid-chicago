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

mpl.rcParams['pdf.fonttype'] = 42
today = dt.datetime.today()
#datetoday = date(today.year, today.month, today.day)
from processing_helpers import *

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()

def load_sim_data(exp_name, input_wdir=None, input_sim_output_path=None, column_list=None):
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'), usecols=column_list)
    return df

first_date = dt.datetime(day=6,month=9,year=2020)
column_list = ['scen_num', 'run_num', 'campus_quarantine_pop', 'campus_isolation_pop', 'detection_rate_official']  #'reopening_multiplier_4'

def get_probs(exp_name):    
    trajectories = load_sim_data(exp_name, column_list=column_list) #pd.read_csv('trajectoriesDat_200814_1.csv', usecols=column_list)
    #filedate = get_latest_filedate()
    qi_path=os.path.join(datapath, 'covid_modeling_northwestern', '201014_QI_tracking.csv')
    qi = pd.read_csv(qi_path)
    tests = pd.read_csv(os.path.join(datapath, 'covid_modeling_northwestern', 'Depersonalized_Test_Result.csv'))

    idx1 = pd.date_range(first_date, pd.to_datetime(np.max(tests['ORDER_DATE'])))

    tests_campus_pos = tests[(tests['LAB_VENDOR'] == 'Tempus') & (tests['UNDERGRAD_FLAG'] == 'Undergrad') & (tests['RESULT'] == 'DETECTED')]
    positive_daily = tests_campus_pos.groupby('ORDER_DATE').agg({'ORDER_ID': pd.Series.nunique})
    positive_daily['specimen_date'] = pd.to_datetime(positive_daily.index)
    positive_daily = positive_daily.set_index(['specimen_date']).reindex(idx1).fillna(0).reset_index()
    positive_daily['specimen_date'] = positive_daily['index']
    #qi = pd.read_csv('201014_QI_tracking.csv')
    qi['date'] = [dt.datetime.strptime(d, '%m/%d').replace(year=2020) for d in qi['Primary Column'].values]

    unique_runs = trajectories.drop_duplicates(subset=['scen_num', 'run_num'])[['scen_num', 'run_num']]
    scen_num, run_num = unique_runs['scen_num'].values, unique_runs['run_num'].values
    traj = []
    channel = 'detection_rate_official'
    for scen, run in zip(scen_num, run_num):
        new = trajectories[(trajectories['scen_num'] == scen) & (trajectories['run_num'] == run)]
        if len(new) > 0:
            traj.append(new[channel].values)
        
    p5 = np.percentile(traj, 2.5, axis=0)
    p25= np.percentile(traj, 25, axis=0)
    med = np.median(traj, axis=0)
    p75= np.percentile(traj, 75, axis=0)
    p95 = np.percentile(traj, 97.5, axis=0)

    #first_date = dt.datetime(day=6,month=9,year=2020)
    idx = pd.date_range(first_date, first_date+dt.timedelta(days=len(p5)))

    fig = plt.figure(figsize=(10,3))
    fig.add_subplot(131)
    first = 0
    last = 150
    plt.plot(idx[first:last], med[first:last], color=sns.color_palette()[3], label='low transmission')
    plt.fill_between(x = idx[first:last], y1 = p5[first:last], y2 = p95[first:last], color=sns.color_palette()[3], alpha=0.25, linewidth=0)
    plt.fill_between(x = idx[first:last], y1 = p25[first:last], y2 = p75[first:last], color=sns.color_palette()[3], alpha=0.25, linewidth=0)
    plt.scatter(x=positive_daily['specimen_date'], y=positive_daily['ORDER_ID'], c='k')
    plt.plot(positive_daily['specimen_date'], positive_daily['ORDER_ID'].rolling(window=7, center=True).mean(), c='k')
    plt.xlim([dt.datetime(day=1,month=9,year=2020), dt.datetime.today()])
    ax = plt.gca()
    formatter = mdates.DateFormatter("%b")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(formatter)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylabel('Daily Positive Tests',fontsize=14)

    traj = []
    channel = 'campus_isolation_pop'
    for scen, run in zip(scen_num, run_num):
        new = trajectories[(trajectories['scen_num'] == scen) & (trajectories['run_num'] == run)]
        if len(new) > 0:
            traj.append(new[channel].values)
        
    p5 = np.percentile(traj, 2.5, axis=0)
    p25= np.percentile(traj, 25, axis=0)
    med = np.median(traj, axis=0)
    p75= np.percentile(traj, 75, axis=0)
    p95 = np.percentile(traj, 97.5, axis=0)

    fig.add_subplot(132)
    first = 0
    last = 150
    plt.plot(idx[first:last], med[first:last], color=sns.color_palette()[3], label='low transmission')
    plt.fill_between(x = idx[first:last], y1 = p5[first:last], y2 = p95[first:last], color=sns.color_palette()[3], alpha=0.25, linewidth=0)
    plt.fill_between(x = idx[first:last], y1 = p25[first:last], y2 = p75[first:last], color=sns.color_palette()[3], alpha=0.25, linewidth=0)
    plt.scatter(x=qi['date'], y=qi['Total students in isolation'], c='k')
    plt.xlim([dt.datetime(day=1,month=9,year=2020), dt.datetime.today()])
    ax = plt.gca()
    formatter = mdates.DateFormatter("%b")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(formatter)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylabel('Isolation Population',fontsize=14)

    traj = []
    channel = 'campus_quarantine_pop'
    for scen, run in zip(scen_num, run_num):
        new = trajectories[(trajectories['scen_num'] == scen) & (trajectories['run_num'] == run)]
        if len(new) > 0:
            traj.append(new[channel].values)
        
    p5 = np.percentile(traj, 2.5, axis=0)
    p25= np.percentile(traj, 25, axis=0)
    med = np.median(traj, axis=0)
    p75= np.percentile(traj, 75, axis=0)
    p95 = np.percentile(traj, 97.5, axis=0)

    fig.add_subplot(133)
    first = 0
    last = 150
    plt.plot(idx[first:last], med[first:last], color=sns.color_palette()[3], label='low transmission')
    plt.fill_between(x = idx[first:last], y1 = p5[first:last], y2 = p95[first:last], color=sns.color_palette()[3], alpha=0.25, linewidth=0)
    plt.fill_between(x = idx[first:last], y1 = p25[first:last], y2 = p75[first:last], color=sns.color_palette()[3], alpha=0.25, linewidth=0)
    plt.scatter(x=qi['date'], y=qi['Total students in quarantine'], c='k')
    plt.xlim([dt.datetime(day=1,month=9,year=2020), dt.datetime.today()])
    ax = plt.gca()
    formatter = mdates.DateFormatter("%b")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(formatter)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.ylabel('Quarantine Population',fontsize=14)
    fig.tight_layout()
    plt.savefig(os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data.png'), dpi=200, bbox_inches='tight')
    #civis_template.to_csv(os.path.join(wdir, 'simulation_output', exp_name, file_str), index=False)

    
if __name__ == '__main__':
    stem = sys.argv[1]
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    for exp_name in exp_names:
        get_probs(exp_name)
