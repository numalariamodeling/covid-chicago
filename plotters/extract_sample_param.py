"""
Exract samples values that successfully ran
"""
import argparse
import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import sys
sys.path.append('../')
from load_paths import load_box_paths
import random
from processing_helpers import *

mpl.rcParams['pdf.fonttype'] = 42


def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-e",
        "--exp_name",
        type=str,
        help="Experiment name "
    )
    parser.add_argument(
        "-l",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default="Local"
    )

    return parser.parse_args()


def plot_param_by_channel(sample_df, param_list, param_class, plot_path, region_suffix='All', channel=None,
                          time_step=None):
    if time_step is None:
        time_step = 262
    if channel is None:
        channel = 'crit_det'
    channel_name = f'{channel}_{region_suffix}'
    df = load_sim_data(exp_name, region_suffix=None, column_list=['time', 'startdate', 'scen_num', 'sample_num', 'run_num', channel_name], add_incidence=False)
    df['time'] = df['time'].astype('int64')
    df = df[df['time'] == time_step]
    df = pd.merge(how='left', left=df, left_on=['scen_num', 'sample_num'], right=sample_df,
                  right_on=['scen_num', 'sample_num'])

    len(param_list)
    param_list = param_list[:25]
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle(x=0.5, y=0.989, t=f'{param_class}\n{channel_name} at t={time_step}')
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.5, wspace=0.3, top=0.92, bottom=0.05)

    for e, param in enumerate(param_list):
        ax = fig.add_subplot(5, 5, e + 1)
        ax.set_title(param, y=0.95, fontsize=10)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        ax.scatter(df[param], df[channel_name], s=1)

    plot_name = f'scatter_{param_class}_{channel_name}'
    plt.savefig(os.path.join(plot_path, plot_name + '.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', plot_name + '.pdf'))


def plot_param_distributions(df, param_list, param_class, plot_path):
    len(param_list)
    param_list = param_list[:25]
    fig = plt.figure(figsize=(12, 8))
    fig.suptitle(x=0.5, y=0.989, t=param_class)
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.93, bottom=0.05)

    for e, param in enumerate(param_list):
        param_mean = np.mean(df[param])
        param_median = CI_50(df[param])

        ax = fig.add_subplot(5, 5, e + 1)
        ax.set_title(param, y=0.95, fontsize=10)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        ax.hist(df[param], bins=50)
        ax.axvline(x=param_mean, color='#737373', linestyle='-')
        ax.axvline(x=param_median, color='#737373', linestyle='--')

    plot_name = f'histogram_{param_class}'
    plt.savefig(os.path.join(plot_path, plot_name + '.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', plot_name + '.pdf'))


def extract_samples(nsamples=100, seed_nr=751, save_dir=None, save_all_successfull=False, plot_dists=False,
                    include_grp_param=True):
    sample_params, sample_params_core, IL_specific_param, IL_locale_param_stem = get_parameter_names(include_new=False)

    if include_grp_param:
        IL_locale_param = []
        for reg_nr in range(1, 12):
            for param in IL_locale_param_stem:
                IL_locale_param = IL_locale_param + [f'{param}_EMS_{reg_nr}']
        sample_params = sample_params + IL_locale_param

    fname = 'trajectoriesDat_trim.csv'
    if not os.path.exists(os.path.join(sim_output_path, fname)):
        fname = 'trajectoriesDat.csv'
    df = load_sim_data(exp_name, column_list=['time','startdate', 'scen_num', 'sample_num', 'run_num'], add_incidence=False)
    sample_df = pd.read_csv(os.path.join(wdir, 'simulation_output', exp_name, 'sampled_parameters.csv'))

    scen_success = list((df.scen_num.unique()))
    del df

    random.seed(seed_nr)
    if nsamples > len(scen_success):
        nsamples = len(scen_success)
    scen_success_extract = random.sample(scen_success, nsamples)
    df_extract = sample_df[sample_df['scen_num'].isin(scen_success_extract)]
    df_extract = df_extract.reset_index()
    df_extract = df_extract.rename(columns={'scen_num': 'scen_num_extract'})
    df_extract['extract_exp_name'] = exp_name
    df_extract['scen_num'] = range(len(df_extract.index))

    if save_dir is None:
        save_dir = sim_output_path
    df_extract.to_csv(os.path.join(save_dir, f'sample_parameters_extract_n{str(nsamples)}.csv'), index=False)
    if save_all_successfull:
        df_all_success = sample_df[sample_df['scen_num'].isin(scen_success)]
        df_all_success.to_csv(os.path.join(save_dir, f'sample_parameters_extract_all_success.csv'), index=False)

    if plot_dists:
        plot_param_distributions(df=df_extract, param_list=sample_params_core, param_class="Core_model_parameters",
                                 plot_path=plot_path)
        plot_param_distributions(df=df_extract, param_list=IL_specific_param, param_class="IL_specific_model_parameters",
                                 plot_path=plot_path)
        plot_param_by_channel(sample_df=df_extract, param_list=sample_params_core, param_class="Core_model_parameters",
                              plot_path=plot_path)
        plot_param_by_channel(sample_df=df_extract, param_list=IL_specific_param, param_class="IL_specific_model_parameters",
                              plot_path=plot_path)


def extract_mean_of_samples(save_dir=None, plot_dists=False, include_grp_param=True, fname=None):
    sample_params, sample_params_core, IL_specific_param, IL_locale_param_stem = get_parameter_names(include_new=False)

    if include_grp_param:
        IL_locale_param = []
        for reg_nr in range(1, 12):
            for param in IL_locale_param_stem:
                IL_locale_param = IL_locale_param + [f'{param}_EMS_{reg_nr}']
        sample_params = sample_params + IL_locale_param

    df = load_sim_data(exp_name, column_list=['time','startdate', 'scen_num', 'sample_num', 'run_num'], add_incidence=False)
    sample_df = pd.read_csv(os.path.join(sim_output_path, 'sampled_parameters.csv'))

    scen_success = list((df.scen_num.unique()))
    del df
    sample_df_success = sample_df[sample_df['scen_num'].isin(scen_success)]
    sample_df_success['dummy'] = 1

    df_stats = pd.DataFrame()
    for stat in [np.mean, CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]:
        mdf = sample_df_success.groupby('dummy')[sample_params].agg(stat).reset_index().melt(var_name='parameter',
                                                                                             value_name=stat.__name__)
        if df_stats.empty:
            df_stats = mdf
        else:
            df_stats = pd.merge(how='left', left=df_stats, left_on='parameter', right=mdf, right_on='parameter')

    if save_dir is None:
        save_dir = sim_output_path
    df_stats.to_csv(os.path.join(save_dir, 'sample_parameters_summary_stats.csv'), index=False)
    df_mean = sample_df_success.groupby('dummy')[sample_df.columns].agg(np.mean).reset_index()
    df_mean['index'] = 1
    df_mean['scen_num'] = 1
    df_mean['sample_num'] = 1
    df_mean['startdate'] = sample_df_success['startdate'].unique()
    df_mean.to_csv(os.path.join(save_dir, 'sample_parameters_mean.csv'), index=False)

    if plot_dists:
        plot_param_distributions(df=sample_df, param_list=sample_params_core, param_class="Core_model_parameters",
                                 plot_path=plot_path)
        plot_param_distributions(df=sample_df, param_list=IL_specific_param, param_class="IL_specific_model_parameters",
                                 plot_path=plot_path)
        plot_param_distributions(df=sample_df, param_list=IL_locale_param[1:20],
                                 param_class="IL_specific_grp_parameters", plot_path=plot_path)



    if plot_dists:
        plot_param_distributions(df=sample_df, param_list=sample_params_core, param_class="Core_model_parameters",
                                 plot_path=plot_path, fname=fname)
        plot_param_distributions(df=sample_df, param_list=IL_specific_param, param_class="IL_specific_model_parameters",
                                 plot_path=plot_path)
        plot_param_distributions(df=sample_df, param_list=IL_locale_param[1:20],
                                 param_class="IL_specific_grp_parameters", plot_path=plot_path)


if __name__ == '__main__':
    args = parse_args()
    exp_name = args.exp_name
    Location = args.Location

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location="Local")
    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = os.path.join(sim_output_path, '_plots')

    extract_samples(save_dir=None, plot_dists=True, include_grp_param=True)
    extract_mean_of_samples(save_dir=None, plot_dists=False, include_grp_param=True)
