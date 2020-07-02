import os
import geopandas as gpd
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns
import matplotlib.colors as colors

mpl.rcParams['pdf.fonttype'] = 42


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

plot_dir = os.path.join(projectpath, 'Plots + Graphs')
datapath = os.path.join(datapath, 'covid_IDPH')
shp_path = os.path.join(datapath, 'shapefiles')


def plot_IL_cases() :

    IL_fname = os.path.join(datapath, 'Corona virus reports', 'illinois_public.csv')
    df = pd.read_csv(IL_fname, parse_dates=['update_date'])
    df = df.rename(columns={'update_date' : 'date'})
    df = df.sort_values(by='date')
    df = df.fillna(0)

    formatter = mdates.DateFormatter("%m-%d")
    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(10,6))
    fig.subplots_adjust(left=0.07, right=0.97)

    ax = fig.add_subplot(3,1,1)
    df['daily_pos'] = np.insert(np.diff(df['tests_pos']), 0, 0)
    ax.bar(df['date'].values[1:], np.diff(df['tests_pos']),
           align='center', color='#a187be', linewidth=0)
    df['moving_ave'] = df['daily_pos'].rolling(window=7, center=True).mean()
    ax.plot(df['date'], df['moving_ave'], '-', color='#414042')
    ax.set_ylabel('positives')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    ax = fig.add_subplot(3,1,2)
    ax.bar(df['date'].values[1:], df['new_tests'][1:],
           align='center', color='#7AC4AD', linewidth=0)
    df['moving_ave'] = df['new_tests'].rolling(window=7, center=True).mean()
    ax.plot(df['date'], df['moving_ave'], '-', color='#414042')
    ax.set_ylabel('tests')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    ax = fig.add_subplot(3,1,3)
    ax.bar(df['date'].values[1:], np.diff(df['deaths']),
           align='center', color='#fbb46c', linewidth=0)
    df['daily_death'] = np.insert(np.diff(df['deaths']), 0, 0)
    df['moving_ave'] = df['daily_death'].rolling(window=7, center=True).mean()
    ax.plot(df['date'], df['moving_ave'], '-', color='#414042')
    ax.set_ylabel('deaths')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.savefig(os.path.join(plot_dir, 'idph_public_cases_and_deaths.pdf'), format='PDF')


def plot_cases_by_county() :

    county_fname = os.path.join(datapath, 'Corona virus reports', 'IDPH Stats County public.csv')
    county_shp = gpd.read_file(os.path.join(shp_path, 'IL_BNDY_County', 'IL_BNDY_County_Py.shp'))
    county_pop = pd.read_csv(os.path.join(datapath, 'population', 'illinois_pop_by_county.csv'))

    df = pd.read_csv(county_fname)
    df['update_date'] = pd.to_datetime(df['update_date'])
    df = df[df['update_date'] == date(2020, 6, 8)]
    df = df[~df['NOFO_Region'].isin(['Illinois', 'Out Of State', 'Unassigned'])]

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


if __name__ == '__main__' :

    plot_IL_cases()
    # plot_cases_by_county()
    plt.show()
