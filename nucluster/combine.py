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
from datetime import date, timedelta
import shutil

#from load_paths import load_box_paths
#datapath, projectpath, WDIR, EXE_DIR, GIT_DIR = load_box_paths()

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
        "-add",
        "--addsamples",
        type=str,
        help="Merge with sample parameters",
        choices=['True', 'False'],
        default='True',
    )
    
    parser.add_argument(
        "-lagtime_days",
        "--lagtime_days",
        type=str,
        help="Time to keep before 'today'",
        default='15'
    )
    
    return parser.parse_args()
    
def writeTxt(txtdir, filename, textstring) :
    file = open(os.path.join(txtdir, filename), 'w')
    file.write(textstring)
    file.close()
   
   
def reprocess(input_fname='trajectories.csv', output_fname=None):
    fname = os.path.join(temp_exp_dir, input_fname)
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
 
 
def combineTrajectories(Nscenarios,trajectories_dir, temp_exp_dir, deleteFiles=False,addSamples = True):
    sampledf = pd.read_csv(os.path.join(temp_exp_dir,"sampled_parameters.csv"))
    if addSamples == False:
        sampledf = sampledf[["scen_num", "sample_num","startdate"]]
    df_list = []
    for scen_i in range(Nscenarios+1):
        input_name = "trajectories_scen" + str(scen_i) + ".csv"
        try:
            df_i = reprocess(os.path.join(trajectories_dir,input_name))
            df_i['scen_num'] = scen_i
            df_i = df_i.merge(sampledf, on=['scen_num'])
            df_list.append(df_i)
        except:
            continue

        if deleteFiles == True: os.remove(os.path.join(git_dir, input_name))

    dfc = pd.concat(df_list)
    dfc.to_csv( os.path.join(temp_exp_dir,"trajectoriesDat.csv"), index=False)

    nscenarios = sampledf['scen_num'].max()
    nscenarios_processed = len(dfc['scen_num'].unique())
    trackScen = "Number of scenarios processed n= " + str(nscenarios_processed) + " out of total N= " + str(nscenarios) + " (" + str(nscenarios_processed/ nscenarios)+ " %)"
    writeTxt(temp_exp_dir, "Simulation_report.txt" ,trackScen)

    return dfc
    
def trim_trajectories_Dat(df, exp_dir, VarsToKeep=None, keepTimes='today',lagtime_days=15, grpnames=None, channels=None, grpspecific_params=None):
    """Generate a subset of the trajectoriesDat dataframe
    The new csv file is saved under trajectoriesDat_trim.csv, no dataframe is returned
    """
    
    if VarsToKeep== None :
      VarsToKeep = ['startdate', 'time', 'scen_num','sample_num', 'run_num']
    
    if grpnames ==None :
        grpnames = ['All', 'EMS-1', 'EMS-2', 'EMS-3', 'EMS-4', 'EMS-5', 'EMS-6', 'EMS-7', 'EMS-8', 'EMS-9', 'EMS-10', 'EMS-11']
        grpnames_ki = ['EMS-1', 'EMS-2', 'EMS-3', 'EMS-4', 'EMS-5', 'EMS-6', 'EMS-7', 'EMS-8', 'EMS-9', 'EMS-10', 'EMS-11']
        
    if channels ==None :
        channels = ['susceptible', 'infected', 'recovered', 'infected_cumul', 'asymp_cumul', 'asymp_det_cumul', 'symp_mild_cumul', 'symp_severe_cumul', 'symp_mild_det_cumul',
        'symp_severe_det_cumul', 'hosp_det_cumul', 'hosp_cumul', 'detected_cumul', 'crit_cumul', 'crit_det_cumul', 'death_det_cumul', 
        'deaths', 'crit_det', 'critical_det', 'critical', 'hospitalized_det', 'hospitalized']

    if grpspecific_params ==None :
        grpspecific_params = ['Ki_t_'] # ['Ki_t_', 'triggertime_','reopening_multiplier_4_']

    column_list = VarsToKeep
    for channel in channels:
     for grp in grpnames:
        column_list.append(channel + "_" + str(grp))

    for grpspecific_param in grpspecific_params:
     for grp in grpnames_ki:
        column_list.append(grpspecific_param + "_" + str(grp))


    df = df[column_list]
    
    if keepTimes is not None:
        if keepTimes !='today':
            df = df[df['time'] >= int(keepTimes)]

        if keepTimes =='today':
            today = datetime.today()
            datetoday = date(today.year, today.month, today.day)
            datetoday = pd.to_datetime(datetoday)
            df['startdate'] = pd.to_datetime(df['startdate'])
            df['todayintime'] = datetoday - df['startdate']
            df['todayintime'] = pd.to_numeric(df['todayintime'].dt.days, downcast='integer')
            ## keep 15 days before today
            df = df[df['time'] >= df['todayintime'] - lagtime_days]

     
    return df
 
    
if __name__ == '__main__':
  args = parse_args()  
  sim_out_dir = "/projects/p30781/covidproject/covid-chicago/_temp/"
  stem = args.stem
  add_samples = True
  if args.addsamples =="False": add_samples = False 
    
  #stem = "20200525_EMS_11"
  exp_names = [x for x in os.listdir(sim_out_dir) if stem in x]


  for exp_name in exp_names :
    print(exp_name)
    temp_exp_dir =os.path.join(sim_out_dir, exp_name)
    trajectories_dir = os.path.join(temp_exp_dir,'trajectories' ) 
    sampledf = pd.read_csv(os.path.join(temp_exp_dir,"sampled_parameters.csv"))
    Nscenarios = sampledf['scen_num'].max()
    
    dfc = combineTrajectories(Nscenarios=Nscenarios,trajectories_dir=trajectories_dir, temp_exp_dir=temp_exp_dir,addSamples=add_samples)
    
    dfctrim = trim_trajectories_Dat(df=dfc,exp_dir =temp_exp_dir,lagtime_days = int(lagtime_days))
    dfctrim.to_csv(os.path.join(exp_dir, 'trajectoriesDat_trim.csv'), index=False)   

