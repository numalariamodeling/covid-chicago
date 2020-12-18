"""
Compare COVID-19 simulation outputs to data.
Used for spatial - covidregion - model
Allow lines per varying input parameter to be specified
"""
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
today = datetime.today()
datetoday = date(today.year, today.month, today.day)


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
        help="Name of trajectoriesDat file, trajectoriesDat.csv or trajectoriesDat_trim.csv",
        default='trajectoriesDat.csv',
    )
    return parser.parse_args()


def plot_sim_and_ref(df, ems_nr, ref_df, channels, data_channel_names,region_label,
                     titles, param, first_day, last_day, ymax=10000, logscale=True):

    fig = plt.figure(figsize=(15, 8))
    palette = sns.color_palette('husl', 12)

    for c, channel in enumerate(channels):
        ax = fig.add_subplot(2, 3, c + 1)

        mdf = df.groupby(['date',param])[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        for i, rtc in enumerate(mdf[param].unique()):
            mdf_sub = mdf[mdf[param] == rtc]
            ax.plot(mdf_sub['date'], mdf_sub['CI_50'], color=palette[i], label=rtc)

        ax.fill_between(mdf_sub['date'], mdf_sub['CI_2pt5'], mdf_sub['CI_97pt5'], color=palette[i], linewidth=0, alpha=0.2)

        ax.set_title(titles[c], y=0.8, fontsize=12)
        ax.legend()

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        ax.set_xlim(first_day, last_day)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        if logscale:
            ax.set_ylim(0.1, ymax)
            ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0, ms=1)
        ax.plot(ref_df['date'], ref_df[data_channel_names[c]].rolling(window=7, center=True).mean(), c='k', alpha=1.0)
        if c == len(channels)-1:
            ax.legend()

    fig.suptitle(region_label, y=1, fontsize=14)
    fig.tight_layout()
    fig.subplots_adjust(top=0.88)

    plot_name = 'compare_to_data_covidregion_' + str(ems_nr)
    if logscale == False:
        plot_name = plot_name + "_nolog"
    plt.savefig(os.path.join(plot_path, plot_name + '.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', plot_name + '.pdf'), format='PDF')


def compare_ems(exp_name,fname, param, ems_nr,first_day,last_day):

    if ems_nr == 0:
        region_suffix = "_All"
        region_label = 'Illinois'
    else:
        region_suffix = "_EMS-" + str(ems_nr)
        region_label = region_suffix.replace('_EMS-', 'COVID-19 Region ')

    column_list = ['time', 'startdate', 'scen_num', 'sample_num', 'run_num']
    outcome_channels = ['hosp_det_cumul', 'hosp_cumul', 'hosp_det', 'hospitalized',
                        'crit_det_cumul', 'crit_cumul', 'crit_det', 'critical',
                        'death_det_cumul', 'deaths']

    ref_df = load_ref_df(ems_nr)

    for channel in outcome_channels:
        column_list.append(channel + region_suffix)

    df = load_sim_data(exp_name, region_suffix=region_suffix, fname=fname, column_list=column_list)
    df = df[(df['date'] >= first_day) & (df['date'] <= last_day)]
    df['critical_with_suspected'] = df['critical']

    sampled_df = pd.read_csv(os.path.join(wdir, 'simulation_output', exp_name, "sampled_parameters.csv"), usecols=['scen_num', param])
    df = pd.merge(how='left', left=df, left_on='scen_num', right=sampled_df, right_on='scen_num')

    channels = ['new_detected_deaths', 'crit_det', 'hosp_det', 'new_deaths', 'new_detected_hospitalized',
                'new_detected_hospitalized']
    data_channel_names = ['confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'covid_non_icu', 'deaths', 'inpatient', 'admissions']
    titles = ['New Detected\nDeaths (EMR)', 'Critical Detected (EMR)', 'Inpatient non-ICU\nCensus (EMR)',
              'New Detected\nDeaths (LL)',
              'Covid-like illness\nadmissions (IDPH)', 'New Detected\nHospitalizations (LL)']

    plot_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,
                     region_label=region_label, logscale=True,param=param,first_day=first_day,last_day=last_day)

if __name__ == '__main__':

    args = parse_args()
    trajectoriesName = args.trajectoriesName
    Location = args.Location
    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    first_plot_day = date(2020, 2, 13)
    today = datetime.today() + timedelta(15)
    last_plot_day = date(today.year, today.month, today.day)

    stem = args.stem
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    for exp_name in exp_names:
        plot_path = os.path.join(wdir, 'simulation_output', exp_name, '_plots')
        for ems_nr in range(0, 12):
            print("Start processing region " + str(ems_nr))
            compare_ems(exp_name, fname=trajectoriesName, ems_nr=int(ems_nr), param="recovery_time_crit",
                        first_day=first_plot_day, last_day=last_plot_day)