"""
Compare COVID-19 simulation outputs to data.
Used for spatial - covidregion - model
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
        default = "Local"
    )

    return parser.parse_args()
    
def plot_sim_and_ref(df, ems_nr, ref_df, channels, data_channel_names, titles, region_label,
                     first_day, last_day,plot_path, ymax=10000, logscale=False,plot_name_suffix=None):

    fig = plt.figure(figsize=(13, 6))
    palette = sns.color_palette('husl', 8)
    k = 0
    for c, channel in enumerate(channels):
        ax = fig.add_subplot(2, 3, c + 1)

        mdf = df.groupby('date')[channel].agg([CI_50,CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
        ax.plot(mdf['date'], mdf['CI_50'], color=palette[k])
        ax.fill_between(mdf['date'], mdf['CI_2pt5'], mdf['CI_97pt5'],
                        color=palette[k], linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'], mdf['CI_25'], mdf['CI_75'],
                        color=palette[k], linewidth=0, alpha=0.4)

        ax.set_title(titles[c], y=0.8, fontsize=12)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        ax.set_xlim(first_day, last_day)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        if logscale :
            ax.set_ylim(0.1, ymax)
            ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0, ms=1)
        ax.plot(ref_df['date'], ref_df[data_channel_names[c]].rolling(window = 7, center=True).mean(), c='k', alpha=1.0)

    fig.suptitle(region_label, y=1, fontsize=14)
    fig.tight_layout()
    fig.subplots_adjust(top=0.88)

    plot_name = 'compare_to_data_covidregion_' + str(ems_nr)
    if logscale == False :
        plot_name = plot_name + "_nolog"
    if plot_name_suffix is not None:
        plot_name= plot_name + plot_name_suffix
    plt.savefig(os.path.join(plot_path, plot_name + '.png'))
    plt.savefig(os.path.join(plot_path,'pdf', plot_name + '.pdf'), format='PDF')

def compare_ems(exp_name, ems_nr,first_day,last_day,plot_path):

    if ems_nr == 0:
        region_suffix = "_All"
        region_label = 'Illinois'
    else:
        region_suffix = "_EMS-" + str(ems_nr)
        region_label = region_suffix.replace('_EMS-', 'COVID-19 Region ')

    column_list = ['time', 'startdate', 'scen_num', 'sample_num','run_num']
    outcome_channels, channels, data_channel_names, titles = get_datacomparison_channels()
    
    for channel in outcome_channels:
        column_list.append(channel + region_suffix)

    df = load_sim_data(exp_name, region_suffix=region_suffix, column_list=column_list)
    df = df[df['date'].between(first_day, last_day)]

    df['critical_with_suspected'] = df['critical']

    ref_df = load_ref_df(ems_nr)

    #plot_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,
    #                 region_label=region_label,first_day= first_day, last_day= last_day,plot_path=plot_path, logscale=True)
    plot_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,
                     region_label=region_label, first_day= first_day, last_day= last_day,plot_path=plot_path)


if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    Location = args.Location

    first_plot_day = pd.Timestamp('2020-02-13')
    last_plot_day = pd.Timestamp.today()+ pd.Timedelta(15,'days')

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        sim_output_path  = os.path.join(wdir, 'simulation_output',exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')
        for ems_nr in range(1,12):
            print("Start processing region " + str(ems_nr))
            compare_ems(exp_name, ems_nr=int(ems_nr),first_day=first_plot_day,last_day=last_plot_day,plot_path=plot_path)
