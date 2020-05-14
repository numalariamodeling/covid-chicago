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

mpl.rcParams['pdf.fonttype'] = 42
testMode = True
simdate = "20200513"

plot_first_day = pd.to_datetime('2020/3/1')
plot_last_day = pd.to_datetime('2020/10/1')

if __name__ == '__main__' :

    stem = "20200512_IL"
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    #exp_name = "20200512_IL__EMSgrp_scenario3"

    for exp_name in exp_names:
        exp_suffix = exp_name.split("_")[-1]
        if exp_suffix =="reopen" : scenarioName  = "reopen"
        if exp_suffix =="interventionStop" : scenarioName  = "endsip"
        if exp_suffix =="scenario3" : scenarioName  = "baseline"
        if exp_suffix =="neverSIP" : scenarioName  = "neversip"


        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')

        if not os.path.exists(sim_output_path):
            os.makedirs(sim_output_path)

        if not os.path.exists(plot_path):
            os.makedirs(plot_path)

        df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
        suffix_names = [x.split('_')[1] for x in df.columns.values if 'susceptible' in x]
        base_names = [x.split('_%s' % suffix_names[0])[0] for x in df.columns.values if suffix_names[0] in x]

        first_day = datetime.strptime(df['first_day'].unique()[0], '%Y-%m-%d')
        df['Date'] = df['time'].apply(lambda x : first_day + timedelta(days=int(x)))
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[(df['Date'] >= plot_first_day) & (df['Date'] <= plot_last_day)]

        dfAll = pd.DataFrame()
        for grp in suffix_names :

            observe_col = [col for col in df.columns if grp in col]
            model_col = ['time', 'run_num','scen_num','sample_num']
            if suffix_names == 'EMS-1':
                observe_col = observe_col[:25]

            adf = df[model_col + observe_col].copy()
            adf.columns = adf.columns.str.replace('_'+ grp , "")

            #df['infected_cumul_%s' % age_group] = df['infected_%s' % age_group]  + df['recovered_%s' % age_group]  + df['deaths_%s' % age_group]
            adf['infected'] = adf['asymptomatic'] + adf['presymptomatic'] + adf['symptomatic_mild'] + adf['symptomatic_severe'] +  adf['hospitalized'] + adf['critical']
            adf['infected_cumul'] = adf['infected'] + adf['recovered'] + adf['deaths']

            adf = calculate_incidence(adf)
            adf['ems'] = grp

            dfAll = pd.concat([dfAll, adf])
            del adf


        pd.crosstab(index=dfAll["ems"],  columns="count")
        channels = ['infected','new_infected', 'new_symptomatic', 'new_deaths', 'hospitalized', 'critical', 'ventilators', 'recovered']

        dfAll['ventilators'] = dfAll['critical'] * 0.8
        dfAll['new_symptomatic'] = dfAll['new_symptomatic_severe'] + dfAll['new_symptomatic_mild'] + dfAll['new_detected_symptomatic_severe'] + dfAll['new_detected_symptomatic_mild']

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
        #adf.to_csv(os.path.join(sim_output_path, 'projection_for_civis.csv'), index=False)

        adf = adf.rename(columns={"date": "Date",
                       "ems" : "geography_modeled",
                       "infected_median": "Number of Covid-19 infections",
                       "infected_95CI_lower": "Lower error bound of covid-19 infections",
                       "infected_95CI_upper": "Upper error bound of covid-19 infections",
                       "new_infected_95CI_upper": "Upper error bound of covid-19 new infections",
                       "new_infected_median": "Number of Covid-19 new infections",
                       "new_infected_95CI_lower": "Lower error bound of covid-19 new infections",
                       "new_symptomatic_median": "Number of Covid-19 symptomatic",
                       "new_symptomatic_95CI_lower": "Lower error bound of covid-19 symptomatic",
                       "new_symptomatic_95CI_upper": "Upper error bound of covid-19 symptomatic",
                       "new_deaths_median": "Number of covid-19 deaths",
                       "new_deaths_95CI_lower": "Lower error bound of covid-19 deaths",
                       "new_deaths_95CI_upper": "Upper error bound of covid-19 deaths",
                       "hospitalized_median": "Number of hospital beds occupied",
                       "hospitalized_95CI_lower": "Lower error bound of number of hospital beds occupied",
                       "hospitalized_95CI_upper": "Upper error bound of number of hospital beds occupied",
                       "critical_median": "Number of ICU beds occupied",
                       "critical_95CI_lower": "Lower error bound of number of ICU beds occupied",
                       "critical_95CI_upper": "Upper error bound of number of ICU beds occupied",
                       "ventilators_median": "Number of ventilators used",
                       "ventilators_95CI_lower": "Lower error bound of number of ventilators used",
                       "ventilators_95CI_upper": "Upper error bound of number of ventilators used",
                       "recovered_median": "Total recovered",
                       "recovered_95CI_lower": "Lower error bound on recovered",
                       "recovered_95CI_upper": "Upper error bound on recovered" })

        adf.geography_modeled = adf.geography_modeled.str.replace('-' , "")
        adf.geography_modeled = adf.geography_modeled.str.lower()
        adf.geography_modeled = adf.geography_modeled.str.replace('regionall', "illinois")

        filename = "nu_ems_" + scenarioName + '_' + simdate+".csv"
        #adf.to_csv(os.path.join(sim_output_path, filename), index=False)
        #adf.to_csv(os.path.join(out_dir, filename), index=False)

        for ems in suffix_names :
            if not ems == "regionAll" :
                ems_nr = int(ems.split("-")[1])
                capacity = load_capacity(ems_nr)

            dfsub = dfAll[dfAll['ems'] == ems]
            fig = plt.figure(figsize=(12, 12))
            fig.subplots_adjust(right=0.97, wspace=0.2, left=0.07, hspace=0.15)
            palette = sns.color_palette('Set1', len(channels))

            for c, channel in enumerate(channels) :
                ax = fig.add_subplot(4,2,c+1)
                mdf = dfsub.groupby('time')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
                mdf['date'] = mdf['time'].apply(lambda x : first_day + timedelta(days=int(x)))

                ax.plot(mdf['date'], mdf['CI_50'], color=palette[c])
                ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
                                color=palette[c], linewidth=0, alpha=0.2)
                ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                                color=palette[c], linewidth=0, alpha=0.4)

                if not ems == "regionAll":
                    if channel in capacity.keys():
                            ax.plot([np.min(mdf['date']), np.max(mdf['date'])],
                            [capacity[channel], capacity[channel]], '--', linewidth=2, color=palette[c])

                ax.set_title(channel, y=0.85)
                formatter = mdates.DateFormatter("%m-%d")
                ax.xaxis.set_major_formatter(formatter)
                ax.xaxis.set_major_locator(mdates.MonthLocator())

            #filename = 'projection_for_civis_' + ems
            if ems =="regionAll" : ems = "IL"
            filename = 'nu_'+scenarioName +'_' + ems
            #plt.savefig(os.path.join(sim_output_path, filename + '.png'))
            #plt.savefig(os.path.join(sim_output_path, ilename + '.pdf'), format='PDF')
            #plt.show()


