"""
Combine, reformat and trim single simulation trajectories.
Output: tracjectoriesDat including all outcome channels, and trajectoriesDat_trim including key channels only
If number of trajectories exceeds a specified limit, multiple trajectories in chunks will be returned.
"""
import argparse
import subprocess
import pandas as pd
import os
import shutil
import sys
sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *

def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-exp",
        "--exp_name",
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
        "--time_start",
        type=int,
        help="Lower limit of time steps to keep",
        default=1
    )
    parser.add_argument(
        "--time_stop",
        type=int,
        help="Upper limit of time steps to keep",
        default=1000
    )
    parser.add_argument(
        "-limit",
        "--scen_limit",
        type=int,
        help="Number of simulations to combine",
        default = 700
    )
    parser.add_argument(
        "--additional_sample_param",
        type=str,
        nargs='+',
        help="""Name of additional sample parameters to keep, reduced to minimum to reduce file size
                format: --additional_sample_param time_to_infectious time_to_death (no quotes)
                Note: sample parameters can also always be added from the sample_parameters.csv if required in the postprocessing""",
        default = ''
    )
    parser.add_argument(
        "--delete_trajectories",
        action='store_true',
        help="If specified, single trajectories will be deleted after postprocessing.",
    )

    return parser.parse_args()
    

def reprocess(input_fname='trajectories.csv'):
    fname = os.path.join(git_dir, input_fname)
    row_df = pd.read_csv(fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    run_time = len([x for x in df.columns.values if '{0}' in x])
    num_runs = int((len(row_df)) / run_time)
    df = df.reset_index(drop=False)
    df = df.rename(columns={'index': 'time'})
    df['time'] = df['time'].astype(float)
    adf = pd.DataFrame()
    for run_num in range(num_runs):
        channels = [x for x in df.columns.values if '{%d}' % run_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x: x.split('{')[0] for x in channels
        })
        sdf['run_num'] = run_num
        adf = pd.concat([adf, sdf])
    adf = adf.reset_index()
    del adf['index']
    return adf

def trim_trajectories(df, fname,sample_param_to_keep, time_start=1, time_stop=1000,
                      time_varying_params=None, grpnames=None):
    """Generate a subset of the trajectoriesDat dataframe
    The new csv file is saved under trajectoriesDat_trim.csv, no dataframe is returned
    """

    channels = ['susceptible', 'infected', 'recovered', 'infected_cumul', 'detected_cumul',
                'asymp_cumul', 'asymp', 'asymp_det_cumul',
                'symp_mild_cumul', 'symp_mild', 'symp_mild_det_cumul',
                'symp_severe_cumul','symp_severe', 'symp_severe_det_cumul',
                'hosp_det_cumul', 'hosp_cumul', 'hosp_det', 'hospitalized',
                'crit_cumul','crit_det_cumul', 'crit_det',  'critical',
                'deaths_det_cumul', 'deaths']

    if time_varying_params == None:
        time_varying_params = ['Ki_t']

    column_list = ['time', 'run_num'] + sample_param_to_keep
    if grpnames is not None:
        for grp in grpnames:
            grp_ch = str(grp.replace('_', '-'))
            [column_list.append(f'{channel}_{str(grp_ch)}') for channel in channels]
            if grp_ch !="All" and not 'age' in grp_ch :
                [column_list.append(f'{time_varying_param}_{str(grp_ch)}') for time_varying_param in time_varying_params]
            del grp, grp_ch
        column_list = column_list + ['N_All']
    else:
        column_list = column_list + channels + time_varying_params

    """Trim df and save"""
    df = df[column_list]
    df = df[df['time'] > time_start]
    df = df[df['time'] < time_stop]
    df.to_csv(os.path.join(exp_path, fname + '_trim.csv'), index=False, date_format='%Y-%m-%d')


def combine_trajectories(sampledf, Nscenarios_start=0, Nscenarios_stop=1000, fname='trajectoriesDat.csv',SAVE=True):

    df_list = []
    n_errors = 0
    for scen_i in range(Nscenarios_start, Nscenarios_stop):
        input_name = "trajectories_scen" + str(scen_i) + ".csv"
        try:
            df_i = reprocess(os.path.join(trajectories_path, input_name))
            df_i['scen_num'] = scen_i
            df_i = df_i.merge(sampledf, on=['scen_num'])
            df_list.append(df_i)
        except:
            n_errors += 1
            continue
    print("Number of errors:" + str(n_errors))
    try:
        dfc = pd.concat(df_list)
        dfc = dfc.dropna()
        if SAVE:
            dfc.to_csv(os.path.join(exp_path, fname), index=False, date_format='%Y-%m-%d')
    except ValueError:
        print('WARNING: No objects to concatenate - either no trajectories or n_scen_limit size is too small')
        dfc = pd.DataFrame()

    return dfc

def combine_trajectories_chunks(grp_list, useTrim=True):

    """workaround for using EMS vs region in filename for spatial model and keep suffix also for 'All'"""
    grp_save_suffix = [grp for grp in grp_list[1:]][0][:3]
    if grp_save_suffix == 'EMS': grp_save_suffix = 'region'

    files = os.listdir(exp_path)
    files = [file for file in files if '.csv' in file ]
    files = [file for file in files if not grp_save_suffix in file ]
    files = [file for file in files if 'trajectories' in file]
    files_not_trim = [file for file in files if not 'trim' in file]
    files_trim = [file for file in files if 'trim' in file]
    if useTrim:
        files = files_trim
        [os.unlink(os.path.join(exp_path, file)) for file in files_not_trim]
        del files_trim,  files_not_trim
    else:
        files = files_not_trim
        [os.unlink(os.path.join(exp_path, file)) for file in files_trim]
        del files_trim,  files_not_trim

    for i, grp in enumerate(grp_list):
        print(f'Combine trajectories for {grp}')
        """extract grp suffix, might need to be applicable for age model or any other grp"""
        grp_suffix = grp[:3]
        df_all = pd.DataFrame()
        for file in files:
            df_f = pd.read_csv(os.path.join(exp_path, file))
            df_cols = df_f.columns
            outcome_cols = [df_col for df_col in df_cols if grp_suffix in df_col or 'All' in df_col ]
            outcomeVars_to_drop = [outcome_col for outcome_col in outcome_cols if not grp in outcome_col]
            outcomeVars_to_drop = [outcome_col for outcome_col in outcomeVars_to_drop if not grp.replace(f'{grp_suffix}_',f'{grp_suffix}-') in outcome_col]

            df_f = df_f.drop(outcomeVars_to_drop, axis=1)
            if df_all.empty:
                df_all = df_f
            else:
                df_all.append(df_f)
            del df_f

        fname = f'trajectoriesDat_{grp_save_suffix}_{i}'
        if useTrim: fname = f'{fname}_trim'
        df_all.to_csv(os.path.join(exp_path, f'{fname}.csv'), index=False, date_format='%Y-%m-%d')
        if i ==0:
            write_report(nscenarios_processed= len(df_all['scen_num'].unique()))
    [os.unlink(os.path.join(exp_path,file)) for file in files]

def write_report(nscenarios_processed):
    trackScen = f'Number of scenarios processed n= {str(nscenarios_processed)} out of total ' \
                f'N= {str(Nscenario)} ({str(nscenarios_processed / Nscenario)} %)'
    file = open(os.path.join(exp_path, "Simulation_report.txt"), 'w')
    file.write(trackScen)
    file.close()

if __name__ == '__main__':

    args = parse_args()  
    exp_name = args.exp_name
    time_start = args.time_start
    time_stop = args.time_stop
    Location = args.Location
    additional_sample_param = args.additional_sample_param
    Scenario_save_limit = args.scen_limit

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)
    sim_out_dir = os.path.join(wdir, "simulation_output")
    if not os.path.exists(os.path.join(sim_out_dir,exp_name)):
        sim_out_dir = os.path.join(git_dir, "_temp")
    print(f'Processing trajectories from {sim_out_dir}')

    exp_path = os.path.join(sim_out_dir, exp_name)
    trajectories_path = os.path.join(exp_path, 'trajectories')

    """Define model type and grp suffix of parameters and outcome channels"""
    sampledf = pd.read_csv(os.path.join(exp_path, "sampled_parameters.csv"))
    N_cols = [col for col in sampledf.columns if 'N_' in col]
    if len(N_cols)!=0:
        grp_list = ['All'] + [col.replace('N_','') for col in N_cols]
        grp_suffix = grp_list[0][:3]
    else:
        grp_list = None
        N_cols = ['speciesS', 'initialAs']

    """Define parameters to keep"""
    sample_param_to_keep = ['startdate', 'scen_num', 'sample_num'] + N_cols
    if isinstance(additional_sample_param, list): sample_param_to_keep = sample_param_to_keep + additional_sample_param

    try:
        sampledf = pd.read_csv(os.path.join(exp_path, "sampled_parameters.csv"), usecols= sample_param_to_keep)
    except:
        """when running from input csv sample_num might be missing"""
        sample_param_to_keep = ['startdate', 'scen_num'] + N_cols
        if isinstance(additional_sample_param, list): sample_param_to_keep = sample_param_to_keep + additional_sample_param
        sampledf = pd.read_csv(os.path.join(exp_path, "sampled_parameters.csv"), usecols= sample_param_to_keep)
        sample_param_to_keep = sample_param_to_keep + ['sample_num']
        sampledf['sample_num'] = 0
    Nscenario = max(sampledf['scen_num'])

    if Nscenario <= Scenario_save_limit:
        fname = "trajectoriesDat.csv"
        if not os.path.exists(os.path.join(exp_path, fname)):
            dfc = combine_trajectories(sampledf=sampledf,
                                       Nscenarios_start=0,
                                       Nscenarios_stop=Nscenario + 1,
                                       fname=fname)
        else:
            dfc = pd.read_csv(os.path.join(exp_path, fname))

        """Update group names"""
        grp_list, grp_suffix,grp_numbers = get_group_names(exp_path=exp_path)
        trim_trajectories(df=dfc,
                          sample_param_to_keep = sample_param_to_keep,
                          time_start=time_start,
                          time_stop=time_stop,
                          grpnames = grp_list ,
                          fname=fname.split(".csv")[0])

        write_report(nscenarios_processed= len(dfc['scen_num'].unique()))

    if Nscenario > Scenario_save_limit:
        n_subsets = int(Nscenario/Scenario_save_limit)

        """Combine trajectories in specified chunks for n subsets"""
        for i in range(1,n_subsets+2):
            if i ==1 : Nscenario_stop=Scenario_save_limit
            if i > 1 : Nscenario_stop = Nscenario_stop + Scenario_save_limit
            print(Nscenario_stop)
            Nscenarios_start = Nscenario_stop-Scenario_save_limit
            fname = 'trajectoriesDat_'+str(Nscenario_stop)+'.csv'
            if not os.path.exists(os.path.join(exp_path, fname)):
                dfc = combine_trajectories(sampledf=sampledf,
                                           Nscenarios_start=Nscenarios_start,
                                           Nscenarios_stop=Nscenario_stop,
                                           fname=fname)
            else:
                dfc = pd.read_csv(os.path.join(exp_path, fname))

            """Trim trajectories"""
            if not dfc.empty:
                trim_trajectories(df=dfc,
                                  sample_param_to_keep=sample_param_to_keep,
                                  time_start=time_start,
                                  time_stop=time_stop,
                                  grpnames=grp_list,
                                  fname=fname.split(".csv")[0])
                del dfc
            else:
                print(f'WARNING: No trajectories found for scenarios {Nscenarios_start} to {Nscenario_stop}')
                continue

        """Combine trajectory scenario batches per grp, 
        if grpList not specified default to spatial (EMS) model,
        deletes the trajectory chunks when done"""
        combine_trajectories_chunks(grp_list= grp_list)

    if args.delete_trajectories:
        """THIS WILL DELETE ALL SINGLE TRAJECTORIES!"""
        shutil.rmtree(trajectories_path, ignore_errors=True)
        print(f'Single trajectories deleted')

    """ Start parallel rt estimation per trajectory """
    # FIXME permission denied
    #if Location == "NUCLUSTER" :
    #    exp_dir = os.path.join(sim_out_dir, exp_name)
    #    p = os.path.join(exp_dir, 'submit_runRtEstimation_trajectories.sh')
    #    subprocess.call([p])