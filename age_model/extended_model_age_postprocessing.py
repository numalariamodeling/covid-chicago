import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import sys
sys.path.append('../')
from processing_helpers import *
from load_paths import load_box_paths

mpl.rcParams['pdf.fonttype'] = 42
testMode = True

exp_name = '20200415_NMH_catchment_TEST_4grp_rn_rn69'
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

if testMode == True :
    sim_output_path = os.path.join(git_dir,'age_model', '_temp',exp_name)
    plot_path = sim_output_path
else :
    sim_output_path = os.path.join(wdir, 'simulation_output_age', exp_name)
    plot_path = sim_output_path

if not os.path.exists(sim_output_path):
    os.makedirs(sim_output_path)

if not os.path.exists(plot_path):
    os.makedirs(plot_path)

master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild',
                       'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
detection_channel_list = ['detected', 'detected_cumul', 'asymp_det_cumul', 'hosp_det_cumul']
custom_channel_list = ['detected_cumul', 'symp_severe_cumul', 'asymp_det_cumul', 'hosp_det_cumul',
                       'symp_mild_cumul', 'asymp_cumul', 'hosp_cumul', 'crit_cumul']

first_day = date(2020, 2, 28)


def calculate_incidence(adf, age_group, output_filename=None) :

    inc_df = pd.DataFrame()
    for (run, samp, scen), df in adf.groupby(['run_num','sample_num', 'scen_num']) :

        sdf = pd.DataFrame( { 'time' : df['time'],
                              'new_exposures_%s' % age_group : [-1*x for x in count_new(df, 'susceptible_%s' % age_group)],
                              'new_asymptomatic_%s' % age_group : count_new(df, 'asymp_cumul_%s' % age_group),
                              'new_asymptomatic_detected_%s' % age_group : count_new(df, 'asymp_det_cumul_%s' % age_group),
                              #'new_symptomatic_mild_%s' % age_group : count_new(df, 'symp_mild_cumul_%s' % age_group),
                              'new_detected_hospitalized_%s' % age_group : count_new(df, 'hosp_det_cumul_%s' % age_group),
                              'new_detected_%s' % age_group : count_new(df, 'detected_cumul_%s' % age_group),
                              'new_critical_%s' % age_group : count_new(df, 'crit_cumul_%s' % age_group),
                              'new_deaths_%s' % age_group : count_new(df, 'deaths_%s' % age_group)
                              })
        sdf['run_num'] = run
        sdf['sample_num'] = samp
        sdf['scen_num'] = scen
        inc_df = pd.concat([inc_df, sdf])
    adf = pd.merge(left=adf, right=inc_df, on=['run_num', 'sample_num', 'scen_num', 'time'])
    if output_filename :
        adf.to_csv(os.path.join(sim_output_path, output_filename), index=False)
    return adf


def calculate_mean_and_CI(adf, channel, output_filename=None) :

    mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
    if output_filename :
        mdf.to_csv(os.path.join(sim_output_path, output_filename), index=False)


def plot(adf,age_group,filename) :

    fig = plt.figure(figsize=(12,6))

    plotchannels = [ '%s_%s' % (x, age_group) for x in [
        'susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild',
                    'detected', 'hospitalized', 'critical', 'deaths',
                    'new_detected', 'new_detected_hospitalized', 'new_critical', 'new_deaths']]
    palette = sns.color_palette('muted', len(plotchannels))
    axes = [fig.add_subplot(3,4,x+1) for x in range(len(plotchannels))]
    fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
    for c, channel in enumerate(plotchannels) :

        mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
        ax = axes[c]
        dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
        ax.plot(dates, mdf['mean'], label=channel, color=palette[c])
        ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                        color=palette[c], linewidth=0, alpha=0.2)
        ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                        color=palette[c], linewidth=0, alpha=0.4)

        ax.set_title(channel, y=0.8)

        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_xlim(first_day, )

    plt.savefig(os.path.join(plot_path, '%s.png' % filename))


if __name__ == '__main__' :

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    suffix_names = [x.split('_')[1] for x in df.columns.values if 'susceptible' in x]
    base_names = [x.split('_%s' % suffix_names[0])[0] for x in df.columns.values if suffix_names[0] in x]
    sample_index_names = [x for x in df.columns.values if ('num' in x or 'time' in x)]

    for col in base_names :
        df['%s_%s' % (col, 'all')] = sum([df['%s_%s' % (col, age_group)] for age_group in suffix_names])

    suffix_names.append('all')
    for age_group in suffix_names :
        cols = sample_index_names + [ "%s_%s" % (channel, age_group) for channel in base_names]
        adf = df[cols]
        adf = calculate_incidence(adf, age_group, output_filename='trajectoriesDat_withIncidence_%s.csv' % age_group)
        #adf['infections_cumul_%s' % age_group] = adf['asymp_cumul_%s' % age_group] + adf['symp_cumul_%s' % age_group]
        #for channel in ['infections_cumul_%s' % age_group, 'detected_cumul_%s' % age_group] :
        #    calculate_mean_and_CI(adf, channel, output_filename='%s.csv' % (channel, age_group))

        plot(adf, age_group, 'plot_withIncidence_%s' % age_group)

    # plt.show()

