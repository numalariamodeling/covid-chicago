"""
Assigns negative log-likelihoods to each trace in a set of trajectories.
"""
import argparse
import os
import pandas as pd
import numpy as np
import scipy.stats
import sys

sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime
from processing_helpers import *

def parse_args():

    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-s",
        "--stem",
        type=str,
        help="Name of simulation experiment"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default = "Local"
    )
    parser.add_argument(
        "-t", "--trajectoriesName",
        type=str,
        help="Name of trajectoriesDat file, trajectoriesDat.csv or trajectoriesDat_trim.csv",
        default='trajectoriesDat.csv'
    )
    parser.add_argument(
        "--deaths_weight",
        type=float,
        help="Weight of deaths in negative log likelihood calculation. Default is 1.0.",
        default=1.0
    )
    parser.add_argument(
        "--crit_weight",
        type=float,
        help="Weight of ICU population in negative log likelihood calculation. Default is 1.0.",
        default=1.0
    )
    parser.add_argument(
        "--non_icu_weight",
        type=float,
        help="Weight of non-ICU population in negative log likelihood calculation. Default is 1.0.",
        default=1.0
    )
    parser.add_argument(
        "--cli_weight",
        type=float,
        help="Weight of CLI admissions in negative log likelihood calculation. Default is 1.0.",
        default=1.0
    )
    return parser.parse_args()
    
def sum_nll(df_values, ref_df_values):
    try:
        x = -np.log10(scipy.stats.poisson(mu=df_values).pmf(k=ref_df_values))
    except ValueError:
        print('ERROR: The simulation and reference arrays may not be the same length.')
        print('Length simulation: ' + str(len(df_values)))
        print('Length reference: ' + str(len(ref_df_values)))
    x[np.abs(x) == np.inf] = 0
    return np.sum(x)

def compare_sim_and_ref(df, ems_nr, ref_df, channels, data_channel_names, titles, region_label,
                     first_day, last_day, ymax=10000, logscale=True, weights_array=[1.0,1.0,1.0,1.0]):

    [deaths_weight, crit_weight, non_icu_weight, cli_weight] = weights_array
    ref_df_trunc = ref_df[(ref_df['date'] > first_day) & (ref_df['date'] < last_day)]
    df_trunc = df[(df['date'] > first_day) & (df['date'] < last_day)]
    run_sample_scen_list = list(df_trunc.groupby(['run_num','sample_num','scen_num']).size().index)
    rank_export_df = pd.DataFrame({'run_num':[], 'sample_num':[], 'scen_num':[], 'nll':[]})
    for x in run_sample_scen_list:
        total_nll = 0
        (run_num, sample_num, scen_num) = x
        df_trunc_slice = df_trunc[(df_trunc['run_num'] == run_num) & (df_trunc['sample_num'] == sample_num) & (df_trunc['scen_num'] == scen_num)]
        total_nll += deaths_weight*sum_nll(df_trunc_slice['new_detected_deaths'].values, ref_df_trunc['deaths'].values)
        total_nll += crit_weight*sum_nll(df_trunc_slice['crit_det'].values, ref_df_trunc['confirmed_covid_icu'].values)
        total_nll += cli_weight*sum_nll(df_trunc_slice['new_detected_hospitalized'].values, ref_df_trunc['inpatient'].values)
        total_nll += non_icu_weight*sum_nll(df_trunc_slice['hosp_det'].values, ref_df_trunc['covid_non_icu'].values)
        rank_export_df = rank_export_df.append(pd.DataFrame({'run_num':[run_num], 'sample_num':[sample_num], 'scen_num':[scen_num], 'nll':[total_nll]}))
    rank_export_df['norm_rank'] = (rank_export_df['nll'].rank()-1)/(len(rank_export_df)-1)
    rank_export_df = rank_export_df.sort_values(by=['norm_rank']).reset_index(drop=True)
    rank_export_df.to_csv(os.path.join(output_path,'traces_ranked_region_' + str(ems_nr) + '.csv'), index=False)


def compare_ems(exp_name,fname, ems_nr,first_day,last_day,weights_array):

    if ems_nr == 0:
        region_suffix = "_All"
        region_label = 'Illinois'
    else:
        region_suffix = "_EMS-" + str(ems_nr)
        region_label = region_suffix.replace('_EMS-', 'COVID-19 Region ')

    column_list = ['time', 'startdate', 'scen_num', 'sample_num','run_num']
    outcome_channels = ['hosp_det_cumul', 'hosp_cumul', 'hosp_det', 'hospitalized',
                        'crit_det_cumul', 'crit_cumul', 'crit_det', 'critical',
                        'death_det_cumul', 'deaths']

    for channel in outcome_channels:
        column_list.append(channel + region_suffix)

    df = load_sim_data(exp_name, region_suffix=region_suffix, fname=fname,column_list=column_list)
    df = df[(df['date'] >= first_day) & (df['date'] <= last_day)]
    df['critical_with_suspected'] = df['critical']

    ref_df = load_ref_df(ems_nr)

    channels = ['new_detected_deaths', 'crit_det', 'hosp_det', 'new_deaths','new_detected_hospitalized',
                'new_detected_hospitalized']
    data_channel_names = ['confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'covid_non_icu', 'deaths','inpatient', 'admissions']
    titles = ['New Detected\nDeaths (EMR)', 'Critical Detected (EMR)', 'Inpatient non-ICU\nCensus (EMR)', 'New Detected\nDeaths (LL)',
              'Covid-like illness\nadmissions (IDPH)', 'New Detected\nHospitalizations (LL)']

    compare_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,
                     region_label=region_label,first_day= first_day, last_day= last_day, logscale=True, weights_array=weights_array)

if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    trajectoriesName = args.trajectoriesName
    Location = args.Location
    weights_array = [args.deaths_weight, args.crit_weight, args.non_icu_weight, args.cli_weight]

    first_plot_day = date(2020, 3, 25)
    last_plot_day = date(2021, 1, 1)

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        output_path = os.path.join(wdir, 'simulation_output',exp_name)
        for ems_nr in range(0,12):
            print("Start processing region " + str(ems_nr))
            compare_ems(exp_name,fname=trajectoriesName, ems_nr=int(ems_nr),first_day=first_plot_day,last_day=last_plot_day,weights_array=weights_array)
