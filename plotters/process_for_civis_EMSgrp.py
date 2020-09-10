import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import sys
sys.path.append('../')
from data_comparison import load_sim_data
from processing_helpers import *
from load_paths import load_box_paths
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

mpl.rcParams['pdf.fonttype'] = 42
testMode = True
simdate = datetime.today().strftime('%Y%m%d') # "20200804"

plot_first_day = pd.to_datetime('2020/3/1')
plot_last_day = pd.to_datetime('2021/4/1')

def get_scenarioName(exp_suffix) :
    scenarioName = exp_suffix
    if exp_suffix == "reopen": scenarioName = "reopen_gradual"
    if exp_suffix == "gradual": scenarioName = "reopen_gradual"
    if exp_suffix == "interventionStop": scenarioName = "endsip"
    if exp_suffix == "scen3": scenarioName = "baseline"
    if exp_suffix == "neverSIP": scenarioName = "neversip"
    if exp_suffix == "stopSIP30": scenarioName = "july1partial30"
    if exp_suffix == "stopSIP10": scenarioName = "july1partial10"

    return(scenarioName)


def plot_sim(dat,suffix,channels) :

        if suffix not in ["All","central","southern","northeast","northcentral"]:
            suffix_nr = str(suffix.split("-")[1])
        if suffix == "All":
            suffix_nr ="illinois"
        capacity = load_capacity(suffix_nr)

        fig = plt.figure(figsize=(18, 12))
        fig.subplots_adjust(right=0.97, wspace=0.2, left=0.07, hspace=0.15)
        palette = sns.color_palette('Set1', len(channels))

        for c, channel in enumerate(channels):
            ax = fig.add_subplot(3, 3, c + 1)

            ax.plot(dat['date'], dat['%s_median' % channel], color=palette[c])
            ax.fill_between(dat['date'].values, dat['%s_95CI_lower' % channel], dat['%s_95CI_upper' % channel],
                            color=palette[c], linewidth=0, alpha=0.2)
            ax.fill_between(dat['date'].values, dat[ '%s_50CI_lower' % channel], dat[ '%s_50CI_upper' % channel],
                            color=palette[c], linewidth=0, alpha=0.4)

            if channel in capacity.keys():
                ax.plot([np.min(dat['date']), np.max(dat['date'])],
                      [capacity[channel], capacity[channel]], '--', linewidth=2, color=palette[c])

            ax.set_title(channel, y=0.85)
            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_major_locator(mdates.MonthLocator())

        plotname = scenarioName +"_" + suffix
        plotname = plotname.replace('EMS-','covidregion_')

        plt.savefig(os.path.join(plot_path, plotname + '.png'))
        plt.savefig(os.path.join(plot_path, plotname + '.pdf'), format='PDF')
        # plt.show()

def load_and_plot_data(ems_region, fname='trajectoriesDat.csv' , savePlot=True) :

    column_list = ['startdate', 'time', 'scen_num', 'sample_num', 'run_num']

    outcome_channels = ['susceptible', 'infected', 'recovered', 'infected_cumul', 'asymp_cumul', 'asymp_det_cumul', 'symp_mild_cumul', 'symp_severe_cumul', 'symp_mild_det_cumul',
        'symp_severe_det_cumul', 'hosp_det_cumul', 'hosp_cumul', 'detected_cumul', 'crit_cumul', 'crit_det_cumul', 'death_det_cumul',
        'deaths', 'crit_det',  'critical', 'hospitalized_det', 'hospitalized']

    for channel in outcome_channels:
        column_list.append(channel + "_" + str(ems_region))

    df = load_sim_data(exp_name,region_suffix = '_'+ems_region,fname=fname, column_list=column_list)

    df['ems'] = ems_region
    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
    df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
    df = df[(df['date'] >= plot_first_day) & (df['date'] <= plot_last_day)]

    df['ventilators'] = get_vents(df['crit_det'].values)
    df['new_symptomatic'] = df['new_symptomatic_severe'] + df['new_symptomatic_mild'] + df['new_detected_symptomatic_severe'] + df['new_detected_symptomatic_mild']

    channels = ['infected', 'new_infected', 'new_symptomatic', 'new_deaths', 'new_detected_deaths', 'hospitalized', 'critical', 'ventilators', 'recovered']

    adf = pd.DataFrame()
    for c, channel in enumerate(channels):
        mdf = df.groupby(['date', 'ems'])[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        mdf = mdf.rename(columns={'CI_50': '%s_median' % channel,
                              'CI_2pt5': '%s_95CI_lower' % channel,
                              'CI_97pt5': '%s_95CI_upper' % channel,
                              'CI_25': '%s_50CI_lower' % channel,
                              'CI_75': '%s_50CI_upper' % channel})
        if adf.empty:
            adf = mdf
        else:
            adf = pd.merge(left=adf, right=mdf, on=['date', 'ems'])

    if savePlot :
        plot_sim(adf, ems_region, channels)

    return adf


def process_and_save(adf,ems_region, SAVE = True) :
    col_names = civis_colnames(reverse=False)
    adf = adf.rename(columns=col_names)

    adf.geography_modeled = adf.geography_modeled.str.replace('-', "")
    adf.geography_modeled = adf.geography_modeled.str.lower()
    adf.geography_modeled = adf.geography_modeled.str.replace('all', "illinois")

    adf['scenario_name'] = scenarioName

    dfout = adf[
        ['date', 'geography_modeled', 'scenario_name', 'cases_median', 'cases_lower', 'cases_upper', 'cases_new_median',
         'cases_new_lower', 'cases_new_upper',
         'deaths_median', 'deaths_lower', 'deaths_upper', 'deaths_det_median', 'deaths_det_lower', 'deaths_det_upper',
         'hosp_bed_median', 'hosp_bed_lower', 'hosp_bed_upper',
         'icu_median', 'icu_lower', 'icu_upper', 'vent_median', 'vent_lower', 'vent_upper', 'recovered_median',
         'recovered_lower', 'recovered_upper']]

    if SAVE :
        filename = "nu_" + simdate + "_" + ems_region + ".csv"
        rename_geography_and_save(dfout, filename=filename)

    return dfout

def rename_geography_and_save(df,filename) :

    dfout = df.copy()
    if "geography_modeled" not in dfout.columns:
        dfout.rename(columns={'ems': 'covid_region'}, inplace=True)
        dfout['covid_region'] = dfout['covid_region'].str.replace('EMS-', '')

    if "geography_modeled" in dfout.columns:
        dfout['geography_modeled'] = dfout['geography_modeled'].str.replace('ems', 'covidregion_')

    dfout.to_csv(os.path.join(sim_output_path, filename), index=False)


if __name__ == '__main__' :

    exp_name = sys.argv[1]
    processStep = sys.argv[2]
    #exp_name = "20200910_IL_RR_baseline_combined"
    #processStep = 'generate_outputs'

    regions = ['All', 'EMS-1', 'EMS-2', 'EMS-3', 'EMS-4', 'EMS-5', 'EMS-6', 'EMS-7', 'EMS-8', 'EMS-9', 'EMS-10','EMS-11']

    exp_suffix = exp_name.split("_")[-1]
    scenarioName = get_scenarioName(exp_suffix)

    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = os.path.join(sim_output_path, '_plots')

    if not os.path.exists(sim_output_path):
        os.makedirs(sim_output_path)

    if not os.path.exists(plot_path):
        os.makedirs(plot_path)

    if processStep == 'generate_outputs' :
        dfAll = pd.DataFrame()
        for reg in regions :
            tdf = load_and_plot_data(reg,fname='trajectoriesDat.csv' , savePlot=True)
            adf = process_and_save(tdf, reg, SAVE=True)
            dfAll = pd.concat([dfAll, adf])
            del tdf

        if len(regions) == 12 :
            filename = "nu_" + simdate + ".csv"
            rename_geography_and_save(dfAll,filename=filename)

    ### Optional
    if processStep == 'combine_outputs' :

        for reg in ['All', 'EMS-1', 'EMS-2', 'EMS-3', 'EMS-4', 'EMS-5', 'EMS-6', 'EMS-7', 'EMS-8', 'EMS-9', 'EMS-10','EMS-11'] :
            filename = "nu_" + simdate + "_" + reg + ".csv"
            adf = pd.read_csv(os.path.join(sim_output_path, filename))
            dfAll = pd.concat([dfAll, adf])

        filename_new = "nu_" + simdate + ".csv"
        rename_geography_and_save(dfAll, filename=filename_new)

