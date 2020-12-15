import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
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
        help="Name of simulation experiment",default="20201202_IL_mr_v0_testrun"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default = "Local"
    )
    parser.add_argument(
        "-t", "--trajectoriesName",
        type=str,
        help="Name of trajectoriesDat file, trajectoriesDat.csv or trajectoriesDat_trim.csv",
        default='trajectoriesDat.csv',
    )
    return parser.parse_args()

def plot_on_fig(df, channels, axes, color, label, addgrid=True) :

    for c, channel in enumerate(channels) :
        ax = axes[c]

        for scen in  df['scen_num'].unique():
            pdf = df[df['scen_num']==scen]
            ax.plot(pdf['date'], pdf[channel], color=color, label=label)

        if addgrid :
            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)

        ax.set_title(' '.join(channel.split('_')), y=0.85)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        #ax.set_ylim(0, max(df[channel])+10)

def plot_on_fig2(df, c, axes,channel, color,panel_heading, label, addgrid=True, ymax=50) :
    ax = axes[c]
    if addgrid:
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
    for scen in list(df['scen_num'].unique()):
        pdf = df[df['scen_num'] == scen]
        ax.plot(pdf['date'], pdf[channel], color=color, label=label)

    ax.set_title(panel_heading, y=0.85)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
    ax.set_ylim(0, ymax)

def plot_main(nscen=None, showLegend =True) :
    fig = plt.figure(figsize=(15, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
    palette = sns.color_palette('GnBu_d', len(exp_names))

    channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']
    axes = [fig.add_subplot(3, 2, x + 1) for x in range(len(channels))]

    for d, exp_name in enumerate(exp_names) :
        df = load_sim_data(exp_name)
        df = df[(df['date'] >= first_plot_day) & (df['date'] <= last_plot_day)]

        if nscen != None :
            df = df[df['scen_num'].isin(nscen)]

        df['symptomatic_census'] = df['symptomatic_mild'] + df['symptomatic_severe']
        df['ventilators'] = get_vents(df['crit_det'].values)

        plot_on_fig(df, channels, axes, color=palette[d], label=exp_name)

    if showLegend:
        axes[-1].legend()

    plt.savefig(os.path.join(plot_path, 'trajectories_IL.png'))
    #plt.savefig(os.path.join(plot_path,'pdf', 'trajectories_IL.pdf'), format='PDF')

def plot_covidregions(subgroups =None,nscen=None, showLegend=True) :

    if subgroups == None:
        subgroups = ['_EMS-1', '_EMS-2', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-6', '_EMS-7', '_EMS-8', '_EMS-9',
                     '_EMS-10', '_EMS-11']

    for region_suffix in subgroups :

        region_label= region_suffix.replace('_EMS-', 'COVID-19 region ')
        region_label2 = region_label.replace(' ', '_')

        fig = plt.figure(figsize=(12, 8))
        fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
        palette = sns.color_palette('GnBu_d', len(exp_names))
        channels = ['infected', 'new_deaths', 'hospitalized', 'critical', 'd_Sym_t','Ki_t']
        axes = [fig.add_subplot(3, 2, x + 1) for x in range(len(channels))]


        for d, exp_name in enumerate(exp_names) :
            df = load_sim_data(exp_name, region_suffix=region_suffix, add_incidence=True)

            if nscen != None:
                df = df[df['scen_num'].isin(nscen)]

            df['symptomatic_census'] = df['symptomatic_mild'] + df['symptomatic_severe']
            df['ventilators'] = get_vents(df['crit_det'].values)

            plot_on_fig(df, channels, axes, color=palette[d], label=exp_name)

        if showLegend :
            axes[-1].legend()

        fig.suptitle(region_label)
        plt.savefig(os.path.join(plot_path, 'trajectories_%s.png' % region_label2))
        #plt.savefig(os.path.join(plot_path, 'pdf', 'trajectories_%s.pdf' % region_label2))

def plot_covidregions_inone(subgroups=None,channel='hospitalized',nscen=None,showLegend = True, ymax=50) :

    if subgroups ==None:
        subgroups = ['_EMS-1', '_EMS-2', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-6', '_EMS-7', '_EMS-8', '_EMS-9',
                 '_EMS-10', '_EMS-11']

    fig = plt.figure(figsize=(16,8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    palette = sns.color_palette('GnBu_d', len(exp_names))
    axes = [fig.add_subplot(3, 4, x + 1) for x in range(len(subgroups))]

    for c, region_suffix in enumerate(subgroups) :

        region_label= region_suffix.replace('_EMS-', 'COVID-19 region ')

        for d, exp_name in enumerate(exp_names) :
            df = load_sim_data(exp_name, region_suffix=region_suffix)

            if nscen != None:
                df = df[df['scen_num'].isin(nscen)]

            plot_on_fig2(df, c, axes, channel=channel, color=palette[d],
                         panel_heading = region_label,  label=exp_name, ymax=ymax)

        if showLegend :
            axes[-1].legend()

        fig.suptitle(x=0.5, y=0.999,t=channel)
        plt.tight_layout()
    plt.savefig(os.path.join(plot_path, 'trajectories_covidregion_%s.png' % channel))
    #plt.savefig(os.path.join(plot_path,'pdf', 'trajectories_covidregion_%s.pdf' % channel))


if __name__ == '__main__' :

    args = parse_args()
    stem = args.stem
    trajectoriesName = args.trajectoriesName
    Location = args.Location

    first_plot_day = date(2020, 3, 1)
    last_plot_day = date(2020, 12, 31)

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location="Local")

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    showLegend = False
    if len(exp_names) >1:
        showLegend = True

    plot_path = os.path.join(wdir, 'simulation_output', exp_names[len(exp_names) - 1], '_plots')
    plot_main(nscen=None, showLegend=showLegend)
    #plot_covidregions(nscen=None, showLegend=showLegend)
    plot_covidregions_inone(channel='Ki_t', nscen=None, showLegend=showLegend, ymax=1.5)
    plot_covidregions_inone(channel='d_Sym_t', nscen=None, showLegend=showLegend, ymax=1)
