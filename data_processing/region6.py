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
import matplotlib.colors as colors
from plotting.colors import load_color_palette
from public_idph_data import assign_counties_restore_region

mpl.rcParams['pdf.fonttype'] = 42


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

plot_dir = os.path.join(projectpath, 'Plots + Graphs', '_trend_tracking')
datapath = os.path.join(datapath, 'covid_IDPH')
shp_path = os.path.join(datapath, 'shapefiles')


if __name__ == '__main__' :

    df = assign_counties_restore_region()
    df = df[df['new_restore_region'] == 6]
    df_all = df.groupby('update_date')[['Positive_Cases', 'Tested']].agg(np.sum).reset_index()
    df_no6 = df[df['County'] != 'CHAMPAIGN'].groupby('update_date')[['Positive_Cases', 'Tested']].agg(np.sum).reset_index()
    df_6only = df[df['County'] == 'CHAMPAIGN'].groupby('update_date')[['Positive_Cases', 'Tested']].agg(np.sum).reset_index()

    pop_df = pd.read_csv(os.path.join(datapath, 'EMS Population', 'covidregion_population_by_county.csv'))
    pops = {
        'all' : np.sum(pop_df[pop_df['new_restore_region'] == 6]['pop']),
        'no Champaign' : np.sum(pop_df[(pop_df['new_restore_region'] == 6) & (pop_df['County'] != 'CHAMPAIGN')]['pop']),
        'Champaign only' : np.sum(pop_df[pop_df['County'] == 'CHAMPAIGN']['pop'])
    }

    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(12,3))
    fig.subplots_adjust(left=0.07, right=0.98, wspace=0.2)
    palette = load_color_palette('wes')
    formatter = mdates.DateFormatter("%m-%d")

    for i, (name, cdf) in enumerate(zip(['all', 'no Champaign', 'Champaign only'], [df_all, df_no6, df_6only])) :
        ax = fig.add_subplot(1,3,1)
        cdf['daily_pos'] = np.insert(np.diff(cdf['Positive_Cases']), 0, 0)
        cdf['daily_test'] = np.insert(np.diff(cdf['Tested']), 0, 0)
        cdf.loc[cdf['daily_test'] == 0, 'daily_test'] = 1
        cdf['daily_tpr'] = cdf['daily_pos']/cdf['daily_test']

        cdf['moving_ave'] = cdf['daily_pos'].rolling(window=7, center=False).mean()
        max_pos = np.max(cdf['moving_ave'])
        ax.plot(cdf['update_date'], cdf['moving_ave']/pops[name]*100000, '-', color=palette[i], label=name)
        ax.legend()
        ax.set_xlim(np.min(df['update_date']) - timedelta(days=1),
                    np.max(df['update_date']) + timedelta(days=1))

        ax.set_ylabel('cases per 100,000')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

        ax = fig.add_subplot(1,3,2)
        cdf = cdf[cdf['Positive_Cases'] <= cdf['Tested']]
        cdf['moving_ave'] = cdf['daily_tpr'].rolling(window=7, center=False).mean()
        ax.plot(cdf['update_date'], cdf['moving_ave'], '-', color=palette[i], label=name)
        ax.legend()
        ax.set_xlim(np.min(cdf['update_date']) - timedelta(days=1),
                    np.max(cdf['update_date']) + timedelta(days=1))
        ax.set_ylabel('test positivity rate')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

        ax = fig.add_subplot(1,3,3)
        cdf = cdf[cdf['update_date'] >= date(2020,5,3)]
        cdf['moving_ave'] = cdf['daily_test'].rolling(window=7, center=False).mean()
        ax.plot(cdf['update_date'], cdf['moving_ave']/pops[name]*1000, '-', color=palette[i], label=name)
        ax.legend()
        ax.set_xlim(np.min(cdf['update_date']) - timedelta(days=1),
                    np.max(cdf['update_date']) + timedelta(days=1))
        ax.set_ylabel('tests per 1000')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

    plt.savefig(os.path.join(plot_dir, 'region6.png'))
    plt.savefig(os.path.join(plot_dir, 'region6.pdf'), format='PDF')
    plt.show()