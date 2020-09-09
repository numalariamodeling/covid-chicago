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
        default = "Local"
    )
    return parser.parse_args()
    
def load_sim_data(exp_name, ems_nr,  input_wdir=None, input_sim_output_path=None, column_list=None):

    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'), usecols=column_list)
    if 'Ki' not in df.columns.values:
        scen_df = pd.read_csv(os.path.join(sim_output_path, 'sampled_parameters.csv'))
        df = pd.merge(left=df, right=scen_df[['scen_num', 'Ki']], on='scen_num', how='left')

    #df.columns = df.columns.str.replace('_All', '')
    df.columns = df.columns.str.replace('_EMS-' +str(ems_nr), '')
    df['infected_cumul'] = df['infected'] + df['recovered'] + df['deaths']
    df = calculate_incidence(df)

    return df


def plot_sim_and_ref(df, ems_nr, ref_df, channels, data_channel_names, titles, first_day=date(2020, 2, 22),
                     ymax=40, plot_path=None, logscale=True):
    fig = plt.figure(figsize=(10, 6))
    palette = sns.color_palette('husl', 8)
    k = 0
    for c, channel in enumerate(channels):
        ax = fig.add_subplot(2, 3, c + 1)

        # for k, (ki, kdf) in enumerate(df.groupby('Ki')) :
        mdf = df.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
        dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
        ax.plot(dates, mdf['mean'], color=palette[k])
        ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                        color=palette[k], linewidth=0, alpha=0.2)
        ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                        color=palette[k], linewidth=0, alpha=0.4)

        ax.set_title(titles[c], y=0.8, fontsize=12)
        # ax.legend()

        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_xlim(first_day, datetoday)
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
        plt.savefig(os.path.join(wdir, 'simulation_output', exp_name,  plot_name + '.png'))
        plt.savefig(os.path.join(wdir, 'simulation_output', exp_name,  plot_name + '.pdf'), format='PDF')
    # return a


def compare_ems(exp_name, ems=0):

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'emresource_by_region.csv'))

    if ems > 0:
        ref_df = ref_df[ref_df['covid_region'] == ems]
    else:
        ref_df = ref_df.groupby('date_of_extract').agg(np.sum).reset_index()
    ref_df['suspected_and_confirmed_covid_icu'] = ref_df['suspected_covid_icu'] + ref_df['confirmed_covid_icu']
    data_channel_names = ['confirmed_covid_deaths_prev_24h', 'confirmed_covid_icu', 'covid_non_icu']
    ref_df = ref_df.groupby('date_of_extract')[data_channel_names].agg(np.sum).reset_index()
    ref_df['date'] = pd.to_datetime(ref_df['date_of_extract'])

    column_list = ['time', 'startdate', 'scen_num', 'sample_num','run_num']
    for ems_region in range(1, 12):
        column_list.append('susceptible_EMS-' + str(ems_region))
        column_list.append('infected_EMS-' + str(ems_region))
        column_list.append('recovered_EMS-' + str(ems_region))
        column_list.append('infected_cumul_EMS-' + str(ems_region))
        column_list.append('asymp_cumul_EMS-' + str(ems_region))
        column_list.append('asymp_det_cumul_EMS-' + str(ems_region))
        column_list.append('symp_mild_cumul_EMS-' + str(ems_region))
        column_list.append('symp_severe_cumul_EMS-' + str(ems_region))
        column_list.append('symp_mild_det_cumul_EMS-' + str(ems_region))
        column_list.append('symp_severe_det_cumul_EMS-' + str(ems_region))
        column_list.append('hosp_det_cumul_EMS-' + str(ems_region))
        column_list.append('hosp_cumul_EMS-' + str(ems_region))
        column_list.append('detected_cumul_EMS-' + str(ems_region))
        column_list.append('crit_cumul_EMS-' + str(ems_region))
        column_list.append('crit_det_cumul_EMS-' + str(ems_region))
        column_list.append('death_det_cumul_EMS-' + str(ems_region))
        column_list.append('deaths_EMS-' + str(ems_region))
        column_list.append('crit_det_EMS-' + str(ems_region))
        column_list.append('critical_det_EMS-' + str(ems_region))
        column_list.append('critical_EMS-' + str(ems_region))
        column_list.append('hospitalized_det_EMS-' + str(ems_region))
        column_list.append('hospitalized_EMS-' + str(ems_region))

    df = load_sim_data(exp_name, ems_nr, column_list=column_list)
    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')

    df['critical_with_suspected'] = df['critical']
    ref_df_emr = ref_df

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', '200831_jg_aggregated_covidregion.csv'))

    if ems > 0:
        ref_df = ref_df[ref_df['covid_region'] == ems]
    else:
        ref_df = ref_df.groupby('date').agg(np.sum).reset_index()
    ref_df['date'] = pd.to_datetime(ref_df['date'])

    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
    df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
    df = df[df['date']  <=  datetime.today()]
    ref_df_ll = ref_df
    ref_df = pd.merge(how='outer', left=ref_df_ll, left_on='date', right=ref_df_emr, right_on='date')
    ref_df = ref_df.sort_values('date')
    channels = ['new_detected_deaths', 'crit_det', 'hospitalized_det', 'new_detected_deaths', 'new_deaths',
                'new_detected_hospitalized']
    data_channel_names = ['confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'covid_non_icu', 'deaths', 'deaths', 'admissions']
    titles = ['New Detected\nDeaths (EMR)', 'Critical Detected (EMR)', 'Inpatient non-ICU\nCensus (EMR)', 'New Detected\nDeaths (LL)',
              'New Deaths (LL)', 'New Detected\nHospitalizations (LL)']
    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_combo')
    plot_sim_and_ref(df,ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles, ymax=10000,
                     plot_path=plot_path, first_day=first_day)

    # return ref_df_emr, ref_df_ll


if __name__ == '__main__':

    args = parse_args()  
    #Location = 'Local'
    Location = args.Location
    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()

    stem = args.stem
    #stem = "20200816_IL_testbaseline"
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    for exp_name in exp_names:
        for ems_nr in range(1,12):
            compare_ems(exp_name, ems=int(ems_nr))
