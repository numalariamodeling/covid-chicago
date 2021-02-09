import argparse
import numpy as np
import pandas as pd
import subprocess
import sys 
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
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
        "-delsim",
        "--delete_simsfiles",
        type=str,
        help="Delete single emodl simulation files"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default = "NUCLUSTER"
    )

    return parser.parse_args()
    
def cleanup(temp_dir, temp_exp_dir, sim_output_path, delete_temp_dir=True) :
    # Delete simulation model and emodl files
    # But keeps per default the trajectories, better solution, zip folders and copy
    if delete_temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print('temp_dir folder deleted')
    shutil.copytree(temp_exp_dir, sim_output_path)
    # Delete files after being copied to the project folder
    if os.path.exists(sim_output_path):
        shutil.rmtree(temp_exp_dir, ignore_errors=True)
    elif not os.path.exists(sim_output_path):
        print('Sim_output_path does not exists')

    
if __name__ == '__main__':
  args = parse_args()  
  stem = args.stem
  
  Location = args.Location
  datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)
  sim_out_dir = os.path.join(git_dir, "_temp")
  
  delete_temp_dir=False
  if args.delete_simsfiles == "True" : 
      delete_temp_dir = True
   
  exp_names = [x for x in os.listdir(sim_out_dir) if stem in x]
  for exp_name in exp_names :
    print(exp_name)
    temp_exp_dir =os.path.join(sim_out_dir, exp_name)
    temp_dir =os.path.join(sim_out_dir, exp_name, 'simulations')
    simulation_output = os.path.join(wdir, "simulation_output",exp_name)
    trajectories_dir = os.path.join(temp_exp_dir,'trajectories' ) 
    
    cleanup(temp_dir= temp_dir,temp_exp_dir=temp_exp_dir,sim_output_path=simulation_output, delete_temp_dir=delete_temp_dir)
    