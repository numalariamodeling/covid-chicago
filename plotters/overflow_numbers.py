import os
import sys
sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.dates as mdates
import datetime
from datetime import date, timedelta
# sns.set(color_codes=True)
import matplotlib as mpl

mpl.rcParams['pdf.fonttype'] = 42

sns.set_style('whitegrid', {'axes.linewidth': 0.5})
datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()


def load_sim_data(exp_name, input_wdir=None, input_sim_output_path=None):
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df = pd.read_csv(os.path.join(sim_output_path, f'nu_{str(exp_name[:8])}.csv'))
    return df


def get_latest_filedate(file_path=os.path.join(datapath, 'covid_IDPH', 'Corona virus reports',
                                               'hospital_capacity_thresholds'), extraThresholds=False):
    files = os.listdir(file_path)
    files = sorted(files, key=len)
    if extraThresholds == False:
        files = [name for name in files if not 'extra_thresholds' in name]
    if extraThresholds == True:
        files = [name for name in files if 'extra_thresholds' in name]

    filedates = [item.replace('capacity_weekday_average_', '') for item in files]
    filedates = [item.replace('.csv', '') for item in filedates]
    latest_filedate = max([int(x) for x in filedates])
    fname = f'capacity_weekday_average_{latest_filedate}.csv'
    if extraThresholds == True:
        fname = f'capacity_weekday_average_{latest_filedate}__extra_thresholds.csv'
    return fname

def get_plot(selected_resource_type='hb_availforcovid', errorbars=True):
    #from plotnine import ggplot, geom_point, aes, stat_smooth, facet_wrap
    fig = plt.figure(figsize=(10, 10))
    fig.tight_layout()
    selected_resource_type_label ="Number of available ICU beds for COVID-19 patients"

    if selected_resource_type == 'hb_availforcovid':
        selected_resource_type_label ="Number of available hospital beds for COVID-19 patients"

    fig.suptitle(selected_resource_type_label, y=1, fontsize=14)
    fig.subplots_adjust(top=0.88)
    fig.subplots_adjust(right=0.97, wspace=0.5, left=0.1, hspace=0.9, top=0.95, bottom=0.07)
    #palette = sns.color_palette('Set1', 11)
    axes = [fig.add_subplot(4, 2, x + 1) for x in range(len(civis_template['date_window_upper_bound'].unique()))]

    for c, upper_limit in enumerate(civis_template['date_window_upper_bound'].unique()):
        mdf = civis_template
        mdf = mdf[(mdf['date_window_upper_bound'] == upper_limit)].reset_index()
        mdf = mdf[(mdf['resource_type'] == selected_resource_type)].reset_index()
        mdf['region'] = mdf['geography_modeled'].replace(regex=r'covidregion_', value=' ')
        mdf['myerr'] = mdf['number_that_exceed_upper'] - mdf['number_that_exceed_lower']

        mdf_1 = mdf[(mdf['overflow_threshold_percent'] == 1.00)]
        mdf_1b = mdf_1[(mdf_1['number_that_exceed_median'] < 0)]
        mdf_2 = mdf[(mdf['overflow_threshold_percent'] == 0.75)]
        mdf_2b = mdf_2[(mdf_2['number_that_exceed_median'] < 0)]

        ax = axes[c]
        upper_limit = pd.to_datetime(upper_limit)
        upper_limit = date(upper_limit.year ,upper_limit.month,upper_limit.day)

        ax.set_title(upper_limit, y=0.85)
        ax.set_xlabel('Covid regions')
        ax.set_ylabel('Number of beds available')
        ax.axhline(y=0, xmin=0, xmax=12, linewidth=0.8, color='black')
        #ax.bar(mdf_1['region'], mdf_1['number_that_exceed_median'], 1, label='1')

        if errorbars:
            ax.bar(mdf_2['region'], mdf_2['number_that_exceed_median'], 1, yerr=mdf_2['myerr'], label='0.75',
                   linewidth=1)
            ax.bar(mdf_2b['region'], mdf_2b['number_that_exceed_median'], 1, color='red', yerr=mdf_2b['myerr'],
                   label='0.75', linewidth=1)
            plotname = f'covidregion_overflow_numbers_{selected_resource_type}'
        else:
            ax.bar(mdf_2['region'], mdf_2['number_that_exceed_median'], 1, label='0.75', linewidth=1)
            ax.bar(mdf_2b['region'], mdf_2b['number_that_exceed_median'], 1,color='red',  label='0.75', linewidth=1)
            plotname = f'covidregion_overflow_numbers_{selected_resource_type}_noerrorbars'

    fig.tight_layout()
    exp_dir = os.path.join(wdir, 'simulation_output', exp_name)
    fig.savefig(os.path.join(exp_dir, '_plots',f'{plotname}.png'))
    fig.savefig(os.path.join(exp_dir, '_plots', 'pdf', f'{plotname}.pdf'))

def get_numbers(exp_name, load_template=False):
    trajectories = load_sim_data(exp_name)  # pd.read_csv('trajectoriesDat_200814_1.csv', usecols=column_list)

    if load_template:
        fname = get_latest_filedate()
        civis_template = pd.read_csv(
            os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'hospital_capacity_thresholds', fname))
        civis_template = civis_template.drop_duplicates()

    else:
        civis_template = pd.read_csv(os.path.join(wdir, 'simulation_output', exp_name,
                                                  f'nu_hospitaloverflow_{str(exp_name[:8])}.csv'))

    civis_template['date_window_upper_bound'] = pd.to_datetime(civis_template['date_window_upper_bound'])
    civis_template['number_that_exceed_median'] = ''
    civis_template['number_that_exceed_median'] = ''
    civis_template['number_that_exceed_median'] = ''

    trajectories['total_hosp_census_lower'] = trajectories['hosp_bed_lower'] + trajectories['icu_lower']
    trajectories['total_hosp_census_median'] = trajectories['hosp_bed_median'] + trajectories['icu_median']
    trajectories['total_hosp_census_upper'] = trajectories['hosp_bed_upper'] + trajectories['icu_upper']
    trajectories['date'] = pd.to_datetime(trajectories['date'])

    for index, row in civis_template.iterrows():
        upper_limit = pd.to_datetime(row['date_window_upper_bound'])
        if row['resource_type'] == 'hb_availforcovid':
            metric_root = 'total_hosp_census'
        elif row['resource_type'] == 'icu_availforcovid':
            metric_root = 'icu'
        thresh = row['avg_resource_available']
        region = str(row['geography_modeled'])

        new = trajectories[(trajectories['date'] == upper_limit)].reset_index()
        new = new[(new['geography_modeled'] == region)].reset_index()

        civis_template.loc[index, 'number_that_exceed_median'] = thresh - int(new[f'{metric_root}_median'])
        civis_template.loc[index, 'number_that_exceed_lower'] =  thresh - int(new[f'{metric_root}_lower'])
        civis_template.loc[index, 'number_that_exceed_upper'] =  thresh- int(new[f'{metric_root}_upper'])

    #civis_template['scenario_name'] = trajectories['scenario_name'].unique()
    civis_template.to_csv(os.path.join(wdir, 'simulation_output', exp_name,
                                       f'nu_hospitaloverflow_{str(exp_name[:8])}.csv'), index=False)
    return civis_template



if __name__ == '__main__':
    stem = sys.argv[1]
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    #exp_names = ['20201028_IL_rollback_toki8']

    for exp_name in exp_names:
        civis_template = get_numbers(exp_name)
        get_plot(selected_resource_type='icu_availforcovid')
        get_plot(selected_resource_type='hb_availforcovid')
        get_plot(selected_resource_type='icu_availforcovid', errorbars=False)
        get_plot(selected_resource_type='hb_availforcovid', errorbars=False)

