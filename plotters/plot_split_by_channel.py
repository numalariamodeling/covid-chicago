import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import seaborn as sns
from processing_helpers import *
from data_comparison import load_sim_data
from copy import copy
import re

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

# first_day = date(2020, 2, 13) # IL
# first_day = date(2020, 2, 18) # Chicago
first_day = date(2020, 2, 13) # NMH


def plot_on_fig(df, channels, axes, color, label) :

    for c, channel in enumerate(channels) :
        channeltitle = re.sub('_detected', '', str(channel), count=1)
        channeltitle = re.sub('_det','', str(channeltitle), count=1)

        ax = axes[c]
        mdf = df.groupby('time')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        mdf['date'] = mdf['time'].apply(lambda x: first_day + timedelta(days=int(x)))
        mdf = mdf[(mdf['date'] >= date(2020, 5, 1)) & (mdf['date'] <= date(2020, 10, 1))]
        ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
        # ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
        #                 color=color, linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=color, linewidth=0, alpha=0.4)
        ax.set_title(' '.join(channeltitle.split('_')), y=0.85)
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())


if __name__ == '__main__' :

    exp_name = '20200816_IL_testbaseline'

    fig = plt.figure(figsize=(12, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)

    nchannels = {'channels1': ['symptomatic_mild', 'infectious_undet', 'prevalence', 'seroprevalence', 'hospitalized'],
                 'channels2': ['symptomatic_mild_det',  'infectious_det', 'prevalence_det', 'seroprevalence_det', 'hospitalized_det'] }
    #nchannels = {'channels1': ['hospitalized', 'new_hospitalized', 'hosp_cumul', 'critical', 'new_critical', 'crit_cumul'],
    #             'channels2': ['hospitalized_det',  'new_detected_hospitalized', 'hosp_det_cumul','crit_det',  'new_detected_critical', 'crit_det_cumul'] }

    palette = sns.color_palette('Set1', len(nchannels))
    axes = [fig.add_subplot(2, 3, x + 1) for x in range(len(nchannels['channels1']))]

    for d, key in enumerate(nchannels.keys()) :
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        df = load_sim_data(exp_name)

        channels = nchannels[key]
        if d == 0:
            label="all"
        if d == 1:
            label = "detected"

        plot_on_fig(df, channels, axes, color=palette[d], label=label)
    axes[-1].legend()

    plt.savefig(os.path.join(sim_output_path, 'channel_comparison.png'))
    plt.savefig(os.path.join(sim_output_path, 'channel_comparison.pdf'), format='PDF')
    plt.show()

