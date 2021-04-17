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
        help="Name of simulation experiment",
        default="20201202_IL_mr_v0_testrun"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default="Local"
    )
    return parser.parse_args()


def plot_Ki(exp_name,first_day,last_day):

    base_list = ['time', 'startdate', 'scen_num', 'sample_num', 'run_num']
    """Get group names"""
    grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=sim_output_path)
    grp_list = [grp for grp in grp_list if grp !="All"]

    column_list = base_list + [f'Ki_t_{grp}' for grp in grp_list ]
    df = load_sim_data(exp_name, region_suffix=None, column_list=column_list)
    df = df[df['date'].between(pd.Timestamp(first_day), pd.Timestamp(last_day))]

    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    palette = sns.color_palette('Set1', 12)

    for c, grp in enumerate(grp_list):
        ax = fig.add_subplot(3, 4, c + 1)
        mdf = df.groupby('date')[f'Ki_t_{grp}'].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        ax.set_title(grp.replace('_EMS-', 'COVID-19 Region '))
        ax.plot(mdf['date'], mdf['CI_50'], color=palette[0])
        ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'], color=palette[0], linewidth=0, alpha=0.2)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))

    plotname = f'Ki_by_covidregion'
    plt.suptitle('Time varying transmission rate (Ki_t)', x=0.5, y=0.999, fontsize=14)
    plt.tight_layout()

    plt.savefig(os.path.join(plot_path, plotname + '.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', plotname + '.pdf'), format='PDF')


if __name__ == '__main__' :

    args = parse_args()
    stem = args.stem
    Location = args.Location

    first_plot_day = pd.Timestamp('2020-12-01') #pd.Timestamp.today()- pd.Timedelta(60,'days')
    last_plot_day = pd.Timestamp.today()+ pd.Timedelta(90,'days')

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)


    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')

        plot_Ki(exp_name,first_day=first_plot_day, last_day=last_plot_day)
