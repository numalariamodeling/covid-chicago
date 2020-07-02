import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
from idph_exploration import load_cleaned_line_list

mpl.rcParams['pdf.fonttype'] = 42

box_data_path = '/Users/jlg1657/Box/NU-malaria-team/data/covid_IDPH'
project_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago'
plot_path = os.path.join(project_path, 'Plots + Graphs', 'county_timeseries')


first_day = date(2020,2,29)
last_day = date(2020,6,8)

def plot_ems_timeseries(adf, ems) :

    df = adf[adf['EMS'] == ems]
    plot_timeseries(df, 'EMS_%d' % ems)


def plot_county_timeseries(adf, county) :

    df = adf[adf['county_at_onset'] == county]
    plot_timeseries(df, county)


def plot_timeseries(df, name) :

    cols = ['id', 'deceased_date', 'onset_date', 'earliest_spec_coll_date']

    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(name, figsize=(8,6))
    fig.subplots_adjust(bottom=0.05, hspace=0.15)
    formatter = mdates.DateFormatter("%m-%d")

    for i, c in enumerate([x for x in cols if 'date' in x]) :
        df[c] = pd.to_datetime(df[c])
        ax = fig.add_subplot(3,1,1+i)

        gdf = df.groupby(c)['id'].agg(len).reset_index()
        gdf = gdf.rename(columns={'id' : 'number'})

        ax.bar(gdf[c].values, gdf['number'],
               align='center', color='#a187be', linewidth=0)
        gdf['moving_ave'] = gdf['number'].rolling(window=7, center=True).mean()
        ax.plot(gdf[c], gdf['moving_ave'], '-', color='#414042')
        ax.set_title('daily by %s' % c, y=0.85)
        ax.set_xlim(first_day, last_day)
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

    fig.suptitle(name)
    plt.savefig(os.path.join(plot_path, '%s.png' % name))


if __name__ == '__main__' :

    counties = ['Union']
    df = load_cleaned_line_list()
    for county in counties :
        plot_county_timeseries(df, county)

    # for ems in range(1, 12) :
    #     plot_ems_timeseries(df, ems)

    plt.show()
