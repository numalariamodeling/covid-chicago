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
        df['fraction_critical'] = np.random.uniform(0.1, 0.3, samples)
        df['cfr'] = np.random.uniform(0.0009, 0.0017, samples)
        df['fraction_dead'] = df.apply(lambda x: x['cfr'] / x['fraction_severe'], axis=1)
        df['fraction_hospitalized'] = df.apply(lambda x: 1 - x['fraction_critical'] - x['fraction_dead'], axis=1)
        df['reduced_inf_of_det_cases'] = np.random.uniform(0.5, 0.9, samples)
        df['d_Sym'] = np.random.uniform(0.2, 0.3, samples)
        df['d_Sys'] = np.random.uniform(0.7, 0.9, samples)
        df['d_As'] = np.random.uniform(0, 0, samples)

        df['social_multiplier_1'] = np.random.uniform(0.9, 1, samples)
        df['social_multiplier_2'] = np.random.uniform(0.6, 0.9, samples)
        df['social_multiplier_3'] = np.random.uniform( 0.005 , 0.3, samples) #0.2, 0.6

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

def generateSubmissionFile(scen_num,exp_name):
        file = open(os.path.join(trajectories_dir, 'runSimulations.bat'), 'w')
        file.write("ECHO start" + "\n" + "FOR /L %%i IN (1,1,{}) DO ( {} -c {} -m {})".format(
            str(scen_num),
            os.path.join(exe_dir, "compartments.exe"),
            os.path.join(temp_dir, "model_%%i" + ".cfg"),
            os.path.join(temp_dir, "simulation_%%i" + ".emodl")
        ) + "\n ECHO end")
        file.close()

        # Hardcoded Quest directories for now!
        # additional parameters , ncores, time, queue...
        exp_name_short = exp_name[-20:]
        header = '#!/bin/bash\n#SBATCH -A p30781\n#SBATCH -p short\n#SBATCH -t 04:00:00\n#SBATCH -N 5\n#SBATCH --ntasks-per-node=5'
        jobname = '#SBATCH	--job-name="'  + exp_name_short +'"'
        module = '\nmodule load singularity'
        singularity = '\nsingularity exec /software/singularity/images/singwine-v1.img wine'
        array = '\n#SBATCH --array=1-' + str(scen_num)
        email = '\n# SBATCH --mail-user=manuela.runge@northwestern.edu'  ## create input mask or user txt where specified
        emailtype = '\n# SBATCH --mail-type=ALL'
        err = '\n#SBATCH --error=log/arrayJob_%A_%a.err'
        out = '\n#SBATCH --output=log/arrayJob_%A_%a.out'
        exe = '\n/home/mrm9534/Box/NU-malaria-team/projects/binaries/compartments/compartments.exe'
        cfg = ' -c /home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/'+exp_name+'/simulations/model_${SLURM_ARRAY_TASK_ID}.cfg'
        emodl = ' -m /home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/'+exp_name+'/simulations/simulation_${SLURM_ARRAY_TASK_ID}.emodl'
        file = open(os.path.join(trajectories_dir,'runSimulations.sh'), 'w')
        file.write(header + jobname + email + emailtype + array + err + out + module + singularity  + exe + cfg + emodl)
        file.close()


def runExp(Location = 'Local'):
    if Location =='Local' :
        p = os.path.join(trajectories_dir,  'runSimulations.bat')
        subprocess.call([p])
    if Location =='NUCLUSTER' :
        print('please submit sbatch runSimulations.sh in the terminal')


def reprocess(input_fname='trajectories.csv', output_fname=None):
    fname = os.path.join(trajectories_dir, input_fname)
    row_df = pd.read_csv(fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    num_channels = len([x for x in df.columns.values if '{0}' in x])
    num_samples = int((len(row_df)) / num_channels)

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
    if output_fname:
        adf.to_csv(os.path.join(temp_exp_dir,output_fname), index=False)
    return adf


def combineTrajectories(Nscenarios, deleteFiles=False):
    scendf = pd.read_csv(os.path.join(temp_exp_dir,"scenarios.csv"))

    df_list = []
    for scen_i in range(Nscenarios):
        input_name = "trajectories_scen" + str(scen_i) + ".csv"
        try:
            df_i = reprocess(input_name)
            df_i['scen_num'] = scen_i
            df_i = df_i.merge(scendf, on=['scen_num','sample_num'])
            df_list.append(df_i)
        except:
            continue

        if deleteFiles == True: os.remove(os.path.join(git_dir, input_name))

    dfc = pd.concat(df_list)
    dfc.to_csv( os.path.join(temp_exp_dir,"trajectoriesDat.csv"), index=False)

    return dfc


def cleanup(delete_temp_dir=True) :
    # Delete simulation model and emodl files
    # But keeps per default the trajectories, better solution, zip folders and copy
    if delete_temp_dir ==True :
        shutil.rmtree(temp_dir, ignore_errors=True)
        print('temp_dir folder deleted')
    shutil.copytree(temp_exp_dir, sim_output_path)
    if not os.path.exists(plot_path):
        os.makedirs(plot_path)
    # Delete files after being copied to the project folder
    if os.path.exists(sim_output_path):
        shutil.rmtree(temp_exp_dir, ignore_errors=True)
    elif not os.path.exists(sim_output_path):
        print('Sim_output_path does not exists')

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

    #exp_name = today.strftime("%Y%m%d") + '_cobeyModel_updatedParam_infectious_det_urban' + '_rn' + str(int(np.random.uniform(10, 99)))
    #exp_name = today.strftime("%Y%m%d") + '_cobeyModel_updatedParam_infectious_det_rural' + '_rn' + str(int(np.random.uniform(10, 99)))
    #exp_name = today.strftime("%Y%m%d") + '_cobeyModel__IL_updatedParam_infectious_det_urban' + '_rn' + str(int(np.random.uniform(10, 99)))
    exp_name = today.strftime("%Y%m%d") + '_test' + '_rn' + str(int(np.random.uniform(10, 99)))


    # Selected SEIR model
    emodlname = 'extendedmodel_cobey.emodl'

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder()

    # Simlation setup
    simulation_population = 2700000  # 2700000  #1000  # 12830632 Illinois   # 2700000  Chicago
    number_of_samples = 20
    number_of_runs = 3
    duration = 120
    monitoring_samples = 120  # needs to be smaller than duration

    # Parameter values
    Kivalues =  np.linspace(2.e-7,2.5e-7,5) *0.9  # np.linspace(2.e-7,2.5e-7,5) # np.logspace(-8, -4, 4)

    nscen = generateScenarios(simulation_population,
                              Kivalues,
                              nruns=number_of_runs,
                              sub_samples=number_of_samples,
                              duration = duration,
                              monitoring_samples = monitoring_samples,
                              modelname=emodlname)

    generateSubmissionFile(nscen, exp_name)
  
  if Location == 'Local' :
    #runExp(Location='Local')

    # Once the simulations are done
    combineTrajectories(500)
    cleanup(delete_temp_dir=False)
    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    # Plots for quick check of simulation results
    #first_day = date(2020, 2, 22)
    plot(df, allchannels=master_channel_list, plot_fname='main_channels.png')
    plot(df, allchannels=detection_channel_list, plot_fname='detection_channels.png')
    plot(df, allchannels=custom_channel_list, plot_fname='cumulative_channels.png')
