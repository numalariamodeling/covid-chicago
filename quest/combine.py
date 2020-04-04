import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def reprocess(input_fname='trajectories.csv', output_fname=None):
    fname = os.path.join(git_dir, input_fname)
    row_df = pd.read_csv(fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    num_channels = len([x for x in df.columns.values if '{0}' in x])
    num_samples = int((len(row_df) - 1) / num_channels)
    df = df.reset_index(drop=False)
    df = df.rename(columns={'index': 'time'})
    df['time'] = df['time'].astype(float)
    adf = pd.DataFrame()
    for sample_num in range(num_samples):
        channels = [x for x in df.columns.values if '{%d}' % sample_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x: x.split('{')[0] for x in channels
        })
        sdf['sample_num'] = sample_num
        adf = pd.concat([adf, sdf])
    adf = adf.reset_index()
    del adf['index']
    return adf


def combineTrajectories(Nscenarios):
    scendf = pd.read_csv(os.path.join(temp_exp_dir,"scenarios.csv"))
    df_list = []
    for scen_i in range(1, Nscenarios):
        input_name = "trajectories_scen" + str(scen_i) + ".csv"
        try:
            df_i = reprocess(input_name)
            df_i['scen_num'] = scen_i
            df_i = df_i.merge(scendf, on=['scen_num','sample_num'])
            df_list.append(df_i)
        except:
            continue
    dfc = pd.concat(df_list)
    dfc.to_csv( os.path.join(temp_exp_dir,"trajectoriesDat.csv"))
    return dfc
	
#git_dir ="/home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/20200403_cobeyModel_TimeEvent_scalingFactors_rn80/"
git_dir ="/home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/20200403_cobeyModel_TimeEvent_randomSampling_rn35/"
temp_exp_dir  = git_dir
nscen =1000
combineTrajectories(nscen)