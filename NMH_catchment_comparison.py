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


def load_sim_data(exp_name) :

    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    scen_df = pd.read_csv(os.path.join(sim_output_path, 'scenarios.csv'))

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    if 'Ki' not in df.columns.values :
        df = pd.merge(left=df, right=scen_df[['scen_num', 'Ki']], on='scen_num', how='left')

    df = calculate_incidence(df)

    return df


def count_new(df, curr_ch) :

    ch_list = list(df[curr_ch].values)
    diff = [0] + [ch_list[x] - ch_list[x - 1] for x in range(1, len(df))]
    return diff


def calculate_incidence(adf, output_filename=None) :

    inc_df = pd.DataFrame()
    for (samp, scen), df in adf.groupby(['sample_num', 'scen_num']) :

        sdf = pd.DataFrame( { 'time' : df['time'],
                              'new_exposures' : [-1*x for x in count_new(df, 'susceptible')],
                              'new_asymptomatic' : count_new(df, 'asymp_cumul'),
                              'new_asymptomatic_detected' : count_new(df, 'asymp_det_cumul'),
                              'new_symptomatic' : count_new(df, 'symp_cumul'),
                              'new_symptomatic_detected' : count_new(df, 'symp_det_cumul'),
                              'new_hospitalized' : count_new(df, 'hosp_cumul'),
                              'new_detected' : count_new(df, 'detected_cumul'),
                              'new_critical' : count_new(df, 'crit_cumul'),
                              'new_deaths' : count_new(df, 'deaths')
                              })
        sdf['sample_num'] = samp
        sdf['scen_num'] = scen
        inc_df = pd.concat([inc_df, sdf])
    adf = pd.merge(left=adf, right=inc_df, on=['sample_num', 'scen_num', 'time'])
    if output_filename :
        adf.to_csv(os.path.join(sim_output_path, output_filename), index=False)
    return adf


def compare_NMH(exp_name) :

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_chicago', 'NMH', 'Modeling COVID Data NMH_v1_200327_jg.csv'))
    ref_df['date'] = pd.to_datetime(ref_df['date'])

    df = load_sim_data(exp_name)

    plot_path = os.path.join(wdir, 'simulation_output', exp_name)

    channels = ['new_hospitalized_all', 'hosp_cumul_all', 'hospitalized_all', 'critical_all']
    data_channel_names = ['covid pos admissions', 'cumulative admissions', 'inpatient census', 'ICU census']

    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=40)


def plot_sim_and_ref(df, ref_df, channels, data_channel_names, ymax=40) :

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
        ax.set_ylim(0,ymax)

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#969696', linewidth=0)
    plt.show()


def compare_county(exp_name, county_name) :

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', '200401_aggregated_data_cleaned.csv'))
    ref_df = ref_df[ref_df['county'] == county_name]
    ref_df['spec_date'] = pd.to_datetime(ref_df['spec_date'])
    ref_df = ref_df.rename(columns={'spec_date' : 'date'})

    df = load_sim_data(exp_name)

    channels = ['new_detected', 'new_hospitalized', 'detected_cumul', 'hosp_cumul']
    data_channel_names = ['new_case', 'new_hospitalizations', 'total_case', 'total_hospitalizations']

    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=1100)


if __name__ == '__main__' :

    exp_name = '20200402_extendedModel_TEST1'
    compare_county(exp_name, 'Cook')
