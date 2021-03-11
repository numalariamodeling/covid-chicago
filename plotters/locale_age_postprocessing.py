import argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib.dates as mdates
import sys
sys.path.append('../')
from processing_helpers import *
from load_paths import load_box_paths

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

def calculate_mean_and_CI(adf, channel, output_filename=None) :

    mdf = adf.groupby('time')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
    if output_filename :
        mdf.to_csv(os.path.join(sim_output_path, output_filename), index=False)


def plot(adf, channels, grp, filename=None) :

    plotchannels = [ '%s_%s' % (x, grp) for x in channels]

    fig = plt.figure(figsize=(12, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
    axes = [fig.add_subplot(3, 3, x + 1) for x in range(len(channels))]

    palette = sns.color_palette('coolwarm', 9)
    for c, channel in enumerate(plotchannels) :

        mdf = adf.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        ax = axes[c]
        ax.plot(mdf['date'], mdf['CI_50'], label=channel, color=palette[c])
        ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
                        color=palette[c], linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=palette[c], linewidth=0, alpha=0.4)

        ax.set_title(channel, y=0.8)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))

    if filename :
        plt.savefig(os.path.join(plot_path, '%s.png' % filename))


if __name__ == '__main__' :

    args = parse_args()
    stem = args.stem
    Location = args.Location
    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    first_plot_day = pd.Timestamp.today() - pd.Timedelta(30,'days')
    last_plot_day = pd.Timestamp.today() + pd.Timedelta(15,'days')

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')

        df = load_sim_data(exp_name, region_suffix=None, add_incidence=True)
        suffix_names = [x.split('_')[1] for x in df.columns.values if 'susceptible' in x]
        base_names = [x.split('_%s' % suffix_names[0])[0] for x in df.columns.values if suffix_names[0] in x]

        startdate = pd.Timestamp(df['startdate'].unique()[0])
        df['date'] = df['time'].apply(lambda x: startdate + pd.Timedelta(int(x), 'days'))
        df['date'] = pd.to_datetime(df['date'])

        channels = ['infected', 'new_deaths', 'hospitalized', 'critical', 'ventilators','recovered']

        fig = plt.figure(figsize=(12, 8))
        fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
        axes = [fig.add_subplot(3, 3, x + 1) for x in range(len(channels))]
        palette = sns.color_palette('coolwarm', len([x for x in suffix_names if 'All' not in x]))

        days_to_plot = len(df['date'].unique())
        last = {x: [0] * days_to_plot for x in channels}
        a = 0
        for grp in suffix_names :
            df['ventilators_%s' % grp] = df['crit_det_%s' % grp]
            df['infected_%s' % grp] = df['asymptomatic_%s' % grp] + df['presymptomatic_%s' % grp] + \
                                            df['symptomatic_mild_%s' % grp] + df['symptomatic_severe_%s' % grp] + \
                                            df['hospitalized_%s' % grp] + df['critical_%s' % grp]

            df['infections_cumul_%s' % grp] = df['asymp_cumul_%s' % grp] + \
                                                    df['symp_mild_cumul_%s' % grp] + \
                                                    df['symp_severe_cumul_%s' % grp]
            for channel in ['infections_cumul_%s' % grp, 'detected_cumul_%s' % grp] :
                calculate_mean_and_CI(df, channel, output_filename='%s_%s.csv' % (channel, grp))

            plot(df, channels, grp, 'plot_withIncidence_%s' % grp)
            if 'All' in grp :
                continue

            for c, channel in enumerate(channels) :
                ax = axes[c]
                col = '%s_%s' % (channel, grp)
                mdf = df.groupby('date')[col].agg(CI_50).reset_index()

                ax.fill_between(mdf['date'].values, last[channel],
                                [x + y for x, y in zip(last[channel], mdf[col].values)],
                                color=palette[a], label=grp,
                                linewidth=0)
                last[channel] = [x + y for x, y in zip(last[channel], mdf[col].values)]

                if a == 0 :
                    ax.set_title(' '.join(channel.split('_')), y=0.85)
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
            a += 1

        axes[-1].legend()
        fig.savefig(os.path.join(plot_path, 'stacked_median.png'))
        fig.savefig(os.path.join(plot_path, 'stacked.median.pdf'), format='PDF')
        #plt.show()

