"""
Extract sampled paramaters of selected traces
Outputs:
- 2 csvs with fitting paramerers for a) single best fit and b) n best fits
- 2 csv with samples parameters that can be used as input csv for subsequent simulation (for a and b as above)
"""
import argparse
import os
import pandas as pd
import numpy as np
import sys
import subprocess
sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *
from sample_parameters import make_identifier, gen_combos

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
        "--traces_to_keep_ratio",
        type=int,
        help="Ratio of traces to keep out of all trajectories",
        default=2
    )
    parser.add_argument(
        "--traces_to_keep_min",
        type=int,
        help="Minimum number of traces to keep, might overwrite traces_to_keep_ratio for small simulations",
        default=5
    )
    parser.add_argument(
        "--trace_to_run",
        type=str,
        choices=["ntraces", "besttrace",None],
        help="Whether to run single best trace or n best traces as defined in traces_to_keep_ratio ",
        default=None
    )

    return parser.parse_args()



def write_submission_file(trace_selection, r= 'IL'):
    emodl_name = [file for file in os.listdir(output_path) if 'emodl' in file][0].replace('.emodl','')
    yaml_file = [file for file in os.listdir(output_path) if 'yaml' in file][-1]  # placeholder
    sample_csv = f'sample_parameters_{trace_selection}.csv'
    input_csv_str = f'--load_sample_parameters --sample_csv {sample_csv}'
    new_exp_name = f'{exp_name}_resim_{trace_selection}'

    csv_from = os.path.join(output_path, sample_csv ).replace("/","\\")
    csv_to = os.path.join(git_dir,"experiment_configs","input_csv").replace ("/","\\")
    emodl_from = os.path.join(output_path,emodl_name+".emodl")
    emodl_to = os.path.join(git_dir,"emodl",emodl_name+"_resim.emodl").replace("/","\\")
    file = open(os.path.join(output_path, 'bat', f'runScenarios_{trace_selection}.bat'), 'w')
    file.write(
        f'copy {csv_from} {csv_to}\n'
        f'copy {emodl_from} {emodl_to}\n'
        f'cd {git_dir} \n python runScenarios.py -rl {Location} -r {r} -c {str(yaml_file)} -e {str(emodl_name)}_resim.emodl --exp-name {new_exp_name} {input_csv_str} \npause')
    file.close()

def extract_sample_traces(traces_to_keep_ratio, traces_to_keep_min,trace_to_run):

    df_samples = pd.read_csv(os.path.join(output_path, 'sampled_parameters.csv'))
    """Drop parameter columns that have equal values in all scenarios (rows) to assess fitted parameters"""
    nunique = df_samples.apply(pd.Series.nunique)
    cols_to_drop = nunique[nunique == 1].index
    df_samples = df_samples.drop(cols_to_drop, axis=1)
    grp_list = get_grp_list(exp_name)

    df_traces = pd.DataFrame()
    for grp in grp_list:
        grp_nr = grp.split('_')[-1]
        grp_suffix= grp.split('_')[0]

        """Drop parameters that correspond to other regions"""
        grp_channels = [i for i in df_samples.columns if grp_suffix in i]
        grp_cols_to_drop = [i for i in grp_channels if grp_nr != i.split('_')[-1]]
        df_samples_sub = df_samples.drop(grp_cols_to_drop, axis=1)

        rank_export_df = pd.read_csv(os.path.join(output_path, f'traces_ranked_region_{str(grp_nr)}.csv'))
        n_traces_to_keep = int(len(rank_export_df) / traces_to_keep_ratio)
        if n_traces_to_keep < traces_to_keep_min and len(rank_export_df) >= traces_to_keep_min:
            n_traces_to_keep = traces_to_keep_min
        if len(rank_export_df) < traces_to_keep_min:
            n_traces_to_keep = len(rank_export_df)

        df_samples_sub = pd.merge(how='left', left=rank_export_df[['scen_num','norm_rank']], left_on=['scen_num'], right=df_samples_sub, right_on=['scen_num'])
        df_samples_sub = df_samples_sub.sort_values(by=['norm_rank']).reset_index(drop=True)
        df_samples_sub = df_samples_sub.drop(['scen_num','sample_num','norm_rank'], axis=1)
        df_samples_sub.columns = df_samples_sub.columns + f'_{str(grp)}'
        df_samples_sub.columns = [col.replace( f'_{str(grp)}_{str(grp)}', f'_{str(grp)}') for col in df_samples_sub.columns ]
        df_samples_sub['row_num'] = df_samples_sub.index

        if df_traces.empty:
            df_traces = df_samples_sub
        else:
            df_traces = pd.merge(how='left', left=df_traces, left_on=['row_num'], right=df_samples_sub, right_on=['row_num'])
        del df_samples_sub, rank_export_df
    del df_samples

    """Export fitted parameters"""
    if 'Ki' not in df_traces.columns:
        df_traces['Ki'] = -9 #placeholder for runScenarios.oy which requires Ki
    df_traces.to_csv(os.path.join(output_path, f'fitted_parameters_ntraces{n_traces_to_keep}.csv'), index=False)
    df_traces.head(n=1).to_csv(os.path.join(output_path, f'fitted_parameters_besttrace.csv'), index=False)

    """Export all parameter columns to be used as simulation input"""
    df_samples = pd.read_csv(os.path.join(output_path, 'sampled_parameters.csv'))
    df_samples = df_samples.loc[:n_traces_to_keep+1 , cols_to_drop]
    df_samples['scen_num'] = df_samples.reset_index().index

    """Generate combinations of samples (df_samples) and fitted parameters (df_traces)"""
    df_traces_n = gen_combos(df_samples, df_traces)
    df_traces_best = gen_combos(df_samples, df_traces.head(n=1))
    df_traces_n.to_csv(os.path.join(output_path, f'sample_parameters_ntraces{n_traces_to_keep}.csv'), index=False)
    df_traces_best.to_csv(os.path.join(output_path, f'sample_parameters_besttrace.csv'), index=False)

    """Per default save and overwrite in experiment_configs/input_csv to run in next simulation"""
    df_traces_n.to_csv(os.path.join(git_dir,'experiment_configs','input_csv', f'sample_parameters_ntraces.csv'), index=False)
    df_traces_best.to_csv(os.path.join(git_dir,'experiment_configs','input_csv', f'sample_parameters_besttrace.csv'), index=False)

    """ToDo expand below to be applicable to base and age model"""
    #if len(grp_list) == 11 and grp_suffix == 'EMS':
    #    r = 'IL'

    trace_selections = ['besttrace', f'ntraces']
    for trace_selection in trace_selections:
        write_submission_file(trace_selection)

    if trace_to_run is not None:
        p0 = os.path.join(output_path, 'bat', f'runScenarios_{trace_to_run}.bat')
        subprocess.call([p0])


if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    Location = args.Location
    trace_to_run = args.trace_to_run

    """For extracting best traces"""
    traces_to_keep_ratio = args.traces_to_keep_ratio
    traces_to_keep_min = args.traces_to_keep_min

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        print(exp_name)
        output_path = os.path.join(wdir, 'simulation_output',exp_name)
        for ems_nr in range(0,12):
            print("Start processing region " + str(ems_nr))
        extract_sample_traces(traces_to_keep_ratio=traces_to_keep_ratio,traces_to_keep_min=traces_to_keep_min,trace_to_run=trace_to_run)