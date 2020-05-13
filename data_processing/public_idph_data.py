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

    IL_fname = os.path.join(datapath, 'Corona virus reports', 'covid_tracking_project_200505.csv')
    df = pd.read_csv(IL_fname)
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

    fig = plt.figure()
    ax = fig.gca()
    ax.plot(df['date'], df['positive'], label='positives')
    ax.plot(df['date'], df['death'], label='death')
    ax.legend()
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    plt.savefig(os.path.join(plot_dir, 'idph_public_cases_and_deaths.pdf'), format='PDF')


def plot_cases_by_county() :

    county_fname = os.path.join(datapath, 'Corona virus reports', 'IDPH Stats County public.csv')
    county_shp = gpd.read_file(os.path.join(shp_path, 'IL_BNDY_County', 'IL_BNDY_County_Py.shp'))
    county_pop = pd.read_csv(os.path.join(datapath, 'population', 'illinois_pop_by_county.csv'))

    df = pd.read_csv(county_fname)
    df['update_date'] = pd.to_datetime(df['update_date'])
    df = df[df['update_date'] == date(2020, 5, 5)]
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
