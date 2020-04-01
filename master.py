
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

##directories
user_path = os.path.expanduser('~')
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

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


### emodl_generation/editing

def read_group_dictionary(filename='county_dic.csv',grpname ='county', Testmode=True, ngroups=2):
    grp_dic = {}
    with open(os.path.join(git_dir, filename)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            grp_dic[row[grpname]] = [int(x) for x in row['val_list'].strip('][').split(', ')]

    if Testmode == True:
        grp_dic = {k: grp_dic[k] for k in sorted(grp_dic.keys())[:ngroups]}

    return grp_dic

#**** only if group used****
from emodl_generator_extended import read_group_dictionary
group_dic= read_group_dictionary(filename='county_dic.csv',grpname ='county', Testmode=True, ngroups=2)
#*****

from locale_emodl_generator import generate_locale_emodl, generate_locale_cfg

generate_locale_emodl(county_dic, param_dic,file_output, verbose=False)

