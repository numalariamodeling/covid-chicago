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
exp_name = today.strftime("%Y%m%d") + '_cobeyModel_testTimeEvent' + '_rn' + str(int(np.random.uniform(10, 99)))

emodlname = 'extendedmodel_cobey.emodl'


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

# Create temporary folder for the simulation files
# currently allowing to run only 1 experiment at a time locally
temp_exp_dir = os.path.join(git_dir, '_temp', exp_name)
temp_dir = os.path.join(temp_exp_dir,  'simulations')
if not os.path.exists(os.path.join(git_dir, '_temp')):
    os.makedirs(os.path.join(os.path.join(git_dir, '_temp') ))
if not os.path.exists(temp_exp_dir):
    os.makedirs(temp_exp_dir)
    os.makedirs(temp_dir)
    os.makedirs(os.path.join(temp_exp_dir, 'log'))  # Required on quest

## Copy emodl and cfg file  to experiment folder
shutil.copyfile(os.path.join(emodl_dir, emodlname), os.path.join(temp_exp_dir, emodlname))
shutil.copyfile(os.path.join(cfg_dir, 'model.cfg'), os.path.join(temp_exp_dir, 'model.cfg'))


def getKiredCMS(i, scl):
    y = i * scl
    if y > 1: y = 1
    return (y)

def addTimeEvent(samples , scalingFactors=None, method="randomSampling"):
    Ki_red_dic = {}

    if method == 'randomSampling' :
        social_multiplier_1 = np.random.uniform(0.9, 1, samples)
        social_multiplier_2 = np.random.uniform(0.6, 0.9, samples)
        social_multiplier_3 = np.random.uniform(0.2, 0.6, samples)
        for nr in range(samples) :
            Ki_red_dic[nr] = [social_multiplier_1[nr], social_multiplier_2[nr], social_multiplier_3[nr]]
    elif method != 'randomSampling' :
        if scalingFactors == None :
            scalingFactors = [2, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
         for nr, scl in enumerate(scalingFactors):
            # scl = 0.5
            Set1 = [0.65, 0.4, 0.1]  # np.random.uniform(0,0.5, 10)
            Ki_red_dic[nr] = [getKiredCMS(x, scl) for x in Set1]

    return(Ki_red_dic)

# parameter samples                
def generateParameterSamples(samples, pop):
        df =  pd.DataFrame()
        df['sample_num'] = range(samples)
        df['speciesS'] = pop
        df['initialAs'] = 10#np.random.uniform(1, 5, samples)

        df['incubation_pd'] = np.random.uniform(4.2, 6.63, samples)
        df['time_to_symptoms'] = np.random.uniform(1, 5,samples)
        df['time_to_hospitalization'] = np.random.uniform(2, 10, samples)
        df['time_to_critical'] = np.random.uniform(4, 9, samples)
        df['time_to_death'] = np.random.uniform(3, 11, samples)
        df['recovery_rate_asymp'] = np.random.uniform(6, 16, samples)
        df['recovery_rate_mild'] = np.random.uniform(6, 16, samples)
        df['recovery_rate_hosp'] = np.random.uniform(6, 16, samples)
        df['recovery_rate_crit'] = np.random.uniform(6, 16, samples)
        df['fraction_symptomatic'] = np.random.uniform(0.5, 0.8, samples)
        df['fraction_severe'] = np.random.uniform(0.2, 0.5, samples)
        df['fraction_critical'] = np.random.uniform(0.1, 0.3, samples)
        df['cfr'] = np.random.uniform(0.008, 0.04, samples)
        df['fraction_dead'] = df.apply(lambda x : x['cfr']/x['fraction_severe'], axis=1)
        df['fraction_hospitalized'] = df.apply(lambda x : 1 - x['fraction_critical'] - x['fraction_dead'], axis=1)
        df['reduced_inf_of_det_cases'] = np.random.uniform(0.5, 0.9, samples)
        df['d_Sym'] = np.random.uniform(0.2, 0.3, samples)
        df['d_Sys'] = np.random.uniform(0.7, 0.9, samples)
        df['d_As'] = np.random.uniform(0, 0, samples)
        #df['Ki'] = Ki_i
        
        df.to_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"), index=False)
        return(df)

def replaceParameters(df, Ki_i, Ki_multiplier1, Ki_multiplier2, Ki_multiplier3, sample_nr, emodlname,  scen_num) :
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
    data = data.replace('@Ki_multiplier1@', '%.09f'% Ki_multiplier1)
    data = data.replace('@Ki_multiplier2@', '%.09f'% Ki_multiplier2)
    data = data.replace('@Ki_multiplier3@', '%.09f'% Ki_multiplier3)
    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_"+str(scen_num)+".emodl"), "wt")
    fin.write(data)
    fin.close()
    
    
    
def generateScenarios(simulation_population, Kivalues,Ki_red_dic, nruns, sub_samples, modelname):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population)
    for sample in range(sub_samples):
        for Kindex , Kval in enumerate(Ki_red_dic.values()):
            #print(Kindex , Kval)
            for i in Kivalues:
                scen_num += 1
                #print(i)

                #lst.append([simulation_population, sample, nruns, scen_num, i, Kval])
                lst.append([sample, scen_num, i, Kval])
                replaceParameters(df=dfparam, Ki_i=i, Ki_multiplier1 =Kval[0] , Ki_multiplier2=Kval[1], Ki_multiplier3=Kval[2], sample_nr= sample, emodlname=modelname, scen_num=scen_num)

                # adjust model.cfg
                fin = open(os.path.join(temp_exp_dir,"model.cfg"), "rt")
                data_cfg = fin.read()
                data_cfg = data_cfg.replace('@nruns@', str(nruns))
                data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
                fin.close()
                fin = open(os.path.join(temp_dir,"model_"+str(scen_num)+".cfg"), "wt")
                fin.write(data_cfg)
                fin.close()

    #df = pd.DataFrame(lst, columns=['statisticalPop','sample_num','nruns', 'scen_num', 'Ki', 'Ki_red'])
    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki', 'Ki_red'])
    df.to_csv(os.path.join(temp_exp_dir,"scenarios.csv"), index=False)
    return (scen_num)

def generateSubmissionFile(scen_num,exp_name, Location='Local'):
    if Location =='Local':
        file = open(os.path.join(temp_exp_dir,'runSimulations.bat'), 'w')
        for i in range(1, scen_num):
            file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '" -c "' + os.path.join(temp_dir, "model_" + str(i) + ".cfg") +
																															 
                       '" -m "' + os.path.join(temp_dir, "simulation_" + str(i) + ".emodl") + '"')
        file.close()
    if Location == 'NUCLUSTER':
        # Hardcoded Quest directories for now!
        # additional parameters , ncores, time, queue...
        header = '#!/bin/bash\n#SBATCH -A p30781\n#SBATCH -p short\n#SBATCH -t 04:00:00\n#SBATCH -N 5\n#SBATCH --ntasks-per-node=5'
        module = '\nmodule load singularity'
        singularity = '\nsingularity exec /software/singularity/images/singwine-v1.img wine'
        array = '\n#SBATCH --array=1-' + str(scen_num)
        #ID = '\nID=${SLURM_ARRAY_TASK_ID}'
        err = '\n#SBATCH --error=log/arrayJob_%A_%a.err'
        out = '\n#SBATCH --output=log/arrayJob_%A_%a.out'
        exe = '\n/home/mrm9534/Box/NU-malaria-team/projects/binaries/compartments/compartments.exe'
        cfg = ' -c /home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/'+exp_name+'/simulations/model_${SLURM_ARRAY_TASK_ID}.cfg'
        emodl = ' -m /home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/'+exp_name+'/simulations/simulation_${SLURM_ARRAY_TASK_ID}.emodl'
        file = open(os.path.join(temp_exp_dir,'runSimulations.sh'), 'w')
        file.write(header + array + err + out + module + singularity  + exe + cfg + emodl)
        file.close()


def runExp(Location = 'Local'):
    if Location =='Local' :
        p = os.path.join(temp_exp_dir, ‘runSimulations.bat’)
        subprocess.call([p])
    if Location =='NUCLUSTER' :
        print('please submit sbatch runSimulations.sh in the terminal')


def reprocess(input_fname='trajectories.csv', output_fname=None):
    fname = os.path.join(git_dir, input_fname)
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

#def cleanup(Nscenarios) :
#    if os.path.exists(os.path.join(temp_exp_dir,"trajectoriesDat.csv")):
#        for scen_i in range(1, Nscenarios):
#            input_name = "trajectories_scen" + str(scen_i) + ".csv"
#            try:
#                    os.remove(os.path.join(git_dir, input_name))
#            except:
#                continue
#    os.remove(os.path.join(temp_dir, "simulation_i.emodl"))
#    os.remove(os.path.join(temp_dir, "model_i.cfg"))

def cleanup(delete_temp_dir=True) :
    if delete_temp_dir ==True : 
        shutil.rmtree(temp_dir, ignore_errors=True)
        print('temp_dir folder deleted')
    shutil.move(temp_exp_dir, sim_output_path)

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

    # Experiment design, fitting parameter and population
    Kivalues =  np.linspace(2.e-7,2.5e-7,5) # np.logspace(-8, -4, 4)
    simulation_population = 2700000  #1000
    number_of_samples = 20
    number_of_runs = 3
    
    Ki_red_dic = addTimeEvent(scalingFactors=[2, 1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2], method='scaling', samples=None)

    nscen = generateScenarios(simulation_population,
                              Kivalues,
                              Ki_red_dic,
                              nruns=number_of_runs,
                              sub_samples=number_of_samples,
                              modelname=emodlname )

    generateSubmissionFile(nscen, exp_name,Location='Local')  # 'NUCLUSTER'
  
  if Location == 'Local' :
    runExp(Location='Local')
    # Once the simulations are done
    combineTrajectories(nscen)
    cleanup(delete_temp_dir=True)
    df = pd.read_csv(os.path.join(temp_exp_dir, 'trajectoriesDat.csv'))

    # Plots for quick check of simulation results
    first_day = date(2020, 2, 22)
    plot(df, allchannels=master_channel_list, plot_fname='main_channels.png')
    plot(df, allchannels=detection_channel_list, plot_fname='detection_channels.png')
    plot(df, allchannels=custom_channel_list, plot_fname='cumulative_channels.png')
