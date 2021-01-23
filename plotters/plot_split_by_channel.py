import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns
from processing_helpers import *
import re

mpl.rcParams['pdf.fonttype'] = 42

def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-stem",
        "--stem",
        type=str,
        help="Name of simulation experiment"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default="Local"
    )
    return parser.parse_args()

def plot_on_fig(df, channels, axes, color, label) :

    for c, channel in enumerate(channels) :
        channeltitle = re.sub('_detected', '', str(channel), count=1)
        channeltitle = re.sub('_det','', str(channeltitle), count=1)

        ax = axes[c]
        mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
        ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
        # ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
        #                 color=color, linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=color, linewidth=0, alpha=0.4)
        ax.set_title(' '.join(channeltitle.split('_')), y=0.85)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))

def compare_channels(channelGrp):
    nchannels_symp = {'channels1': ['symp_severe_cumul', 'symp_mild_cumul', 'symptomatic_severe', 'symptomatic_mild'],
                      'channels2': ['symp_severe_det_cumul', 'symp_mild_det_cumul', 'symptomatic_severe_det',
                                    'symptomatic_mild_det']}

    nchannels_infect = {'channels1': ['infected', 'presymptomatic', 'infectious_undet', 'asymptomatic', 'asymp_cumul'],
                        'channels2': ['infected_det', 'presymptomatic_det', 'infectious_det', 'asymptomatic_det',
                                      'asymp_det_cumul']}

    nchannels_hospCrit = {
        'channels1': ['hospitalized', 'new_hospitalized', 'hosp_cumul', 'critical', 'new_critical', 'crit_cumul'],
        'channels2': ['hosp_det', 'new_detected_hospitalized', 'hosp_det_cumul', 'crit_det', 'new_detected_critical',
                      'crit_det_cumul']}

    if channelGrp == "symp":
        nchannels = nchannels_symp
    if channelGrp == "infect":
        nchannels = nchannels_infect
    if channelGrp == "hospCrit":
        nchannels = nchannels_hospCrit

    palette = sns.color_palette('Set1', len(nchannels))

    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)

    axes = [fig.add_subplot(2, 3, x + 1) for x in range(len(nchannels['channels1']))]

    for d, key in enumerate(nchannels.keys()):

        df = load_sim_data(exp_name)
        df = df[df['date'].between(first_plot_day, last_plot_day)]

        channels = nchannels[key]
        if d == 0:
            label = "all"
        if d == 1:
            label = "detected"

        plot_on_fig(df, channels, axes, color=palette[d], label=label)
    axes[-1].legend()

    fname = 'channel_' + channelGrp + '_comparison'
    plt.savefig(os.path.join(plot_path, fname + '.png'))
    # plt.savefig(os.path.join(plot_path,'pdf', fname + '.pdf'), format='PDF')
    plt.show()

if __name__ == '__main__' :

    args = parse_args()
    stem = args.stem
    Location = args.Location

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()

    first_plot_day = pd.Timestamp.today()- pd.Timedelta(30,'days')
    last_plot_day = pd.Timestamp.today()+ pd.Timedelta(15,'days')

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')
        #compare_channels(channelGrp= "symp")
        #compare_channels(channelGrp= "infect")
        compare_channels(channelGrp= "hospCrit")


