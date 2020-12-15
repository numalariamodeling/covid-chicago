import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import sys

sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
from processing_helpers import *

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
    parser.add_argument(
        "-t", "--trajectoriesName",
        type=str,
        help="Name of trajectoriesDat file, could be trajectoriesDat.csv or trajectoriesDat_trim.csv",
        default='trajectoriesDat.csv',
    )
    return parser.parse_args()


def plot_sim_and_ref(df, ems_nr, ref_df, channels, data_channel_names, titles, plot_name, first_day, last_day,
                     ymax=1000,  logscale=False):

    fig = plt.figure(figsize=(13, 4))
    fig.subplots_adjust(left=0.07, right=0.97, top=2.95, bottom=0.05, hspace=0.25)
    axes = [fig.add_subplot(1,3, x + 1) for x in range(len(channels))]
    palette = sns.color_palette('husl', 8)
    k = 0

    for c, channel in enumerate(channels):
        ax = axes[c]
        df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
        mdf = df.groupby('date')[channel].agg([np.min, CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75, np.max]).reset_index()

        ax.plot(mdf['date'], mdf['CI_50'], color=palette[k])
        ax.fill_between(mdf['date'], mdf['CI_2pt5'], mdf['CI_97pt5'],
                        color=palette[k], linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'], mdf['CI_25'], mdf['CI_75'],
                        color=palette[k], linewidth=0, alpha=0.4)
        ax.fill_between(mdf['date'], mdf['amin'], mdf['amax'],
                        color=palette[k], linewidth=0, alpha=0.1)

        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        ax.set_title(titles[c],  fontsize=12)
        # ax.legend()

        if logscale:
            ax.set_ylim(0.1, ymax)
            ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0, ms=1)
        ax.plot(ref_df['date'], ref_df[data_channel_names[c]].rolling(window=7, center=True).mean(), c='k', alpha=1.0)

        if channel == "hosp_det" or channel == "crit_det":
            capacity = load_capacity(ems_nr)
            if channel == "hosp_det":
                capacitychannel = 'hosp_det'
            if channel == "crit_det":
                capacitychannel = 'crit_det'

            ax.plot([first_plot_day,last_plot_day ], [capacity[capacitychannel], capacity[capacitychannel]], '--', linewidth=1, color='black')
            ax.plot([first_plot_day,last_plot_day ], [capacity[capacitychannel] * 0.75, capacity[capacitychannel] * 0.75], '--', linewidth=0.8, color='grey')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        ax.set_xlim(first_day, last_day)

    fig.suptitle(f'COVID-19 region {ems_nr}        \n',  y=1.0, fontsize=14)
    fig.tight_layout()
    plot_name_full = plot_name + '_covidregion_' + str(ems_nr)
    fig.subplots_adjust(top=0.8)

    if logscale == False:
        plot_name_full = plot_name_full + "_nolog"

    plt.savefig(os.path.join(plot_path, plot_name_full + '.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', plot_name_full + '.pdf'), format='PDF')

def compare_ems(exp_name, fname, plot_name, ems_nr, first_day , last_day):
    region_suffix = "_EMS-" + str(ems_nr)
    column_list = ['time', 'startdate', 'scen_num', 'sample_num', 'run_num']

    outcome_channels = ['hosp_det_cumul', 'hosp_cumul', 'hosp_det', 'hospitalized',
                        'crit_det_cumul', 'crit_cumul', 'crit_det', 'critical',
                        'death_det_cumul', 'deaths']


    for channel in outcome_channels:
        column_list.append(channel + region_suffix)

    df = load_sim_data(exp_name, region_suffix=region_suffix, fname=fname, column_list=column_list)
    df = df[(df['date'] >= first_day) & (df['date'] <= last_day)]

    ref_df = load_ref_df(ems_nr)
    ref_df = ref_df[(ref_df['date'] >= first_plot_day) & (ref_df['date'] <= last_plot_day)]
    channels = ['crit_det', 'hosp_det', 'new_deaths']
    data_channel_names = ['confirmed_covid_icu', 'covid_non_icu', 'deaths']
    titles = ['ICU census\n(EMR)', 'non-ICU inpatient census\n(EMR)','daily deaths\n(LL)']

    #plot_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,plot_name=plot_name,
    #                first_day=first_day, last_day=last_day, logscale=True)
    plot_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,plot_name=plot_name,
                     first_day=first_day, last_day=last_day, logscale=False)

    # return ref_df_emr, ref_df_ll


if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    trajectoriesName = args.trajectoriesName
    Location = args.Location

    first_plot_day = date(2020, 10, 1)
    last_plot_day = date(2020, 12, 31)

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        plot_path = os.path.join(wdir, 'simulation_output', exp_name, '_plots')
        for ems_nr in range(1,12):
            print("Start processing region " + str(ems_nr))
            compare_ems(exp_name, fname=trajectoriesName, ems_nr=int(ems_nr), plot_name='forward_projection',
                        first_day=first_plot_day, last_day=last_plot_day)