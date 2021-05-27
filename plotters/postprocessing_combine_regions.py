import argparse
import numpy as np
import os
import sys
import shutil
import pandas as pd

sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import load_sim_data, get_group_names

try:
    print(Location)
except NameError:
    if os.name == "posix":
        Location = "NUCLUSTER"
    else:
        Location = "Local"

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)


def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "-s",
        "--stem",
        type=str,
        help="Name of pattern that occurs uniquely in the simulations that should be combined"
    )
    return parser.parse_args()


def copy_traces(exp_names):
    for exp_name in exp_names:
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)

        grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=sim_output_path)
        for grp in grp_numbers:
            csv_load_name = os.path.join(sim_output_path, f'traces_ranked_region_{grp}.csv')
            csv_save_name = os.path.join(sim_output_path_new, f'traces_ranked_region_{grp}.csv')
            shutil.copy(csv_load_name, csv_save_name)


def copy_and_rename_trajectories(exp_names):
    for exp_name in exp_names:
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)

        grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=sim_output_path)
        if grp_suffix == 'EMS':
            grp_save_suffix = 'region'

        if "sub" in exp_name:
            print("todo")
            # read and split
        if "localeEMS" in exp_name:
            grp = exp_name.split("_")[3]
            csv_load_name = os.path.join(sim_output_path, f'trajectoriesDat.csv')
            csv_save_name = os.path.join(sim_output_path_new, f'trajectoriesDat_{grp_save_suffix}_{grp}.csv')
            shutil.copy(csv_load_name, csv_save_name)


def trajectories_All(exp_name_new):
    """trajectories for all IL"""

    pattern  =  'trajectoriesDat_region'
    files = os.listdir(sim_output_path_new)
    trajectories = [x.replace(f'{pattern}_','') for x in files if pattern in x]
    grp_numbers = [int(x.replace('.csv','')) for x in trajectories]

    if len(grp_numbers)<11:
        print(f'Warning number of single trajectories csvs <11 (only {len(grp_numbers)} found) '
              f'trajectoriesDat_region_0.csv not generated')
    else:
        dfAll = pd.DataFrame()
        for grp in grp_numbers:
            region_suffix = f'_EMS-{str(grp)}'
            df = load_sim_data(exp_name_new, region_suffix=region_suffix )

            """Scen_num and sample_num wont be the same across regions"""
            df['sample_num'] = df.groupby(['time']).cumcount() + 1
            df['scen_num'] = df.groupby(['time']).cumcount() + 1
            dfAll = pd.concat([dfAll, df])

        """Get all IL"""
        grp_channels = ['time', 'startdate', 'sample_num', 'scen_num', 'date', 'run_num']
        # channels = [ch for ch in dfAll.columns if ch not in  grp_channels]

        """Use f"""
        trajectories_cols = pd.read_csv(os.path.join(sim_output_path_new, f'trajectoriesDat_region_{grp_numbers[0]}.csv'),
                                        index_col=0, nrows=0).columns.tolist()
        channels = [col for col in trajectories_cols if '_EMS-' in col]
        channels = [col.replace(f'_EMS-{grp_numbers[0]}', "") for col in channels if not '_t_' in col]

        dfIL = dfAll.groupby(grp_channels)[channels].agg(np.sum).reset_index()
        for col in channels:
            dfIL.rename(columns={col: f'{col}_All'}, inplace=True)

        dfIL.to_csv(os.path.join(sim_output_path_new, f'trajectoriesDat_region_0.csv'), index=False, date_format='%Y-%m-%d')


def combine_rtNU(exp_names):
    csv_name = 'rtNU.csv'
    region_channel = 'geography_modeled'
    channels = ['rt_median', 'rt_lower', 'rt_upper']

    dfAll = pd.DataFrame()
    for exp_name in exp_names:
        print(exp_name)
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        df = pd.read_csv(os.path.join(sim_output_path, csv_name))
        dfAll = pd.concat([dfAll, df])
        del df

    if len(dfAll['model_date'].unique()) > 1:
        dfAll['model_date'] = dfAll['model_date'].unique()[0]

    """Get all IL"""
    # better to recalculate using trajectoriesDat_region_0.csv, here using mean across regions
    grp_channels = ['model_date', 'date',  'rt_pre_aggr']
    dfIL = dfAll.groupby(grp_channels)[channels].agg(np.mean).reset_index()
    dfIL[region_channel] = 'illinois'
    dfIL = dfIL[dfAll.columns]
    dfAll = pd.concat([dfAll, dfIL])
    print(f'N regions in combined df= {len(dfAll[region_channel].unique())}')
    dfAll.to_csv(os.path.join(sim_output_path_new, csv_name), index=False, date_format='%Y-%m-%d')


def combine_hospitaloverflow(exp_names):
    region_channel = 'geography_modeled'
    grp_channels = ['date_capacity_run', 'resource_type', 'scenario_name', 'date_window_upper_bound',
                    'overflow_threshold_percent']
    dfAll = pd.DataFrame()
    for exp_name in exp_names:
        simdate = exp_name.split("_")[0]
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=sim_output_path)
        geographies = [grp.replace("EMS-","covidregion_") for grp in grp_list  ]
        csv_name = f'nu_hospitaloverflow_{simdate}.csv'
        df = pd.read_csv(os.path.join(sim_output_path, csv_name))
        df = df.loc[df['geography_modeled'].isin(geographies)]
        dfAll = pd.concat([dfAll, df])
        del df

    """Get all IL"""
    # TODO better to recalculate, here using sum and mean across regions
    dfIL = dfAll.groupby(grp_channels).agg(
        {'avg_resource_available': np.sum, 'percent_of_simulations_that_exceed': np.mean}).reset_index()
    dfIL[region_channel] = 'illinois'
    dfIL = dfIL[dfAll.columns]
    dfAll = pd.concat([dfAll, dfIL])
    print(f'N regions in combined df= {len(dfAll[region_channel].unique())}')
    dfAll.to_csv(os.path.join(sim_output_path_new, csv_name), index=False, date_format='%Y-%m-%d')


def combine_civis_csv(exp_names):
    region_channel = 'geography_modeled'
    grp_channels = ['date', 'scenario_name']

    dfAll = pd.DataFrame()
    for exp_name in exp_names:
        print(exp_name)
        simdate = exp_name.split("_")[0]
        csv_name = f'nu_{simdate}.csv'
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        df = pd.read_csv(os.path.join(sim_output_path, csv_name))
        if 'rt_median' in df.columns:
            df = df.drop(['rt_median', 'rt_lower', 'rt_upper', 'rt_pre_aggr', 'model_date'], axis=1)
        dfAll = pd.concat([dfAll, df])
        del df

    """Get all IL"""
    channels = [ch for ch in dfAll.columns if ch not in grp_channels and ch not in region_channel]
    dfIL = dfAll.groupby(grp_channels)[channels].agg(np.sum).reset_index()
    dfIL[region_channel] = 'illinois'
    dfIL = dfIL[dfAll.columns]
    dfAll = pd.concat([dfAll, dfIL])

    if os.path.exists(os.path.join(sim_output_path_new, 'rtNU.csv')):
        #dfAll = pd.read_csv(os.path.join(sim_output_path_new, f'nu_{simdate}.csv'))
        dfAll['date'] = pd.to_datetime(dfAll['date'])
        df_rt_all = pd.read_csv(os.path.join(sim_output_path_new,  'rtNU.csv'))
        df_rt_all['date'] = pd.to_datetime(df_rt_all['date'])

        dfAll = pd.merge(how='left', left=dfAll, right=df_rt_all,
                              left_on=['date', 'geography_modeled'],
                              right_on=['date', 'geography_modeled'])

    print(f'N regions in combined df= {len(dfAll[region_channel].unique())}')
    dfAll.to_csv(os.path.join(sim_output_path_new,  f'nu_{simdate}.csv'), index=False, date_format='%Y-%m-%d')


def copy_regional_plots(exp_names):
    for exp_name in exp_names:
        plot_path = os.path.join(wdir, 'simulation_output', exp_name, '_plots')

        filelist = [f for f in os.listdir(os.path.join(plot_path)) if f.endswith('.png')]
        filelist = [f for f in filelist if "covidregion_" in f or  "EMS-" in f]
        filelist = [f for f in filelist if "rt_" not in f ]
        for file in filelist:
            shutil.copyfile(os.path.join(plot_path, file), os.path.join(plot_path_new, file))


def replace_stem(submission_file):
    fin = open(submission_file, "rt")
    txt = fin.read()
    fin.close()
    txt = txt.replace(f'{exp_names[0]}', f'{exp_name_new}')
    fin = open(submission_file, "w")
    fin.write(txt)
    fin.close()

def copy_submission_files():
    filelist = [f for f in os.listdir(os.path.join(wdir, 'simulation_output', exp_names[0], 'sh')) if f.endswith('.sh')]
    for file in filelist:
        shutil.copyfile(os.path.join(wdir, 'simulation_output', exp_names[0], 'sh', file), os.path.join(sim_output_path_new, 'sh', file))
        replace_stem(submission_file=os.path.join(sim_output_path_new, 'sh', file))

    filelist = [f for f in os.listdir(os.path.join(wdir, 'simulation_output', exp_names[0])) if f.endswith('.sh')]
    for file in filelist:
        shutil.copyfile(os.path.join(wdir, 'simulation_output', exp_names[0], file), os.path.join(sim_output_path_new, file))
        replace_stem(submission_file=os.path.join(sim_output_path_new, file))

    filelist = [f for f in os.listdir(os.path.join(wdir, 'simulation_output', exp_names[0], 'bat')) if  f.endswith('.bat')]
    for file in filelist:
        shutil.copyfile(os.path.join(wdir, 'simulation_output', exp_names[0], 'bat', file), os.path.join(sim_output_path_new, 'bat', file))
        replace_stem(submission_file=os.path.join(sim_output_path_new, 'bat', file))

if __name__ == '__main__':

    args = parse_args()
    custom_exp_names = True
    if custom_exp_names:
        exp_name_new = '20210527_IL_ae_combined_bvariant_vaccine'
        exp_names = ['20210526_IL_localeEMS_1_ae_v4_bvariant_vaccine',
                     '20210527_IL_localeEMS_2_ae_v5_bvariant_vaccine',
                     '20210527_IL_localeEMS_3_ae_v4_bvariant_vaccine',
                     '20210526_IL_localeEMS_4_ae_v1_bvariant_vaccine',
                     '20210526_IL_localeEMS_5_ae_v2_bvariant_vaccine',
                     '20210526_IL_localeEMS_6_ae_v2_bvariant_vaccine',
                     '20210527_IL_localeEMS_7_ae_v5_bvariant_vaccine',
                     '20210527_IL_localeEMS_8_ae_v3_bvariant_vaccine',
                     '20210527_IL_localeEMS_9_ae_v3_bvariant_vaccine',
                     '20210526_IL_localeEMS_10_ae_v1_bvariant_vaccine',
                     '20210527_IL_localeEMS_11_ae_v3_bvariant_vaccine']
    else:
        stem = args.stem
        exp_name_new = f'{stem}_combined'
        exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
        exp_names = [x for x in exp_names if 'zip' not in x]  ### exclude zips
        exp_names = [x for x in exp_names if '_combined' not in x]  ### _combined should not be used in simulation names


    sim_output_path_new = os.path.join(wdir, 'simulation_output', exp_name_new)
    plot_path_new = os.path.join(sim_output_path_new, '_plots')

    if not os.path.exists(sim_output_path_new):
        os.makedirs(sim_output_path_new)
        os.makedirs(plot_path_new)
        os.makedirs(os.path.join(plot_path_new, 'pdf'))
        os.makedirs(os.path.join(sim_output_path_new, 'sh'))
        os.makedirs(os.path.join(sim_output_path_new, 'sh', 'log'))
        os.makedirs(os.path.join(sim_output_path_new, 'bat'))

    """Move sh or bat files"""
    print("Running copy_submission_files")
    copy_submission_files()

    print("Running copy_traces")
    copy_traces(exp_names)
    try:
        print("Running copy_and_rename_trajectories")
        copy_and_rename_trajectories(exp_names)
        print("Generating trajectories_All")
        trajectories_All(exp_name_new)
    except:
        print("Error check trajectories")

    print("Running combine_rtNU")
    combine_rtNU(exp_names)
    print("Running combine_hospitaloverflow")
    combine_hospitaloverflow(exp_names)
    print("Running combine_civis_csv")
    combine_civis_csv(exp_names)
    print("Running copy_regional_plots")
    copy_regional_plots(exp_names)

