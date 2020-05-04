import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import datetime, date, timedelta
import seaborn as sns
from processing_helpers import *
from data_comparison import load_sim_data
from copy import copy

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()


def plot_on_fig(df, channels, axes, color, label) :
    first_day = datetime.strptime(df['first_day'].unique()[0], '%Y-%m-%d')

    for c, channel in enumerate(channels) :
        ax = axes[c]
        mdf = df.groupby('time')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        mdf['date'] = mdf['time'].apply(lambda x: first_day + timedelta(days=int(x)))
        mdf = mdf[(mdf['date'] >= date(2020, 4, 1)) & (mdf['date'] <= date(2020, 8, 1))]
        ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
        # ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
        #                 color=color, linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=color, linewidth=0, alpha=0.4)
        ax.set_title(' '.join(channel.split('_')), y=0.85)
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())


if __name__ == '__main__' :

    subfolder = 'EMS_7_scenarios/'
    exp_names = [subfolder + '20200501_EMS_7_reopening_test1',
                 subfolder + '20200501_EMS_7_ct30_test',
                 subfolder + '20200429_EMS_7_scenario1_v2',
                 subfolder + '20200429_EMS_7_scenario2_v2',
                 subfolder + '20200429_EMS_7_scenario3_v2']

    fig = plt.figure(figsize=(8, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
    palette = sns.color_palette('Set1', len(exp_names))
    channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']
    axes = [fig.add_subplot(3, 2, x + 1) for x in range(len(channels))]

    for d, exp_name in enumerate(exp_names) :
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        df = load_sim_data(exp_name)

        df['symptomatic_census'] = df['symptomatic_mild'] + df['symptomatic_severe']
        df['ventilators'] = df['critical']*0.8

        plot_on_fig(df, channels, axes, color=palette[d], label=exp_name)
    axes[-1].legend()

    plt.savefig(os.path.join(wdir, 'simulation_output',subfolder, 'scenario_comparison.png'))
    #plt.savefig(os.path.join(wdir, 'simulation_output', subfolder, 'scenario_comparison.pdf'), format='PDF')
    plt.show()

