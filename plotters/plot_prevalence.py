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

# from plotting.colors import load_color_palette

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


def trim_trajectories(simpath, scenario, colnames, ems):
    """also see plotter 'trim_trajectoriesDat.py' """
    df = pd.read_csv(os.path.join(simpath, 'trajectoriesDat.csv'))
    df = df.rename(columns={'N_EMS_%d' % ems_num: 'N_EMS-%d' % ems_num for ems_num in range(1, 12)})
    df['N_All'] = df['susceptible_All'] + df['exposed_All'] + df['infected_All'] + df['recovered_All']
    keep_cols = ['%s_%s' % (x, y) for x in colnames for y in ems]
    df['startdate'] = pd.to_datetime(df['startdate'])
    df['date'] = df.apply(lambda x: x['startdate'] + timedelta(days=x['time']), axis=1)
    df = df[['date'] + keep_cols]
    df.to_csv(os.path.join(simpath, 'trimmed_trajectoriesDat_%s.csv' % scenario), index=False)


def plot_prevalences(exp_name, first_day, last_day, channels, fname='trajectoriesDat.csv'):

    ems = ['All'] + ['EMS-%d' % x for x in range(1, 12)]
    get_det =0
    for ch in channels:
        if 'det' in ch: get_det = get_det + 1

        column_list = ['time', 'startdate', 'scen_num', 'run_num', 'sample_num']
        for ems_num in ems:
            column_list.append('N_' + str(ems_num.replace("-", "_")))
            column_list.append('infected_' + str(ems_num))
            column_list.append('infected_cumul_' + str(ems_num))
            column_list.append('recovered_' + str(ems_num))
            column_list.append('deaths_' + str(ems_num))
            if get_det >0:
                column_list.append('infected_det_' + str(ems_num))
                column_list.append('infected_det_cumul_' + str(ems_num))
                column_list.append('recovered_det_' + str(ems_num))
                column_list.append('deaths_det_' + str(ems_num))
        df = load_sim_data(exp_name, region_suffix=None, fname=fname, column_list=column_list, add_incidence=False)

        for ems_num in ems:
            sort_channels = ['scen_num','sample_num','run_num','time']
            group_channels = ['scen_num','sample_num','run_num']
            df[f'new_deaths_{ems_num}'] = df.sort_values(sort_channels).groupby(group_channels)[f'deaths_{ems_num}'].diff()
            df[f'new_recovered_{ems_num}'] = df.sort_values(sort_channels).groupby(group_channels)[f'recovered_{ems_num}'].diff()
            if get_det > 0:
                df[f'new_deaths_det_{ems_num}'] = df.sort_values(sort_channels).groupby(group_channels)[f'deaths_det_{ems_num}'].diff()
                df[f'new_recovered_det_{ems_num}'] = df.sort_values(sort_channels).groupby(group_channels)[f'recovered_det_{ems_num}'].diff()

        df = calculate_prevalence(df,ems=ems)
        #df.to_csv(os.path.join(wdir, 'simulation_output', exp_name, "prevalenceDat.csv"), index=False, date_format='%Y-%m-%d')

    df = df[(df['date'] >= first_day) & (df['date'] <= last_day)]
    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    palette = sns.color_palette('husl', 8)
    for e, ems_num in enumerate(ems):
        ax = fig.add_subplot(3, 4, e + 1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        for k, channel in enumerate(channels):
            plot_label = ''
            if len(channels) > 1:
                plot_label = channel #channel.split('_')[0]
            channel_label = channel
            channel = f'{channel}_{ems_num}'
            df[channel] = df[channel].astype(float)
            mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
            ax.plot(mdf['date'], mdf['CI_50'], color=palette[k], label=plot_label)
            ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
                            color=palette[k], linewidth=0, alpha=0.2)
            ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                            color=palette[k], linewidth=0, alpha=0.4)
        if ems_num == 'EMS-1':
            ax.legend()
        plotsubtitle = ems_num.replace('EMS-', 'COVID-19 Region ')
        if ems_num == 'All':
            plotsubtitle = ems_num.replace('All', 'Illinois')
        ax.set_title(plotsubtitle)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        ax.set_xlim(first_day, last_day)
        ax.axvline(x=date.today(), color='#666666', linestyle='--')

    if len(channels) == 1:
        fig.suptitle(x=0.5, y=0.999, t=channel_label)

    fig_name = channels[0]
    if len(channels) == 2:
        fig_name = channels[0] + '-' + channels[1]

    plt.savefig(os.path.join(plot_path, f'{fig_name}_by_covidregion.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{fig_name}_by_covidregion.pdf'), format='PDF')


if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    trajectoriesName = args.trajectoriesName
    Location = args.Location

    first_plot_day = date.today() - timedelta(300)
    last_plot_day = date.today() + timedelta(15)

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        plot_path = os.path.join(wdir, 'simulation_output', exp_name, '_plots')

        plot_prevalences(exp_name, channels=['prevalence'], fname=trajectoriesName, first_day=first_plot_day,last_day=last_plot_day)
        plot_prevalences(exp_name, channels=['seroprevalence'], fname=trajectoriesName, first_day=first_plot_day,last_day=last_plot_day)
        plot_prevalences(exp_name, channels=['IFR'], fname=trajectoriesName, first_day=first_plot_day,last_day=last_plot_day)
        plot_prevalences(exp_name, channels=['IFR_t'], fname=trajectoriesName, first_day=first_plot_day,last_day=last_plot_day)
        plot_prevalences(exp_name, channels=['IFR', 'IFR_det'], fname=trajectoriesName, first_day=first_plot_day, last_day=last_plot_day)
        plot_prevalences(exp_name, channels=['seroprevalence', 'seroprevalence_det'], fname=trajectoriesName, first_day=first_plot_day, last_day=last_plot_day)
        plot_prevalences(exp_name, channels=['prevalence', 'prevalence_det'], fname=trajectoriesName, first_day=first_plot_day, last_day=last_plot_day)
