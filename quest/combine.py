import numpy as np
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import shutil

mpl.rcParams['pdf.fonttype'] = 42


def reprocess(input_fname='trajectories.csv', output_fname=None):
    fname = os.path.join(git_dir, input_fname)
    row_df = pd.read_csv(fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    num_channels = len([x for x in df.columns.values if '{0}' in x])
    num_runs = int((len(row_df) - 1) / num_channels)
    df = df.reset_index(drop=False)
    df = df.rename(columns={'index': 'time'})
    df['time'] = df['time'].astype(float)
    adf = pd.DataFrame()
    for run_num in range(num_runs):
        channels = [x for x in df.columns.values if '{%d}' % run_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x: x.split('{')[0] for x in channels
        })
        sdf['run_num'] = run_num
        adf = pd.concat([adf, sdf])
    adf = adf.reset_index()
    del adf['index']
    return adf


git_dir = "/home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/20200414_IL_mr__rn82/"
trajectoriesDat = "/home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/20200414_IL_mr__rn82/trajectories/"
temp_exp_dir = git_dir

Nscenarios = 1000

scendf = pd.read_csv(os.path.join(temp_exp_dir, "scenarios.csv"))
sampledf = pd.read_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"))

df_list = []

for scen_i in range(Nscenarios):
    input_name = "trajectories_scen" + str(scen_i) + ".csv"
    try:
        df_i = reprocess(os.path.join(trajectoriesDat, input_name))
        df_i['scen_num'] = scen_i
        df_i = df_i.merge(scendf, on=['scen_num'])
        df_i = df_i.merge(sampledf, on=['sample_num'])
        df_list.append(df_i)
    except:
        continue

dfc = pd.concat(df_list)

dfc.to_csv(os.path.join(temp_exp_dir, "trajectoriesDat.csv"))

import numpy as np


def CI_5(x):
    return np.percentile(x, 5)


def CI_95(x):
    return np.percentile(x, 95)


def CI_25(x):
    return np.percentile(x, 25)


def CI_75(x):
    return np.percentile(x, 75)


def CI_2pt5(x):
    return np.percentile(x, 2.5)


def CI_97pt5(x):
    return np.percentile(x, 97.5)


def CI_50(x):
    return np.percentile(x, 50)


def sampleplot(adf, allchannels, plot_fname=None):
    fig = plt.figure(figsize=(8, 6))
    palette = sns.color_palette('Set1', 10)
    axes = [fig.add_subplot(3, 3, x + 1) for x in range(len(allchannels))]
    fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
    for c, channel in enumerate(allchannels):
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
    if plot_fname:  plt.savefig(os.path.join(git_dir, plot_fname))


master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild', 'hospitalized', 'detected',
                       'critical', 'deaths', 'recovered']
detection_channel_list = ['detected', 'detected_cumul', 'asymp_det_cumul', 'hosp_det_cumul']
custom_channel_list = ['detected_cumul', 'symp_severe_cumul', 'asymp_det_cumul', 'hosp_det_cumul', 'symp_mild_cumul',
                       'asymp_cumul', 'hosp_cumul', 'crit_cumul']

first_day = date(2020, 2, 28)

sampleplot(dfc, allchannels=master_channel_list, plot_fname='main_channels.png')
sampleplot(dfc, allchannels=detection_channel_list, plot_fname='detection_channels.png')
sampleplot(dfc, allchannels=custom_channel_list, plot_fname='cumulative_channels.png')