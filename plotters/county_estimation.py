import os
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime
from processing_helpers import *

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
datapath = os.path.join(datapath, 'covid_IDPH')

if __name__ == '__main__' :

    filename = 'dash_EMS_trajectories_separate_sip_20200419.csv'
    output_filename = '20200419_scen3_tracing_estimation_all.csv'

    df = pd.read_csv(os.path.join(wdir,'simulation_output/_csv', filename))
    df['date'] = pd.to_datetime(df['date'])
    first_plot_day = pd.Timestamp(date.today()) - timedelta(30)
    last_plot_day = pd.Timestamp(date.today()) + timedelta(15)

    df['symptomatic'] = df['output_symptomatic_mild'] + df['output_symptomatic_severe']
    df['new_symptomatic'] = df['output_new_symptomatic_mild'] + df['output_new_symptomatic_severe']
    channels = ['symptomatic', 'new_symptomatic']
    col_names = ['active symptomatic cases Apr 27', 'symptomatic cases Apr 28-May 17']

    df = df[(df['date'] >= first_day) & (df['date'] <= last_day)]
    county_df = pd.read_csv(os.path.join(datapath, 'EMS Population', 'EMS_population_by_county.csv'))

    channel = channels[0]
    mdf = df[df['date'] == first_day].groupby(['date', 'ems'])[channel].agg([CI_50, CI_2pt5, CI_97pt5]).reset_index()
    ch_names = [x for x in mdf.columns.values if 'CI' in x]
    adf = pd.DataFrame()
    for county, cdf in county_df.groupby('county') :
        sdf = mdf[mdf['ems'].isin(cdf['EMS'])]
        sdf = pd.merge(left=sdf, right=cdf, left_on='ems', right_on='EMS')
        for ch in ch_names :
            sdf['%s_scaled' % ch] = sdf[ch] * sdf['share_of_ems_pop']
        tdf = pd.DataFrame( { ch : [np.sum(sdf['%s_scaled' % ch])] for ch in ch_names})
        tdf['county'] = county
        adf = pd.concat([adf, tdf])
    adf = adf.rename(columns={'CI_50' : '%s median' % col_names[0],
                              'CI_2pt5' : '%s LB' % col_names[0],
                              'CI_97pt5' : '%s UB' % col_names[0]})

    channel = channels[1]
    par_cols = [x for x in df.columns.values if ('param' in x or 'run_num' in x)]
    df = df[df['date'] > first_day]
    sum_df = df.groupby(['ems'] + par_cols)[channel].agg(np.sum).reset_index()
    mdf = sum_df.groupby('ems')[channel].agg([CI_50, CI_2pt5, CI_97pt5]).reset_index()
    cumul_df = pd.DataFrame()
    for county, cdf in county_df.groupby('county') :
        sdf = mdf[mdf['ems'].isin(cdf['EMS'])]
        sdf = pd.merge(left=sdf, right=cdf, left_on='ems', right_on='EMS')
        for ch in ch_names :
            sdf['%s_scaled' % ch] = sdf[ch] * sdf['share_of_ems_pop']
        tdf = pd.DataFrame( { ch : [np.sum(sdf['%s_scaled' % ch])] for ch in ch_names})
        tdf['county'] = county
        cumul_df = pd.concat([cumul_df, tdf])

    cumul_df = cumul_df.rename(columns={'CI_50' : '%s median' % col_names[1],
                                        'CI_2pt5' : '%s LB' % col_names[1],
                                        'CI_97pt5' : '%s UB' % col_names[1]})

    adf = pd.merge(left=adf, right=cumul_df, on='county')
    adf.to_csv(os.path.join(wdir,'simulation_output/_csv', output_filename), index=False)
