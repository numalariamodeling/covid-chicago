import os
import geopandas as gpd
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns
from plotting.colors import load_color_palette

mpl.rcParams['pdf.fonttype'] = 42


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

plot_dir = os.path.join(projectpath, 'Plots + Graphs', '_trend_tracking')
datapath = os.path.join(datapath, 'covid_IDPH')
shp_path = os.path.join(datapath, 'shapefiles')


def plot_IL_cases() :

    IL_fname = os.path.join(datapath, 'Corona virus reports', 'illinois_public.csv')
    df = pd.read_csv(IL_fname, parse_dates=['update_date'])
    df = df.rename(columns={'update_date' : 'date'})
    df = df.sort_values(by='date')
    df = df.fillna(0)
    palette = load_color_palette('wes')

    formatter = mdates.DateFormatter("%m-%d")
    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(8,8))
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.05, top=0.97)

    ax = fig.add_subplot(4,1,1)
    df['daily_pos'] = np.insert(np.diff(df['tests_pos']), 0, 0)
    ax.bar(df['date'].values[1:], np.diff(df['tests_pos']),
           align='center', color=palette[0], linewidth=0, alpha=0.5)
    df['moving_ave'] = df['daily_pos'].rolling(window=7, center=False).mean()
    ax.plot(df['date'], df['moving_ave'], '-', color=palette[0])
    ax.set_ylabel('positives')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    ax = fig.add_subplot(4,1,2)
    ax.bar(df['date'].values[1:], df['new_tests'][1:],
           align='center', color=palette[1], linewidth=0, alpha=0.5)
    df['moving_ave'] = df['new_tests'].rolling(window=7, center=False).mean()
    ax.plot(df['date'], df['moving_ave'], '-', color=palette[1])
    ax.set_ylabel('tests')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    ax = fig.add_subplot(4,1,3)
    df['daily_tpr'] = df['daily_pos']/df['new_tests']
    ax.bar(df['date'].values[1:], df['daily_tpr'][1:],
           align='center', color=palette[2], linewidth=0, alpha=0.5)
    df['moving_ave'] = df['daily_tpr'].rolling(window=7, center=False).mean()
    ax.plot(df['date'], df['moving_ave'], '-', color=palette[2])
    ax.set_ylabel('TPR')
    ax.set_ylim(0, 0.3)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    print(df[['date', 'daily_tpr']].tail(20))

    ax = fig.add_subplot(4,1,4)
    ax.bar(df['date'].values[1:], np.diff(df['deaths']),
           align='center', color=palette[3], linewidth=0, alpha=0.5)
    df['daily_death'] = np.insert(np.diff(df['deaths']), 0, 0)
    df['moving_ave'] = df['daily_death'].rolling(window=7, center=False).mean()
    ax.plot(df['date'], df['moving_ave'], '-', color=palette[3])
    ax.set_ylabel('deaths')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.savefig(os.path.join(plot_dir, 'idph_public_cases_and_deaths.pdf'), format='PDF')
    plt.close(fig)


def load_county_cases() :

    county_fname = os.path.join(datapath, 'Corona virus reports', 'IDPH Stats County public.csv')

    df = pd.read_csv(county_fname)
    df['update_date'] = pd.to_datetime(df['update_date'])
    df = df[~df['NOFO_Region'].isin(['Illinois', 'Out Of State', 'Unassigned'])]

    df = df.groupby(['update_date', 'County'])[['Positive_Cases', 'Deaths', 'Tested']].agg(np.max).reset_index()
    return df


def plot_cases_by_county_map() :

    county_shp = gpd.read_file(os.path.join(shp_path, 'IL_BNDY_County', 'IL_BNDY_County_Py.shp'))
    county_pop = pd.read_csv(os.path.join(datapath, 'population', 'illinois_pop_by_county.csv'))

    df = load_county_cases()
    df = df[df['update_date'] == date(2020, 7, 4)]

    sdf = df[df['County'] == 'Chicago']
    sdf = sdf.set_index('County')
    df = df[df['County'] != 'Chicago']

    cols = ['Positive_Cases', 'Deaths']

    for col in cols :
        df.loc[df['County'] == 'Cook', col] = df.loc[df['County'] == 'Cook', col] + sdf.at['Chicago', col]
    df['County'] = df['County'].apply(lambda x : x.upper())

    county_pop['County'] = county_pop['county_name'].apply(lambda x : x.replace(' County', '').upper())
    df = pd.merge(left=df, right=county_pop, on='County', how='left')
    for col in cols :
        df['%s per 1000' % col] = df[col]/df['pop']*1000
    df.loc[df['County'] == 'DE WITT', 'County'] = 'DEWITT'
    ds_shp = pd.merge(left=county_shp, right=df, left_on='COUNTY_NAM', right_on='County')

    fig = plt.figure(figsize=(10, 10))
    fig.subplots_adjust(top=0.95)

    def format_ax(ax, name) :
        ax.set_title(name)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')

    for c, col in enumerate(cols) :

        ax = fig.add_subplot(2, 2, c + 1)
        ds_shp.plot(column=col, ax=ax, cmap='RdYlBu_r', edgecolor='0.8',
                    linewidth=0.8, legend=True)
        format_ax(ax, col)

        ax = fig.add_subplot(2, 2, c + 1 + 2)
        ds_shp.plot(column='%s per 1000' % col, ax=ax, cmap='RdYlBu_r', edgecolor='0.8',
                    linewidth=0.8, legend=True)
        format_ax(ax, '%s per 1000' % col)

    plt.savefig(os.path.join(plot_dir, 'maps', 'idph_public_by_county.pdf'), format='PDF')


def setup_fig(figname) :

    fig = plt.figure(figname, figsize=(28,12))
    fig.subplots_adjust(bottom=0.03, top=0.97, left=0.05, right=0.99, wspace=0.5)
    return fig


def format_axis(ax, ci, df, county, max_pos, plottype='TPR') :

    formatter = mdates.DateFormatter("%m-%d")
    ax.set_ylim(0, max_pos)
    ax.set_xlim(np.min(df['update_date']) - timedelta(days=1),
                np.max(df['update_date']) + timedelta(days=1))
    ax.set_title(county, y=0.75)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    if ci < 92:
        ax.set_xticklabels([])
    if plottype == 'TPR' :
        if max_pos > 0.02 :
            ax.plot([np.min(df['update_date']), np.max(df['update_date'])], [0.02, 0.02], '-',
                    linewidth=0.5, color='#969696')
        if max_pos > 0.05 :
            ax.plot([np.min(df['update_date']), np.max(df['update_date'])], [0.05, 0.05], '-',
                    linewidth=0.5, color='#969696')


def plot_cases_by_county_line() :

    df = load_county_cases()
    df = df.sort_values(by=['update_date', 'County'])

    fig_cases = setup_fig('cases')
    fig_tpr = setup_fig('TPR')
    palette = sns.color_palette('Paired', 12)
    tpr_limits = [0.01, 0.02, 0.05, 0.1, 1]
    palette_scale = [palette[x] for x in [1, 0, 4, 5, 7]]

    for ci, (county, cdf) in enumerate(df.groupby('County')) :
        cdf['daily_pos'] = np.insert(np.diff(cdf['Positive_Cases']), 0, 0)
        cdf['daily_test'] = np.insert(np.diff(cdf['Tested']), 0, 0)
        cdf.loc[cdf['daily_test'] == 0, 'daily_test'] = 1
        cdf['daily_tpr'] = cdf['daily_pos']/cdf['daily_test']

        ax = fig_cases.add_subplot(9,12,ci+1)
        if len(cdf) < 10 :
            ax.bar(cdf['update_date'].values[1:], np.diff(cdf['Positive_Cases']),
                   align='center', color=palette[3], linewidth=0, alpha=0.3)
            max_pos = np.max(cdf['Positive_Cases'])
        else :
            cdf['moving_ave'] = cdf['daily_pos'].rolling(window=7, center=False).mean()
            max_pos = np.max(cdf['moving_ave'])
            if cdf['moving_ave'].values[-1] < 1 :
                colorbin = 7
            elif cdf['moving_ave'].values[-1] > cdf['moving_ave'].values[-8]*1.1 :
                colorbin = 5
            elif cdf['moving_ave'].values[-1] > cdf['moving_ave'].values[-8] :
                colorbin = 4
            else :
                colorbin = 1
            ax.plot(cdf['update_date'], cdf['moving_ave'], '-', color=palette[colorbin])
            ax.fill_between(cdf['update_date'].values, [0]*len(cdf['moving_ave']), cdf['moving_ave'],
                            linewidth=0, color=palette[colorbin], alpha=0.3)
        format_axis(ax, ci, df, county, max_pos, 'cases')

        ax = fig_tpr.add_subplot(9,12,ci+1)
        cdf = cdf[cdf['Positive_Cases'] <= cdf['Tested']]
        if len(cdf) < 10 :
            colorbin = min(b for b,i in enumerate(tpr_limits) if i > cdf['daily_tpr'].values[-1])
            ax.plot(cdf['update_date'], cdf['daily_tpr'], '-', color=palette_scale[colorbin])
            ax.fill_between(cdf['update_date'].values, [0] * len(cdf['daily_tpr']), cdf['daily_tpr'],
                            linewidth=0, color=palette_scale[colorbin], alpha=0.3)
            max_pos = np.max(cdf['daily_tpr'])
        else :
            cdf['moving_ave'] = cdf['daily_tpr'].rolling(window=7, center=False).mean()
            colorbin = min(b for b,i in enumerate(tpr_limits) if i > cdf['moving_ave'].values[-1])
            ax.plot(cdf['update_date'], cdf['moving_ave'], '-', color=palette_scale[colorbin])
            ax.fill_between(cdf['update_date'].values, [0]*len(cdf['moving_ave']), cdf['moving_ave'],
                            linewidth=0, color=palette_scale[colorbin], alpha=0.3)
            max_pos = np.max(cdf['moving_ave'])
        format_axis(ax, ci, df, county, max_pos, 'TPR')

    fig_cases.savefig(os.path.join(plot_dir, 'idph_public_county_cases.pdf'), format='PDF')
    fig_tpr.savefig(os.path.join(plot_dir, 'idph_public_county_tpr.pdf'), format='PDF')
    plt.close(fig_cases)
    plt.close(fig_tpr)


def assign_counties_restore_region() :

    df = load_county_cases()
    ref_df = pd.read_csv(os.path.join(datapath, 'Corona virus reports', 'county_restore_region_map.csv'))
    df['County'] = df['County'].apply(lambda x : x.upper())
    df = pd.merge(left=df, right=ref_df, left_on='County', right_on='county', how='left')
    return df


def plot_agg_by_region() :

    df = assign_counties_restore_region()
    df = df.groupby(['restore_region', 'update_date'])[['Positive_Cases', 'Tested']].agg(np.sum).reset_index()
    df = df.sort_values(by=['restore_region', 'update_date'])

    palette = sns.color_palette('Paired', 12)
    tpr_limits = [0.01, 0.02, 0.05, 0.1, 1]
    palette_scale = [palette[x] for x in [1, 0, 4, 5, 7]]

    fig = plt.figure(figsize=(14,9))
    fig.subplots_adjust(left=0.05, right=0.97, wspace=0.2)
    formatter = mdates.DateFormatter("%m-%d")

    for ri, (region, cdf) in enumerate(df.groupby('restore_region')) :
        ax = fig.add_subplot(3,4,ri+1)
        colorbin = 5
        cdf['daily_pos'] = np.insert(np.diff(cdf['Positive_Cases']), 0, 0)
        cdf['daily_test'] = np.insert(np.diff(cdf['Tested']), 0, 0)
        cdf.loc[cdf['daily_test'] == 0, 'daily_test'] = 1
        cdf['daily_tpr'] = cdf['daily_pos']/cdf['daily_test']

        cdf['moving_ave'] = cdf['daily_pos'].rolling(window=7, center=False).mean()
        max_pos = np.max(cdf['moving_ave'])
        ax.plot(cdf['update_date'], cdf['moving_ave'], '-', color=palette[colorbin])
        ax.fill_between(cdf['update_date'].values, [0]*len(cdf['moving_ave']), cdf['moving_ave'],
                        linewidth=0, color=palette[colorbin], alpha=0.3)

        ax.set_ylim(0, max_pos)
        ax.set_xlim(np.min(df['update_date']) - timedelta(days=1),
                    np.max(df['update_date']) + timedelta(days=1))
        ax.set_title(region)
        if ri == 0 :
            ax.set_ylabel('cases')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

        ax = fig.add_subplot(3,4,8+ri+1)
        cdf = cdf[cdf['Positive_Cases'] <= cdf['Tested']]
        cdf['moving_ave'] = cdf['daily_tpr'].rolling(window=7, center=False).mean()
        colorbin = min(b for b,i in enumerate(tpr_limits) if i > cdf['moving_ave'].values[-1])
        ax.plot(cdf['update_date'], cdf['moving_ave'], '-', color=palette_scale[colorbin])
        ax.fill_between(cdf['update_date'].values, [0]*len(cdf['moving_ave']), cdf['moving_ave'],
                        linewidth=0, color=palette_scale[colorbin], alpha=0.3)
        max_pos = np.max(cdf['moving_ave'])
        ax.plot([np.min(df['update_date']), np.max(df['update_date'])], [0.02, 0.02], '-',
                linewidth=0.5, color='#969696')
        ax.plot([np.min(df['update_date']), np.max(df['update_date'])], [0.05, 0.05], '-',
                linewidth=0.5, color='#969696')

        ax.set_ylim(0, max_pos)
        ax.set_xlim(np.min(df['update_date']) - timedelta(days=1),
                    np.max(df['update_date']) + timedelta(days=1))
        if ri == 0 :
            ax.set_ylabel('test positivity rate')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_ylim(0, 0.2)

        ax = fig.add_subplot(3,4,4+ri+1)
        colorbin = 1
        cdf = cdf[cdf['update_date'] >= date(2020,5,15)]
        cdf['moving_ave'] = cdf['daily_test'].rolling(window=7, center=False).mean()
        ax.plot(cdf['update_date'], cdf['moving_ave'], '-', color=palette[colorbin])
        ax.fill_between(cdf['update_date'].values, [0]*len(cdf['moving_ave']), cdf['moving_ave'],
                        linewidth=0, color=palette[colorbin], alpha=0.3)
        max_pos = np.max(cdf['moving_ave'])

        ax.set_ylim(0, max_pos)
        ax.set_xlim(np.min(df['update_date']) - timedelta(days=1),
                    np.max(df['update_date']) + timedelta(days=1))
        if ri == 0 :
            ax.set_ylabel('tests')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

    fig.savefig(os.path.join(plot_dir, 'idph_public_region.pdf'), format='PDF')
    plt.close(fig)


def plot_county_line_by_region() :

    df = assign_counties_restore_region()
    df = df.sort_values(by=['update_date', 'restore_region', 'County'])

    regions = pd.DataFrame( { 'region' : df['restore_region'].unique(),
                              'cindex' : range(len(df['restore_region'].unique()))})
    regions = regions.set_index('region')

    fig_cases = setup_fig('cases')
    fig_tpr = setup_fig('TPR')
    palette = load_color_palette('wes')

    ci = 0
    for ri, (reg, rdf) in enumerate(df.groupby('restore_region')) :
        for county, cdf in rdf.groupby('County') :
            cdf['daily_pos'] = np.insert(np.diff(cdf['Positive_Cases']), 0, 0)
            cdf['daily_test'] = np.insert(np.diff(cdf['Tested']), 0, 0)
            cdf.loc[cdf['daily_test'] == 0, 'daily_test'] = 1
            cdf['daily_tpr'] = cdf['daily_pos']/cdf['daily_test']

            ax = fig_cases.add_subplot(9,12,ci+1)
            colorbin = regions.at[reg, 'cindex']
            if len(cdf) < 10 :
                ax.bar(cdf['update_date'].values[1:], np.diff(cdf['Positive_Cases']),
                       align='center', color=palette[colorbin], linewidth=0, alpha=0.3)
                max_pos = np.max(cdf['Positive_Cases'])
            else :
                cdf['moving_ave'] = cdf['daily_pos'].rolling(window=7, center=False).mean()
                max_pos = np.max(cdf['moving_ave'])
                ax.plot(cdf['update_date'], cdf['moving_ave'], '-', color=palette[colorbin])
                ax.fill_between(cdf['update_date'].values, [0]*len(cdf['moving_ave']), cdf['moving_ave'],
                                linewidth=0, color=palette[colorbin], alpha=0.3)
            format_axis(ax, ci, df, county, max_pos, 'cases')

            ax = fig_tpr.add_subplot(9,12,ci+1)
            cdf = cdf[cdf['Positive_Cases'] <= cdf['Tested']]
            if len(cdf) < 10 :
                ax.plot(cdf['update_date'], cdf['daily_tpr'], '-', color=palette[colorbin])
                ax.fill_between(cdf['update_date'].values, [0] * len(cdf['daily_tpr']), cdf['daily_tpr'],
                                linewidth=0, color=palette[colorbin], alpha=0.3)
                max_pos = np.max(cdf['daily_tpr'])
            else :
                cdf['moving_ave'] = cdf['daily_tpr'].rolling(window=7, center=False).mean()
                ax.plot(cdf['update_date'], cdf['moving_ave'], '-', color=palette[colorbin])
                ax.fill_between(cdf['update_date'].values, [0]*len(cdf['moving_ave']), cdf['moving_ave'],
                                linewidth=0, color=palette[colorbin], alpha=0.3)
                max_pos = np.max(cdf['moving_ave'])
            format_axis(ax, ci, df, county, max_pos, 'TPR')
            ci += 1

    fig_cases.savefig(os.path.join(plot_dir, 'idph_public_county_region_cases.pdf'), format='PDF')
    fig_tpr.savefig(os.path.join(plot_dir, 'idph_public_county_region_tpr.pdf'), format='PDF')
    plt.close(fig_cases)
    plt.close(fig_tpr)


if __name__ == '__main__' :

    # plot_cases_by_county_map()
    # plot_cases_by_county_line()
    plot_county_line_by_region()
    # plot_agg_by_region()
    # plot_IL_cases()
    # plt.show()
