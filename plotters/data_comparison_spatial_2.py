"""
Compare COVID-19 simulation outputs to data.
Used for spatial - covidregion - model
Allow comparison of multiple simulation experiments
"""
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
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
        "-e",
        "--exp_names",
        type=str,
        nargs='+',
        help="Experiment names to compare, example python data_comparison_spatial_2.py -e  exp_name1 exp_name2"
    )
    parser.add_argument(
        "-l",
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


def load_sim_data(exp_name, ems_nr, fname, input_wdir=None,  input_sim_output_path=None,
                  column_list=None):
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df = pd.read_csv(os.path.join(sim_output_path, fname), usecols=column_list)
    df = df.dropna()
    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
    df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
    df['date'] = pd.to_datetime(df['date']).dt.date

    df.columns = df.columns.str.replace('_EMS-' + str(ems_nr), '')

    df['new_detected_hospitalized'] = count_new(df, 'hosp_det_cumul')
    df['new_hospitalized'] = count_new(df, 'hosp_cumul')
    df['new_critical'] = count_new(df, 'crit_cumul')
    df['new_detected_critical'] = count_new(df, 'crit_det_cumul')
    df['new_detected_deaths'] = count_new(df, 'death_det_cumul')
    df['new_deaths'] = count_new(df, 'deaths')

    return df

def plot_sim_and_ref(exp_names, ems_nr,
                     first_plot_day=None,last_plot_day=None,
                     ymax=10000, logscale=True, fname="trajectoriesDat.csv"):

    channels = ['new_detected_deaths', 'crit_det', 'hosp_det', 'new_deaths','new_detected_hospitalized',
                'new_detected_hospitalized']
    data_channel_names = ['confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'covid_non_icu', 'deaths','inpatient', 'admissions']
    titles = ['New Detected\nDeaths (EMR)', 'Critical Detected (EMR)', 'Inpatient non-ICU\nCensus (EMR)', 'New Detected\nDeaths (LL)',
              'Covid-like illness\nadmissions (IDPH)', 'New Detected\nHospitalizations (LL)']

    ref_df = load_ref_df(ems_nr)

    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, wspace=0.5, left=0.1, hspace=0.9, top=0.95, bottom=0.07)
    palette = sns.color_palette('tab10', len(exp_names))
    axes = [fig.add_subplot(2, 3, x + 1) for x in range(len(channels))]

    for c, channel in enumerate(channels):
        ax = axes[c]
        for d, exp_name in enumerate(exp_names) :

            column_list = ['time', 'startdate', 'scen_num', 'sample_num', 'run_num']
            outcome_channels = ['susceptible', 'infected', 'recovered', 'infected_cumul', 'asymp_cumul',
                                'asymp_det_cumul', 'symp_mild_cumul', 'symp_severe_cumul', 'symp_mild_det_cumul',
                                'symp_severe_det_cumul', 'hosp_det_cumul', 'hosp_cumul', 'detected_cumul', 'crit_cumul',
                                'crit_det_cumul', 'death_det_cumul', 'deaths', 'crit_det', 'critical', 'hosp_det', 'hospitalized']

            for chn in outcome_channels:
                column_list.append(chn + "_EMS-" + str(ems_nr))

            df = load_sim_data(exp_name, ems_nr, fname=fname, column_list=column_list)
            df = df[df['date'] <= ref_df['date'].max()]
            df['critical_with_suspected'] = df['critical']
            exp_name_label = str(exp_name.split('_')[-1])

            mdf = df.groupby('date')[channel].agg([CI_50, CI_5, CI_95, CI_25, CI_75]).reset_index()
            ax.plot(mdf['date'], mdf['CI_50'], color=palette[d], label=exp_name_label)
            ax.fill_between(mdf['date'], mdf['CI_5'], mdf['CI_95'],
                        color=palette[d], linewidth=0, alpha=0.1)
            ax.fill_between(mdf['date'], mdf['CI_25'], mdf['CI_75'],
                        color=palette[d], linewidth=0, alpha=0.3)

            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
            ax.set_title(titles[c], y=0.8, fontsize=12)

        axes[-1].legend()
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        if first_plot_day != None:
            ax.set_xlim(first_plot_day, last_plot_day)
        if logscale:
            ax.set_ylim(0.1, ymax)
            ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0, ms=1)
        ax.plot(ref_df['date'], ref_df[data_channel_names[c]].rolling(window=7, center=True).mean(), c='k', alpha=1.0)

    plt.suptitle(f'Covidregion {ems_nr}', y=1, fontsize=14)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)

    plot_name = f'compare_to_data_{ems_nr}'
    if logscale == False :
        plot_name = plot_name + "_nolog"

    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    if not os.path.exists(os.path.join(plot_path, 'pdf')):
        os.makedirs(os.path.join(plot_path, 'pdf'))
    plt.savefig(os.path.join(plot_path, plot_name + '.png'))
    plt.savefig(os.path.join(plot_path,'pdf', plot_name + '.pdf'))

if __name__ == '__main__':

   # args = parse_args()
    exp_names =["20201103_IL_mr_ae_baselinefit-v1","20201104_IL_mr_ae_baselinefit-v4"]
    Location = 'Local'
    trajectoriesName ="trajectoriesDat.csv"

    """If show defined timeframe only"""
    first_plot_day = None  # date(2020, 3, 1)
    last_plot_day = None  # date(2020, 7, 1)

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)
    plot_path = os.path.join(wdir, 'simulation_output', exp_names[len(exp_names)-1], '_plots')

    for ems_nr in range(1, 12):
        print("Start processing region " + str(ems_nr))
        plot_sim_and_ref(exp_names, ems_nr=ems_nr, first_plot_day=first_plot_day, last_plot_day=last_plot_day,
                         fname=trajectoriesName, logscale=True)
        plot_sim_and_ref(exp_names, ems_nr=ems_nr, first_plot_day=first_plot_day, last_plot_day=last_plot_day,
                         fname=trajectoriesName, logscale=False)
