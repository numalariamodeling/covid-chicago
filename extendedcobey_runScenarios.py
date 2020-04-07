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

mpl.rcParams['pdf.fonttype'] = 42
testMode = False
Location = 'Local'  # 'NUCLUSTER'
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

emodl_dir = os.path.join(git_dir, 'emodl')
cfg_dir = os.path.join(git_dir, 'cfg')

today = date.today()


def makeExperimentFolder() :
    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = sim_output_path
    # Create temporary folder for the simulation files
    # currently allowing to run only 1 experiment at a time locally
    temp_exp_dir = os.path.join(git_dir, '_temp', exp_name)
    temp_dir = os.path.join(temp_exp_dir, 'simulations')
    trajectories_dir = os.path.join(temp_exp_dir, 'trajectories')
    if not os.path.exists(os.path.join(git_dir, '_temp')):
        os.makedirs(os.path.join(os.path.join(git_dir, '_temp')))
    if not os.path.exists(temp_exp_dir):
        os.makedirs(temp_exp_dir)
        os.makedirs(temp_dir)
        os.makedirs(trajectories_dir)
        os.makedirs(os.path.join(temp_exp_dir, 'log'))
        os.makedirs(os.path.join(trajectories_dir, 'log'))  # location of log file on quest

    ## Copy emodl and cfg file  to experiment folder
    shutil.copyfile(os.path.join(emodl_dir, emodlname), os.path.join(temp_exp_dir, emodlname))
    shutil.copyfile(os.path.join(cfg_dir, 'model.cfg'), os.path.join(temp_exp_dir, 'model.cfg'))

    return temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path

# parameter samples
def generateParameterSamples(samples, pop):
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
        #df['fraction_critical'] = np.random.uniform(0.15, 0.35, samples)
        #df['fraction_critical'] = np.random.uniform(0.15, 0.45, samples)
        #df['cfr'] = np.random.uniform(0.008, 0.022, samples)
        #df['cfr'] = np.random.uniform(0.0009, 0.0017, samples)
        #df['cfr'] = np.random.uniform(0.00445, 0.01185, samples)
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
        df['social_multiplier_3'] = np.random.uniform( 0.005 , 0.3, samples) #0.2, 0.6

        df['socialDistance_time1'] = 32 # 24  ## (+8 for NMH)
        df['socialDistance_time2'] = 37 # 29  ## (+8 for NMH)
        df['socialDistance_time3'] = 41 # 33  ## (+8 for NMH)

        df.to_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"), index=False)
        return(df)

def replaceParameters(df, Ki_i,  sample_nr, emodlname,  scen_num) :
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

    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_"+str(scen_num)+".emodl"), "wt")
    fin.write(data)
    fin.close()

    
def generateScenarios(simulation_population, Kivalues, duration, monitoring_samples, nruns, sub_samples,  modelname):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population)
    for sample in range(sub_samples):
        for i in Kivalues:
            scen_num += 1
            #print(i)

            #lst.append([simulation_population, sample, nruns, scen_num, i, Kval])
            lst.append([sample, scen_num, i])
            replaceParameters(df=dfparam, Ki_i=i, sample_nr= sample, emodlname=modelname, scen_num=scen_num)

            # adjust model.cfg
            fin = open(os.path.join(temp_exp_dir,"model.cfg"), "rt")
            data_cfg = fin.read()
            data_cfg = data_cfg.replace('@duration@', str(duration))
            data_cfg = data_cfg.replace('@monitoring_samples@', str(monitoring_samples))
            data_cfg = data_cfg.replace('@nruns@', str(nruns))
            data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
            fin.close()
            fin = open(os.path.join(temp_dir,"model_"+str(scen_num)+".cfg"), "wt")
            fin.write(data_cfg)
            fin.close()

    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki'])
    df.to_csv(os.path.join(temp_exp_dir,"scenarios.csv"), index=False)
    return (scen_num)


def plot(adf, allchannels, plot_fname=None):
    fig = plt.figure(figsize=(8, 6))
    palette = sns.color_palette('Set1', 10)

    axes = [fig.add_subplot(3, 3, x + 1) for x in range(len(allchannels))]
    fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
    for c, channel in enumerate(allchannels):
        mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
        ax = axes[c]
        dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
        ax.plot(dates, mdf['mean'], label=channel, color=palette[c])
        ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                        color=palette[c], linewidth=0, alpha=0.2)
        ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                        color=palette[c], linewidth=0, alpha=0.4)

        ax.set_title(channel, y=0.8)

        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_xlim(first_day, )

    if plot_fname :
        plt.savefig(os.path.join(plot_path, plot_fname))
    plt.show()

if __name__ == '__main__' :

    master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild',
                           'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
    detection_channel_list = ['detected', 'detected_cumul', 'asymp_det_cumul', 'hosp_det_cumul']
    custom_channel_list = ['detected_cumul', 'symp_severe_cumul', 'asymp_det_cumul', 'hosp_det_cumul',
                           'symp_mild_cumul', 'asymp_cumul', 'hosp_cumul', 'crit_cumul']

    #============================================================
    # Experiment design, fitting parameter and population
    #=============================================================

    exp_name = today.strftime("%Y%m%d") + '_TEST' + '_rn' + str(int(np.random.uniform(10, 99)))


    # Selected SEIR model
    emodlname = 'extendedmodel_cobey.emodl'

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder()

    # Simlation setup
    simulation_population = 315000 #  1000  # 12830632 Illinois   # 2700000  Chicago  ## 315000 NMH catchment
    number_of_samples = 20
    number_of_runs = 3
    duration = 365
    monitoring_samples = 365  # needs to be smaller than duration

    # Time event
    ### Cook   -
    # Kivalues  = np.linspace(2.e-7,2.5e-7,5)
    # startDate = '02.20.2020'
    # socialDistance_time = [24, 29, 33]
    ### NMH
    # Kivalues  = np.linspace(1.5e-6, 2e-6, 3)
    # startDate = '02.28.2020'
    # socialDistance_time = [32, 37, 41]

    # Parameter values
    Kivalues =  np.linspace(1.5e-6, 2e-6, 5)

    nscen = generateScenarios(simulation_population,
                              Kivalues,
                              nruns=number_of_runs,
                              sub_samples=number_of_samples,
                              duration = duration,
                              monitoring_samples = monitoring_samples,
                              modelname=emodlname)

    generateSubmissionFile(nscen, exp_name)
  
if Location == 'Local' :
    runExp(trajectories_dir=trajectories_dir, Location='Local')

    # Once the simulations are done
    combineTrajectories(nscen)
    cleanup(delete_temp_dir=False)
    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat_50.csv'))

    first_day = date(2020, 2, 22)
    plot(df, allchannels=master_channel_list, plot_fname='main_channels.png')
    plot(df, allchannels=detection_channel_list, plot_fname='detection_channels.png')
    plot(df, allchannels=custom_channel_list, plot_fname='cumulative_channels.png')
