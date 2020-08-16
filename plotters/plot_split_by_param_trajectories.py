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
from data_comparison import load_sim_data
from copy import copy

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

first_day = date(2020, 2, 13) # IL
first_plot_day = date(2020, 7, 1)
last_plot_day = date(2020, 12, 1)

def plot_on_fig(df, channels, axes, color, label, addgrid=True) :

    for c, channel in enumerate(channels) :
        ax = axes[c]
        mdf=df

        mdf['date'] = mdf['time'].apply(lambda x: first_day + timedelta(days=int(x)))
        mdf = mdf[(mdf['date'] >= first_plot_day) & (mdf['date'] <= last_plot_day)]
        if addgrid :
            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        ax.plot(mdf['date'], mdf[channel], color=color, label=label)
        ax.set_title(' '.join(channel.split('_')), y=0.85)
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        #ax.set_ylim(0, max(mdf[channel])+10)


def plot_on_fig2(df, c, axes,channel, color,panel_heading, label, addgrid=True) :
    ax = axes[c]
    mdf = df
    mdf['date'] = mdf['time'].apply(lambda x: first_day + timedelta(days=int(x)))
    mdf = mdf[(mdf['date'] >= first_plot_day) & (mdf['date'] <= last_plot_day)]
    if addgrid:
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
    ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
    ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                color=color, linewidth=0, alpha=0.4)
    ax.set_title(panel_heading, y=0.85)
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_ylim(0, max(mdf['CI_75']))

def plot_main() :
    fig = plt.figure(figsize=(8, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
    palette = sns.color_palette('GnBu_d', len(exp_names))

    channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']
    axes = [fig.add_subplot(3, 2, x + 1) for x in range(len(channels))]

    for d, exp_name in enumerate(exp_names) :
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        df = load_sim_data(exp_name, fname='trajectoriesDat_trim.csv')

        df['symptomatic_census'] = df['symptomatic_mild'] + df['symptomatic_severe']
        df['ventilators'] = get_vents(df['crit_det'].values)

        plot_on_fig(df, channels, axes, color=palette[d], label=exp_name)
    axes[-1].legend()

    plt.savefig(os.path.join(sim_output_path, 'trajectories_IL.png'))
    #plt.savefig(os.path.join(sim_output_path, 'trajectories_IL.pdf'), format='PDF')
    #plt.show()

def plot_covidregions() :

    subgroups = ['_EMS-1', '_EMS-2', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-6', '_EMS-7', '_EMS-8', '_EMS-9',
                 '_EMS-10', '_EMS-11']

    for region_suffix in subgroups :

        region_label= region_suffix.replace('_EMS-', 'covid region ')
        region_label2 = region_label.replace(' ', '_')

        fig = plt.figure(figsize=(8, 8))
        fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
        palette = sns.color_palette('GnBu_d', len(exp_names))
        channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']
        axes = [fig.add_subplot(3, 2, x + 1) for x in range(len(channels))]


        for d, exp_name in enumerate(exp_names) :
            sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
            df = load_sim_data(exp_name, region_suffix=region_suffix, fname='trajectoriesDat_trim.csv')

            df['symptomatic_census'] = df['symptomatic_mild'] + df['symptomatic_severe']
            df['ventilators'] = get_vents(df['crit_det'].values)

            plot_on_fig(df, channels, axes, color=palette[d], label=exp_name)

        axes[-1].legend()
        fig.suptitle(region_label)
        plt.savefig(os.path.join(sim_output_path, 'trajectories_%s.png' % region_label2))
        #plt.savefig(os.path.join(sim_output_path, 'trajectories_%s.pdf' % region_label2))
        #plt.show()


def plot_covidregions_inone(channel='hospitalized') :

    subgroups = ['_EMS-1', '_EMS-2', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-6', '_EMS-7', '_EMS-8', '_EMS-9',
                 '_EMS-10', '_EMS-11']

    fig = plt.figure(figsize=(12, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
    palette = sns.color_palette('GnBu_d', len(exp_names))
    axes = [fig.add_subplot(4, 3, x + 1) for x in range(len(subgroups))]

    for c, region_suffix in enumerate(subgroups) :

        region_label= region_suffix.replace('_EMS-', 'covid region ')

        for d, exp_name in enumerate(exp_names) :
            sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
            df = load_sim_data(exp_name, region_suffix=region_suffix, fname='trajectoriesDat_trim.csv')

            plot_on_fig2(df, c, axes, channel=channel, color=palette[d],panel_heading = region_label,  label=exp_name)

        axes[-1].legend()
        fig.suptitle(x=0.5, y=0.999,t=channel)
        plt.tight_layout()
    plt.savefig(os.path.join(sim_output_path, 'trajectories_covidregion_%s.png' % channel))
    #plt.savefig(os.path.join(sim_output_path, 'trajectories_covidregion_%s.pdf' % channel))
        #plt.show()

def plot_covidregions_inone2(channels=['infected','new_detected','hospitalized', 'critical', 'deaths']) :

    subgroups = ['_EMS-1', '_EMS-2', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-6', '_EMS-7', '_EMS-8', '_EMS-9',
                 '_EMS-10', '_EMS-11']

    for channel in channels :
        fig = plt.figure(figsize=(12, 8))
        fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
        palette = sns.color_palette('GnBu_d', len(exp_names))
        axes = [fig.add_subplot(4, 3, x + 1) for x in range(len(subgroups))]

        for c, region_suffix in enumerate(subgroups) :

            region_label= region_suffix.replace('_EMS-', 'covid region ')

            for d, exp_name in enumerate(exp_names) :
                sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
                df = load_sim_data(exp_name, region_suffix=region_suffix, fname='trajectoriesDat_trim.csv')

                plot_on_fig2(df, c, axes, channel=channel, color=palette[d],panel_heading = region_label,  label="")

            axes[-1].legend()
            fig.suptitle(x=0.5, y=0.999,t=channel)
            plt.tight_layout()
        if os.path.isdir(os.path.join(sim_output_path,'_plots_covid_region_by_indicator')) ==False  :
            os.mkdir(os.path.join(sim_output_path,'_plots_covid_region_by_indicator'))
        plt.savefig(os.path.join(sim_output_path,'_plots_covid_region_by_indicator', 'covidregion_%s.png' % channel))
        #plt.savefig(os.path.join(sim_output_path,'_plots_covid_region_by_indicator', 'covidregion_%s.pdf' % channel))
        #plt.show()


if __name__ == '__main__' :

    exp_names = [ '20200812_IL_MR_baseline',
                  '20200812_IL_MR_critical75_triggeredrollback']

    plot_main()
    #plot_covidregions()
    #plot_covidregions_inone(channel='hospitalized')
    #plot_covidregions_inone2(channels=['infected','new_detected','hospitalized', 'critical', 'deaths'])
    #plot_covidregions_inone2(channels=['prevalence','recoverged','symptomatic_mild','symptomatic_severe'])
    #plot_covidregions_inone2(channels=['symp_severe_det_cumul','symp_mild_det_cumul','symptomatic_mild','hospitalized_det','deaths_det','infectious_det'])

