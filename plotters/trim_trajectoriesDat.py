import os
import pandas as pd
import sys
sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def trim_trajectories_Dat(exp_name, keepvars, keepTimes=None) :
    """Generate a subset of the trajectoriesDat dataframe
    The new csv file is saved under trajectoriesDat_trim.csv, no dataframe is returned
    Parameters
    ----------
    exp_name : str - name of the experiment
    keepvars : list - column names to keep
    keepTimes : int - minimum timestep to keep (all values below are discarded)
    """

    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))

    df = df[keepvars]

    if keepTimes is not None :
        df = df[df['time']>=int(keepTimes)]

    df.to_csv(os.path.join(sim_output_path, 'trajectoriesDat_trim.csv'), index=False)

if __name__ == '__main__':
    #stem = sys.argv[1]
    stem = "20200805"
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    #exp_name = "20200805_IL_rollback_Sep30"

    keepvars = ['time','startdate','scen_num','run_num','sample_num','reopening_multiplier_4']
    keepvars = keepvars + [x for x in df.columns.values if 'EMS-' in x]
    keepvars = keepvars + [x for x in df.columns.values if 'All' in x]

    for exp_name in exp_names:
        trim_trajectories_Dat(exp_name=exp_name, keepvars=keepvars, keepTimes=120)
