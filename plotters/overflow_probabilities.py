import os
import argparse
import sys

sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


mpl.rcParams['pdf.fonttype'] = 42
sns.set_style('whitegrid', {'axes.linewidth': 0.5})


def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-s",
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
        "-perc",
        "--overflow_threshold_percents",
        type=float,
        nargs='+',
        help="Calculate probability for specified percent of capacity limit",
        default=99
    )
    return parser.parse_args()


def get_latest_filedate(file_path=os.path.join(datapath, 'covid_IDPH', 'Corona virus reports',
                                               'hospital_capacity_thresholds'), extraThresholds=False):
    files = os.listdir(file_path)
    files = sorted(files, key=len)
    if extraThresholds == False:
        files = [name for name in files if not 'extra_thresholds' in name]
    if extraThresholds == True:
        files = [name for name in files if 'extra_thresholds' in name]

    filedates = [item.replace('capacity_weekday_average_', '') for item in files]
    filedates = [item.replace('.csv', '') for item in filedates]
    latest_filedate = max([int(x) for x in filedates])
    fname = f'capacity_weekday_average_{latest_filedate}.csv'
    if extraThresholds == True:
        fname = f'capacity_weekday_average_{latest_filedate}__extra_thresholds.csv'
    return fname


def get_probs(ems_nr, channels=['total_hosp_census', 'crit_det', 'ventilators'], overflow_threshold_percents=[1, 0.8],
              param=None, save_csv=False, plot=True):
    """Define columns and labels"""
    if ems_nr == 0:
        region_suffix = "_All"
        region_label = 'Illinois'
    else:
        region_suffix = "_EMS-" + str(ems_nr)
        region_label = region_suffix.replace('_EMS-', 'COVID-19 Region ')

    column_list = ['scen_num', 'sample_num', 'time', 'startdate']
    grp_channels = ['date']
    if param is not None:
        column_list = column_list + param
        grp_channels = ['date'] + param

    column_list_t = column_list
    for channel in ['hosp_det', 'crit_det']:
        column_list_t.append(channel + region_suffix)

    """ Load dataframes"""
    df = load_sim_data(exp_name, region_suffix=region_suffix, column_list=column_list, add_incidence=False)
    df['total_hosp_census'] = df['hosp_det'] + df['crit_det']
    df['ventilators'] = get_vents(df['crit_det'])

    capacity_df = load_capacity(ems_nr)
    len(df['scen_num'].unique())
    df['N_scen_num'] = df.groupby(grp_channels)['scen_num'].transform('count')

    df_all = pd.DataFrame()
    for channel in channels:
        if channel == "crit_det": channel_label = 'icu_availforcovid'
        #if channel == "hosp_det": channel_label = 'hb_availforcovid'
        if channel == "total_hosp_census": channel_label = 'hb_availforcovid'
        if channel == "ventilators": channel_label = 'vent_availforcovid'

        for overflow_threshold_percent in overflow_threshold_percents:
            thresh = capacity_df[f'{channel}'] * overflow_threshold_percent

            mdf = df.copy()
            mdf.loc[df[f'{channel}'] < thresh, 'above_yn'] = 0
            mdf.loc[df[f'{channel}'] >= thresh, 'above_yn'] = 1

            mdf = mdf.groupby(grp_channels)['above_yn'].agg(['sum', 'count', 'nunique']).rename_axis(None, axis=0)
            mdf = mdf.reset_index()
            mdf['prob'] = mdf['sum'] / mdf['count']

            mdf = mdf.rename(columns={'sum': 'n_above', 'count': 'N_scen_num', 'index': 'date'})
            mdf['overflow_threshold_percent'] = overflow_threshold_percent
            mdf['capacity_channel'] = channel_label
            mdf['availforcovid'] = capacity_df[f'{channel}']
            mdf['region'] = ems_nr
            del thresh

            if df_all.empty:
                df_all = mdf
            else:
                df_all = pd.concat([df_all, mdf])
            del mdf
    if plot:
        plot_probs(df=df_all, region_label=region_label)

    if save_csv:
        filename = f'overflow_probabilities_over_time_region_{ems_nr}.csv'
        df_all.to_csv(os.path.join(sim_output_path, filename), index=False, date_format='%Y-%m-%d')
    return df_all


def plot_probs(df, region_label):
    fig = plt.figure(figsize=(12, 4))
    fig.suptitle(region_label, y=0.97, fontsize=14)
    fig.subplots_adjust(right=0.98, wspace=0.2, left=0.05, hspace=0.4, top=0.84, bottom=0.13)
    palette = sns.color_palette('Set1', 12)
    axes = [fig.add_subplot(1, 3, x + 1) for x in range(3)]

    linestyles = ['solid','dashed']
    for c, channel in enumerate(df.capacity_channel.unique()):

        mdf = df[df['capacity_channel'] == channel]
        ax = axes[c]
        ax.set_ylim(0, 1)
        ax.set_title(channel)
        ax.set_ylabel(f'Probability of overflow')

        for e, t in enumerate(list(df.overflow_threshold_percent.unique())):
            line_label = f'{channel} ({t*100})%'
            adf = mdf[mdf['overflow_threshold_percent'] == t]
            ax.plot(adf['date'], adf['prob'], linestyle=linestyles[e], color=palette[c], label=line_label)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b\n%Y'))

    axes[-1].legend()

    plotname = f'overflow_probabilities_{region_label}'
    plt.savefig(os.path.join(plot_path, f'{plotname}.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{plotname}.pdf'))


def write_probs_to_template(df, plot=True):
    fname_capacity = get_latest_filedate()
    civis_template = pd.read_csv(
        os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'hospital_capacity_thresholds', fname_capacity))
    civis_template = civis_template.drop_duplicates()
    civis_template['date_window_upper_bound'] = pd.to_datetime(civis_template['date_window_upper_bound'])

    civis_template_all = pd.DataFrame()
    for index, row in civis_template.iterrows():
        upper_limit = row['date_window_upper_bound']
        lower_limit = upper_limit - timedelta(7)

        df_sub = df[df['date'].between(lower_limit, upper_limit)]
        df_sub = df_sub[df_sub['region'] == int(row['geography_modeled'].replace("covidregion_", ""))]
        df_sub = df_sub[df_sub['capacity_channel'] == row['resource_type']]
        df_sub = df_sub[df_sub['overflow_threshold_percent'] == row['overflow_threshold_percent']]

        """Take maximum of previous 7 days"""
        civis_template.loc[index, 'percent_of_simulations_that_exceed'] = df_sub['prob'].max()

    if civis_template_all.empty:
        civis_template_all = civis_template
    else:
        civis_template_all = pd.concat([civis_template_all, civis_template])

    """Replace NAs with zero """
    civis_template_all['percent_of_simulations_that_exceed'] = civis_template_all[
        'percent_of_simulations_that_exceed'].fillna(0)
    """Scenario name of simulation - here hardcoded to baseline!!"""
    civis_template_all['scenario_name'] = 'baseline'
    file_str = 'nu_hospitaloverflow_' + str(exp_name[:8]) + '.csv'
    civis_template_all.to_csv(os.path.join(sim_output_path, file_str), index=False)

    if plot:
        plot_probs_from_template(df=civis_template_all)


def plot_probs_from_template(df=None, show_75=True):
    if df is None:
        file_str = 'nu_hospitaloverflow_' + str(exp_name[:8]) + '.csv'
        df = pd.read_csv(os.path.join(sim_output_path, file_str))

    regionlist = df['geography_modeled'].unique()
    df['date_md'] = df['date_window_upper_bound'].dt.strftime('%m-%d\n%Y')
    df['region'] = df['geography_modeled'].str.replace('covidregion_', '')

    fig = plt.figure(figsize=(14, 12))
    fig.suptitle('Overflow probability per week dates by COVID-19 Region', y=0.97, fontsize=14)
    fig.subplots_adjust(right=0.98, wspace=0.4, left=0.05, hspace=0.4, top=0.90, bottom=0.07)
    palette = sns.color_palette('Set1', len(df.resource_type.unique()))
    axes = [fig.add_subplot(4, 3, x + 1) for x in range(len(regionlist))]

    for c, reg_nr in enumerate(regionlist):
        reg_label = reg_nr.replace('covidregion_', 'COVID-19 Region ')
        mdf = df[df['geography_modeled'] == reg_nr]
        ax = axes[c]
        ax.set_ylim(0, 1)
        ax.set_title(reg_label)
        ax.set_ylabel(f'Probability of overflow')

        for e, t in enumerate(list(df.resource_type.unique())):
            adf = mdf[mdf['resource_type'] == t]
            adf1 = adf[adf['overflow_threshold_percent'] == 1]
            adf2 = adf[adf['overflow_threshold_percent'] != 1]
            ax.plot(adf1['date_md'], adf1['percent_of_simulations_that_exceed'], color=palette[e], label=t)
            if show_75:
                ax.plot(adf2['date_md'], adf2['percent_of_simulations_that_exceed'], color=palette[e], label='',
                        alpha=0.5)

    axes[-1].legend()

    plt.savefig(os.path.join(plot_path, 'overflow_probabilities.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', 'overflow_probabilities.pdf'))


if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    Location = args.Location
    overflow_threshold_percents = args.overflow_threshold_percents
    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    first_day = pd.Timestamp(date.today()) - timedelta(14)
    last_day = pd.Timestamp(date.today()) + timedelta(90)

    if overflow_threshold_percents ==99:
        fname_capacity = get_latest_filedate()
        civis_template = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'hospital_capacity_thresholds', fname_capacity))
        overflow_threshold_percents = civis_template.overflow_threshold_percent.unique()
    print(overflow_threshold_percents)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        print(exp_name)
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')

        df_all = pd.DataFrame()
        for ems_nr in range(1, 12):
            print("Start processing region " + str(ems_nr))
            df = get_probs(ems_nr, overflow_threshold_percents=overflow_threshold_percents, save_csv=False, plot=False)
            df = df[df['date'].between(first_day, last_day)]
            if df_all.empty:
                df_all = df
            else:
                df_all = pd.concat([df_all, df])
        df_all.to_csv(os.path.join(sim_output_path, 'overflow_probabilities.csv'), index=False)
        write_probs_to_template(df=df_all)
