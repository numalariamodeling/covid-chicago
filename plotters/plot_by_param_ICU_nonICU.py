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
    return parser.parse_args()

def plot_on_fig(df, c, axes,channel, color,panel_heading, ems, label=None, addgrid=True) :
    ax = axes[c]
    mdf = df.groupby('date')[channel].agg([np.min,CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75,np.max]).reset_index()

    if addgrid:
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
    ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
    ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],color=color, linewidth=0, alpha=0.4)
    ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],color=color, linewidth=0, alpha=0.3)
    ax.fill_between(mdf['date'].values, mdf['amin'], mdf['amax'],color=color, linewidth=0, alpha=0.1)
    ax.set_title(panel_heading)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))

    ref_df = compare_ems(ems=ems, channel=channel)

    if channel=="hosp_det":
        datachannel = 'covid_non_icu'
        capacitychannel = 'hosp_det'
    if channel=="crit_det":
        datachannel = 'confirmed_covid_icu'
        capacitychannel = 'crit_det'

    ax.plot(ref_df['date'], ref_df[datachannel], 'o', color='#303030', linewidth=0, ms=3)
    ax.plot(ref_df['date'], ref_df[datachannel].rolling(window=7, center=True).mean(), c='k', alpha=1.0)

    capacity = load_capacity(ems)
    ax.plot([np.min(mdf['date']), np.max(mdf['date'])],[capacity[capacitychannel], capacity[capacitychannel]], '--', linewidth=1, color='black')
    ax.plot([np.min(mdf['date']), np.max(mdf['date'])],[capacity[capacitychannel]*0.75, capacity[capacitychannel]*0.75], '--', linewidth=0.8, color='grey')

def plot_on_fig2(df, axes,  ems_nr, label=None, addgrid=True) :
    palette = sns.color_palette('Set1', 2)
    for c, channel in enumerate(['hosp_det','crit_det']):
        ax = axes[c]
        mdf = df.groupby('date')[channel].agg([np.min, CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75, np.max]).reset_index()

        if addgrid ==True : ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        ax.plot(mdf['date'], mdf['CI_50'], color=palette[0], label=label)
        ax.fill_between(mdf['date'], mdf['CI_25'], mdf['CI_75'], color=palette[0], linewidth=0, alpha=0.4)
        ax.fill_between(mdf['date'], mdf['CI_2pt5'], mdf['CI_97pt5'], color=palette[0], linewidth=0, alpha=0.3)
        ax.fill_between(mdf['date'], mdf['amin'], mdf['amax'], color=palette[0], linewidth=0, alpha=0.1)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))

        ref_df = compare_ems(ems=ems_nr, channel=channel)

        if channel=="hosp_det":
            datachannel = 'covid_non_icu'
            capacitychannel = 'hosp_det'
            channel_label = 'hospital census'
        if channel=="crit_det":
            datachannel = 'confirmed_covid_icu'
            capacitychannel = 'crit_det'
            channel_label = 'intensive case unit census'

        ax.plot(ref_df['date'], ref_df[datachannel], 'o', color='#303030', linewidth=0, ms=3)
        ax.plot(ref_df['date'], ref_df[datachannel].rolling(window=7, center=True).mean(), c='k', alpha=1.0)

        capacity = load_capacity(ems_nr)
        ax.plot([np.min(mdf['date']), np.max(mdf['date'])],
                    [capacity[capacitychannel], capacity[capacitychannel]], '--', linewidth=1, color='black')
        ax.set_title('capacity limit', y=0.86)
        ax.set_ylabel(f'predicted {channel_label}')
        ax.set_xlim(first_plot_day, last_plot_day)

def compare_ems( ems,channel):
    ref_df = load_ref_df(ems_nr=ems)

    if channel == "hosp_det":
        data_channel_names = ['covid_non_icu']
    if channel == "crit_det":
        data_channel_names = ['confirmed_covid_icu']

    ref_df = ref_df.groupby('date')[data_channel_names].agg(np.sum).reset_index()
    ref_df = ref_df[ref_df['date'].between(first_plot_day, last_plot_day)]

    return ref_df

def plot_covidregions(channel,subgroups, plot_path,first_day, last_day) :

    fig = plt.figure(figsize=(16,8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    palette = sns.color_palette('husl', len(exp_names))
    axes = [fig.add_subplot(3, 4, x + 1) for x in range(len(subgroups))]

    for c, ems_nr in enumerate(subgroups) :

        if ems_nr == 0:
            region_suffix = "_All"
            region_label = 'Illinois'
        else:
            region_suffix = "_EMS-" + str(ems_nr)
            region_label = region_suffix.replace('_EMS-', 'COVID-19 Region ')

        for d, exp_name in enumerate(exp_names) :
            df = load_sim_data(exp_name, region_suffix=region_suffix)
            df = df[(df['date'] >= first_day) & (df['date'] <= last_day)]
            exp_name_label = int(exp_name.split('_')[0])
            plot_on_fig(df, c, axes, channel=channel, color=palette[d],ems=ems_nr, panel_heading = region_label, label="")

        axes[-1].legend()
        #fig.suptitle(x=0.5, y=0.999,t=channel)
        plt.tight_layout()

    plt.savefig(os.path.join(plot_path, f'covidregion_{channel}.png'))
    plt.savefig(os.path.join(plot_path,'pdf', f'covidregion_{channel}.pdf'))

if __name__ == '__main__' :

    args = parse_args()
    exp_names = args.exp_names
    Location = args.Location

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    first_plot_day = pd.Timestamp.today()- pd.Timedelta(60,'days')
    last_plot_day = pd.Timestamp.today()+ pd.Timedelta(15,'days')

    covidregionlist = range(0, 12)

    plot_path = os.path.join(wdir, 'simulation_output', exp_names[len(exp_names)-1], '_plots')
    plot_covidregions(channel='crit_det', subgroups=covidregionlist,
                      plot_path=plot_path, first_day= first_plot_day, last_day=last_plot_day)
    plot_covidregions(channel='hosp_det', subgroups=covidregionlist,
                      plot_path=plot_path, first_day= first_plot_day, last_day=last_plot_day)