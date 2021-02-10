import numpy as np
import os
import pandas as pd
from load_paths import load_box_paths

try:
    print(Location)
except NameError:
    if os.name == "posix": Location ="NUCLUSTER"
    else: Location ="Local"

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths(Location=Location)


def get_grp_list(exp_name,  input_wdir=None, input_sim_output_path =None):
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df_samples = pd.read_csv(os.path.join(sim_output_path, 'sampled_parameters.csv'))
    N_cols = [col for col in df_samples.columns if 'N_' in col]
    if len(N_cols) != 0:
        grp_list = [col.replace('N_', '') for col in N_cols]
    else:
        grp_list = None
    return grp_list

def load_sim_data(exp_name, region_suffix ='_All', input_wdir=None, fname=None,
                  input_sim_output_path =None, column_list=None, add_incidence=True,
                  select_traces=True, traces_to_keep_ratio=4, traces_to_keep_min=100) :
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base


    if region_suffix is not None:
        ems_nr = region_suffix.replace("_EMS-", "")
        if region_suffix == "_All": ems_nr = 0

        if fname is None:
            fname = f'trajectoriesDat_region_{str(ems_nr)}.csv'
            if os.path.exists(os.path.join(sim_output_path, fname)) == False:
                fname = f'trajectoriesDat_region_{str(ems_nr)}_trim.csv'
            if os.path.exists(os.path.join(sim_output_path, fname)) == False:
                fname = 'trajectoriesDat_trim.csv'
            if os.path.exists(os.path.join(sim_output_path, fname)) == False:
                fname = 'trajectoriesDat.csv'

        print(f'Using {fname}')
        df = pd.read_csv(os.path.join(sim_output_path, fname), usecols=column_list)
        df.columns = df.columns.str.replace(region_suffix, '')

        if select_traces:
            if os.path.exists(os.path.join(sim_output_path, f'traces_ranked_region_{str(ems_nr)}.csv')):
                rank_export_df = pd.read_csv(os.path.join(sim_output_path, f'traces_ranked_region_{str(ems_nr)}.csv'))

                n_traces_to_keep = int(len(rank_export_df) / traces_to_keep_ratio)
                if n_traces_to_keep < traces_to_keep_min :
                    n_traces_to_keep = traces_to_keep_min
                if len(rank_export_df) < traces_to_keep_min :
                    n_traces_to_keep = len(rank_export_df)

                rank_export_df_sub = rank_export_df[0:n_traces_to_keep]
                df = df[df['scen_num'].isin(rank_export_df_sub.scen_num.unique())]
    else :
        fname = 'trajectoriesDat.csv'
        if os.path.exists(os.path.join(sim_output_path, fname)) == False:
            fname = 'trajectoriesDat_trim.csv'
        print(f'Using {fname}')
        df = pd.read_csv(os.path.join(sim_output_path, fname), usecols=column_list)  ## engine='python'

    df = df.dropna()
    first_day = pd.Timestamp(df['startdate'].unique()[0])
    df['date'] = df['time'].apply(lambda x: first_day + pd.Timedelta(int(x),'days'))

    if add_incidence:
        if 'recovered' in df.columns:
            df['infected_cumul'] = df['infected'] + df['recovered'] + df['deaths']
            df = calculate_incidence(df)
        else:
            df = calculate_incidence(df, trimmed =True)

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
    ref_df['date'] = pd.to_datetime(ref_df['date'])
    ref_df = ref_df[ref_df['date'].between(pd.Timestamp('2020-01-01'), pd.Timestamp.today())]

    return ref_df


def calculate_prevalence(df):

    df['N'] = df['N'] - df['deaths']
    df['IFR'] = df['deaths'] / (df['recovered'] + df['deaths'])
    df['IFR_t'] = df['new_deaths'] / (df['new_recovered'] + df['new_deaths'])
    df['prevalence'] = df['infected'] / df['N']
    df['seroprevalence_current'] = df['recovered'] / df['N']
    df['seroprevalence'] = df.groupby(['scen_num', 'sample_num'])['seroprevalence_current'].transform('shift', 14)

    if 'infected_det' in df.columns:
        df['N_det'] = df['N'] - df['deaths_det']
        df['IFR_det'] = df['deaths_det'] / (df['recovered_det'] + df['deaths_det'])
        df['IFR_det_t'] = df['new_deaths_det'] / (df['new_recovered_det'] + df['new_deaths_det'])
        df['prevalence_det'] = df['infected_det'] / df['N_det']
        df['seroprevalence_current_det'] = df['recovered_det'] / df['N_det']
        df['seroprevalence_det'] = df.groupby(['scen_num', 'sample_num'])['seroprevalence_current_det'].transform('shift', 14)
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
                                'new_detected_deaths' : count_new(df, 'deaths_det_cumul'),
                                'new_deaths' : count_new(df, 'deaths')
                                })
        if trimmed == True:
            sdf = pd.DataFrame({'time': df['time'],
                                'new_detected_hospitalized' : count_new(df, 'hosp_det_cumul'),
                                'new_hospitalized' : count_new(df, 'hosp_cumul'),
                                'new_critical' : count_new(df, 'crit_cumul'),
                                'new_detected_critical' : count_new(df, 'crit_det_cumul'),
                                'new_detected_deaths' : count_new(df, 'deaths_det_cumul'),
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
                              'new_detected_deaths_%s' % age_group : count_new(df, 'deaths_det_cumul_%s' % age_group),
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
    df = df.drop_duplicates()

    df = df[df['overflow_threshold_percent'] == 1]
    df['ems'] = df['geography_modeled']
    df['ems'] = df['geography_modeled'].replace("covidregion_", "", regex=True)
    df = df[['ems', 'resource_type', 'avg_resource_available']]
    df = df.drop_duplicates()

    ## if conflicting numbers, take the lower ones!
    dups = df.groupby(["ems", "resource_type"])["avg_resource_available"].nunique()
    if int(dups.nunique()) >1 :
        print(f'{ems_fname} contains multiple capacity values, selecting the lower ones.')
        df= df.loc[df.groupby(["ems", "resource_type"])["avg_resource_available"].idxmax()]

    df = df.pivot(index='ems', columns='resource_type', values='avg_resource_available')
    df.index.name = 'ems'
    df.reset_index(inplace=True)

    if ems == 'illinois' or ems == 0:
        df['ems'] = 'illinois'
        df = df.groupby('ems')[['hb_availforcovid', 'icu_availforcovid', 'vent_availforcovid']].agg(np.sum).reset_index()
    else :
        df = df[df['ems'] == str(ems)]

    capacity = {'hosp_det': int(df['hb_availforcovid']),
                'total_hosp_census': int(df['hb_availforcovid']),
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


def get_datacomparison_channels():
    outcome_channels = ['hosp_det_cumul', 'hosp_cumul', 'hosp_det', 'hospitalized',
                    'crit_det_cumul', 'crit_cumul', 'crit_det', 'critical',
                    'deaths_det_cumul', 'deaths']
    channels = ['new_detected_deaths', 'crit_det', 'hosp_det', 'new_deaths','new_detected_hospitalized',
                'new_detected_hospitalized']
    data_channel_names = ['deaths',
                          'confirmed_covid_icu', 'covid_non_icu', 'deaths','inpatient', 'admissions']
    titles = ['New Detected\nDeaths (LL)', 'Critical Detected (EMR)', 'Inpatient non-ICU\nCensus (EMR)', 'New Detected\nDeaths (LL)',
              'Covid-like illness\nadmissions (IDPH)', 'New Detected\nHospitalizations (LL)']
    return outcome_channels, channels, data_channel_names, titles
    
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
                         'd_Sys_incr8',
                         'd_Sym_change1',
                         'd_Sym_change2',
                         'd_Sym_change3',
                         'd_Sym_change4',
                         'd_Sym_change5',
                         'd_Sym_change6',
                         'd_Sym_change7',
                         'd_Sym_change8',
                         'fraction_dead_change1',
                         'fraction_dead_change2',
                         'fraction_dead_change3',
                         'fraction_dead_change4',
                         'fraction_dead_change5',
                         'fraction_dead_change6',
                         'fraction_dead_change7',
                         'fraction_dead_change8',
                         'fraction_dead_change9',
                         'fraction_critical_change1',
                         'fraction_critical_change2',
                         'fraction_critical_change3',
                         'fraction_critical_change4',
                         'fraction_critical_change5',
                         'fraction_critical_change6',
                         'fraction_critical_change7',
                         'fraction_critical_change8',
                         'fraction_critical_change9',
                         'fraction_critical_change10']

    IL_locale_param_stem = ['ki_multiplier_3a','ki_multiplier_3b','ki_multiplier_3c',
                            'ki_multiplier_4','ki_multiplier_5','ki_multiplier_6',
                            'ki_multiplier_7','ki_multiplier_8','ki_multiplier_9',
                            'ki_multiplier_10','ki_multiplier_11','ki_multiplier_12',
                            'ki_multiplier_13','Ki','time_infection_import']

    sample_params = sample_params_core + IL_specific_param

    if include_new:
        sample_params_new = ['reduced_infectious_As', 'time_to_loose_immunity', 'fraction_lost_immunity']
        sample_params = sample_params.append(sample_params_new)

    return sample_params, sample_params_core, IL_specific_param, IL_locale_param_stem
