import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import seaborn as sns
from processing_helpers import *
from simulation_setup import *
from data_comparison import load_sim_data
from copy import copy

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

populations, Kis, startdate = load_setting_parameter()


if __name__ == '__main__' :

    exp_name = '20200416_EMS_11_mr_run4'
    region  = "EMS_11"
    first_day = startdate[region]  # date(2020, 2, 28)

    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    df = load_sim_data(exp_name)

    channels = ['infected', 'deaths', 'hospitalized', 'critical', 'ventilators']
    df['ventilators'] = df['critical']*0.8

    fig = plt.figure(figsize=(8,12))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.07, hspace=0.15)
    palette = sns.color_palette('Set1', len(channels))

    adf = pd.DataFrame()
    for c, channel in enumerate(channels) :
        ax = fig.add_subplot(4,2,c+1)
        mdf = df.groupby('time')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
        mdf['date'] = mdf['time'].apply(lambda x : first_day + timedelta(days=int(x)))

        ax.plot(mdf['date'], mdf['CI_50'], color=palette[c])
        ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
                        color=palette[c], linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=palette[c], linewidth=0, alpha=0.4)
        ax.set_title(channel, y=0.85)
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

        mdf = mdf.rename(columns={'CI_50' : '%s_median' % channel,
                                  'CI_2pt5' : '%s_95CI_lower' % channel,
                                  'CI_97pt5' : '%s_95CI_upper' % channel})
        mdf = mdf[mdf['time'] >= 22]
        del mdf['time']
        del mdf['CI_25']
        del mdf['CI_75']
        if adf.empty :
            adf = mdf
        else :
            adf = pd.merge(left=adf, right=mdf, on='date')
    adf.to_csv(os.path.join(sim_output_path, 'projection_for_civis.csv'), index=False)
    plt.savefig(os.path.join(sim_output_path, 'projection_for_civis.png'))
    plt.savefig(os.path.join(sim_output_path, 'projection_for_civis.pdf'), format='PDF')
    plt.show()

