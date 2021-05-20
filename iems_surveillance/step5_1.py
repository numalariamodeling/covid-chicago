#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 20:08:05 2021

@author: jiayigu
"""
import pandas as pd
import os
import sys
import re
import os.path


def DateToTimestep(date, startdate = pd.Timestamp('2020-02-13')):
        enddate = pd.Timestamp(date)
        datediff = enddate - startdate
        timestep = datediff.days
        return timestep


def create_mitigation_df(path):
    #Rt_df = pd.read_csv('step5_input.csv')
    Rt_df = pd.read_csv(os.path.join('../../projects','covid_chicago', 'cms_sim','simulation_output', path, 'step5_input.csv'))
    Rt_series = list(Rt_df['R_mean'].values)
    Dates = list(Rt_df['date'].values)
    mitigation_list = []
    mitigation = ''
    if Rt_series[250]>0.5:
        print('mitigation')
        mitigation_date = DateToTimestep(Dates[250])+4
        mitigation_list.append([mitigation_date, 0.07])
        mitigation_list.append([mitigation_date, 0.05])
        mitigation_list.append([mitigation_date, 0.09])
        mitigation_df = pd.DataFrame(mitigation_list, columns = ['Date', 'ki_reset'])
        # combine  to create sample parameter mitigation csv
        parameters_df = pd.read_csv(os.path.join('../experiment_configs', 'input_csv','sampled_parameters_single.csv'))
        df = pd.DataFrame()
        df = df.append([parameters_df]*3,ignore_index = True)
        df['sample_num'] = df.index+1
        df['scen_num'] = df.index+1
        df['mitigation_ki'] = mitigation_df['ki_reset']
        df['mitigation_time'] = mitigation_df['Date']
        mitigation = 'mitigation'
        # out put new sample mitigation!!!!!
        df.to_csv(os.path.join('../experiment_configs', 'input_csv','sampled_parameters_mitigation.csv'),index=False)
    else:
        mitigation = 'no mitigation'
    return mitigation

if __name__ == '__main__':
    # Map command line arguments to function arguments.
    create_mitigation_df(*sys.argv[1:])
