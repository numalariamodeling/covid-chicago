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


mpl.rcParams['pdf.fonttype'] = 42
today = datetime.today()
datetoday = date(today.year, today.month, today.day)


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def load_sim_data(exp_name, input_wdir=None, input_sim_output_path =None) :
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    if 'Ki' not in df.columns.values :
        scen_df = pd.read_csv(os.path.join(sim_output_path, 'sampled_parameters.csv'))
        df = pd.merge(left=df, right=scen_df[['scen_num', 'Ki']], on='scen_num', how='left')

    df.columns = df.columns.str.replace('_All', '')
    df['infected_cumul'] = df['infected'] + df['recovered'] + df['deaths']
    df = calculate_incidence(df)

    return df


def compare_NMH(exp_name) :

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_chicago', 'NMH', 'Modeling COVID Data NMH_v1_200415_jg.csv'))
    ref_df['date'] = pd.to_datetime(ref_df['date'])

    df = load_sim_data(exp_name)
    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')

    channels = ['new_detected_hospitalized', 'hosp_det_cumul', 'hospitalized', 'critical']
    data_channel_names = ['covid pos admissions', 'cumulative admissions', 'inpatient census', 'ICU census']

    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_NMH_v1')
    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=1000,
                     plot_path=plot_path, first_day=first_day)

    #data_channel_names = ['new admits v2', 'cumulative admits positive results v2', 'non ICU v2', 'ICU census v2']

    #plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_NMH_v2')
    #plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=1000,
    #                 plot_path=plot_path, first_day=first_day)


def plot_sim_and_ref_Ki(df, ref_df, channels, data_channel_names, first_day=date(2020, 2, 22),
                     ymax=40, plot_path=None) :

    fig = plt.figure()
    palette = sns.color_palette('husl', len(df['Ki'].unique()))
    k = 0
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
        ax.set_xlim(first_day, datetoday)
        ax.set_ylim(1,ymax)
        ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0)
    if plot_path :
        plt.savefig('%s_Kisep.png' % plot_path)
        plt.savefig('%s_Kisep.pdf' % plot_path, format='PDF')

def plot_sim_and_ref(df, ref_df, channels, data_channel_names, titles, first_day=date(2020, 2, 22),
                     ymax=40, plot_path=None) :

    fig = plt.figure(figsize=(10,6))
    palette = sns.color_palette('husl', 8)
    k = 0
    for c, channel in enumerate(channels) :
        ax = fig.add_subplot(2,3,c+1)

        #for k, (ki, kdf) in enumerate(df.groupby('Ki')) :
        mdf = df.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
        dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
        ax.plot(dates, mdf['mean'], color=palette[k])
        ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                        color=palette[k], linewidth=0, alpha=0.2)
        ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                        color=palette[k], linewidth=0, alpha=0.4)

        ax.set_title(titles[c], y=0.8, fontsize=12)
        #ax.legend()

        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_xlim(first_day, datetoday)
        ax.set_ylim(1,ymax)
        ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0)
    fig.tight_layout()
    if plot_path :
        plt.savefig('%s_KiCI.png' % plot_path)
        plt.savefig('%s_KiCI.pdf' % plot_path, format='PDF')
    #return a


def compare_county(exp_name, county_name) :

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', '200401_aggregated_data_cleaned.csv'))
    ref_df = ref_df[ref_df['county'] == county_name]
    ref_df['spec_date'] = pd.to_datetime(ref_df['spec_date'])
    ref_df = ref_df.rename(columns={'spec_date' : 'date'})

    df = load_sim_data(exp_name)
    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')

    channels = ['new_detected', 'new_detected_hospitalized', 'detected_cumul', 'hosp_det_cumul']
    data_channel_names = ['new_case', 'new_hospitalizations', 'total_case', 'total_hospitalizations']

    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data')
    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=1100,
                     plot_path=plot_path, first_day=first_day)

    fname = 'emresource_20200325_20200403.csv'
    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH/Corona virus reports', fname))
    ref_df = ref_df[ref_df['region'] == 11]
    ref_df['suspected_and_confirmed_covid_icu'] = ref_df['suspected_covid_icu'] + ref_df['confirmed_covid_icu']
    data_channel_names = ['suspected_and_confirmed_covid_icu', 'confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'confirmed_covid_on_vents']
    ref_df = ref_df.groupby('date_of_extract')[data_channel_names].agg(np.sum).reset_index()
    ref_df['date'] = pd.to_datetime(ref_df['date_of_extract'])

    df['ventilators'] = df['critical']*0.8
    df['critical_with_suspected'] = df['critical']
    channels = ['critical_with_suspected', 'deaths', 'critical', 'ventilators']
    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_emr')
    plot_sim_and_ref_Ki(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=1100,
                     plot_path=plot_path, first_day=first_day)
    plt.show()


def compare_ems(exp_name, ems=0, source='EMR') :
    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'emresource_by_region.csv'))

    if ems > 0 :
        ref_df = ref_df[ref_df['region'] == ems]
    else :
        ref_df = ref_df.groupby('date_of_extract').agg(np.sum).reset_index()
    ref_df['suspected_and_confirmed_covid_icu'] = ref_df['suspected_covid_icu'] + ref_df['confirmed_covid_icu']
    data_channel_names = ['confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'confirmed_covid_on_vents']
    ref_df = ref_df.groupby('date_of_extract')[data_channel_names].agg(np.sum).reset_index()
    ref_df['date'] = pd.to_datetime(ref_df['date_of_extract'])

    df = load_sim_data(exp_name)
    #for x in df.columns:
    #   print(x)
    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')

    df['ventilators'] = get_vents(df['crit_det'].values)
    df['critical_with_suspected'] = df['critical']
    channels = ['new_detected_deaths', 'crit_det', 'ventilators']
    ref_df_emr = ref_df
    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_emr')
    #plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=5000,
                     #plot_path=plot_path, first_day=first_day)
    #plt.show()
    ref_df1 = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', '200629_jg_deceased_date_ems.csv'))
    ref_df2 = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', '200629_jg_admission_date_ems.csv'))
    if ems > 0 :
        ref_df1 = ref_df1[ref_df1['EMS'] == ems]
        ref_df2 = ref_df2[ref_df2['EMS'] == ems]
    else :
        ref_df1 = ref_df1.groupby('date').agg(np.sum).reset_index()
        ref_df2 = ref_df2.groupby('date').agg(np.sum).reset_index()
    ref_df1 = ref_df1.rename(columns={'cases': 'deaths'})
    ref_df2 = ref_df2.rename(columns={'cases': 'admissions'})
    del ref_df2['EMS']
    ref_df = pd.merge(left=ref_df1, left_on='date', right=ref_df2, right_on='date')
    ref_df['date'] = pd.to_datetime(ref_df['date'])
    data_channel_names = ['deaths', 'deaths', 'admissions']    

    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
    channels = ['new_detected_deaths', 'new_deaths', 'new_hospitalized']
    ref_df_ll = ref_df
    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_line_list')
    #plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, ymax=5000,
                     #plot_path=plot_path, first_day=first_day)
    ref_df = pd.merge(how='outer', left=ref_df_ll, left_on='date', right=ref_df_emr, right_on='date')
    ref_df = ref_df.sort_values('date')
    channels = ['new_detected_deaths', 'crit_det', 'ventilators','new_detected_deaths', 'new_deaths', 'new_detected_hospitalized']
    data_channel_names = ['confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'confirmed_covid_on_vents','deaths', 'deaths', 'admissions']
    titles = ['New Detected\nDeaths (EMR)', 'Critical Detected (EMR)', 'Ventilators (EMR)','New Detected\nDeaths (LL)','New Deaths (LL)', 'New Detected\nHospitalizations (LL)']
    plot_path = os.path.join(wdir, 'simulation_output', exp_name, 'compare_to_data_combo')
    plot_sim_and_ref(df, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles, ymax=5000,
                     plot_path=plot_path, first_day=first_day)
    
    #return ref_df_emr, ref_df_ll

if __name__ == '__main__' :

    stem = "20200522_EMS_1_scenario1_test"
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    for exp_name in exp_names :

        region = exp_name.split('_')[1]

        if("EMS" in exp_name) :
            ems_nr = exp_name.split('_')[2]
            region = exp_name.split('_')[1]

        if region == 'NMH_catchment':
            compare_NMH(exp_name)
        elif region == 'Chicago':
            compare_county(exp_name,  county_name='Cook')
        elif region == 'EMS':
            compare_ems(exp_name,  ems=int(ems_nr))
            print(exp_name)
        elif region == 'IL':
            compare_ems(exp_name, source='line_list')
