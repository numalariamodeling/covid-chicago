import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.patches as patches
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
from processing_helpers import load_capacity

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def load_model_results(results_path, fname) :

    df = pd.read_csv(os.path.join(results_path, fname))
    df['date'] = pd.to_datetime(df['date_clean'])
    df = df.sort_values(by=['date'])
    return df


def plot_with_ref_data(results_path, fname, channel='deaths') :

    df = load_model_results(results_path, fname)

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', 'daily_deaths_line_list_200515.csv'))
    ref_df['date'] = pd.to_datetime(ref_df['deceased_date'])
    ref_df = ref_df[ref_df['date'] <= pd.Timestamp('2020-05-05')]

    df = df[df['geography_modeled'] == 'illinois']
    df = df[df['scenario_name'] == 'baseline']
    df = df[df['date'] <=  pd.Timestamp('2020-06-01')]

    fig = plt.figure(figsize=(5,4))
    ax = fig.gca()
    # fig.subplots_adjust(left=0.05, right=0.98)
    palette = sns.color_palette('Set1')
    formatter = mdates.DateFormatter("%m-%d")

    for g, (gn, gdf) in enumerate(df.groupby('model_team')) :
        ax.plot(gdf['date'], gdf['%s_median' % channel], color=palette[g], label=gn)
        ax.fill_between(gdf['date'].values, gdf['%s_lower' % channel], gdf['%s_upper' % channel],
                           color=palette[g], linewidth=0, alpha=0.2)
    ax.scatter(ref_df['date'].values, ref_df['daily_deaths_line_list'].values, 10, color='k', linewidth=0,
               label='IDPH data')
    # ax.set_ylim(-250, 5300)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_ylabel(channel)
    ax.legend()
    plt.savefig(os.path.join(results_path, 'compare_with_data_illinois.pdf'), format='PDF')


def plot_il_scenarios(results_path, fname, log=False) :

    df = load_model_results(results_path, fname)
    channel = 'icu'

    df = df[df['geography_modeled'] == 'illinois']
    savename = 'illinois' if not log else 'illinois_log'

    fig = plt.figure(figsize=(15,4))
    ax = [fig.add_subplot(1,3,x+1) for x in range(3)]
    fig.subplots_adjust(left=0.05, right=0.98)
    palette = sns.color_palette('Set1')
    formatter = mdates.DateFormatter("%m-%d")

    for s, (scen, sdf) in enumerate(df.groupby('scenario_name')) :
        for g, (gn, gdf) in enumerate(sdf.groupby('model_team')) :
            ax[s].plot(gdf['date'], gdf['%s_median' % channel], color=palette[g], label=gn)
            ax[s].fill_between(gdf['date'].values, gdf['%s_lower' % channel], gdf['%s_upper' % channel],
                               color=palette[g], linewidth=0, alpha=0.2)
        ax[s].set_title(scen)
        if not log :
            pass
            # ax[s].set_ylim(-250, 5300)
        else :
            ax[s].set_yscale('log')
            # ax[s].set_ylim(1, 10**4)
        ax[s].xaxis.set_major_formatter(formatter)
        ax[s].xaxis.set_major_locator(mdates.MonthLocator())
        ax[s].legend()

    ax[0].set_ylabel(channel)
    plt.savefig(os.path.join(results_path, '%s_%s.pdf' % (savename, channel)), format='PDF')


def plot_regional_scenarios(results_path, fname, log=False) :

    df = load_model_results(results_path, fname)
    channel = 'deaths'
    restore_regions = [x for x in df['geography_modeled'].unique() if 'restore' in x]

    df = df[df['geography_modeled'].isin(restore_regions)]
    savename = 'regions' if not log else 'regions_log'

    num_geog = len(df['geography_modeled'].unique())
    num_scen = len(df['scenario_name'].unique())

    fig = plt.figure(figsize=(15,15))
    ax = [fig.add_subplot(num_geog, num_scen, x+1) for x in range(num_geog*num_scen)]
    fig.subplots_adjust(left=0.05, right=0.98)
    palette = sns.color_palette('Set1')
    formatter = mdates.DateFormatter("%m-%d")

    ylims = {
        'central' : (-10, 275),
        'northcentral' : (-20, 850),
        'southern' : (-20, 400),
        'northeast' : (-200, 4500)
    }

    for geo_i, (geo, geo_df) in enumerate(df.groupby('geography_modeled')) :
        for s, (scen, sdf) in enumerate(geo_df.groupby('scenario_name')) :
            a_i = geo_i*num_scen + s
            for g, (gn, gdf) in enumerate(sdf.groupby('model_team')) :
                ax[a_i].plot(gdf['date'], gdf['%s_median' % channel], color=palette[g], label=gn)
                ax[a_i].fill_between(gdf['date'].values, gdf['%s_lower' % channel], gdf['%s_upper' % channel],
                                   color=palette[g], linewidth=0, alpha=0.2)
            ax[a_i].set_title(scen)
            if not log :
                ax[a_i].set_ylim(ylims[geo.split('_')[1]][0],
                                 ylims[geo.split('_')[1]][1])
            else :
                ax[a_i].set_yscale('log')
                ax[a_i].set_ylim(1,ylims[geo.split('_')[1]][1])
            ax[a_i].xaxis.set_major_formatter(formatter)
            ax[a_i].xaxis.set_major_locator(mdates.MonthLocator())
            ax[a_i].legend()
            if s == 0 :
                ax[a_i].set_ylabel(geo)
    plt.savefig(os.path.join(results_path, '%s_%s.pdf' % (savename, channel)), format='PDF')


def plot_overall_nums(results_path, fname, geog) :

    df = load_model_results(results_path, fname)

    num_geog = len(df['geography_modeled'].unique())
    num_scen = len(df['scenario_name'].unique())
    num_groups = len(df['model_team'].unique())

    df = df[df['geography_modeled'] == geog]
    df = df[df['date'] >= pd.Timestamp('2020-06-01')]

    colors = {
        'uiuc' : '#00b9f2',
        'nu' : '#00a875',
        'uchicago' : '#f7941d'
    }

    fig = plt.figure(geog, figsize=(14,6))
    axes = [fig.add_subplot(1,3,x+1) for x in range(3)]
    ylabels = []

    for s, (scen, sdf) in enumerate(df.groupby('scenario_name')) :
        for g, (gn, gdf) in enumerate(sdf.groupby('model_team')) :

            yval = s*num_groups + g
            ylabels.append('%s %s' % (scen, gn))

            ax = axes[0]
            channel = 'deaths'
            med = int(np.sum(gdf['%s_median' % channel]))
            lb = int(np.sum(gdf['%s_lower' % channel]))
            ub = int(np.sum(gdf['%s_upper' % channel]))

            ax.plot([lb, ub], [yval]*2, '-k', linewidth=0.5)
            ax.plot([med], [yval], "D", color=colors[gn])

            ax.set_xlabel('cumulative deaths')
            ax.set_yticklabels([])

            ax = axes[1]
            channel = 'icu'
            med = int(np.max(gdf['%s_median' % channel]))
            lb = int(np.max(gdf['%s_lower' % channel]))
            ub = int(np.max(gdf['%s_upper' % channel]))

            ax.plot([lb, ub], [yval]*2, '-k', linewidth=0.5)
            ax.plot([med], [yval], "D", color=colors[gn])

            ax.set_xlabel('peak ICU')
            ax.set_yticklabels([])

            ax = axes[2]
            channel = 'cases'
            med = int(np.max(gdf['%s_median' % channel]))
            lb = int(np.max(gdf['%s_lower' % channel]))
            ub = int(np.max(gdf['%s_upper' % channel]))

            ax.plot([lb, ub], [yval]*2, '-k', linewidth=0.5)
            ax.plot([med], [yval], "D", color=colors[gn])

            ax.set_xlabel('peak cases')
            ax.set_yticklabels([])

    if geog == 'illinois' :
        rect = patches.Rectangle((2000, 0), 1000, 8, linewidth=0, facecolor='k', alpha=0.2)
        axes[1].add_patch(rect)
    axes[0].set_yticks(range(9))
    axes[0].set_yticklabels(ylabels)

    plt.savefig(os.path.join(results_path, 'overall_jun_oct_numbers_%s.pdf' % geog), format='PDF')


if __name__ == '__main__' :

    results_path = os.path.join(projectpath, 'civis', '200515_combined_model_results')
    fname = 'combined_model_results_20200515.csv'
    # plot_with_ref_data(results_path, fname)
    # plot_il_scenarios(results_path, fname, log=False)
    # plot_regional_scenarios(results_path, fname, log=False)
    # plot_regional_scenarios(results_path, fname, log=True)

    for geog in ['illinois', 'restore_southern', 'restore_central', 'restore_northcentral', 'restore_northeast'] :
        plot_overall_nums(results_path, fname, geog)

    plt.show()
