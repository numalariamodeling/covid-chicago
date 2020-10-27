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
today = datetime.today()
datetoday = date(today.year, today.month, today.day) #date(2020, 10,1)

first_plot_day = pd.to_datetime(date(2020, 3, 1))
last_plot_day = pd.to_datetime(datetoday)

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

    # df.columns = df.columns.str.replace('_All', '')
    df.columns = df.columns.str.replace('_EMS-' + str(ems_nr), '')
    df['infected_cumul'] = df['infected'] + df['recovered'] + df['deaths']
    df = calculate_incidence(df)

    return df

def plot_sim_and_ref(exp_names, ems_nr,
                     first_plot_day=first_plot_day,last_plot_day=last_plot_day,
                     ymax=10000, logscale=True, fname="trajectoriesDat.csv"):

    channels = ['new_detected_deaths', 'crit_det', 'hosp_det', 'new_deaths','new_detected_hospitalized',
                'new_detected_hospitalized']
    data_channel_names = ['confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'covid_non_icu', 'deaths','inpatient', 'admissions']
    titles = ['New Detected\nDeaths (EMR)', 'Critical Detected (EMR)', 'Inpatient non-ICU\nCensus (EMR)', 'New Detected\nDeaths (LL)',
              'Covid-like illness\nadmissions (IDPH)', 'New Detected\nHospitalizations (LL)']

    ref_df = load_ref_df(ems_nr)
    ref_df = ref_df[(ref_df['date'] >= first_plot_day) & (ref_df['date'] <= last_plot_day)]

    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, wspace=0.5, left=0.1, hspace=0.9, top=0.95, bottom=0.07)
    palette = sns.color_palette('Set2', len(exp_names))
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
            first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d') #  '%m/%d/%Y'
            df['critical_with_suspected'] = df['critical']
            df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
            df = df[(df['date'] >= first_plot_day) & (df['date'] <= last_plot_day)]
            exp_name_label =  str(exp_name.split('_')[-1])

            # for k, (ki, kdf) in enumerate(df.groupby('Ki')) :
            mdf = df.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
            dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
            ax.plot(dates, mdf['mean'], color=palette[d], label=exp_name_label)
            ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                        color=palette[d], linewidth=0, alpha=0.1)
            ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                        color=palette[d], linewidth=0, alpha=0.3)

            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
            ax.set_title(titles[c], y=0.8, fontsize=12)

        axes[-1].legend()
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_xlim(first_plot_day, last_plot_day)
        if logscale:
            ax.set_ylim(0.1, ymax)
            ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0, ms=1)
        ax.plot(ref_df['date'], ref_df[data_channel_names[c]].rolling(window=7, center=True).mean(), c='k', alpha=1.0)

    plt.suptitle(f'Covidregion {ems_nr}', y=1, fontsize=14)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88)
    plt.savefig(os.path.join(wdir, 'simulation_output', exp_names[len(exp_names)-1], 'compare_to_data_%s.png' % ems_nr))
    plt.savefig(os.path.join(wdir, 'simulation_output', exp_names[len(exp_names)-1], 'compare_to_data_%s.pdf' % ems_nr))

    #return plt


if __name__ == '__main__':

   # args = parse_args()
    exp_names =["20200929_IL_mr_baseline","20201003_IL_mr_resimsm4"]
    Location =  'Local'
    trajectoriesName ="trajectoriesDat.csv"

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    for ems_nr in range(1,12):
        print("Start processing region " + str(ems_nr))
        plot_sim_and_ref(exp_names, ems_nr=ems_nr, first_plot_day=first_plot_day, last_plot_day=last_plot_day,  fname=trajectoriesName)
