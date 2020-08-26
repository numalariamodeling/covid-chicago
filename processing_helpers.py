import numpy as np
import os
import pandas as pd
from load_paths import load_box_paths
from datetime import datetime, timedelta

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def get_vents(crit_det_array):

	vent_frac_global = 0.660
	
	return crit_det_array * vent_frac_global

def loadEMSregions(regionname) :
    regions = {'northcentral' : ['EMS_1', 'EMS_2'],
               'northeast' : ['EMS_7', 'EMS_8', 'EMS_9', 'EMS_10', 'EMS_11'],
               'central' : ['EMS_3', 'EMS_6'],
               'southern': ['EMS_4', 'EMS_5']
    }

    if regionname != "all" :
        out = regions[regionname]
    elif regionname == "all" :
        out = regions
    return out

def count_new(df, curr_ch) :

    ch_list = list(df[curr_ch].values)
    diff = [0] + [ch_list[x] - ch_list[x - 1] for x in range(1, len(df))]
    return diff

def CI_5(x) :

    return np.percentile(x, 5)


def CI_95(x) :

    return np.percentile(x, 95)


def CI_25(x) :

    return np.percentile(x, 25)


def CI_75(x) :

    return np.percentile(x, 75)

def CI_2pt5(x) :

    return np.percentile(x, 2.5)

def CI_97pt5(x) :

    return np.percentile(x, 97.5)

def CI_50(x) :

    return np.percentile(x, 50)



def calculate_incidence(adf, output_filename=None) :

    inc_df = pd.DataFrame()
    for (run, samp, scen), df in adf.groupby(['run_num','sample_num', 'scen_num']) :

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
        inc_df = pd.concat([inc_df, sdf])

    adf = pd.merge(left=adf, right=inc_df, on=['run_num','sample_num', 'scen_num', 'time'])
    if output_filename :
        adf.to_csv(output_filename, index=False)
    return adf


def calculate_incidence_by_age(adf, age_group, output_filename=None) :

    inc_df = pd.DataFrame()
    for (run, samp, scen), df in adf.groupby(['run_num','sample_num', 'scen_num']) :

        sdf = pd.DataFrame( { 'time' : df['time'],
                              'new_exposures_%s' % age_group : [-1*x for x in count_new(df, 'susceptible_%s' % age_group)],
                              'new_asymptomatic_%s' % age_group : count_new(df, 'asymp_cumul_%s' % age_group),
                              'new_asymptomatic_detected_%s' % age_group : count_new(df, 'asymp_det_cumul_%s' % age_group),
                              'new_symptomatic_mild_%s' % age_group : count_new(df, 'symp_mild_cumul_%s' % age_group),
                              'new_symptomatic_severe_%s' % age_group: count_new(df, 'symp_severe_cumul_%s' % age_group),
                              'new_detected_symptomatic_mild_%s' % age_group: count_new(df, 'symp_mild_det_cumul_%s' % age_group),
                              'new_detected_symptomatic_severe_%s' % age_group: count_new(df, 'symp_severe_det_cumul_%s' % age_group),
                              'new_detected_hospitalized_%s' % age_group : count_new(df, 'hosp_det_cumul_%s' % age_group),
                              'new_hospitalized_%s' % age_group : count_new(df, 'hosp_cumul_%s' % age_group),
                              'new_detected_%s' % age_group : count_new(df, 'detected_cumul_%s' % age_group),
                              'new_critical_%s' % age_group : count_new(df, 'crit_cumul_%s' % age_group),
                              'new_detected_critical_%s' % age_group : count_new(df, 'crit_det_cumul_%s' % age_group),
                              'new_detected_deaths_%s' % age_group : count_new(df, 'death_det_cumul_%s' % age_group),
                              'new_deaths_%s' % age_group : count_new(df, 'deaths_%s' % age_group)
                              })
        sdf['run_num'] = run
        sdf['sample_num'] = samp
        sdf['scen_num'] = scen
        inc_df = pd.concat([inc_df, sdf])
    adf = pd.merge(left=adf, right=inc_df, on=['run_num', 'sample_num', 'scen_num', 'time'])
    if output_filename :
        adf.to_csv(output_filename, index=False)
    return adf


def load_capacity(ems, simdate='20200825') :
    ### note, names need to match, simulations and capacity data already include outputs for all illinois
    
    fname = 'capacity_by_covid_region_' + simdate + '.csv'
    ems_fname = os.path.join(datapath, 'covid_IDPH/Corona virus reports', fname)
    ems_df = pd.read_csv(ems_fname)

    filterdate = max(ems_df['date'])
    filterdate = datetime.strptime(filterdate, "%Y-%m-%d")  # string to date
    filterdate = filterdate - timedelta(days=14)  # date - days
    filterdate = pd.to_datetime(filterdate)

    ems_df['date'] = pd.to_datetime(ems_df['date'])
    ems_df = ems_df[ems_df['date'] > filterdate]
    #ems_df['ems'] = ems_df['Region'].apply(lambda x : int(x.split('-')[0]))
    ems_df['ems'] = ems_df['geography_name']
    ems_df['ems'] = ems_df['ems'].replace("restore_", "", regex=True)
    ems_df = ems_df.set_index('ems')

    ems_df['hospitalized'] = ems_df[ 'medsurg_total'] - ems_df[ 'medsurg_noncovid']
    ems_df['critical'] = ems_df[ 'icu_total'] - ems_df[ 'icu_noncovid']
    ems_df['ventilators'] = ems_df[ 'vent_total'] - ems_df[ 'vent_noncovid']

    ems_df = ems_df.groupby(['geography_name']).agg(np.mean).reset_index()

    ems_df = ems_df[ems_df['geography_name']==str(ems)]

    capacity = {
            'hospitalized' :  int(ems_df['hospitalized']),
            'critical' : int(ems_df['critical']),
            'ventilators' : int(ems_df['ventilators'])
    }
    return capacity


def civis_colnames(reverse=False) :
    colnames = {"date": "Date",
     "ems": "geography_modeled",
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
     "new_detected_deaths_median": "Number of detected covid-19 deaths",
     "new_detected_deaths_95CI_lower": "Lower error bound of detected covid-19 deaths",
     "new_detected_deaths_95CI_upper": "Upper error bound of detected covid-19 deaths",
     "hospitalized_median": "Number of hospital beds occupied",
     "hospitalized_95CI_lower": "Lower error bound of number of hospital beds occupied",
     "hospitalized_95CI_upper": "Upper error bound of number of hospital beds occupied",
     "critical_median": "Number of ICU beds occupied",
     "critical_95CI_lower": "Lower error bound of number of ICU beds occupied",
     "critical_95CI_upper": "Upper error bound of number of ICU beds occupied",
     "ventilators_median": "Number of ventilators used",
     "ventilators_95CI_lower": "Lower error bound of number of ventilators used",
     "ventilators_95CI_upper": "Upper error bound of number of ventilators used",
     "recovered_median": "Number of recovered Covid-19 infections",
     "recovered_95CI_lower": "Lower error bound on recovered Covid-19 infections",
     "recovered_95CI_upper": "Upper error bound on recovered Covid-19 infections"}

    if reverse == True : colnames = {value: key for key, value in col_names.items()}
    return(colnames)