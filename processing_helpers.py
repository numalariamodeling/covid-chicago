import numpy as np
import os
import pandas as pd
from load_paths import load_box_paths
from datetime import date, timedelta, datetime

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()


def load_sim_data(exp_name, region_suffix ='_All', input_wdir=None, fname='trajectoriesDat.csv',
                  input_sim_output_path =None, column_list=None, add_incidence=True) :
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df = pd.read_csv(os.path.join(sim_output_path, fname), usecols=column_list, engine='python')
    df = df.dropna()
    try:
        first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
    except:
        first_day = datetime.strptime(df['startdate'].unique()[0], '%m/%d/%Y')
    df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
    df['date'] = pd.to_datetime(df['date']).dt.date

    if region_suffix !=None :
        df.columns = df.columns.str.replace(region_suffix, '')

    if add_incidence:
        if 'recovered' in df.columns:
            df['infected_cumul'] = df['infected'] + df['recovered'] + df['deaths']
            df = calculate_incidence(df)
        else:
            df = calculate_incidence(df, trimmed =True)

    return df

def load_sim_data_age(exp_name,channel, age_suffix ='_All', input_wdir=None,fname='trajectoriesDat.csv', input_sim_output_path =None) :
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    column_list = ['scen_num',  'time', 'startdate']
    for grp in ageGroup_list:
        column_list.append(channel + str(grp))

    df = pd.read_csv(os.path.join(sim_output_path, fname), usecols=column_list)
    df = df.dropna()
    first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
    df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
    df['date'] = pd.to_datetime(df['date']).dt.date
    df.columns = df.columns.str.replace(age_suffix, '')

    return df

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
    data_channel_names_emr = ['confirmed_covid_deaths_prev_24h', 'confirmed_covid_icu', 'covid_non_icu','suspected_covid_icu','suspected_and_confirmed_covid_icu']
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

    ref_df_public = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'IDPH_public_county.csv'))
    ref_df_public = merge_county_covidregions(df_x=ref_df_public, key_x='county', key_y='County')
    ref_df_public = ref_df_public.groupby(['test_date','new_restore_region'])['confirmed_cases'].agg(np.sum).reset_index()
    ref_df_public = ref_df_public.rename(columns={'new_restore_region': 'covid_region'})
    ref_df_public['test_date'] = pd.to_datetime(ref_df_public['test_date'])
    ref_df_public.rename(columns={"test_date" : "date"}, inplace=True)

    if not isinstance(ems_nr, list):
        if ems_nr > 0:
            ref_df_emr = ref_df_emr[ref_df_emr['covid_region'] == ems_nr]
            ref_df_ll = ref_df_ll[ref_df_ll['covid_region'] == ems_nr]
            ref_df_cli = ref_df_cli[ref_df_cli['covid_region'] == ems_nr]
            ref_df_public = ref_df_public[ref_df_public['covid_region'] == ems_nr]
        if ems_nr == 0:
            ref_df_emr['covid_region'] = 0
            ref_df_ll['covid_region'] = 0
            ref_df_cli['covid_region'] = 0
            ref_df_public['covid_region'] = 0

            ref_df_emr = ref_df_emr.groupby('date').agg(np.sum).reset_index()
            ref_df_ll = ref_df_ll.groupby('date').agg(np.sum).reset_index()
            ref_df_cli = ref_df_cli.groupby('date').agg(np.sum).reset_index()
            ref_df_public = ref_df_public.groupby('date').agg(np.sum).reset_index()

        ref_df_public = ref_df_public.sort_values('date')
        ref_df_public['new_confirmed_cases'] = count_new(ref_df_public, 'confirmed_cases')

    if isinstance(ems_nr, list):
        inc_df = pd.DataFrame()
        for region, df in ref_df_public.groupby('covid_region'):
            df = df.sort_values('date')
            sdf = pd.DataFrame({'date': df['date'], 'new_confirmed_cases': count_new(df, 'confirmed_cases')})
            sdf['covid_region'] = region
            inc_df = pd.concat([inc_df, sdf])
        ref_df_public_ext = pd.merge(left=ref_df_public, right=inc_df, on=['date', 'covid_region'])
        ref_df_public = ref_df_public_ext

    merge_keys = ['date', 'covid_region']
    ref_df = pd.merge(how='outer', left=ref_df_ll,  right=ref_df_emr, on=merge_keys)
    ref_df = pd.merge(how='outer', left=ref_df, right=ref_df_cli, on=merge_keys)
    ref_df = pd.merge(how='outer', left=ref_df, right=ref_df_public, on=merge_keys)

    if isinstance(ems_nr, list):
        ref_df[ref_df['covid_region'].isin(ems_nr)]

    ref_df = ref_df.sort_values(['covid_region', 'date'])
    ref_df['date'] = pd.to_datetime(ref_df['date']).dt.date
    ref_df = ref_df[(ref_df['date'] > pd.to_datetime(date(2020,1,1))) &
                    (ref_df['date'] <= pd.to_datetime(date.today()))]

    return ref_df


def calculate_prevalence(df, ems=None):
    if ems is None:
        ems = ['EMS-%d' % x for x in range(1, 12)]

    for ems_num in ems:
            df[f'N_{ems_num}'] = df[f'N_{str(ems_num.replace("-","_"))}'] - df[f'deaths_{ems_num}']
            df[f'IFR_{ems_num}'] = df[f'deaths_{ems_num}'] / (df[f'recovered_{ems_num}'] + df[f'deaths_{ems_num}'])
            df[f'IFR_t_{ems_num}'] = df[f'new_deaths_{ems_num}'] / (df[f'new_recovered_{ems_num}'] + df[f'new_deaths_{ems_num}'])
            df[f'prevalence_{ems_num}'] = df[f'infected_{ems_num}'] / df[f'N_{ems_num}']
            df[f'seroprevalence_current_{ems_num}'] = df[f'recovered_{ems_num}'] / df[f'N_{ems_num}']
            df[f'seroprevalence_{ems_num}'] = df.groupby(['scen_num', 'sample_num'])[f'seroprevalence_current_{ems_num}'].transform('shift', 14)

            if f'infected_det_{ems_num}' in df.columns:
                df[f'N_det_{ems_num}'] = df[f'N_{str(ems_num.replace("-", "_"))}'] - df[f'deaths_det_{ems_num}']
                df[f'IFR_det_{ems_num}'] = df[f'deaths_det_{ems_num}'] / (df[f'recovered_det_{ems_num}'] + df[f'deaths_det_{ems_num}'])
                df[f'IFR_det_t_{ems_num}'] = df[f'new_deaths_det_{ems_num}'] / (df[f'new_recovered_det_{ems_num}'] + df[f'new_deaths_det_{ems_num}'])
                df[f'prevalence_det_{ems_num}'] = df[f'infected_det_{ems_num}'] / df[f'N_det_{ems_num}']
                df[f'seroprevalence_current_det_{ems_num}'] = df[f'recovered_det_{ems_num}'] / df[f'N_det_{ems_num}']
                df[f'seroprevalence_det_{ems_num}'] = df.groupby(['scen_num', 'sample_num'])[f'seroprevalence_current_det_{ems_num}'].transform('shift', 14)
    return df

def calculate_incidence(adf, output_filename=None, trimmed=False) :

    inc_df = pd.DataFrame()
    for (run, samp, scen), df in adf.groupby(['run_num','sample_num', 'scen_num']) :

        if trimmed == False:
            sdf = pd.DataFrame({'time' : df['time'],
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
        if trimmed == True:
            sdf = pd.DataFrame({'time': df['time'],
                                'new_detected_hospitalized' : count_new(df, 'hosp_det_cumul'),
                                'new_hospitalized' : count_new(df, 'hosp_cumul'),
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

    if ems == 'illinois' or ems == 0:
        df['ems'] = 'illinois'
        df = df.groupby('ems')[['hb_availforcovid', 'icu_availforcovid', 'vent_availforcovid']].agg(np.sum).reset_index()
    else :
        df = df[df['ems'] == str(ems)]

    capacity = {'hosp_det': int(df['hb_availforcovid']),
                'crit_det': int(df['icu_availforcovid']),
                'ventilators': int(df['vent_availforcovid'])}
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
                 "hosp_det_median": "hosp_det_bed_median",
                 "hosp_det_95CI_lower": "hosp_det_bed_lower",
                 "hosp_det_95CI_upper": "hosp_det_bed_upper",
                 "critical_median": "icu_median",
                 "critical_95CI_lower": "icu_lower",
                 "critical_95CI_upper": "icu_upper",
                 "crit_det_median": "icu_det_median",
                 "crit_det_95CI_lower": "icu_det_lower",
                 "crit_det_95CI_upper": "icu_det_upper",
                 "ventilators_median": "vent_median",
                 "ventilators_95CI_lower": "vent_lower",
                 "ventilators_95CI_upper": "vent_upper",
                 "recovered_median": "recovered_median",
                 "recovered_95CI_lower": "recovered_lower",
                 "recovered_95CI_upper": "recovered_upper"}

    if reverse == True : colnames = {value: key for key, value in col_names.items()}
    return(colnames)

def get_parameter_names(include_new=True):

    sample_params_core = ['time_to_infectious',
                          'time_to_symptoms',
                          'time_to_hospitalization',
                          'time_to_critical',
                          'time_to_death',
                          'time_to_detection',
                          'time_to_detection_As',
                          'time_to_detection_Sym',
                          'time_to_detection_Sys',
                          'recovery_time_asymp',
                          'recovery_time_mild',
                          'recovery_time_hosp',
                          'recovery_time_crit',
                          'fraction_symptomatic',
                          'fraction_severe',
                          'fraction_critical',
                          'cfr',
                          'reduced_inf_of_det_cases',
                          'd_Sys',
                          'd_As',
                          'd_P']

    IL_specific_param = ['d_Sys_incr1',
                         'd_Sys_incr2',
                         'd_Sys_incr3',
                         'd_Sys_incr4',
                         'd_Sys_incr5',
                         'd_Sys_incr6',
                         'd_Sys_incr7',
                         'fraction_critical_incr1',
                         'fraction_critical_incr2',
                         'fraction_critical_incr3',
                         'detection_time_1',
                         'detection_time_2',
                         'detection_time_3',
                         'detection_time_4',
                         'detection_time_5',
                         'detection_time_6',
                         'detection_time_7',
                         'crit_time_1',
                         'crit_time_2',
                         'crit_time_3',
                         'd_Sym_change_time_1',
                         'd_Sym_change_time_2',
                         'd_Sym_change_time_3',
                         'd_Sym_change_time_4',
                         'd_Sym_change_time_5',
                         'cfr_time_1',
                         'cfr_time_2']

    IL_locale_param_stem = ['ki_multiplier_3a','ki_multiplier_3b','ki_multiplier_3c',
                            'ki_multiplier_4','ki_multiplier_5','ki_multiplier_6',
                            'ki_multiplier_7','ki_multiplier_8','ki_multiplier_9',
                            'ki_multiplier_10','ki_multiplier_11','ki_multiplier_12',
                            'd_Sym','d_Sym_change1','d_Sym_change2','d_Sym_change3',
                            'd_Sym_change4','d_Sym_change5','Ki','time_infection_import']

    sample_params = sample_params_core + IL_specific_param

    if include_new:
        sample_params_new = ['reduced_infectious_As', 'time_to_loose_immunity', 'fraction_lost_immunity']
        sample_params = sample_params.append(sample_params_new)

    return sample_params, sample_params_core, IL_specific_param, IL_locale_param_stem