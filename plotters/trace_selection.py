"""
Assigns negative log-likelihoods to each trace in a set of trajectories.
"""
import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import sys
from data_comparison_spatial import plot_sim_and_ref

sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.dates as mdates
import seaborn as sns
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
        "--deaths_weight",
        type=float,
        help="Weight of deaths in negative log likelihood calculation. Default is 1.0.",
        default=0.0
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
        default=0.0
    )
    parser.add_argument(
        "--plot",
        action='store_true',
        help="If specified, plots with top 50% best-fitting trajectories will be generated.",
    )
    parser.add_argument(
        "--traces_to_keep_ratio",
        type=int,
        help="Ratio of traces to keep out of all trajectories",
        default=4
    )
    parser.add_argument(
        "--traces_to_keep_min",
        type=int,
        help="Minimum number of traces to keep, might overwrite traces_to_keep_ratio for small simulations",
        default=100
    )
    return parser.parse_args()

def sum_nll(df_values, ref_df_values):
    """remove NAs in data from both arrays"""
    na_pos = np.argwhere(np.isnan(ref_df_values))
    if len(na_pos) != 0 :
        df_values = np.delete(df_values, na_pos)
        ref_df_values = np.delete(ref_df_values, na_pos)
    try:
        x = -np.log10(scipy.stats.poisson(mu=df_values).pmf(k=ref_df_values))
    except ValueError:
        print('ERROR: The simulation and reference arrays may not be the same length.')
        print('Length simulation: ' + str(len(df_values)))
        print('Length reference: ' + str(len(ref_df_values)))
    len_inf = len(list(i for i in list(x) if i == np.inf))
    if len_inf <= len(x)*0.9:
        x[np.abs(x) == np.inf] = 0
    return np.sum(x)

def rank_traces_nll(df, ems_nr, ref_df, weights_array=[1.0,1.0,1.0,1.0]):
    #Creation of rank_df
    [deaths_weight, crit_weight, non_icu_weight, cli_weight] = weights_array

    """ Ensure common dates"""
    df_dates = df[df['date'].isin(ref_df['date'].unique())].date.unique()
    ref_df_dates = ref_df[ref_df['date'].isin(df['date'].unique())].date.unique()
    common_dates = df_dates[np.isin(df_dates, ref_df_dates)]
    df_trunc = df[df['date'].isin(common_dates)]
    ref_df_trunc = ref_df[ref_df['date'].isin(common_dates)]

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
    rank_export_df = rank_export_df.dropna()
    rank_export_df['norm_rank'] = (rank_export_df['nll'].rank()-1)/(len(rank_export_df)-1)
    rank_export_df = rank_export_df.sort_values(by=['norm_rank']).reset_index(drop=True)
    rank_export_df.to_csv(os.path.join(output_path,'traces_ranked_region_' + str(ems_nr) + '.csv'), index=False)

    return rank_export_df


def compare_ems(exp_name, ems_nr,first_day,last_day,weights_array,
                traces_to_keep_ratio=2,traces_to_keep_min=1,plot_trajectories=False):

    if ems_nr == 0:
        region_suffix = "_All"
        region_label = 'Illinois'
    else:
        region_suffix = "_EMS-" + str(ems_nr)
        region_label = region_suffix.replace('_EMS-', 'COVID-19 Region ')

    column_list = ['time', 'startdate', 'scen_num', 'sample_num','run_num']
    outcome_channels, channels, data_channel_names, titles = get_datacomparison_channels()

    for channel in outcome_channels:
        column_list.append(channel + region_suffix)

    ref_df = load_ref_df(ems_nr)
    ref_df = ref_df[ref_df['date'].between(first_day, last_day)]

    df = load_sim_data(exp_name, region_suffix=region_suffix, column_list=column_list)
    df = df[df['date'].between(first_day, ref_df['date'].max())]
    df['critical_with_suspected'] = df['critical']
    rank_export_df = rank_traces_nll(df, ems_nr, ref_df, weights_array=weights_array)

    #Creation of plots
    if plot_trajectories:
        plot_path = os.path.join(output_path, '_plots')

        n_traces_to_keep = int(len(rank_export_df) / traces_to_keep_ratio)
        if n_traces_to_keep < traces_to_keep_min and len(rank_export_df) >= traces_to_keep_min:
            n_traces_to_keep = traces_to_keep_min
        if len(rank_export_df) < traces_to_keep_min:
            n_traces_to_keep = len(rank_export_df)

        df = pd.merge(rank_export_df[0:int(n_traces_to_keep)],df)

        plot_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,
                         region_label=region_label, first_day=first_day, last_day=last_day, plot_path=plot_path,
                         plot_name_suffix =f'_best_fit_{str(1/traces_to_keep_ratio)}_n{str(n_traces_to_keep)}')


if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    Location = args.Location
    weights_array = [args.deaths_weight, args.crit_weight, args.non_icu_weight, args.cli_weight]

    """ For plotting"""
    traces_to_keep_ratio = args.traces_to_keep_ratio
    traces_to_keep_min = args.traces_to_keep_min

    """If fitting to deaths, include a lag of 14 days (applies to all indicators)"""
    timelag_days = 0
    if args.deaths_weight != 0:
        timelag_days = 14

    first_plot_day = pd.Timestamp('2020-03-25')
    last_plot_day =  pd.Timestamp.today() - pd.Timedelta(timelag_days,'days')

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        print(exp_name)
        output_path = os.path.join(wdir, 'simulation_output',exp_name)
        for ems_nr in range(0,12):
            print("Start processing region " + str(ems_nr))
            compare_ems(exp_name, ems_nr=int(ems_nr),first_day=first_plot_day,last_day=last_plot_day,
                        weights_array=weights_array, plot_trajectories=True,
                        traces_to_keep_ratio=traces_to_keep_ratio,traces_to_keep_min=traces_to_keep_min)