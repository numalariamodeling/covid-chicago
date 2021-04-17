import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
import geopandas as gpd
import matplotlib.colors as colors
from shapely.geometry import mapping, Point, Polygon
import copy
from statsmodels.stats.proportion import proportion_confint

mpl.rcParams['pdf.fonttype'] = 42

LL_date = '210413'

idph_data_path = '/Volumes/fsmresfiles/PrevMed/Covid-19-Modeling/IDPH line list'
line_list_fname = os.path.join(idph_data_path,
                               'tests_LL_%s.csv' % LL_date)
cleaned_line_list_fname = os.path.join(idph_data_path,
                                       'tests_LL_%s_JGcleaned.csv' % LL_date)
box_data_path = '/Users/jlg1657/Box/NU-malaria-team/data/covid_IDPH'
project_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago'
plot_path = os.path.join(project_path, 'Plots + Graphs')
plot_dir = os.path.join(plot_path, '_trend_tracking')
shp_path = os.path.join(box_data_path, 'shapefiles')


def plot_weekly_share_by_age() :

    df = pd.read_csv(line_list_fname)
    df = df.groupby(['age', 'date'])['total_specs', 'positive_specs'].agg(np.sum).reset_index()
    agebins = [10, 20, 30, 40, 50, 60, 70, 80, 200]
    labels = ['<10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '80+']
    df = df.dropna(subset=['age'])
    df = df[(df['age'] >= 0) & (df['age'] <= 110)]
    df['age'] = df['age'].astype(int)
    df['agebin'] = df['age'].apply(lambda x : min([y for y in agebins if y > x]))
    df = df.groupby(['agebin', 'date'])['total_specs', 'positive_specs'].agg(np.sum).reset_index()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    firstday = np.min(df['date'])
    df['week'] = df['date'].apply(lambda x : int((x - firstday).days/7))
    gdf = df.groupby(['week', 'agebin']).agg(np.sum).reset_index()
    total_by_date = gdf.groupby('week')['total_specs'].agg(np.sum).reset_index()
    total_by_date = total_by_date.rename(columns={'total_specs' : 'total_all_age'})
    gdf = pd.merge(left=gdf, right=total_by_date, on='week', how='left')
    gdf['share'] = gdf['total_specs']/gdf['total_all_age']
    gdf['date'] = gdf['week'].apply(lambda x : firstday + timedelta(days=x*7))

    fig = plt.figure(figsize=(5,3))
    fig.subplots_adjust(right=0.7)
    ax = fig.gca()
    palette = sns.color_palette('Paired', len(agebins))
    bottom = [0]*len(gdf['date'].unique())
    for a, (age, adf) in enumerate(gdf.groupby('agebin')) :
        top = [x + y for x, y in zip(bottom, adf['share'].values)]
        ax.fill_between(adf['date'].values, bottom, top, color=palette[a], linewidth=0, label=labels[a])
        bottom = top
    ax.legend(bbox_to_anchor=(1.5, 1))
    ax.set_ylabel('fraction of tests')
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.savefig(os.path.join(plot_path, 'IDPH Line-List Plots', 'Testing', '%s_weekly_test_share_by_age.png' % LL_date))
    plt.savefig(os.path.join(plot_path, 'IDPH Line-List Plots', 'Testing', '%s_weekly_test_share_by_age.pdf' % LL_date), format='PDF')


def plot_tests_per_pop_covid_region() :

    adf = pd.read_csv(line_list_fname)
    adf = adf[adf['covid_region'].isin(range(1,12))]
    # adf = adf[adf['county'] != 'Champaign']
    channel = 'total_specs'

    county_pop = pd.read_csv(os.path.join(box_data_path, 'EMS Population', 'covidregion_population_by_county.csv'))
    # county_pop = county_pop[county_pop['County'] != 'CHAMPAIGN']
    county_pop = county_pop.groupby('new_restore_region')['pop'].agg(np.sum).reset_index()

    adf = adf.groupby(['date', 'covid_region']).agg(np.sum).reset_index()
    adf = pd.merge(left=adf, right=county_pop, left_on='covid_region', right_on='new_restore_region')
    adf['covid_region'] = adf['covid_region'].astype(int)
    adf['date'] = pd.to_datetime(adf['date'])

    rr_colors = ['#397FB9', '#397FB9', '#E21E26', '#98509F', '#98509F', '#E21E26',
                 '#4EAF49', '#4EAF49', '#4EAF49', '#4EAF49', '#4EAF49']
    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(11,6))
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.05, top=0.95, hspace=0.3, wspace=0.25)
    formatter = mdates.DateFormatter("%m-%d")
    for i, (region, cdf) in enumerate(adf.groupby('covid_region')) :
        ax = fig.add_subplot(3,4,i+1)
        cdf[channel] = cdf[channel]/cdf['pop']*1000
        cdf['moving_ave'] = cdf[channel].rolling(window=7, center=False).mean()
        ax.plot(cdf['date'], cdf['moving_ave'], '-', color=rr_colors[region-1], linewidth=1)
        ax.fill_between(cdf['date'].values, [0] * len(cdf['moving_ave']), cdf['moving_ave'],
                        linewidth=0, color=rr_colors[region-1], alpha=0.3)
        ax.set_ylim(0, 25)
        # ax.set_ylim(0, 11)
        ax.set_xlim(date(2020, 3, 1), date(2021, 1, 1))
        ax.set_title('Covid Region %d' % region)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

    fig.savefig(os.path.join(plot_dir, 'tests_per_1000_pop_covid_region_LL%s.pdf' % LL_date), format='PDF')


def plot_test_per_pos() :

    adf = pd.read_csv(line_list_fname)
    adf = adf[adf['covid_region'].isin(range(1,12))]
    # adf = adf[adf['county'] != 'Champaign']

    adf['date'] = pd.to_datetime(adf['date'])
    adf = adf.groupby(['date', 'covid_region']).agg(np.sum).reset_index()
    firstday = np.min(adf['date'])
    adf['week'] = adf['date'].apply(lambda x : int((x - firstday).days/7))
    adf = adf.groupby(['week', 'covid_region']).agg({'total_specs' : np.sum,
                                                     'positive_specs' : np.sum}).reset_index()
    adf['date'] = adf['week'].apply(lambda x : firstday + timedelta(days=x*7))
    adf['covid_region'] = adf['covid_region'].astype(int)
    adf = adf.sort_values(by=['covid_region', 'week'])
    adf = adf[adf['positive_specs'] > 0]
    adf['tests_per_pos'] = adf['total_specs'] / adf['positive_specs']

    rr_colors = ['#397FB9', '#397FB9', '#E21E26', '#98509F', '#98509F', '#E21E26',
                 '#4EAF49', '#4EAF49', '#4EAF49', '#4EAF49', '#4EAF49']
    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(11,6))
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.05, top=0.95, hspace=0.3, wspace=0.25)
    formatter = mdates.DateFormatter("%m-%d")

    for i, (region, cdf) in enumerate(adf.groupby('covid_region')) :
        ax = fig.add_subplot(3,4,i+1)
        ax.plot(cdf['date'], cdf['tests_per_pos'], '-', color=rr_colors[region-1], linewidth=1)
        ax.fill_between(cdf['date'].values, [0] * len(cdf['tests_per_pos']), cdf['tests_per_pos'],
                        linewidth=0, color=rr_colors[region-1], alpha=0.3)
        ax.set_ylim(0, 150)
        ax.set_xlim(firstday, date(2020, 9, 29))
        ax.set_title('Covid Region %d' % region)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

    fig.savefig(os.path.join(plot_dir, 'tests_per_pos_covid_region_LL%s.pdf' % LL_date), format='PDF')


def plot_tpr() :

    adf = pd.read_csv(line_list_fname)
    adf = adf[adf['covid_region'].isin(range(1,12))]
    # adf = adf[adf['county'] != 'Champaign']

    adf['date'] = pd.to_datetime(adf['date'])
    adf = adf.groupby(['date', 'covid_region']).agg(np.sum).reset_index()
    # firstday = np.min(adf['date'])
    # adf['week'] = adf['date'].apply(lambda x : int((x - firstday).days/7))
    # adf = adf.groupby(['week', 'covid_region']).agg({'total_specs' : np.sum,
    #                                                  'positive_specs' : np.sum}).reset_index()
    # adf['date'] = adf['week'].apply(lambda x : firstday + timedelta(days=x*7))
    # adf['covid_region'] = adf['covid_region'].astype(int)
    # adf = adf.sort_values(by=['covid_region', 'week'])
    adf = adf.sort_values(by=['covid_region', 'date'])
    adf = adf[adf['total_specs'] > 0]
    adf['tpr'] = adf['positive_specs']/adf['total_specs']

    rr_colors = ['#397FB9', '#397FB9', '#E21E26', '#98509F', '#98509F', '#E21E26',
                 '#4EAF49', '#4EAF49', '#4EAF49', '#4EAF49', '#4EAF49']
    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(11,6))
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.05, top=0.95, hspace=0.3, wspace=0.25)
    formatter = mdates.DateFormatter("%m-%d")

    for i, (region, cdf) in enumerate(adf.groupby('covid_region')) :
        ax = fig.add_subplot(3,4,i+1)
        cdf = copy.copy(cdf)

        cdf['moving_ave_frac'] = cdf['tpr'].rolling(window=7, center=True).mean()
        ax.plot(cdf['date'], cdf['moving_ave_frac'], '-')
        cdf['moving_ave_test'] = cdf['total_specs'].rolling(window=7, center=True).sum()
        cdf['moving_ave_pos'] = cdf['positive_specs'].rolling(window=7, center=True).sum()
        lows, highs = [], []
        for r, row in cdf.iterrows():
            low, high = proportion_confint(row['moving_ave_pos'], row['moving_ave_test'])
            lows.append(low)
            highs.append(high)

        ax.fill_between(cdf['date'].values, lows, highs, linewidth=0, alpha=0.3)

        # ax.fill_between(cdf['date'].values, [0] * len(cdf['tpr']), cdf['tpr'],
        #                 linewidth=0, color=rr_colors[region-1], alpha=0.3)
        ax.set_ylim(0, 0.18)
        ax.set_xlim(date(2020,6,10), date(2021, 1, 15))
        ax.set_title('Covid Region %d' % region)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

    fig.savefig(os.path.join(plot_dir, 'tpr_covid_region_LL%s.png' % LL_date))
    fig.savefig(os.path.join(plot_dir, 'tpr_covid_region_LL%s.pdf' % LL_date), format='PDF')


def plot_tests_by_county_map() :

    def format_ax(ax, name):
        ax.set_title(name)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.axis('off')

    def plot_subset(adf, channel, county_shp, maxdate, mindate, ax, bins) :
        vmin, vmax = np.min(bins), np.max(bins)
        norm = colors.Normalize(vmin=vmin, vmax=vmax)
        colormap = 'plasma'

        df = adf[(adf['date'] > mindate) & (adf['date'] <= maxdate)].groupby('county').agg(np.mean).reset_index()

        df['per pop'] = df[channel] / df['pop'] * 1000
        print(max(df['per pop']))
        df.loc[df['per pop'] > 20, 'per pop'] = 11
        ds_shp = pd.merge(left=county_shp, right=df, left_on='COUNTY_NAM', right_on='county')
        ds_shp.crs = {'init': 'epsg:4326'}
        ds_shp = ds_shp.to_crs({'init': 'epsg:3395'})
        ds_shp.plot(ax=ax, column='per pop',
                    cmap=colormap, edgecolor='0.8',
                    linewidth=0.8, legend=False, norm=norm)
        sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
        sm._A = []
        cbar = fig.colorbar(sm, ax=ax)

    adf = pd.read_csv(line_list_fname)
    adf = adf[adf['covid_region'].isin(range(1,12))]
    adf['county'] = adf['county'].apply(lambda x : x.upper())
    adf.loc[adf['covid_region'] == 11, 'county'] = 'CHICAGO'
    adf = adf.groupby(['date', 'county'])['positive_specs', 'total_specs'].agg(np.sum).reset_index()

    county_pop = pd.read_csv(os.path.join(box_data_path, 'EMS Population', 'covidregion_population_by_county.csv'))
    county_pop.loc[county_pop['new_restore_region'] == 11, 'County'] = 'CHICAGO'
    adf.loc[adf['county'] == 'DEWITT', 'county'] = 'DE WITT'
    adf = pd.merge(left=adf, right=county_pop, left_on='county', right_on='County')

    county_shp = gpd.read_file(os.path.join(shp_path, 'covid_regions', 'counties.shp'))
    adf['date'] = pd.to_datetime(adf['date'])

    fig = plt.figure(figsize=(10,8))
    # chunks = np.linspace(0, 0.4, 20)
    chunks = np.linspace(0.2, 5, 20)

    maxdate = date(2020,10,26)
    mindate = maxdate - timedelta(days=7)
    ax = fig.add_subplot(1,2,1)
    plot_subset(adf, 'positive_specs', county_shp, maxdate, mindate, ax, chunks)
    format_ax(ax, 'positive_specs')

    ax = fig.add_subplot(1,2,2)
    plot_subset(adf, 'total_specs', county_shp, maxdate, mindate, ax, chunks)
    format_ax(ax, 'total_specs')
    fig.savefig(os.path.join(plot_dir, 'tests_and_pos_per_1000_pop_county_%s.pdf' % str(maxdate)), format='PDF')
    plt.show()


if __name__ == '__main__' :

    # plot_weekly_share_by_age()
    # plot_tests_per_pop_covid_region()
    plot_tpr()
    # plot_tests_by_county_map()