"""
Extract sampled paramaters of selected traces and prepare simulation input files with fitted parameters
Outputs:
- 2 csvs with fitting paramerers for a) single best fit and b) n best fits
- 2 csv with samples parameters that can be used as input csv for subsequent simulation (for a and b as above)
- 1 emodl with fitting parameters renamed for each grp for next simulation
- 2 batch files to submit run scenarios for either a) or b) from above
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
from simulation_helpers import shell_header
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
        default=10
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


def modify_emodl_and_save(exp_name,output_path):
    """Reads in emodl file and renames the parameters that had been identified in exact_sample_traces
        with grp_suffix to have grp specific parameters.
        Assumptions:
        1 - each fitting parameters occurs once or twice the lengths as the defined groups (i.e. EMS-1 to 11)
        2 - if parameters occur twice for each group, they do that in repeated order (i.e. EMS-1, EMS-1, EMS-2, EMS-2 ...)
        3 - duplicated group names are not wanted and removed if accidentally added (i.e. EMS-1_EMS-1)
    """
    """Get group names"""
    grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=output_path)
    param_cols = pd.read_csv(os.path.join(output_path, f'fitted_parameters_besttrace.csv')).columns
    param_cols = [i for i in param_cols if grp_suffix in i]

    param_cols_unique = param_cols
    for grp in reversed(grp_list):
        param_cols_unique = [col.replace(f'_{grp}', '') for col in param_cols_unique]
    param_cols_unique = list(set(param_cols_unique))

    emodl_name = [file for file in os.listdir(output_path) if '.emodl' in file][0].replace('.emodl','')
    emodl_name_new = f'{emodl_name}_resim'

    fin = open(os.path.join(output_path, f'{emodl_name}.emodl'), "rt")
    emodl_txt = fin.read()
    fin.close()
    emodl_chunks = emodl_txt.split('@')

    sample_cols=[]
    for col in param_cols_unique:
        col_pos = []
        for i, chunk in enumerate(emodl_chunks):
            if col in chunk:
                col_pos = col_pos + [i]

        for i, pos in enumerate(col_pos):
            #print(emodl_chunks[pos])
            if len(col_pos) <len(grp_list):
                sample_cols = sample_cols + [col]
            if len(col_pos) == len(grp_list):
                emodl_chunks[pos] = f'{emodl_chunks[pos]}_{grp_list[i]}'
            if len(col_pos) == len(grp_list)*2:
                """assuming if occuring twice, its the same grp in two consecutive instances"""
                grp_list_dup = [grp for grp in grp_list for i in range(2)]
                emodl_chunks[pos] = f'{emodl_chunks[pos]}_{grp_list_dup[i]}'
            #print(emodl_chunks[pos])

    emodl_txt_new = '@'.join(emodl_chunks)
    for grp in grp_list:
        emodl_txt_new = emodl_txt_new.replace(f'{grp}_{grp}',f'{grp}')
    fin = open(os.path.join(output_path, f'{emodl_name_new}.emodl'), "w")
    fin.write(emodl_txt_new)
    fin.close()


def write_submission_file(trace_selection,Location, r= 'IL',model='locale'):
    """Writes batch file that copies required input csvs and emodl to the corresponding location in git_dir
       Assumptions:
       Running location fixed to IL for spatial model (momentarily)
    """
    emodl_name = [file for file in os.listdir(output_path) if 'emodl' in file][0].replace('.emodl','')
    sample_csv = f'sample_parameters_{trace_selection}.csv'
    input_csv_str = f' --sample_csv {sample_csv}'
    model_str = f' --model {model}'
    new_exp_name = f'{exp_name}_resim_{trace_selection}'

    csv_from = os.path.join(output_path, sample_csv ).replace("/","\\")
    csv_to = os.path.join(git_dir,"experiment_configs","input_csv").replace ("/","\\")
    emodl_from = os.path.join(output_path,emodl_name+"_resim.emodl")
    emodl_to = os.path.join(git_dir,"emodl",emodl_name+"_resim.emodl").replace("/","\\")
    if Location =='Local':
        file = open(os.path.join(output_path, 'bat', f'00_runScenarios_{trace_selection}.bat'), 'w')
        file.write(
            f'copy {csv_from} {csv_to}\n'
            f'copy {emodl_from} {emodl_to}\n'
            f'cd {git_dir} \n python runScenarios.py -r {r} '
            f'-e {str(emodl_name)}_resim.emodl -n {new_exp_name} {model_str} {input_csv_str} \npause')
        file.close()
    if Location =='NUCLUSTER':
        csv_from = csv_from.replace("\\","/")
        csv_to = csv_to.replace("\\","/")
        emodl_to = emodl_to.replace("\\","/")
        jobname = 'runFittedParamSim'
        header = shell_header(job_name=jobname)
        commands = f'\ncp {csv_from} {csv_to}\n' \
                   f'\ncp {emodl_from} {emodl_to}\n' \
                   f'\ncd {git_dir} \n python runScenarios.py -r {r}  ' \
                   f'-e {str(emodl_name)}_resim.emodl -n {new_exp_name} {model_str} {input_csv_str}'
        file = open(os.path.join(output_path,'sh', f'00_runScenarios_{trace_selection}.sh'), 'w')
        file.write(header + commands)
        file.close()

        file = open(os.path.join(output_path, f'submit_runScenarios_{trace_selection}.sh'), 'w')
        file.write(
            f'cd {os.path.join(output_path,"sh")}\n'
            f'sbatch 00_runScenarios_{trace_selection}.sh\n')
        file.close()

def extract_sample_traces(exp_name,traces_to_keep_ratio, traces_to_keep_min):
    """Identifies parameters that vary as fitting parameters and writes them out into csvs.
       Combines fitting with sample parameters to simulate 'full' simulation.
       Assumption:
       Parameter that wish to no be grp specific were fixed
       (could be aggregated before fitting, which needs to be edited together with trace_selection.py)
    """

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
        df_samples_sub = df_samples_sub.loc[df_samples_sub.groupby(['sample_num']).scen_num.idxmin()]

        rank_export_df = pd.read_csv(os.path.join(output_path, f'traces_ranked_region_{str(grp_nr)}.csv'))
        n_traces_to_keep = int(len(rank_export_df) / traces_to_keep_ratio)
        if n_traces_to_keep < traces_to_keep_min and len(rank_export_df) >= traces_to_keep_min:
            n_traces_to_keep = traces_to_keep_min
        if len(rank_export_df) < traces_to_keep_min:
            n_traces_to_keep = len(rank_export_df)

        df_samples_sub = pd.merge(how='left', left=rank_export_df[['sample_num','norm_rank']], left_on=['sample_num'], right=df_samples_sub, right_on=['sample_num'])
        df_samples_sub = df_samples_sub.sort_values(by=['norm_rank']).reset_index(drop=True)
        df_samples_sub = df_samples_sub.drop(['scen_num', 'sample_num', 'norm_rank'], axis=1)
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
    df_samples['sample_num'] = df_samples.reset_index().index

    """Generate combinations of samples (df_samples) and fitted parameters (df_traces)"""
    df_traces_n = gen_combos(df_samples, df_traces)
    df_traces_best = gen_combos(df_samples, df_traces.head(n=1))
    df_traces_n.to_csv(os.path.join(output_path, f'sample_parameters_ntraces{n_traces_to_keep}.csv'), index=False)
    df_traces_best.to_csv(os.path.join(output_path, f'sample_parameters_besttrace.csv'), index=False)

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
        extract_sample_traces(exp_name,traces_to_keep_ratio,traces_to_keep_min)
        modify_emodl_and_save(exp_name, output_path)

        """ToDo expand below to be applicable to base and age model"""
        # if len(grp_list) == 11 and grp_suffix == 'EMS':
        #    r = 'IL'
        trace_selections = ['besttrace', f'ntraces']
        for trace_selection in trace_selections:
            write_submission_file(trace_selection,Location,r = 'IL')

        """Submit simulations to run"""
        if trace_to_run is not None:
            if Location =='Local':
                p0 = os.path.join(output_path, 'bat', f'runScenarios_{trace_to_run}.bat')
            if Location =='NUCLUSTER':
                p0 = os.path.join(output_path, f'submit_runScenarios_{trace_selection}.sh')
            subprocess.call([p0])