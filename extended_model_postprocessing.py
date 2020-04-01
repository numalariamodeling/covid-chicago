import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
from processing_helpers import *
from load_paths import load_box_paths


#### overall, this file takes the trajectories and calculates the incidence for all of the channels. There may need to be an intermediate step between the runScenerios file and this, because of the age and county. if we run it for groups, {susceptable_H} where H can be county/locale/agegroup etc. can put into a long format for those groups and do the plotting via groupby. 

mpl.rcParams['pdf.fonttype'] = 42
testMode = False

exp_name = '30032020_extendedModel_base_chicago'
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

if testMode == True :
    sim_output_path = os.path.join(wdir, 'sample_trajectories')
    plot_path = os.path.join(wdir, 'sample_plots')
else :
    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path =  sim_output_path

if not os.path.exists(sim_output_path):
    os.makedirs(sim_output_path)

if not os.path.exists(plot_path):
    os.makedirs(plot_path)

master_channel_list = ['susceptible', 'exposed', 'infectious', 'symptomatic', 'detected',
                       'hospitalized', 'critical', 'deaths', 'recovered']
first_day = date(2020, 3, 1)


def count_new(df, curr_ch) :

    ch_list = list(df[curr_ch].values)
    diff = [0] + [ch_list[x] - ch_list[x - 1] for x in range(1, len(df))]
    return diff


def calculate_incidence(adf, output_filename=None) : ## incidence is new outcome, it's ~ events happening between timesteps. this is a proper channel to use to compare to the data (IDPH or chicago). 

    inc_df = pd.DataFrame()
    for (samp, scen), df in adf.groupby(['sample_num', 'scen_num']) :

        sdf = pd.DataFrame( { 'time' : df['time'],
                              'new_exposures' : [-1*x for x in count_new(df, 'susceptible')],
                              'new_asymptomatic' : count_new(df, 'asymp_cumul'),
                              'new_asymptomatic_detected' : count_new(df, 'asymp_det_cumul'),
                              'new_symptomatic' : count_new(df, 'symp_cumul'),
                              'new_symptomatic_detected' : count_new(df, 'symp_det_cumul'),
                              'new_hospitalized' : count_new(df, 'hosp_cumul'),
                              'new_detected' : count_new(df, 'detected_cumul'),
                              'new_critical' : count_new(df, 'crit_cumul'),
                              'new_deaths' : count_new(df, 'deaths')
                              })
        sdf['sample_num'] = samp
        sdf['scen_num'] = scen
        inc_df = pd.concat([inc_df, sdf])
    adf = pd.merge(left=adf, right=inc_df, on=['sample_num', 'scen_num', 'time'])
    if output_filename :
        adf.to_csv(os.path.join(sim_output_path, output_filename), index=False)
    return adf


def calculate_mean_and_CI(adf, channel, output_filename=None) :

    mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
    if output_filename :
        mdf.to_csv(os.path.join(sim_output_path, output_filename), index=False)


def plot(adf) :

    fig = plt.figure(figsize=(12,6))

    plotchannels = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic',
                    'detected', 'hospitalized', 'critical', 'deaths', 'recovered',
                    'new_detected', 'new_hospitalized', 'new_deaths']
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

    plt.savefig(os.path.join(plot_path, 'sample_plot_withIncidence.png'))

    plt.show()


if __name__ == '__main__' :
    ### trajectories vs trajectories_with_Incidence.   
    ### fitting is not yet included
    ### use trajectories w/ incidence, this just add new channels.
    ### 
    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    adf = calculate_incidence(df, output_filename='trajectoresDat_withIncidence.csv')
    adf['infections_cumul'] = adf['asymp_cumul'] + adf['symp_cumul']
    for channel in ['infections_cumul', 'detected_cumul'] :
        calculate_mean_and_CI(adf, channel, output_filename='%s.csv' % channel)
    plot(adf)
