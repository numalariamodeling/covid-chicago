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

first_day = date(2020, 2, 28)


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
                              # 'new_symptomatic_mild' : count_new(df, 'symp_mild_cumul'),
                              'new_detected_hospitalized' : count_new(df, 'hosp_det_cumul'),
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

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_chicago', 'NMH', 'Modeling COVID Data NMH_v2_200406_jg.csv'))
    ref_df['date'] = pd.to_datetime(ref_df['date'])

    df = load_sim_data(exp_name)

    channels = ['new_detected_hospitalized', 'hosp_det_cumul', 'hospitalized', 'critical']
    data_channel_names = ['covid pos admissions', 'cumulative admissions', 'inpatient census', 'ICU census']

    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_NMH_v1')
    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=40,
                     plot_path=plot_path)

    data_channel_names = ['new admits v2', 'cumulative admits positive results v2', 'non ICU v2', 'ICU census v2']

    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_NMH_v2')
    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=40,
                     plot_path=plot_path)


def plot_sim_and_ref(df, ref_df, channels, data_channel_names, ymax=40, plot_path=None) :

    fig = plt.figure()
    palette = sns.color_palette('husl', len(df['Ki'].unique()))
    k = 0
    for c, channel in enumerate(channels) :
        ax = fig.add_subplot(2,2,c+1)

        for k, (ki, kdf) in enumerate(df.groupby('Ki')) :
            mdf = kdf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
            dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
            ax.plot(dates, mdf['mean'], color=palette[k], label=ki)
            # ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
            #                 color=palette[k], linewidth=0, alpha=0.2)
            ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                            color=palette[k], linewidth=0, alpha=0.4)

        ax.set_title(channel, y=0.8)
        # ax.legend()

        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_xlim(first_day, date(2020, 4, 4))
        # ax.set_ylim(1,ymax)
        ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0)
    if plot_path :
        plt.savefig('%s.png' % plot_path)
        plt.savefig('%s.pdf' % plot_path, format='PDF')


def compare_county(exp_name, county_name) :

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', '200401_aggregated_data_cleaned.csv'))
    ref_df = ref_df[ref_df['county'] == county_name]
    ref_df['spec_date'] = pd.to_datetime(ref_df['spec_date'])
    ref_df = ref_df.rename(columns={'spec_date' : 'date'})

    df = load_sim_data(exp_name)

    channels = ['new_detected', 'new_detected_hospitalized', 'detected_cumul', 'hosp_det_cumul']
    data_channel_names = ['new_case', 'new_hospitalizations', 'total_case', 'total_hospitalizations']

    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data')
    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=1100,
                     plot_path=plot_path)

    fname = 'emresource_20200325_20200403.csv'
    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH/Corona virus reports', fname))
    ref_df = ref_df[ref_df['region'] == 11]
    ref_df['suspected_and_confirmed_covid_icu'] = ref_df['suspected_covid_icu'] + ref_df['confirmed_covid_icu']
    data_channel_names = ['suspected_and_confirmed_covid_icu', 'confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'confirmed_covid_on_vents']
    ref_df = ref_df.groupby('last_update')[data_channel_names].agg(np.sum).reset_index()
    ref_df['date'] = pd.to_datetime(ref_df['last_update'])

    df['ventilators'] = df['critical']*0.8
    df['critical_with_suspected'] = df['critical']
    channels = ['critical_with_suspected', 'deaths', 'critical', 'ventilators']
    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_emr')
    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=1100,
                     plot_path=plot_path)
    plt.show()


if __name__ == '__main__' :

    exp_name = '20200407mr_NMH_catchment_JG_run3'
    # compare_county(exp_name, 'Cook')
    compare_NMH(exp_name)
