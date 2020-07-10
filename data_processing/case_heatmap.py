import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns

mpl.rcParams['pdf.fonttype'] = 42


idph_data_path = '/Volumes/fsmresfiles/PrevMed/Covid-19-Modeling/IDPH line list'
cleaned_line_list_fname = os.path.join(idph_data_path,
                                       'LL_200708_JGcleaned_no_race.csv')
box_data_path = '/Users/jlg1657/Box/NU-malaria-team/data/covid_IDPH'
project_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago'
plot_path = os.path.join(project_path, 'Plots + Graphs')
emr_fname = os.path.join(box_data_path, 'emresource_by_region.csv')


def load_cleaned_line_list() :

    df = pd.read_csv(cleaned_line_list_fname)
    return df


def make_heatmap(ax, adf, col) :

    palette = sns.color_palette('RdYlBu_r', 101)

    df = adf.dropna(subset=[col])
    df = df.groupby([col, 'EMS'])['id'].agg(len).reset_index()
    df = df.rename(columns={'id' : col,
                            col : 'date'})
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['EMS', 'date'])

    ax.fill_between([np.min(df['date']), np.max(df['date']) + timedelta(days=1)],
                    [0.5, 0.5], [11.5, 11.5], linewidth=0, color=palette[0])
    for ems, edf in df.groupby('EMS') :
        max_in_col = np.max(edf[col])
        print(ems, max_in_col)
        for r, row in edf.iterrows() :
            ax.fill_between([row['date'], row['date'] + timedelta(days=1)],
                            [ems-0.5, ems-0.5], [ems+0.5, ems+0.5],
                            color=palette[int(row[col]/max_in_col*100)],
                            linewidth=0)
    ax.set_title(col)
    ax.set_ylabel('EMS region')
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())


def heatmap() :

    adf = load_cleaned_line_list()

    fig = plt.figure(figsize=(10,5))
    fig.subplots_adjust(left=0.05, right=0.97)
    cols = ['specimen_collection', 'deceased_date']

    for c, col in enumerate(cols) :
        ax = fig.add_subplot(1,len(cols),c+1)
        make_heatmap(ax, adf, col)

    plt.savefig(os.path.join(plot_path, 'EMS_cases_deaths_heatmap_200708LL.png'))
    plt.show()


if __name__ == '__main__' :

    adf = load_cleaned_line_list()
    col = 'specimen_collection'
    df = adf.dropna(subset=[col])
    df = df.groupby([col, 'EMS'])['id'].agg(len).reset_index()
    df = df.rename(columns={'id' : col,
                            col : 'date'})
    df = df.sort_values(by=['EMS', 'date'])
    df.to_csv(os.path.join(box_data_path, 'Corona virus reports', '200708_LL_cases_by_EMS_spec_collection.csv'), index=False)
    exit()


    heatmap()
    exit()
    adf = load_cleaned_line_list()

    fig = plt.figure(figsize=(10,5))
    fig.subplots_adjust(left=0.05, right=0.97)
    col = 'specimen_collection'

    df = adf.dropna(subset=[col])
    df = df.groupby([col, 'EMS'])['id'].agg(len).reset_index()
    df = df.rename(columns={'id' : col,
                            col : 'date'})
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['EMS', 'date'])

    ax = fig.gca()
    palette = sns.color_palette('rainbow', 11)
    for e, (ems, edf) in enumerate(df.groupby('EMS')) :
        max_in_col = np.max(edf[col])
        edf['norm'] = edf[col]/max_in_col
        ax.plot(edf['date'], edf['norm'], color=palette[e], label=ems)

    ax.legend()
    plt.show()