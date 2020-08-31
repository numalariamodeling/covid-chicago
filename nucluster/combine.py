import numpy as np
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import shutil


import numpy as np

def writeTxt(txtdir, filename, textstring) :
    file = open(os.path.join(txtdir, filename), 'w')
    file.write(textstring)
    file.close()
   
   
def reprocess(input_fname='trajectories.csv', output_fname=None):
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
    
    

sim_out_dir = "/projects/p30781/covidproject/covid-chicago/_temp/"



stem = "20200525_EMS_11"
exp_names = [x for x in os.listdir(sim_out_dir) if stem in x]


for exp_name in exp_names :
  print(exp_name)
  git_dir =os.path.join(sim_out_dir, exp_name)
  trajectoriesDat = os.path.join(git_dir,'trajectories' ) 
  temp_exp_dir  = git_dir
  Nscenarios =10000
  sampledf = pd.read_csv(os.path.join(temp_exp_dir,"sampled_parameters.csv"))
  df_list = []
  n_errors = 0
  for scen_i in range(Nscenarios):
     input_name = "trajectories_scen" + str(scen_i) + ".csv"
     try:
         df_i = reprocess(os.path.join(trajectoriesDat,input_name))
         df_i['scen_num'] = scen_i
         #print("df_length " + str(len(df_i))) 
         df_i = df_i.merge(sampledf, on=['scen_num'])
         #print("df_length " + str(len(df_i)))
         df_list.append(df_i)
     except:
         n_errors += 1
         continue
  print("Number of errors:" + str(n_errors))
  try:
       dfc = pd.concat(df_list)
       dfc.to_csv( os.path.join(temp_exp_dir,"trajectoriesDat.csv"), index=False)
  except:
       continue
       
   
   