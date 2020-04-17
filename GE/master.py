
"""
###project structure###    *= optional

run scenerios:
    emodl_generation(arg):
        if arg=='age':
            run x_emodl_gen
            ...
    *config_generation(arg):
        ...
    run emodl *scenerios of different subsamples/Ki
    combine trajectories
    *preliminary plotting for QC
    

Potential intermediate processing
    *handle datastructures for age/locale -> longformat by group
            for age groups could look like Ki_{}_{}: ie  Ki_{agegrp1}_{agegrp2}  (contact between agegrp1 and agegrp2)
    *Fitting -> might be recursive with run_scenerios
    *interventions (could maybe be done in run scenerios)    
        pick multiple Ki values and compare across Ki_{intervention} groups  (product of contact rate and transmission proba)
        can show effect of different interventions. 
    *...
    
post-processing:
    calculate incidence
    saves files
        trajectoriesDat
        trajectoriesDat_withIncidence ** this is the main file to use going forward

analysis:
    plotting
    *?

"""

import os
import sys
import numpy as np
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import itertools
from scipy.interpolate import interp1d #for linear least squares fitting
from load_paths import load_box_paths
mpl.rcParams['pdf.fonttype'] = 42


##directories and system path appending
user_path = os.path.expanduser('~')
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

sim_output_path = os.path.join(wdir, 'sample_trajectories')
plot_path = os.path.join(wdir, 'sample_plots')

sys.path.append(git_dir)
sys.path.append(os.path.join(git_dir, '{}/'.format(param.modeltype))) ##note this will change for each type of model. need to make this a param



## importing parameters from parameters.py
import parameters as param
# may need to append the folder with parameters.py to system path if not able to load:  sys.path.append('/Users/geickelb1/Documents/GitHub/covid-chicago/')

### notebook 
testMode = param.testMode
modeltype= param.modeltype

first_date = param.first_date
Kivalues =  param.Kivalues


### designating output paths
if testMode == True :
    sim_output_path = os.path.join(wdir, 'sample_trajectories')
    plot_path = os.path.join(wdir, 'sample_plots')
else :
    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = sim_output_path

if not os.path.exists(sim_output_path):
    os.makedirs(sim_output_path)

if not os.path.exists(plot_path):
    os.makedirs(plot_path)

### designating channel lists 
master_channel_list = param.master_channel_list
detection_channel_list = param.detection_channel_list
custom_channel_list = param.custom_channel_list




### defining some analysis functions

def CI_5(x) :
    return np.percentile(x, 5)

def CI_95(x) :
    return np.percentile(x, 95)

def CI_25(x) :
    return np.percentile(x, 25)

def CI_75(x) :
    return np.percentile(x, 75)


