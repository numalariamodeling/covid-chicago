import argparse
import subprocess
import sys
import os
import shutil

sys.path.append('../')
from load_paths import load_box_paths


def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-stem",
        "--stem",
        type=str,
        help="Name of simulation experiment"
    )

    parser.add_argument(
        "-keepsim",
        "--keep_simsfiles",
        action='store_true',
        help="Delete single emodl simulation files"
    )

    parser.add_argument(
        "-keeptraj",
        "--keep_single_trajectories",
        action='store_true',
        help="Delete single emodl simulation files"
    )

    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default="Local"
    )

    return parser.parse_args()


def cleanup(exp_name, sim_out_dir, wdir, keep_simsfiles=False, keep_single_trajectories=False):
    temp_dir = os.path.join(sim_out_dir, exp_name, 'simulations')

    temp_exp_dir = os.path.join(sim_out_dir, exp_name)
    sim_output_path = os.path.join(wdir, "simulation_output", exp_name)
    trajectories_dir = os.path.join(temp_exp_dir, 'trajectories')


    """ Copy trajectory log files """
    shutil.copytree(os.path.join(trajectories_dir, 'log'), os.path.join(temp_exp_dir, 'log', 'trajectories_log'))

    """ Delete simulation model and emodl files """
    if not keep_simsfiles:
        if os.path.exists(temp_dir):
            print(f'WARNING (cleanup) deleting {temp_dir}')
            ### FIXME: time.sleep(5) - need to add time module to py environment
            shutil.rmtree(temp_dir, ignore_errors=True)
        else :
            print(f'{temp_dir} does not exist or already removed')

    if not keep_single_trajectories:
        if os.path.exists(trajectories_dir):
            print(f'WARNING (cleanup) deleting {trajectories_dir}')
            ### FIXME: time.sleep(5) - need to add time module to py environment
            shutil.rmtree(trajectories_dir, ignore_errors=True)
        else :
            print(f'{trajectories_dir} does not exist or already removed')

    """ for large simulations trajectores are written out per chunk or region
    i.e. trajectoriesDat_11.csv or trajectoriesDat_300.csv 
    Therefore searching for any trajectoriesDat file"""
    csvfiles = [f for f in os.listdir(temp_exp_dir) if '.csv' in f]
    n_traj_files = len([f for f in csvfiles if 'trajectoriesDat' in f])
    if n_traj_files > 0:
        shutil.copytree(temp_exp_dir, sim_output_path)

    """ Delete files after being copied to the project folder"""
    if os.path.exists(sim_output_path):
        print(f'Clean up SUCCESSFUL, files copied to {sim_output_path}')
        shutil.rmtree(temp_exp_dir, ignore_errors=True)
    elif not os.path.exists(sim_output_path):
        print(f'{sim_output_path} does not exists, please check your _temp folder')


if __name__ == '__main__':
    args = parse_args()
    stem = args.stem

    Location = args.Location
    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)
    sim_out_dir = os.path.join(git_dir, "_temp")

    exp_names = [x for x in os.listdir(sim_out_dir) if stem in x]
    for exp_name in exp_names:
        print(exp_name)

        cleanup(exp_name, sim_out_dir, wdir, keep_simsfiles=args.keep_simsfiles,
                keep_single_trajectories=args.keep_single_trajectories)
