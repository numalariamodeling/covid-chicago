import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import datetime, date, timedelta
import seaborn as sns
from processing_helpers import *
from data_comparison import load_sim_data
from copy import copy

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()



def load_sim_data(exp_name, scenario_param, input_wdir=None, input_sim_output_path =None) :
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))

    df.columns = df.columns.str.replace('_All', '')
    df['infected_cumul'] = df['infected'] + df['recovered'] + df['deaths']
    df = calculate_incidence(df,scenario_param)

    return df

def calculate_incidence(adf, scenario_param, output_filename=None) :

    inc_df = pd.DataFrame()
    for i in scenario_param:
        for (run, samp, scen, scenario_param_i), df in adf.groupby(['run_num','sample_num', 'scen_num' , i]) :
            sdf = pd.DataFrame( { 'time' : df['time'],
                                  'new_exposures' : [-1*x for x in count_new(df, 'susceptible')],
                                  'new_infected': count_new(df, 'infected_cumul'),
                                #'new_infected_detected': count_new(df, 'infected_det_cumul'),
                                  'new_asymptomatic' : count_new(df, 'asymp_cumul'),
                                  'new_asymptomatic_detected' : count_new(df, 'asymp_det_cumul'),
                                  'new_symptomatic_mild' : count_new(df, 'symp_mild_cumul'),
                                  'new_symptomatic_severe': count_new(df, 'symp_severe_cumul'),
                                  'new_detected_symptomatic_mild': count_new(df, 'symp_mild_det_cumul'),
                                  'new_detected_symptomatic_severe': count_new(df, 'symp_severe_det_cumul'),
                                  'new_detected_hospitalized' : count_new(df, 'hosp_det_cumul'),
                                  'new_hospitalized' : count_new(df, 'hosp_cumul'),
                                  'new_detected' : count_new(df, 'detected_cumul'),
                                  'new_critical' : count_new(df, 'crit_cumul'),
                                  'new_detected_critical' : count_new(df, 'crit_det_cumul'),
                                  'new_detected_deaths' : count_new(df, 'death_det_cumul'),
                                  'new_deaths' : count_new(df, 'deaths')
                                  })
            sdf['run_num'] = run
            sdf['sample_num'] = samp
            sdf['scen_num'] = scen
            sdf[i] =scenario_param_i
            inc_df = pd.concat([inc_df, sdf])

    adf = pd.merge(left=adf, right=inc_df, on=['run_num','sample_num', 'scen_num', 'time']+scenario_param)
    if output_filename :
        adf.to_csv(output_filename, index=False)
    return adf


def plot_on_fig(df, channels, axes, color, label) :
    #first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
    first_day = date(2020, 2, 20)

    for c, channel in enumerate(channels) :
        ax = axes[c]
        mdf = df.groupby('time')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        mdf['date'] = mdf['time'].apply(lambda x: first_day + timedelta(days=int(x)))
        mdf = mdf[(mdf['date'] >= date(2020, 4, 1)) & (mdf['date'] <= date(2020, 8, 1))]
        ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
        # ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
        #                 color=color, linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=color, linewidth=0, alpha=0.4)
        ax.set_title(' '.join(channel.split('_')), y=0.85)
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())


if __name__ == '__main__' :

    exp_name = '20200604_IL_EMS_scen3_changeTD12'
    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    scenario_param = ['time_to_detection_1']
    df = load_sim_data(exp_name, scenario_param)

    fig = plt.figure(figsize=(8, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
    palette = sns.color_palette('Set1', len(df.time_to_detection_1.unique()))
    channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']
    axes = [fig.add_subplot(3, 2, x + 1) for x in range(len(channels))]

    for d,  scen_val in enumerate(df.time_to_detection_1.unique() ):
        #print(scen_val)
        adf = df[df.time_to_detection_1==scen_val]
        label = "test delay = " + str(scen_val)

        adf['symptomatic_census'] = adf['symptomatic_mild'] + adf['symptomatic_severe']
        adf['ventilators'] = get_vents(adf['crit_det'].values)

        plot_on_fig(adf, channels, axes, color=palette[d], label=label)
    axes[-1].legend()

    plt.savefig(os.path.join(sim_output_path,'scenario_comparison.png'))
    #plt.savefig(os.path.join(sim_output_path,  'scenario_comparison.pdf'), format='PDF')
    plt.show()