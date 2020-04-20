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
from load_paths import load_box_paths
from processing_helpers import *
from simulation_helpers import *
from simulation_setup import *


mpl.rcParams['pdf.fonttype'] = 42
testMode = False
Location = 'Local'  # 'NUCLUSTER'
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

emodl_dir = os.path.join(git_dir, 'emodl')
cfg_dir = os.path.join(git_dir, 'cfg')

today = date.today()


# parameter samples
def generateParameterSamples(samples, pop, first_day):
        df =  pd.DataFrame()
        df['sample_num'] = range(samples)
        df['speciesS'] = pop
        df['initialAs'] = 10 #np.random.uniform(1, 5, samples)

        df['incubation_pd'] = np.random.uniform(4.2, 6.63, samples)
        df['time_to_symptoms'] = np.random.uniform(1, 5, samples)
        df['time_to_hospitalization'] = np.random.uniform(2, 10, samples)
        df['time_to_critical'] = np.random.uniform(4, 9, samples)
        df['time_to_death'] = np.random.uniform(3, 11, samples)
        df['recovery_rate_asymp'] = np.random.uniform(6, 16, samples)
        df['recovery_rate_mild'] = np.random.uniform(19.4, 21.3, samples)
        df['recovery_rate_hosp'] = np.random.uniform(19.5, 21.1, samples)
        df['recovery_rate_crit'] = np.random.uniform(25.3, 31.6, samples)
        df['fraction_symptomatic'] = np.random.uniform(0.5, 0.8, samples)
        df['fraction_severe'] = np.random.uniform(0.2, 0.5, samples)
        df['fraction_critical'] = np.random.uniform(0.2, 0.5, samples)
        df['cfr'] = np.random.uniform(0.002675, 0.007775, samples)
        df['fraction_dead'] = df.apply(lambda x: x['cfr'] / x['fraction_severe'], axis=1)
        df['fraction_hospitalized'] = df.apply(lambda x: 1 - x['fraction_critical'] - x['fraction_dead'], axis=1)
        df['reduced_inf_of_det_cases'] = np.random.uniform(0.5, 0.9, samples)
        df['d_Sym'] = np.random.uniform(0.2, 0.3, samples)
        df['d_Sys'] = np.random.uniform(0.7, 0.9, samples)
        df['d_As'] = np.random.uniform(0, 0, samples)
        #df['Ki'] = np.random.uniform(2.e-7, 2.5e-7, samples)

        df['social_multiplier_1'] = np.random.uniform(0.9, 1, samples)
        df['social_multiplier_2'] = np.random.uniform(0.6, 0.9, samples)
        df['social_multiplier_3'] = np.random.uniform(0.05 , 0.3, samples) #0.2, 0.6

        df['socialDistance_time1'] = DateToTimestep(date(2020, 3, 12), startdate=first_day)
        df['socialDistance_time2'] = DateToTimestep(date(2020, 3, 17), startdate=first_day)
        df['socialDistance_time3'] = DateToTimestep(date(2020, 3, 21), startdate=first_day)

        df.to_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"), index=False)
        return(df)

def replaceParameters(df, Ki_i,  sample_nr, emodlname, scen_num,  stop_date, backtonormal_multiplier) :
    fin = open(os.path.join(temp_exp_dir,emodlname), "rt")          
    data = fin.read()
    data = data.replace('@speciesS@', str(df.speciesS[sample_nr]))
    data = data.replace('@initialAs@', str(df.initialAs[sample_nr]))
    data = data.replace('@incubation_pd@', str(df.incubation_pd[sample_nr]))
    data = data.replace('@time_to_symptoms@', str(df.time_to_symptoms[sample_nr]))
    data = data.replace('@time_to_hospitalization@', str(df.time_to_hospitalization[sample_nr]))
    data = data.replace('@time_to_critical@', str(df.time_to_critical[sample_nr]))
    data = data.replace('@time_to_death@', str(df.time_to_death[sample_nr]))
    data = data.replace('@fraction_hospitalized@', str(df.fraction_hospitalized[sample_nr]))
    data = data.replace('@fraction_symptomatic@', str(df.fraction_symptomatic[sample_nr]))
    data = data.replace('@fraction_severe@', str(df.fraction_severe[sample_nr]))
    data = data.replace('@fraction_critical@', str(df.fraction_critical[sample_nr]))
    data = data.replace('@reduced_inf_of_det_cases@', str(df.reduced_inf_of_det_cases[sample_nr]))
    data = data.replace('@fraction_dead@', str(df.fraction_dead[sample_nr]))
    data = data.replace('@d_As@', str(df.d_As[sample_nr]))
    data = data.replace('@d_Sym@', str(df.d_Sym[sample_nr]))
    data = data.replace('@d_Sys@', str(df.d_Sys[sample_nr]))
    data = data.replace('@recovery_rate_asymp@', str(df.recovery_rate_asymp[sample_nr]))
    data = data.replace('@recovery_rate_mild@', str(df.recovery_rate_mild[sample_nr]))
    data = data.replace('@recovery_rate_hosp@', str(df.recovery_rate_hosp[sample_nr]))
    data = data.replace('@recovery_rate_crit@', str(df.recovery_rate_crit[sample_nr]))
    data = data.replace('@Ki@', '%.09f'% Ki_i)
    data = data.replace('@social_multiplier_1@',  str(df.social_multiplier_1[sample_nr]))
    data = data.replace('@social_multiplier_2@',  str(df.social_multiplier_2[sample_nr]))
    data = data.replace('@social_multiplier_3@',  str(df.social_multiplier_3[sample_nr]))
    data = data.replace('@socialDistance_time1@',  str(df.socialDistance_time1[sample_nr]))
    data = data.replace('@socialDistance_time2@',  str(df.socialDistance_time2[sample_nr]))
    data = data.replace('@socialDistance_time3@',  str(df.socialDistance_time3[sample_nr]))
    data = data.replace('@socialDistanceSTOP_time@',  str(DateToTimestep(stop_date,startdate= first_day)))
    data = data.replace('@backtonormal_multiplier@', str(backtonormal_multiplier))

    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_"+str(scen_num)+".emodl"), "wt")
    fin.write(data)
    fin.close()

    
def generateScenarios(simulation_population, Kivalues, duration, monitoring_samples, nruns, sub_samples,  modelname ,first_day , stop_dates,backtonormal_multiplier_values):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population, first_day=first_day)
    for sample in range(sub_samples):
        for i in Kivalues:
            for backtonormal_multiplier in backtonormal_multiplier_values :
                for stop_date in  stop_dates:
                    scen_num += 1
                    #print(i)

                    #lst.append([simulation_population, sample, nruns, scen_num, i, Kval])
                    lst.append([sample, scen_num, i, backtonormal_multiplier, stop_date])
                    replaceParameters(df=dfparam, Ki_i=i, sample_nr= sample, emodlname=modelname, scen_num=scen_num, stop_date=stop_date, backtonormal_multiplier=backtonormal_multiplier)

                    # adjust model.cfg
                    fin = open(os.path.join(temp_exp_dir,"model.cfg"), "rt")
                    data_cfg = fin.read()
                    data_cfg = data_cfg.replace('@duration@', str(duration))
                    data_cfg = data_cfg.replace('@monitoring_samples@', str(monitoring_samples))
                    data_cfg = data_cfg.replace('@nruns@', str(nruns))
                    if Location == 'Local' :
                        data_cfg = data_cfg.replace('trajectories', './_temp/'+exp_name+'/trajectories/trajectories_scen' + str(scen_num))
                    if not Location == 'Local' :
                        data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
                    fin.close()
                    fin = open(os.path.join(temp_dir,"model_"+str(scen_num)+".cfg"), "wt")
                    fin.write(data_cfg)
                    fin.close()

    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki', 'backtonormal_multiplier','socialDistance_multiplier'])
    df.to_csv(os.path.join(temp_exp_dir,"scenarios.csv"), index=False)
    return (scen_num)


if __name__ == '__main__' :

    master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild',
                           'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
    detection_channel_list = ['detected', 'detected_cumul', 'asymp_det_cumul', 'hosp_det_cumul']
    custom_channel_list = ['detected_cumul', 'symp_severe_cumul', 'asymp_det_cumul', 'hosp_det_cumul',
                           'symp_mild_cumul', 'asymp_cumul', 'hosp_cumul', 'crit_cumul']

    #============================================================
    # Experiment design, fitting parameter and population
    #=============================================================

    region = 'NMH_catchment'
    exp_name = today.strftime("%Y%m%d") + '_%s_test_SocialDistance' % region  + '_rn' + str(int(np.random.uniform(10, 99)))

    # Selected SEIR model
    emodlname = 'extendedmodel_cobey_interventionStop.emodl'

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder(exp_name,emodl_dir,emodlname, cfg_dir) ## GE 04/10/20 added exp_name,emodl_dir,emodlname, cfg_dir here to fix exp_name not defined error

    ## function in simulation_setup.py
    populations, Kis, startdate = load_setting_parameter()

    simulation_population = populations[region]
    number_of_samples = 20
    number_of_runs = 3
    duration = 365
    monitoring_samples = 365  # needs to be smaller than duration

    # Parameter values
    Kivalues = Kis[region]
    first_day = startdate[region]
    stop_dates = [date(2020, 4, 30), date(2020, 5, 30), date(2020, 6, 30), date(2020, 7, 30)]
    backtonormal_multiplier_values = np.linspace(0, 1, 6)

    nscen = generateScenarios(simulation_population,
                              Kivalues,
                              nruns=number_of_runs,
                              sub_samples=number_of_samples,
                              duration = duration,
                              monitoring_samples = monitoring_samples,
                              modelname=emodlname,
                              first_day = first_day,
                              stop_dates=stop_dates,
                              backtonormal_multiplier_values=backtonormal_multiplier_values)

    generateSubmissionFile(nscen, exp_name, trajectories_dir, temp_dir, temp_exp_dir)
  
if Location == 'Local' :
    runExp(trajectories_dir=trajectories_dir, Location='Local') 

    # Once the simulations are done
    combineTrajectories(Nscenarios=nscen, trajectories_dir=trajectories_dir, temp_exp_dir=temp_exp_dir, deleteFiles=False)
    cleanup(temp_exp_dir=temp_exp_dir, sim_output_path=sim_output_path,plot_path=plot_path, delete_temp_dir=False)
    df = pd.read_csv(os.path.join(temp_exp_dir, 'trajectoriesDat.csv'))

    sampleplot(df, allchannels=master_channel_list, plot_fname='main_channels.png')
    sampleplot(df, allchannels=detection_channel_list, plot_fname='detection_channels.png')
    sampleplot(df, allchannels=custom_channel_list, plot_fname='cumulative_channels.png')