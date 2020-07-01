import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
import geopandas as gpd
from shapely.geometry import mapping, Point, Polygon

mpl.rcParams['pdf.fonttype'] = 42


fsm_path = '/Volumes/fsmresfiles/PrevMed/Covid-19-Modeling'
idph_data_path = os.path.join(fsm_path, 'IDPH line list',)
ltcf_data_path = os.path.join('/Users/jlg1657/Box/Data Uploads/IDPH', 'untitled folder')
cleaned_line_list_fname = os.path.join(idph_data_path,
                                       'LL_200616_JGcleaned.csv')
ltcf_fname = os.path.join(ltcf_data_path, 'Modelors LTC Report_200617.xlsx')
cleaned_ltcf_fname = os.path.join(ltcf_data_path, 'Modelors LTC Report_200617_first_specimen.csv')

box_data_path = '/Users/jlg1657/Box/NU-malaria-team/data/covid_IDPH'
project_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago'
plot_path = os.path.join(project_path, 'Plots + Graphs')
shp_path = os.path.join(box_data_path, 'shapefiles')


def load_daily_ll_deaths() :

    df = pd.read_csv(cleaned_line_list_fname)
    df = df.dropna(subset=['deceased_date'])
    df = df.groupby('deceased_date')['id'].agg(len).reset_index()
    df = df.rename(columns={'id' : 'daily_deaths_line_list',
                            'deceased_date' : 'Deceased Date'})
    df['Deceased Date'] = pd.to_datetime(df['Deceased Date'])
    return df


def clean_ltcf() :

    df = pd.read_excel(ltcf_fname, skiprows=3)
    gdf = df.groupby('State Case Number')['Outbreak ID'].agg(len).reset_index()
    gdf = gdf.rename(columns={'Outbreak ID': 'num'})
    gdf = gdf[gdf['num'] > 1]

    adf = pd.DataFrame()
    for d, ddf in df.groupby('State Case Number') :
        sdf = ddf.head(1)
        adf = pd.concat([adf, sdf])
    adf.to_csv(cleaned_ltcf_fname, index=False)


def load_daily_ltcf_deaths() :

    df = pd.read_csv(cleaned_ltcf_fname)
    df = df.dropna(subset=['Deceased Date'])
    df = df.groupby('Deceased Date')['State Case Number'].agg(len).reset_index()
    df = df.rename(columns={'State Case Number' : 'daily_deaths_LTCF'})
    df['Deceased Date'] = pd.to_datetime(df['Deceased Date'])
    return df


def merge_LL_LTCF_deaths() :

    ll_df = load_daily_ll_deaths()
    ltcf_df = load_daily_ltcf_deaths()

    df = pd.merge(left=ll_df, right=ltcf_df, on='Deceased Date', how='outer')
    df = df.fillna(0)
    return df


def plot_daily_LL_LTCF_deaths() :

    df = merge_LL_LTCF_deaths()
    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    palette = sns.color_palette('Set1')
    fig = plt.figure(figsize=(10,6))
    ax = fig.add_subplot(2,1,1)
    ax.fill_between(df['Deceased Date'].values, [0]*len(df),
                    df['daily_deaths_line_list'], label='LL 200616', color=palette[0], alpha=0.5)
    ax.fill_between(df['Deceased Date'].values, [0]*len(df),
                    df['daily_deaths_LTCF'], label='LTCF 200617', color=palette[1], alpha=0.5)
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.set_ylabel('daily deaths')
    ax.legend()

    df['deaths'] = df['daily_deaths_line_list']
    df.loc[df['deaths'] < df['daily_deaths_LTCF'], 'deaths'] = df.loc[df['deaths'] < df['daily_deaths_LTCF'], 'daily_deaths_LTCF']
    df['frac LTCF'] = df['daily_deaths_LTCF']/df['deaths']

    ax = fig.add_subplot(2,1,2)
    ax.plot(df['Deceased Date'], df['frac LTCF'], color=palette[2])
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.set_ylabel('fraction of deaths in LTCF')

    fig.savefig(os.path.join(plot_path, 'LTCF', 'LTCF share of deaths 200619.png'))
    fig.savefig(os.path.join(plot_path, 'LTCF', 'LTCF share of deaths 200619.pdf'), format='PDF')
    plt.show()


def format_x_axis(ax) :

    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())


if __name__ == '__main__' :

    # clean_ltcf()
    # plot_daily_LL_LTCF_deaths()

    df = merge_LL_LTCF_deaths()
    df['non_LTCF_deaths'] = df['daily_deaths_line_list'] - df['daily_deaths_LTCF']
    df = df[df['non_LTCF_deaths'] >= 0]

    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    palette = sns.color_palette('Set1')
    fig = plt.figure(figsize=(10,5))
    fig.subplots_adjust(left=0.05, right=0.97)
    axes = [fig.add_subplot(1,2,x+1) for x in range(2)]
    for c, col in enumerate(['non_LTCF_deaths', 'daily_deaths_LTCF']) :
        ax = axes[0]
        ax.plot(df['Deceased Date'], df[col], color=palette[c], label=col)
        ax = axes[1]
        sdf = df[df[col] > 0]
        ax.scatter(sdf['Deceased Date'].values, sdf[col], 20, color=palette[c], linewidth=0)

    for ax in axes :
        ax.set_ylabel('number of deaths')
        format_x_axis(ax)
        ax.legend()
    axes[1].set_yscale('log')

    fig.savefig(os.path.join(plot_path, 'LTCF', 'LTCF and non LTCF deaths 200619.png'))
    fig.savefig(os.path.join(plot_path, 'LTCF', 'LTCF and non LTCF deaths 200619.pdf'), format='PDF')
    plt.show()
