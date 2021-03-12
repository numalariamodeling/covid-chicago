"""
Compare COVID-19 simulation outputs to data.
Comparison for single regions, base or age model.
"""
import argparse
import os
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib.dates as mdates
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
    return parser.parse_args()

def compare_NMH(exp_name) :

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_chicago', 'NMH', 'Modeling COVID Data NMH_v1_200415_jg.csv'))
    ref_df['date'] = pd.to_datetime(ref_df['date'])

    df = load_sim_data(exp_name)
    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')

    channels = ['new_hosp_det', 'hosp_det_cumul', 'hospitalized', 'critical']
    data_channel_names = ['covid pos admissions', 'cumulative admissions', 'inpatient census', 'ICU census']

    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_NMH_v1')
    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names,
                     plot_path=plot_path, first_day=first_day)

    #data_channel_names = ['new admits v2', 'cumulative admits positive results v2', 'non ICU v2', 'ICU census v2']

    #plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_NMH_v2')
    #plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=1000,
    #                 plot_path=plot_path, first_day=first_day)


def plot_sim_and_ref_by_param(df, ems_nr, ref_df, channels, data_channel_names, titles, first_day, last_day,
                     ymax=1000, plot_path=None, logscale=False, param="Ki"):

    fig = plt.figure(figsize=(13, 6))
    palette = sns.color_palette('husl', 8)
    k = 0
    for c, channel in enumerate(channels):
        ax = fig.add_subplot(2, 3, c + 1)

        for i, par in enumerate(df[param].unique()):
            df_sub = df[df[param] == par]
            mdf = df_sub.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
            ax.plot(mdf['date'], mdf['CI_50'], color=palette[i], label=round(par,3))
            ax.fill_between(mdf['date'], mdf['CI_2pt5'], mdf['CI_97pt5'],
                            color=palette[i], linewidth=0, alpha=0.2)
            ax.fill_between(mdf['date'], mdf['CI_25'], mdf['CI_75'],
                            color=palette[i], linewidth=0, alpha=0.4)

        ax.set_title(titles[c], y=0.8, fontsize=12)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        ax.set_xlim(first_day, last_day)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        if c==len(channels)-1:
            ax.legend()
        if logscale :
            ax.set_ylim(0.1, ymax)
            ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0, ms=1)
        ax.plot(ref_df['date'], ref_df[data_channel_names[c]].rolling(window = 7, center=True).mean(), c='k', alpha=1.0)

    fig.tight_layout()
    if plot_path:
        plot_name = f'compare_to_data_covidregion_{str(ems_nr)}_{param}'
        if logscale == False :
            plot_name = plot_name + "_nolog"
        plt.savefig(os.path.join(plot_path, plot_name + '.png'))
        plt.savefig(os.path.join(plot_path,'pdf',  plot_name + '.pdf'), format='PDF')


def plot_sim_and_ref(df, ems_nr, ref_df, channels, data_channel_names, titles, first_day, last_day,
                     ymax=1000, plot_path=None, logscale=False):
    fig = plt.figure(figsize=(13, 6))
    palette = sns.color_palette('husl', 8)
    k = 0
    for c, channel in enumerate(channels):
        ax = fig.add_subplot(2, 3, c + 1)

        mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
        ax.plot(mdf['date'], mdf['CI_50'], color=palette[k])
        ax.fill_between(mdf['date'], mdf['CI_2pt5'], mdf['CI_97pt5'],
                        color=palette[k], linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'], mdf['CI_25'], mdf['CI_75'],
                        color=palette[k], linewidth=0, alpha=0.4)

        ax.set_title(titles[c], y=0.8, fontsize=12)
        # ax.legend()

        ax.set_title(titles[c], y=0.8, fontsize=12)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        ax.set_xlim(first_day, last_day)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        if logscale :
            ax.set_ylim(0.1, ymax)
            ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0, ms=1)
        ax.plot(ref_df['date'], ref_df[data_channel_names[c]].rolling(window = 7, center=True).mean(), c='k', alpha=1.0)
    fig.tight_layout()
    if plot_path:
        plot_name = 'compare_to_data_covidregion_' + str(ems_nr)
        if logscale == False :
            plot_name = plot_name + "_nolog"
        plt.savefig(os.path.join(plot_path, plot_name + '.png'))
        plt.savefig(os.path.join(plot_path,'pdf',  plot_name + '.pdf'), format='PDF')

def compare_county(exp_name, county_name, first_day, last_day) :

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', '200401_aggregated_data_cleaned.csv'))
    ref_df = ref_df[ref_df['county'] == county_name]
    ref_df['spec_date'] = pd.to_datetime(ref_df['spec_date'])
    ref_df = ref_df.rename(columns={'spec_date' : 'date'})

    df = load_sim_data(exp_name)
    df['critical_with_suspected'] = df['critical']


    channels = ['new_detected', 'new_hosp_det', 'detected_cumul', 'hosp_det_cumul']
    data_channel_names = ['new_case', 'new_hospitalizations', 'total_case', 'total_hospitalizations']

    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data')
    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names,
                     plot_path=plot_path, first_day=first_day, last_day=last_day)

    fname = 'emresource_20200325_20200403.csv'
    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH/Corona virus reports', fname))
    ref_df = ref_df[ref_df['region'] == 11]
    ref_df['suspected_and_confirmed_covid_icu'] = ref_df['suspected_covid_icu'] + ref_df['confirmed_covid_icu']
    data_channel_names = ['suspected_and_confirmed_covid_icu', 'confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'confirmed_covid_on_vents']
    ref_df = ref_df.groupby('date_of_extract')[data_channel_names].agg(np.sum).reset_index()
    ref_df['date'] = pd.to_datetime(ref_df['date_of_extract'])

    df['ventilators'] = df['critical']*0.8

    channels = ['critical_with_suspected', 'deaths', 'critical', 'ventilators']
    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_emr')
    plot_sim_and_ref_Ki(df, ref_df, channels=channels, data_channel_names=data_channel_names,
                     plot_path=plot_path, first_day=first_day, last_day=last_day)
    plt.show()

def compare_ems(exp_name, ems, first_day, last_day,param=None) :

    df = load_sim_data(exp_name)
    df = df[df['date'].between(first_day, last_day)]
    df['critical_with_suspected'] = df['critical']

    ref_df = load_ref_df(ems_nr=ems)
    outcome_channels, channels, data_channel_names, titles = get_datacomparison_channels()

    plot_path = os.path.join(wdir, 'simulation_output', exp_name, '_plots')
    if param == None :
        plot_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,
                         plot_path=plot_path, first_day=first_day, last_day=last_day)
    else :
        plot_sim_and_ref_by_param(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,
                         plot_path=plot_path,first_day=first_day, last_day=last_day, param=param)


if __name__ == '__main__' :

    args = parse_args()
    stem = args.stem
    Location = args.Location
    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    first_plot_day = pd.Timestamp('2020-02-13')
    today = pd.Timestamp.today()+ pd.Timedelta(15,'days')
    last_plot_day = today

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names :

        region = exp_name.split('_')[1]

        if("EMS" in exp_name) :
            ems_nr = exp_name.split('_')[2]
            region = exp_name.split('_')[1]

        if region == 'NMH_catchment':
            compare_NMH(exp_name)
        elif region == 'Chicago':
            compare_county(exp_name,  county_name='Cook')
        elif region == 'EMS':
            compare_ems(exp_name,  ems=int(ems_nr),first_day=first_plot_day, last_day=last_plot_day)
            #compare_ems(exp_name,  ems=int(ems_nr), param='Ki')
            print(exp_name)
        elif region == 'IL':
            compare_ems(exp_name, source='line_list')
