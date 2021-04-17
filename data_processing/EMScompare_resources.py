import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
from processing_helpers import *
from plotting.colors import load_color_palette


mpl.rcParams['pdf.fonttype'] = 42
today = datetime.today()

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
plotdir = os.path.join(projectpath, 'Plots + Graphs', 'Emresource Plots')


def emresource_by_ems() :

    df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'emresource_by_hospital.csv'))
    cols = ['confirmed_covid_deaths_prev_24h',
            'confirmed_covid_icu',
            'covid_non_icu']

    gdf = df.groupby(['date_of_extract', 'region'])[cols].agg(np.sum).reset_index()
    gdf = gdf.sort_values(by=['date_of_extract', 'region'])
    gdf.to_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'emresource_by_EMSregion.csv'), index=False)


def plot_emresource(scale='') :

    ems_regions = {
        'northcentral' : [1, 2],
        'northeast' : [7, 8, 9, 10, 11],
        'central' : [3, 6],
        'southern' : [4, 5]
    }

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports',
                                      'emresource_by_region.csv'))

    sxmin = '2020-03-24'
    xmin = datetime.strptime(sxmin, '%Y-%m-%d')
    xmax = datetime.today()
    datetoday = xmax.strftime('%y%m%d')

    ref_df['suspected_and_confirmed_covid_icu'] = ref_df['suspected_covid_icu'] + ref_df['confirmed_covid_icu']
    ref_df['date'] = pd.to_datetime(ref_df['date_of_extract'])
    first_day = datetime.strptime('2020-03-24', '%Y-%m-%d')

    ref_df = ref_df.rename(columns={
        'confirmed_covid_deaths_prev_24h' : 'deaths',
        'confirmed_covid_icu' : 'ICU conf',
        'confirmed_covid_on_vents' : 'vents conf',
        'suspected_and_confirmed_covid_icu' : 'ICU conf+susp',
        'covid_non_icu' : 'non ICU'
    })

    # channels = ['ICU conf+susp', 'ICU conf', 'vents conf', 'deaths', 'non ICU']
    channels = ['ICU conf', 'non ICU']
    ref_df = ref_df[['date', 'covid_region'] + channels]

    palette = load_color_palette('wes')
    formatter = mdates.DateFormatter("%m-%d")

    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(14,10))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.95, bottom=0.05, hspace=0.25)

    # ref_df = ref_df[(ref_df['date'] >= date(2020, 3, 1)) & (ref_df['date'] < date(2021, 1, 1))]

    def format_plot(ax) :
        ax.set_xlim(xmin, )
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        if scale == 'log' :
            ax.set_yscale('log')

    for ri, (covid_region, pdf) in enumerate(ref_df.groupby('covid_region')) :
        ax = fig.add_subplot(4,3,ri+1)

        for (c,name) in enumerate(channels):
            if name == 'non ICU' :
                df = pdf[pdf['date'] >= date(2020,5,6)]
            else :
                df = pdf
            df['moving_ave'] = df[name].rolling(window = 7, center=True).mean()
            ax.plot(df['date'].values, df['moving_ave'], color=palette[c], label=name)
            ax.scatter(df['date'].values, df[name], s=10, linewidth=0, color=palette[c], alpha=0.3, label='')
            if name == 'non ICU' :
                ax.set_ylim(0,)
            # ax.set_xlim(date(2020,3,25), date(2021,1,1))

        ax.set_title('covid region %d' % covid_region)
        format_plot(ax)

    il_df = ref_df.groupby('date')[channels].agg(np.sum).reset_index()
    # print(il_df.tail(10))
    ax = fig.add_subplot(4, 3, 12)
    for (c, name) in enumerate(channels):
        if name == 'non ICU':
            df = il_df[il_df['date'] >= date(2020, 5, 6)]
        else:
            df = il_df
        df['moving_ave'] = df[name].rolling(window=7, center=True).mean()
        ax.plot(df['date'].values, df['moving_ave'], color=palette[c], label=name)
        ax.scatter(df['date'].values, df[name], s=10, linewidth=0, color=palette[c], alpha=0.3, label='')

    ax.set_title('Illinois')
    format_plot(ax)
    ax.legend()
    # ax.legend(bbox_to_anchor=(1.5, 1))

    fig.savefig(os.path.join(plotdir, 'EMResource_by_covid_region_%s.png' % scale))
    fig.savefig(os.path.join(plotdir, 'EMResource_by_covid_region_%s.pdf' % scale), format='PDF')


if __name__ == '__main__' :

    plot_emresource('nolog')
    # plot_emresource('log')
    # emresource_by_ems()
    # plt.show()
