import numpy as np
import os
import pandas as pd
from load_paths import load_box_paths
from datetime import datetime, timedelta

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def get_vents(crit_det_array):

	vent_frac_global = 0.660
	
	return crit_det_array * vent_frac_global

def get_latest_LLfiledate(file_path, split_string ='_jg_' , file_pattern='aggregated_covidregion.csv'):

    files= os.listdir(file_path)
    filedates = [x.split(split_string)[0] for x in files if file_pattern in x]
    latest_filedate = max([int(x) for x in filedates])

    return latest_filedate

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


def load_capacity(ems, simdate='20200929') :
    ### note, names need to match, simulations and capacity data already include outputs for all illinois
    
    fname = 'capacity_weekday_average_' + simdate + '.csv'
    ems_fname = os.path.join(datapath, 'covid_IDPH/Corona virus reports/hospital_capacity_thresholds/', fname)
    df = pd.read_csv(ems_fname)

    df = df[df['overflow_threshold_percent']==1]
    df['ems'] = df['geography_modeled']
    df['ems'] = df['geography_modeled'].replace("covidregion_", "", regex=True)
    df =  df[['ems','resource_type','avg_resource_available']]
    df = df.drop_duplicates()
   # df = df.sort_values(by=['ems'])
    df = df.pivot(index='ems', columns='resource_type', values='avg_resource_available')

    df.index.name = 'ems'
    df.reset_index(inplace=True)

    if ems =='illinois' :
        df['grp']= 'illinois'
        df = df.groupby('grp')[['hb_availforcovid','icu_availforcovid']].agg(np.sum).reset_index()
    if ems != 'illinois':
        df = df[df['ems'] == str(ems)]

    capacity = {
            'hospitalized' :  int(df['hb_availforcovid']),
            'critical' : int(df['icu_availforcovid'])
    }
    return capacity


def civis_colnames(reverse=False) :
    colnames = { "ems": "geography_modeled",
     "infected_median": "cases_median",
     "infected_95CI_lower": "cases_lower",
     "infected_95CI_upper": "cases_upper",
     "new_infected_median": "cases_new_median",
     "new_infected_95CI_lower": "cases_new_lower",
     "new_infected_95CI_upper": "cases_new_upper",
     "new_symptomatic_median": "symptomatic_new_median",
     "new_symptomatic_95CI_lower": "symptomatic_new_lower",
     "new_symptomatic_95CI_upper": "symptomatic_new_upper",
     "new_deaths_median": "deaths_median",
     "new_deaths_95CI_lower": "deaths_lower",
     "new_deaths_95CI_upper": "deaths_upper",
     "new_detected_deaths_median": "deaths_det_median",
     "new_detected_deaths_95CI_lower": "deaths_det_lower",
     "new_detected_deaths_95CI_upper": "deaths_det_upper",
     "hospitalized_median": "hosp_bed_median",
     "hospitalized_95CI_lower": "hosp_bed_lower",
     "hospitalized_95CI_upper": "hosp_bed_upper",
     "critical_median": "icu_median",
     "critical_95CI_lower": "icu_lower",
     "critical_95CI_upper": "icu_upper",
     "ventilators_median": "vent_median",
     "ventilators_95CI_lower": "vent_lower",
     "ventilators_95CI_upper": "vent_upper",
     "recovered_median": "recovered_median",
     "recovered_95CI_lower": "recovered_lower",
     "recovered_95CI_upper": "recovered_upper"}

    if reverse == True : colnames = {value: key for key, value in col_names.items()}
    return(colnames)