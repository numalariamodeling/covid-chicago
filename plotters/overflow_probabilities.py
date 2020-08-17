import os
import sys
sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *

import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
import numpy as np
import matplotlib.dates as mdates
import datetime
#sns.set(color_codes=True)
import matplotlib as mpl
mpl.rcParams['pdf.fonttype'] = 42
import statistics as st
sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
from statsmodels.distributions.empirical_distribution import ECDF
import scipy
import gc
import sys


datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()

def load_sim_data(exp_name, input_wdir=None, input_sim_output_path=None, column_list=None):
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'), usecols=column_list)
    return df


def exceeds(trajectory, metric, lower_limit, upper_limit, maximum):
    return (trajectory[metric].values[lower_limit:upper_limit] > maximum).any()

def when_exceeds(trajectory, metric, lower_limit, upper_limit, maximum):
    ii = lower_limit
    while trajectory[metric].values[ii] <= maximum:
        ii += 1
    return ii

column_list = ['scen_num', 'reopening_multiplier_4', 'hospitalized_det_All', 'crit_det_All']
for ems_region in range(1,12):
    column_list.append('hospitalized_det_EMS-' + str(ems_region))
    column_list.append('crit_det_EMS-' + str(ems_region))
    #column_list.append('death_det_cumul_EMS-' + str(ems_region))
    
    
def get_probs(exp_name):    
    trajectories = load_sim_data(exp_name, column_list=column_list) #pd.read_csv('trajectoriesDat_200814_1.csv', usecols=column_list)
    capacity = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'capacity_by_covid_region.csv'))

    for ems_region in range(1,12):
        trajectories['total_hosp_census_EMS-' + str(ems_region)] = trajectories['hospitalized_det_EMS-'+str(ems_region)]+trajectories['crit_det_EMS-'+str(ems_region)]


    #capacity = pd.read_csv('capacity_by_covid_region.csv')
    capacity = capacity[capacity['geography_level'] == 'covid region']
    capacity['date'] = pd.to_datetime(capacity['date'])
    icu_available = []
    hb_available = []
    for region in range(1,12):

        cap = capacity[(capacity['geography_name'] == str(region)) & (capacity['date'].dt.dayofweek < 5)].sort_values('date').reset_index()

        cap['icu_covid_avail'] = cap['icu_total'] - cap['icu_noncovid']
        icu_available.append(np.mean(cap['icu_covid_avail'].values[-10:]))
        cap['beds_covid_avail'] = cap['hb_total'] - cap['hb_noncovid']
        hb_available.append(np.mean(cap['beds_covid_avail'].values[-10:]))

    ### Measure from tomorrow:
    lower_limit = (dt.datetime.today() - dt.datetime(month=2, day=13, year=2020)).days + 1
    ### Measure from today (uncomment):
    #lower_limit = (dt.datetime.today() - dt.datetime(month=2, day=13, year=2020)).days
    ### Measure from a week from now (uncomment):
    #lower_limit = (dt.datetime.today() - dt.datetime(month=2, day=13, year=2020)).days + 7

    probabilities = []
    days_array = [7,14,21,28,30,60,90]
    percents = [75,100]
    bed_types = ['icu', 'hb']
    unique_scen = np.array(list(set(trajectories['scen_num'].values)))
    n_scenarios = len(unique_scen)
    for region in range(1,12):
        region_prob = [0]*len(days_array)*len(percents)*len(bed_types)
        column_list_output = []
        for scen in unique_scen:
            new = trajectories[(trajectories['scen_num'] == scen)].reset_index()
            ii = 0
            for bed_type in bed_types:
                for percent in percents:
                    if bed_type == 'icu':
                        capacity = round(0.01*percent*icu_available[region-1])
                        metric = 'crit_det_EMS-' + str(region)
                    if bed_type == 'hb':
                        capacity = round(0.01*percent*hb_available[region-1])
                        metric = 'total_hosp_census_EMS-' + str(region)
                    for day_num in days_array:
                        if exceeds(new, metric, lower_limit, lower_limit+day_num, capacity):
                            region_prob[ii] += 1
                        ii += 1
                        column_list_output.append('p_' + bed_type + '_overflow_' + str(percent) + '_next' + str(day_num))
        probabilities.append(region_prob)
    probabilities = np.array(probabilities)/len(unique_scen)

    output = pd.DataFrame()#pd.DataFrame(probabilities).rename(get_name, axis='columns')
    output['region'] = range(1,12)
    output['icu_available'] = np.round(icu_available)
    output['hb_available'] = np.round(hb_available)
    
    def get_name(ii):
        return column_list_output[ii]

    prob_output = pd.DataFrame(probabilities).rename(get_name, axis='columns')
    prob_output['region'] = range(1,12)
    true_output = pd.merge(output, prob_output)
    #true_output = output[['region', 'icu_available', 'hb_available', 'p_icu_overflow_75_next30', 'p_icu_overflow_75_next60', 'p_hosp_overflow_75_next30', 'p_hosp_overflow_75_next60']]

    true_output.to_csv(os.path.join(wdir, 'simulation_output', exp_name, 'overflow_probabilities.csv'), index=False)
    
if __name__ == '__main__':
    stem = sys.argv[1]
    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]

    for exp_name in exp_names:
        get_probs(exp_name)