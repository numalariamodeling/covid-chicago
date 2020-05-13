import os
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime
from processing_helpers import calculate_incidence

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

if __name__ == '__main__' :

    output_dir = os.path.join(wdir, '..', 'NU_civis_outputs', '20200506', 'trajectories')
    exp_name = 'Trajectories_set5'
    adf = pd.read_csv(os.path.join(output_dir, '%s.csv' % exp_name))

    # adf['date'] = pd.to_datetime(adf['date'])
    # adf = adf[adf['date'] == date(2020,5,7)]
    # adf = adf[['susceptible', 'exposed', 'infected', 'recovered', 'deaths', 'ems']]
    # df = adf.groupby('ems').agg(np.mean).reset_index()
    # print(np.sum(df['recovered']))
    # print(np.sum(df['recovered'])/sum([np.sum(df[x]) for x in df.columns.values if x != 'ems']))
    # exit()
    adf = calculate_incidence(adf)

    filename = 'dash_EMS_trajectories_set5_200506.csv'
    print(adf.columns.values)

    keep = ['date', 'ems', 'run_num']
    output_channels = ['infected', 'recovered', 'new_critical',
                       'new_symptomatic_mild', 'new_symptomatic_severe', 'new_deaths']
    params_of_interest = ['d_Sym', 'd_Sys', 'd_As',
                          'fraction_symptomatic',
                          'fraction_severe',
                          'fraction_dead',
                          'reduced_inf_of_det_cases',
                          'social_multiplier_3']
    adf = adf[keep + output_channels + params_of_interest]

    output_mapping = {'infected' : 'number currently infectious',
                              'recovered' : 'number recovered',
                              'new_critical' : 'daily new ICU cases',
                              'new_symptomatic_mild' : 'daily new mild symptomatic cases',
                              'new_symptomatic_severe' : 'daily new severe symptomatic cases',
                              'new_deaths' : 'daily new deaths'}
    param_mapping = {'d_Sym' : 'fraction mild symptomatic cases detected',
                     'd_As' : 'fraction asymptomatic cases detected',
                     'd_Sys' : 'fraction severe cases detected',
                     'fraction_symptomatic' : 'fraction of infections that are symptomatic',
                     'fraction_severe' : 'fraction of symptomatic cases that are severe',
                     'fraction_dead' : 'fraction of severe cases that die',
                     'reduced_inf_of_det_cases' : 'reduced infectiousness of detected cases',
                     'social_multiplier_3' : 'reduced contact after stay at home'}

    adf = adf.rename(columns=output_mapping)
    adf = adf.rename(columns=param_mapping)

    adf = adf.rename(columns={ x : 'param_%s' % x for k,x in param_mapping.items()})
    adf = adf.rename(columns={ x : 'output_%s' % x for k,x in output_mapping.items()})
    adf.to_csv(os.path.join(wdir,'simulation_output/_csv', filename),
               index=False)
