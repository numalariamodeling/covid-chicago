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

def exceeds(trajectory, metric, lower_limit, upper_limit, maximum):
    return (trajectory[metric].values[lower_limit:upper_limit] > maximum).any()

def when_exceeds(trajectory, metric, lower_limit, upper_limit, maximum):
    ii = lower_limit
    while trajectory[metric].values[ii] <= maximum:
        ii += 1
    return ii

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


def get_probs(exp_name,select_traces=True):

    fname = get_latest_filedate()
    civis_template = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'hospital_capacity_thresholds', fname))
    civis_template = civis_template.drop_duplicates()
    civis_template['date_window_upper_bound'] = pd.to_datetime(civis_template['date_window_upper_bound'])
    lower_limit = 170

    civis_template_all = pd.DataFrame()
    region_list = ['EMS-%d' % x for x in range(1, 12)]
    for ems_region in region_list:
        ems_nr = ems_region.replace("EMS-","")
        column_list = ['scen_num','sample_num','run_num','startdate','time']
        column_list.append('hosp_det_' + str(ems_region))
        column_list.append('crit_det_' + str(ems_region))

        df = load_sim_data(exp_name, region_suffix= f'_{ems_region}', column_list=column_list,add_incidence=False)
        df = df.dropna()
        df['total_hosp_census'] = df['hosp_det'] + df['crit_det']

        if select_traces:
            if os.path.exists(os.path.join(sim_output_path, f'traces_ranked_region_{str(ems_nr)}.csv')) :
                rank_export_df = pd.read_csv(os.path.join(sim_output_path, f'traces_ranked_region_{str(ems_nr)}.csv'))
                rank_export_df_sub = rank_export_df[0:int(len(rank_export_df) / 2)]
                df = df[df['scen_num'].isin(rank_export_df_sub.scen_num.unique())]

        unique_scen = np.array(list(set(df['scen_num'].values)))
        civis_template_sub = civis_template[civis_template['geography_modeled']==f'covidregion_{ems_nr}']

        for index, row in civis_template_sub.iterrows():
            upper_limit = (row['date_window_upper_bound'] - dt.datetime(month=2, day=13, year=2020)).days
            if row['resource_type'] == 'hb_availforcovid':
                metric_root = 'total_hosp_census'
            if row['resource_type'] == 'icu_availforcovid':
                metric_root = 'crit_det'
            elif row['resource_type'] == 'vent_availforcovid':
                metric_root = 'vent'
            thresh = row['avg_resource_available']
            prob = 0
            for scen in unique_scen:
                new = df[(df['scen_num'] == scen)].reset_index()
                if row['resource_type'] == 'vent_availforcovid':
                    new[metric_root] = get_vents(new['crit_det'])
                if exceeds(new, metric_root, lower_limit, upper_limit, thresh):
                    prob += 1/len(unique_scen)
            civis_template_sub.loc[index, 'percent_of_simulations_that_exceed'] = prob

        if civis_template_all.empty:
            civis_template_all = civis_template_sub
        else:
            civis_template_all = pd.concat([civis_template_all, civis_template_sub])

    civis_template_all['scenario_name'] = 'baseline'
    file_str = 'nu_hospitaloverflow_' + str(exp_name[:8]) + '.csv'
    civis_template_all.to_csv(os.path.join(sim_output_path, file_str), index=False)

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
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        print(exp_name)
        get_probs(exp_name)
        plot_probs(exp_name)
