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

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

first_day = date(2020, 3, 1)

if __name__ == '__main__' :

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_chicago', 'NMH', 'Modeling COVID Data NMH_v1_200327_jg.csv'))
    ref_df['date'] = pd.to_datetime(ref_df['date'])
    exp_name = '20200402_extendedModel_age_NMH_test4'
    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = sim_output_path

    scen_df = pd.read_csv(os.path.join(sim_output_path, 'scenarios.csv'))

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoresDat_withIncidence_all.csv'))
    df = pd.merge(left=df, right=scen_df[['scen_num', 'Ki']], on='scen_num', how='left')
    channels = ['new_hospitalized_all', 'hosp_cumul_all', 'hospitalized_all', 'critical_all']
    data_channel_names = ['covid pos admissions', 'cumulative admissions', 'inpatient census', 'ICU census']

    fig = plt.figure()
    palette = sns.color_palette('muted', len(channels))
    for c, channel in enumerate(channels) :
        ax = fig.add_subplot(2,2,c+1)

        for k, (ki, kdf) in enumerate(df.groupby('Ki')) :
            mdf = kdf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
            dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
            ax.plot(dates, mdf['mean'], color=palette[k], label=ki)
            ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                            color=palette[k], linewidth=0, alpha=0.2)
            ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                            color=palette[k], linewidth=0, alpha=0.4)

        ax.set_title(channel, y=0.8)
        ax.legend()

        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_xlim(first_day, date(2020, 4, 1))
        ax.set_ylim(0,40)

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#969696', linewidth=0)
    plt.show()