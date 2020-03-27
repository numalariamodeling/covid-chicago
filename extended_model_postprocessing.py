import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
from processing_helpers import *

mpl.rcParams['pdf.fonttype'] = 42

user_path = '/Users/jlg1657'
# user_path = '/Users/mrung'

wdir = os.path.join(user_path, 'Box/NU-malaria-team/projects/covid_chicago/cms_sim')
sim_output_path = os.path.join(wdir, 'sample_trajectories')
plot_path = os.path.join(wdir, 'sample_plots')


master_channel_list = ['susceptible', 'exposed', 'infectious', 'symptomatic', 'detected',
                       'hospitalized', 'critical', 'deaths', 'recovered']
first_day = date(2020, 3, 1)


def count_new(df, curr_ch) :

    ch_list = list(df[curr_ch].values)
    diff = [0] + [ch_list[x] - ch_list[x - 1] for x in range(1, len(df))]
    return diff


def calculate_incidence(adf, output_filename=None) :

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

    plt.savefig(os.path.join(plot_path, 'sample_plot.png'))

    plt.show()


if __name__ == '__main__' :

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    adf = calculate_incidence(df, output_filename='trajectoresDat_withIncidence.csv')
    plot(adf)
