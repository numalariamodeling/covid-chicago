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
from simulation_setup import *
from data_comparison import load_sim_data

mpl.rcParams['pdf.fonttype'] = 42
today = datetime.today()

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def read_and_combine_data(stem):
   #stem = 'scenario1'
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    adf = pd.DataFrame()
    for d, exp_name in enumerate(exp_names):

        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        ems = int(exp_name.split('_')[2])
        cdf = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
        #channels = cdf.columns
        first_day = datetime.strptime(cdf['first_day'].unique()[0], '%Y-%m-%d')

        cdf['ems'] = ems
        cdf['date'] = cdf['time'].apply(lambda x: first_day + timedelta(days=int(x)))
        adf = pd.concat([adf, cdf])


    sum_channels = [ 'susceptible', 'exposed', 'asymptomatic',
       'presymptomatic', 'symptomatic_mild', 'symptomatic_severe',
       'hospitalized', 'critical', 'deaths', 'recovered', 'asymp_cumul',
       'asymp_det_cumul', 'symp_mild_cumul', 'symp_mild_det_cumul',
       'symp_severe_cumul', 'symp_severe_det_cumul', 'hosp_cumul',
       'hosp_det_cumul', 'crit_cumul', 'crit_det_cumul', 'crit_det',
       'death_det_cumul', 'detected_cumul', 'detected', 'infected']

    mdf = adf.groupby(['date','run_num','scen_num','sample_num'])[sum_channels].agg(np.sum).reset_index()

    return(mdf)

def save_plot_csv(scen):
    df = read_and_combine_data(scen)

    channels = ['infected', 'deaths', 'hospitalized', 'critical', 'ventilators']
    df['ventilators'] = df['critical']*0.8

    fig = plt.figure(figsize=(18,12))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.07, hspace=0.15)
    palette = sns.color_palette('Set1', len(channels))

    adf = pd.DataFrame()
    for c, channel in enumerate(channels) :
        ax = fig.add_subplot(4,2,c+1)
        mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

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

        plot_first_day = date(2020, 3, 13)
        plot_last_day = date(2020, 7, 31)
        mdf = mdf[(mdf['date'] >= plot_first_day) & (mdf['date'] <= plot_last_day)]

        del mdf['CI_25']
        del mdf['CI_75']
        if adf.empty :
            adf = mdf
        else :
            adf = pd.merge(left=adf, right=mdf, on='date')

    if scen =="scenario1":
        filename = 'nu_illinois_endsip_20200419'
    if scen =="scenario2":
        filename = 'nu_illinois_neversip_20200419'
    if scen =="scenario3":
        filename = 'nu_illinois_baseline_20200419'

    adf.to_csv(os.path.join(wdir, 'simulation_output/_csv', filename + '.csv'), index=False)
    plt.savefig(os.path.join(wdir, 'simulation_output/_plots/IL', filename + '.png'))
    plt.savefig(os.path.join(wdir, 'simulation_output/_plots/IL', filename + '.pdf'), format='PDF')
    #plt.show()
    return()


if __name__ == '__main__' :
    save_plot_csv("scenario1")
    save_plot_csv("scenario2")
    save_plot_csv("scenario3")