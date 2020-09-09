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

def load_trajectoriesDat(sim_output_path, plot_first_day=None, plot_last_day=None, column_list=None) :

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'), usecols=column_list)

    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
    df['Date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
    df['Date'] = pd.to_datetime(df['Date'])

    if plot_first_day == None: plot_first_day = first_day
    if plot_last_day == None: plot_last_day = max(df['Date']).unique()

    df = df[(df['Date'] >= plot_first_day) & (df['Date'] <= plot_last_day)]
    return(df,first_day)

def append_data_byGroup(dat, suffix) :
    dfAll = pd.DataFrame()
    for grp in suffix:
        observe_col = [col for col in dat.columns if grp == col.split('_')[-1]]
        model_col = ['time', 'run_num', 'scen_num', 'sample_num']
        adf = dat[model_col + observe_col].copy()
        adf.columns = adf.columns.str.replace('_' + grp, "")
        adf = calculate_incidence(adf)
        adf['ems'] = grp
        dfAll = pd.concat([dfAll, adf])
        del adf

    #pd.crosstab(index=dfAll["ems"], columns="count")
    dfAll['ventilators'] = get_vents(dfAll['crit_det'].values)
    dfAll['new_symptomatic'] = dfAll['new_symptomatic_severe'] + dfAll['new_symptomatic_mild'] + dfAll[ 'new_detected_symptomatic_severe'] + dfAll['new_detected_symptomatic_mild']

    return(dfAll)


def plot_sim(dat, suffix) :
    for ems in suffix:

        ems_nr = ems
        if ems not in ["All","central","southern","northeast","northcentral"]:
            ems_nr = str(ems.split("-")[1])
        if ems == "All":
            ems_nr ="illinois"
        capacity = load_capacity(ems_nr)

        dfsub = dat[dat['ems'] == ems]
        fig = plt.figure(figsize=(18, 12))
        fig.subplots_adjust(right=0.97, wspace=0.2, left=0.07, hspace=0.15)
        palette = sns.color_palette('Set1', len(channels))

        for c, channel in enumerate(channels):
            ax = fig.add_subplot(3, 3, c + 1)
            mdf = dfsub.groupby('time')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
            mdf['date'] = mdf['time'].apply(lambda x: first_day + timedelta(days=int(x)))

            ax.plot(mdf['date'], mdf['CI_50'], color=palette[c])
            ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
                            color=palette[c], linewidth=0, alpha=0.2)
            ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                            color=palette[c], linewidth=0, alpha=0.4)

            if not ems == "All":
                if channel in capacity.keys():
                    ax.plot([np.min(mdf['date']), np.max(mdf['date'])],
                            [capacity[channel], capacity[channel]], '--', linewidth=2, color=palette[c])

            ax.set_title(channel, y=0.85)
            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_major_locator(mdates.MonthLocator())

        plotname = scenarioName +"_" + ems
        plotname = plotname.replace('EMS-','covidregion_')
        if ems == "All": ems = "IL"
        filename = 'nu_' + scenarioName + '_' + ems
        plt.savefig(os.path.join(plot_path, plotname + '.png'))
        plt.savefig(os.path.join(plot_path, plotname + '.pdf'), format='PDF')
        # plt.show()


def rename_geography_and_save(df,filename) :

    dfout = df.copy()
    if "geography_modeled" not in dfout.columns:
        dfout.rename(columns={'ems': 'covid_region'}, inplace=True)
        dfout['covid_region'] = dfout['covid_region'].str.replace('EMS-', '')

    if "geography_modeled" in dfout.columns:
        dfout['geography_modeled'] = dfout['geography_modeled'].str.replace('ems', 'covidregion_')

    dfout.to_csv(os.path.join(sim_output_path, filename), index=False)


if __name__ == '__main__' :

    #stem = sys.argv[1]
    stem = "20200816_IL_testbaseline"
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]


    for exp_name in exp_names:
        exp_suffix = exp_name.split("_")[-1]
        scenarioName = get_scenarioName(exp_suffix)

        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')

        if not os.path.exists(sim_output_path):
            os.makedirs(sim_output_path)

        if not os.path.exists(plot_path):
            os.makedirs(plot_path)

        column_list =  ['startdate', 'time', 'scen_num','sample_num', 'run_num']
        for ems_region in ['All', 'EMS-1', 'EMS-2','EMS-3','EMS-4','EMS-5','EMS-6','EMS-7','EMS-8','EMS-9','EMS-10','EMS-11']:
            column_list.append('susceptible_' + str(ems_region))
            column_list.append('infected_' + str(ems_region))
            column_list.append('recovered_' + str(ems_region))
            column_list.append('infected_cumul_' + str(ems_region))
            column_list.append('asymp_cumul_' + str(ems_region))
            column_list.append('asymp_det_cumul_' + str(ems_region))
            column_list.append('symp_mild_cumul_' + str(ems_region))
            column_list.append('symp_severe_cumul_' + str(ems_region))
            column_list.append('symp_mild_det_cumul_' + str(ems_region))
            column_list.append('symp_severe_det_cumul_' + str(ems_region))
            column_list.append('hosp_det_cumul_' + str(ems_region))
            column_list.append('hosp_cumul_' + str(ems_region))
            column_list.append('detected_cumul_' + str(ems_region))
            column_list.append('crit_cumul_' + str(ems_region))
            column_list.append('crit_det_cumul_' + str(ems_region))
            column_list.append('death_det_cumul_' + str(ems_region))
            column_list.append('deaths_' + str(ems_region))
            column_list.append('crit_det_' + str(ems_region))
            column_list.append('critical_' + str(ems_region))
            column_list.append('hosp_det_' + str(ems_region))
            column_list.append('hospitalized_' + str(ems_region))

        df, first_day = load_trajectoriesDat(sim_output_path, plot_first_day=plot_first_day, plot_last_day=plot_last_day,column_list=column_list)
        df = df[df.columns.drop(list(df.filter(regex='southern')))]
        df = df[df.columns.drop(list(df.filter(regex='central')))]
        df = df[df.columns.drop(list(df.filter(regex='northeast')))]
        df = df[df.columns.drop(list(df.filter(regex='northcentral')))]
        suffix_names = [x.split('_')[1] for x in df.columns.values if 'susceptible' in x]
        #base_names = [x.split('_%s' % suffix_names[0])[0] for x in df.columns.values if suffix_names[0] in x]

        dfAll = append_data_byGroup(df, suffix_names)

        channels = ['infected', 'new_infected', 'new_symptomatic', 'new_deaths', 'new_detected_deaths', 'hospitalized', 'critical', 'ventilators', 'recovered']
        adf = pd.DataFrame()
        for c, channel in enumerate(channels) :
            mdf = dfAll.groupby(['time','ems'])[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
            mdf['date'] = mdf['time'].apply(lambda x : first_day + timedelta(days=int(x)))

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
                adf = pd.merge(left=adf, right=mdf, on=['date', 'ems'])

        print(f'Writing "projection_for_civis.*" files to {sim_output_path}.')

        col_names = civis_colnames(reverse=False)
        adf = adf.rename(columns=col_names)

        adf.geography_modeled = adf.geography_modeled.str.replace('-' , "")
        adf.geography_modeled = adf.geography_modeled.str.lower()
        adf.geography_modeled = adf.geography_modeled.str.replace('all', "illinois")

        plot_sim(dfAll, suffix_names)

        adf['scenario_name'] = scenarioName

        adf = adf[['date' ,'geography_modeled' ,'scenario_name' ,'cases_median' ,'cases_lower' ,'cases_upper' ,'cases_new_median' ,'cases_new_lower' ,'cases_new_upper' ,
           'deaths_median' ,'deaths_lower' ,'deaths_upper' ,'deaths_det_median' ,'deaths_det_lower' ,'deaths_det_upper' ,'hosp_bed_median' ,'hosp_bed_lower' ,'hosp_bed_upper' ,
            'icu_median' ,'icu_lower' ,'icu_upper' , 'vent_median' ,'vent_lower' ,'vent_upper' ,'recovered_median' ,'recovered_lower' ,'recovered_upper' ]]

        filename_new = "nu_" + simdate + ".csv"
        rename_geography_and_save(adf,filename=filename_new)


