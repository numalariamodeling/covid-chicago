import argparse
import os
import pandas as pd
import numpy as np
import sys

sys.path.append('../')
from load_paths import load_box_paths

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns


#from plotting.colors import load_color_palette
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
        "--labels",
        type=str,
        nargs='+',
        help="Experiment labels, if not specified will be extracted from exp_names"
    )
    parser.add_argument(
        "-ch",
        "--channel",
        type=str,
        default = 'deaths',
        help="Outcome channel to plot"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default = "Local"
    )
    return parser.parse_args()


def cumulative_barplot(exp_names,channel,labels, first_day,last_day,  region="All"):

    fig = plt.figure(figsize=(6, 4))
    fig.subplots_adjust(left=0.2)
    ax = fig.gca()
    #p = load_color_palette('wes')
    #palette = [p[x] for x in [8, 4, 2, 1, 3]]
    palette = ('#913058', "#F6851F", "#00A08A", "#D61B5A", "#5393C3", "#F1A31F", "#98B548", "#8971B3", "#969696")
    first_md = first_day.strftime('%b %d')
    last_md = last_day.strftime('%b %d')

    for s, exp_name in enumerate(exp_names):
        simpath = os.path.join(projectpath, 'cms_sim', 'simulation_output', exp_name)
        exp_date = exp_name.split("_")[0]
        fname = f'nu_{exp_date}_{region}.csv'

        df = pd.read_csv(os.path.join(simpath, fname))
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'].between(pd.Timestamp(first_day), pd.Timestamp(last_day))]

        ax.bar([s], np.sum(df['%s_median' % channel]), align='center', color=palette[s], label=labels[s])
        ax.plot([s, s], [np.sum(df['%s_lower' % channel]), np.sum(df['%s_upper' % channel])], color='k', linewidth=0.5)
    ax.legend()
    ax.set_ylabel(f'cumulative {channel} {first_md} - {last_md}')
    plt.savefig(os.path.join(plot_path, f'{channel}_barplot.png'))
    plt.savefig(os.path.join(plot_path,"pdf", f'{channel}_barplot.pdf'), format='PDF')
    #plt.show()

def timeline_plot(exp_names,channel,labels, first_day,last_day,  region="All"):

    fig = plt.figure(figsize=(6, 4))
    fig.subplots_adjust(left=0.2)
    ax = fig.gca()
    #p = load_color_palette('wes')
    #palette = [p[x] for x in [8, 4, 2, 1, 3]]
    palette = ('#913058', "#F6851F", "#00A08A", "#D61B5A", "#5393C3", "#F1A31F", "#98B548", "#8971B3", "#969696")

    for s, exp_name in enumerate(exp_names):
        simpath = os.path.join(projectpath, 'cms_sim', 'simulation_output', exp_name)
        exp_date = exp_name.split("_")[0]
        fname = f'nu_{exp_date}_{region}.csv'

        df = pd.read_csv(os.path.join(simpath, fname))
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'].between(pd.Timestamp(first_day), pd.Timestamp(last_day))]
        ax.plot(df['date'], df['%s_median' % channel], color=palette[s], label=labels[s])
        ax.fill_between(df['date'], df['%s_lower' % channel], df['%s_upper' % channel], color=palette[s], linewidth=0, alpha=0.4)

    ax.legend()
    ax.set_ylabel(f'{channel}')
    plt.savefig(os.path.join(plot_path, f'{channel}_timelineplot.png'))
    plt.savefig(os.path.join(plot_path,"pdf", f'{channel}_timelineplot.pdf'), format='PDF')
    #plt.show()

if __name__ == '__main__':

    args = parse_args()
    exp_names = args.exp_names
    labels = args.labels
    channel = args.channel
    Location = args.Location
    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    if labels == None:
        labels = [''.join(exp.split("_")[-3:]) for exp in exp_names]

    plot_path = os.path.join(wdir, 'simulation_output', exp_names[len(exp_names) - 1], '_plots')

    first_day = pd.Timestamp('2020-02-01')
    last_day = pd.Timestamp('2021-06-01')

    cumulative_barplot(exp_names,channel,labels, first_day,last_day, region="All")
    timeline_plot(exp_names,channel,labels, first_day,last_day, region="All")
