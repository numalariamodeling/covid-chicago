import numpy as np
import os
import pandas as pd
from load_paths import load_box_paths
from datetime import datetime, timedelta

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def merge_county_covidregions(df_x, key_x='region', key_y='County'):
    """ Add covidregions (new_restore_regions from covidregion_population_by_county.csv)
    to a file that only includes counties. Country names are changes to lowercase before the merge.
    Keeps all rows from df_x and only those that match from df_y (left join).
    """

    df_y = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'EMS Population','covidregion_population_by_county.csv'))

    df_x[key_x] = df_x[key_x] .str.lower()
    df_y[key_y] = df_y[key_y] .str.lower()

    df = pd.merge(how='left', left=df_x, left_on=key_x, right=df_y, right_on=key_y)

    return df

def get_latest_LLfiledate(file_path, split_string ='_jg_' , file_pattern='aggregated_covidregion.csv'):

    files= os.listdir(file_path)
    filedates = [x.split(split_string)[0] for x in files if file_pattern in x]
    latest_filedate = max([int(x) for x in filedates])

    return latest_filedate
    
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


def load_ref_df(ems_nr):
    ref_df_emr = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'emresource_by_region.csv'))
    ref_df_emr['suspected_and_confirmed_covid_icu'] = ref_df_emr['suspected_covid_icu'] + ref_df_emr['confirmed_covid_icu']
    data_channel_names_emr = ['confirmed_covid_deaths_prev_24h', 'confirmed_covid_icu', 'covid_non_icu']
    ref_df_emr = ref_df_emr.groupby(['date_of_extract','covid_region'])[data_channel_names_emr].agg(np.sum).reset_index()
    ref_df_emr['date'] = pd.to_datetime(ref_df_emr['date_of_extract'])

    LL_file_date = get_latest_LLfiledate(file_path=os.path.join(datapath, 'covid_IDPH', 'Cleaned Data'))
    ref_df_ll = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', f'{LL_file_date}_jg_aggregated_covidregion.csv'))
    ref_df_ll['date'] = pd.to_datetime(ref_df_ll['date'])

    ref_df_cli = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'CLI_admissions.csv'))
    ref_df_cli = merge_county_covidregions(df_x=ref_df_cli, key_x='region', key_y='County')
    ref_df_cli = ref_df_cli.groupby(['date','new_restore_region'])['inpatient'].agg(np.sum).reset_index()
    ref_df_cli = ref_df_cli.rename(columns={'new_restore_region': 'covid_region'})
    ref_df_cli['date'] = pd.to_datetime(ref_df_cli['date'])

    if ems_nr > 0:
        ref_df_emr = ref_df_emr[ref_df_emr['covid_region'] == ems_nr]
        ref_df_ll = ref_df_ll[ref_df_ll['covid_region'] == ems_nr]
        ref_df_cli = ref_df_cli[ref_df_cli['covid_region'] == ems_nr]
    else:
        ref_df_emr = ref_df_emr.groupby('date_of_extract').agg(np.sum).reset_index()
        ref_df_ll = ref_df_ll.groupby('date').agg(np.sum).reset_index()
        ref_df_cli = ref_df_cli.groupby('date').agg(np.sum).reset_index()

    merge_keys = ['date', 'covid_region']
    ref_df = pd.merge(how='outer', left=ref_df_ll,  right=ref_df_emr, on=merge_keys)
    ref_df = pd.merge(how='outer', left=ref_df, right=ref_df_cli, on=merge_keys)

    ref_df = ref_df.sort_values('date')

    return ref_df


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


def load_capacity(ems):
    ### note, names need to match, simulations and capacity data already include outputs for all illinois

    file_path = os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'hospital_capacity_thresholds')
    files = os.listdir(file_path)
    files = [name for name in files if not 'extra_thresholds' in name]
    filedates = [item.replace('capacity_weekday_average_', '') for item in files]
    filedates = [item.replace('.csv', '') for item in filedates]
    latest_filedate = max([int(x) for x in filedates])

    fname = 'capacity_weekday_average_' + str(latest_filedate) + '.csv'
    ems_fname = os.path.join(datapath, 'covid_IDPH/Corona virus reports/hospital_capacity_thresholds/', fname)
    df = pd.read_csv(ems_fname)

    df = df[df['overflow_threshold_percent'] == 1]
    df['ems'] = df['geography_modeled']
    df['ems'] = df['geography_modeled'].replace("covidregion_", "", regex=True)
    df = df[['ems', 'resource_type', 'avg_resource_available']]
    df = df.drop_duplicates()

    df = df.pivot(index='ems', columns='resource_type', values='avg_resource_available')

    df.index.name = 'ems'
    df.reset_index(inplace=True)

    if ems == 'illinois':
        df['ems'] = 'illinois'
    df = df.groupby('ems')[['hb_availforcovid', 'icu_availforcovid']].agg(np.sum).reset_index()
    if ems != 'illinois':
        df = df[df['ems'] == str(ems)]

    capacity = {'hospitalized': int(df['hb_availforcovid']), 'critical': int(df['icu_availforcovid'])}
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