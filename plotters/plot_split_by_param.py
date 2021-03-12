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


def plot_on_fig(df, channels, axes, color, label, addgrid=True) :

    for c, channel in enumerate(channels) :
        ax = axes[c]
        mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
        if addgrid :
            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
        # ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
        #                 color=color, linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=color, linewidth=0, alpha=0.4)
        ax.set_title(' '.join(channel.split('_')), y=0.85)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
        ax.set_ylim(0, max(mdf['CI_75']))


def plot_on_fig2(df, c, axes,channel, color,panel_heading, label, addgrid=True) :
    ax = axes[c]

    mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
    if addgrid:
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
    ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
    ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                color=color, linewidth=0, alpha=0.4)
    ax.set_title(panel_heading, y=0.85)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
    if channel=='B_prev':
        ax.set_ylim(0, 1)
        ax.axhline(y=0.5, color='#737373', linestyle='--')
    else:
        ax.set_ylim(0, max(mdf['CI_75']))

def plot_main(channels=None) :

    if channels is None:
        channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']

    fig = plt.figure(figsize=(14, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    palette = sns.color_palette('Set1', len(exp_names))
    axes = [fig.add_subplot(3, 2, x + 1) for x in range(len(channels))]

    for d, exp_name in enumerate(exp_names) :
        df = load_sim_data(exp_name, fname='trajectoriesDat.csv')
        df = df[df['date'].between(first_plot_day, last_plot_day)]
        df['symptomatic_census'] = df['symp_mild'] + df['symp_severe']
        df['ventilators'] = get_vents(df['crit_det'].values)

        plot_on_fig(df, channels, axes, color=palette[d], label=exp_name)
    axes[-1].legend()

    plt.savefig(os.path.join(plot_path, 'iteration_comparison_IL.png'))
    plt.savefig(os.path.join(plot_path,'pdf', 'iteration_comparison_IL.pdf'), format='PDF')
    #plt.show()

def plot_covidregions(subgroups=None,channels=None) :

    if subgroups is None:
        subgroups = ['_EMS-1', '_EMS-2', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-6', '_EMS-7', '_EMS-8', '_EMS-9',
                     '_EMS-10', '_EMS-11']
    if channels is None:
        channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']

    for region_suffix in subgroups :

        region_label= region_suffix.replace('_EMS-', 'covid region ')
        region_label2 = region_label.replace(' ', '_')

        fig = plt.figure(figsize=(16, 8))
        fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
        palette = sns.color_palette('Set1', len(exp_names))

        axes = [fig.add_subplot(3, 2, x + 1) for x in range(len(channels))]

        for d, exp_name in enumerate(exp_names) :
            df = load_sim_data(exp_name, region_suffix=region_suffix)
            df = df[df['date'].between(first_plot_day, last_plot_day)]
            df['symptomatic_census'] = df['symptomatic_mild'] + df['symptomatic_severe']
            df['ventilators'] = get_vents(df['crit_det'].values)

            plot_on_fig(df, channels, axes, color=palette[d], label=exp_name)

        axes[-1].legend()
        fig.suptitle(region_label)
        plt.savefig(os.path.join(plot_path, 'iteration_comparison_%s.png' % region_label2))
        plt.savefig(os.path.join(plot_path,'pdf', 'iteration_comparison_%s.pdf' % region_label2))
        #plt.show()


def plot_covidregions_inone(channel='hospitalized') :

    subgroups = ['_EMS-1', '_EMS-2', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-6', '_EMS-7', '_EMS-8', '_EMS-9',
                 '_EMS-10', '_EMS-11']

    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    palette = sns.color_palette('Set1', len(exp_names))
    axes = [fig.add_subplot(3,4, x + 1) for x in range(len(subgroups))]

    for c, region_suffix in enumerate(subgroups) :

        region_label= region_suffix.replace('_EMS-', 'COVID-19 Region ')

        for d, exp_name in enumerate(exp_names) :
            df = load_sim_data(exp_name, region_suffix=region_suffix, fname='trajectoriesDat.csv')
            df = df[(df['date'] >= first_plot_day) & (df['date'] <= last_plot_day)]
            if channel=='B_prev':
                df['B_prev'] = df['infected_B'] / df['infected']
                df = df.dropna(subset=["B_prev"])
            plot_on_fig2(df, c, axes, channel=channel, color=palette[d], panel_heading= region_label, label=exp_name)

        axes[-1].legend()
        fig.suptitle(x=0.5, y=0.999,t=channel)
        plt.tight_layout()

    plt.savefig(os.path.join(plot_path, 'iteration_comparison_covidregion_%s.png' % channel))
    plt.savefig(os.path.join(plot_path, 'pdf', 'iteration_comparison_covidregion_%s.pdf' % channel))

def plot_covidregions_inone2(channels=None):
    if channels==None:
        channels=['infected', 'new_detected', 'hospitalized', 'critical', 'deaths']

    subgroups = ['_EMS-1', '_EMS-2', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-6', '_EMS-7', '_EMS-8', '_EMS-9',
                 '_EMS-10', '_EMS-11']

    for channel in channels :
        fig = plt.figure(figsize=(12, 8))
        fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
        palette = sns.color_palette('Set1', len(exp_names))
        axes = [fig.add_subplot(3, 4, x + 1) for x in range(len(subgroups))]

        for c, region_suffix in enumerate(subgroups) :

            region_label= region_suffix.replace('_EMS-', 'covid region ')

            for d, exp_name in enumerate(exp_names) :
                df = load_sim_data(exp_name, region_suffix=region_suffix, fname='trajectoriesDat.csv')
                df = df[df['date'].between(first_plot_day, last_plot_day)]
                plot_on_fig2(df, c, axes, channel=channel, color=palette[d],panel_heading = region_label,  label="")

            axes[-1].legend()
            fig.suptitle(x=0.5, y=0.999,t=channel)
            plt.tight_layout()
        if os.path.isdir(os.path.join(plot_path,'_plots_covid_region_by_indicator')) ==False  :
            os.mkdir(os.path.join(plot_path,'_plots_covid_region_by_indicator'))
            os.mkdir(os.path.join(plot_path,'_plots_covid_region_by_indicator','pdf'))
        plt.savefig(os.path.join(plot_path,'_plots_covid_region_by_indicator', 'covidregion_%s.png' % channel))
        #plt.savefig(os.path.join(plot_path, '_plots_covid_region_by_indicator', 'pdf', 'covidregion_%s.pdf' % channel))


def plot_restoreregions_inone(channel='hospitalized') :

    subgroups = ['_northcentral', '_northeast', '_central', '_southern']

    fig = plt.figure(figsize=(8, 6))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
    palette = sns.color_palette('Set1', len(exp_names))
    axes = [fig.add_subplot(2, 2, x + 1) for x in range(len(subgroups))]

    for c, region_suffix in enumerate(subgroups) :

        region_label= region_suffix.replace('_', '')

        for d, exp_name in enumerate(exp_names) :
            df = load_sim_data(exp_name, region_suffix=region_suffix)
            df = df[df['date'].between(first_plot_day, last_plot_day)]
            plot_on_fig2(df, c, axes, channel=channel, color=palette[d],panel_heading = region_label,  label=exp_name)

        axes[-1].legend()
        fig.suptitle(x=0.5, y=0.999,t=channel)
        plt.tight_layout()
    plt.savefig(os.path.join(plot_path, 'iteration_comparison_restoreregion_%s.png' % channel))
    plt.savefig(os.path.join(plot_path, 'pdf', 'iteration_comparison_restoreregion_%s.pdf' % channel))


if __name__ == '__main__' :

    args = parse_args()
    stem = args.stem
    Location = args.Location

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()

    first_plot_day = pd.Timestamp('2020-01-01') #pd.Timestamp.today()- pd.Timedelta(60,'days')
    last_plot_day = pd.Timestamp.today()+ pd.Timedelta(15,'days')

    plot_path = os.path.join(wdir, 'simulation_output', exp_names[-1], '_plots')

    #plot_main()
    #plot_covidregions()
    plot_covidregions_inone(channel='Ki_t')
    #plot_covidregions_inone(channel='B_prev')
    #plot_covidregions_inone(channel='hospitalized')
    #plot_restoreregions_inone(channel='hospitalized')
    #plot_covidregions_inone2(channels=['infected','new_detected','hospitalized', 'critical', 'deaths'])
    #plot_covidregions_inone2(channels=['prevalence','recoverged','symptomatic_mild','symptomatic_severe'])
    #plot_covidregions_inone2(channels=['symp_severe_det_cumul','symp_mild_det_cumul','symptomatic_mild',
    #                                   'hosp_det','deaths_det','infectious_det'])