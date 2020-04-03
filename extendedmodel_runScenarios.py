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
exp_name = today.strftime("%Y%m%d") + '_extendedModel_TEST7' + '_rn' + str(int(np.random.uniform(10, 99)))

emodlname = 'extendedmodel_covid.emodl'
# emodlname = 'extendedmodel_covid_timeevent.emodl'


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

master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
detection_channel_list = ['detected', 'detected_cumul',  'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul',  'crit_det_cumul']
custom_channel_list = ['detected_cumul', 'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul', 'crit_det_cumul', 'symp_cumul',  'asymp_cumul','hosp_cumul', 'crit_cumul']


# Experiment design, fitting parameter and population
Kivalues = np.linspace(0.7, 1, 4)
simulation_population = 2700000
#plt.hist(Kivalues, bins=100)
#plt.show()

def define_intervention_param(df, startDate, reduction):
    df['socialDistance_start'] = startDate
    df['contactReduction'] = reduction
    return df

def replace_intervention_param(data, df, sample_nr) :
    data = data.replace('@socialDistance_start@', str(df.socialDistance_start[sample_nr]))
    data = data.replace('@contactReduction@', str(df.contactReduction[sample_nr]))
    return data

def generateParameterSamples(samples, pop=10000, addIntervention = True, interventionStart=10, coverage=0.4):
        df =  pd.DataFrame()
        df['sample_num'] = range(samples)
        df['speciesS'] = pop
        df['initialAs'] = 10#np.random.uniform(1, 5, samples)
        df['incubation_pd'] = np.random.uniform(4.2, 6.63, samples)
        df['time_to_infectious'] = np.random.uniform(0, df['incubation_pd'],samples)  # placeholder and  time_to_infectious <= incubation_pd
        df['time_to_hospitalization'] = np.random.normal(5.76, 4.22, samples)
        df['time_to_critical'] = np.random.uniform(4, 9, samples)
        df['time_to_death'] = np.random.uniform(3, 11, samples)
        df['recovery_rate'] = np.random.uniform(6, 16, samples)
        df['fraction_hospitalized'] = np.random.uniform(0.1, 1, samples)
        df['fraction_symptomatic'] = np.random.uniform(0.5, 0.8, samples)
        df['fraction_critical'] = np.random.uniform(0.1, 1, samples)
        df['reduced_inf_of_det_cases'] = np.random.uniform(0.2, 0.3, samples)
        df['cfr'] = np.random.uniform(0.008, 0.022, samples)
        df['d_Sy'] = np.random.uniform(0.2, 0.3, samples)
        df['d_H'] = np.random.uniform(0.8, 1, samples)
        df['d_As'] = np.random.uniform(0, 0, samples)
        #df['Ki'] = Ki_i

        if addIntervention == True:
            df = define_intervention_param(df, startDate=interventionStart, reduction=coverage)

        df.to_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"))
        return(df)

def replaceParameters(df, Ki_i, sample_nr, emodlname, ,  scen_num) :
    fin = open(os.path.join(temp_exp_dir,emodlname), "rt")
    data = fin.read()
    data = data.replace('@speciesS@', str(df.speciesS[sample_nr]))
    data = data.replace('@initialAs@', str(df.initialAs[sample_nr]))
    data = data.replace('@incubation_pd@', str(df.incubation_pd[sample_nr]))
    data = data.replace('@time_to_infectious@', str(df.time_to_infectious[sample_nr]))
    data = data.replace('@time_to_hospitalization@', str(df.time_to_hospitalization[sample_nr]))
    data = data.replace('@time_to_critical@', str(df.time_to_critical[sample_nr]))
    data = data.replace('@time_to_death@', str(df.time_to_death[sample_nr]))
    data = data.replace('@fraction_hospitalized@', str(df.fraction_hospitalized[sample_nr]))
    data = data.replace('@fraction_symptomatic@', str(df.fraction_symptomatic[sample_nr]))
    data = data.replace('@fraction_critical@', str(df.fraction_critical[sample_nr]))
    data = data.replace('@reduced_inf_of_det_cases@', str(df.reduced_inf_of_det_cases[sample_nr]))
    data = data.replace('@cfr@', str(df.cfr[sample_nr]))
    data = data.replace('@d_As@', str(df.d_As[sample_nr]))
    data = data.replace('@d_Sy@', str(df.d_Sy[sample_nr]))
    data = data.replace('@d_H@', str(df.d_H[sample_nr]))
    data = data.replace('@recovery_rate@', str(df.recovery_rate[sample_nr]))
    data = data.replace('@Ki@', str(Ki_i))
    # data = data.replace('@Ki@', str(df.Ki[sub_sample]))
    data = replace_intervention_param(data, df, sample_nr)
    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_"+str(scen_num)+".emodl"), "wt")
    fin.write(data)
    fin.close()


def generateScenarios(Kivalues,socialDistance_start,  Ki_red, sub_samples, modelname):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population)
    for sample in range(sub_samples):
        for Ki_red_i in  Ki_red:
            for i in Kivalues:
                scen_num += 1
                #print(i)
                lst.append([sample, scen_num, i, socialDistance_start, Ki_red_i])
                replaceParameters(df=dfparam, Ki_i=i, sample_nr= sample, emodlname=modelname, socialDistance_start=socialDistance_start,Ki_red_i = Ki_red_i ,scen_num=scen_num)
                # adjust model.cfg
                fin = open(os.path.join(temp_exp_dir,"model.cfg"), "rt")
                data_cfg = fin.read()
                data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
                fin.close()
                fin = open(os.path.join(temp_dir,"model_"+str(scen_num)+".cfg"), "wt")
                fin.write(data_cfg)
                fin.close()
    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki', 'socialDistance_start', 'Ki_red'])
    df.to_csv(os.path.join(temp_dir,"scenarios.csv"))
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
        header = '#!/bin/bash\n#SBATCH -A p30781\n#SBATCH -p short\n#SBATCH -t 04:00:00\n#SBATCH -N 1\n#SBATCH --ntasks-per-node=5'
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
        subprocess.call([r'runSimulations.bat'])
    if Location =='NUCLUSTER' :
        print('please submit sbatch runSimulations.sh in the terminal')

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
    if output_fname:
        adf.to_csv(os.path.join(temp_exp_dir,output_fname))
    return adf


def combineTrajectories(Nscenarios, deleteFiles=False):
    scendf = pd.read_csv(os.path.join(temp_exp_dir,"scenarios.csv"))
    del scendf['Unnamed: 0']

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

        if deleteFiles == True: os.remove(os.path.join(git_dir, input_name))

    dfc = pd.concat(df_list)
    dfc.to_csv( os.path.join(temp_exp_dir,"trajectoriesDat.csv"))

    return dfc

#def cleanup(Nscenarios) :
#    if os.path.exists(os.path.join(sim_output_path,"trajectoriesDat.csv")):
#        for scen_i in range(1, Nscenarios):
#            input_name = "trajectories_scen" + str(scen_i) + ".csv"
#            try:
#                    os.remove(os.path.join(git_dir, input_name))
#            except:
#                continue
#    os.remove(os.path.join(temp_dir, "simulation_i.emodl"))
#    os.remove(os.path.join(temp_dir, "model_i.cfg"))


def cleanup() :
    os.remove(os.path.join(temp_dir, "simulation_*"))
    os.remove(os.path.join(temp_dir, "model_*"))
    shutil.move(temp_exp_dir, sim_output_path)

def plot(adf, allchannels=master_channel_list, plot_fname=None):
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


# if __name__ == '__main__' :


### Intervention scenarios 
def getKiredCMS( i) :
    if i == 0:
        Ki_red_CMS = 0.7
    elif i>0 :
        Ki_red_CMS = 0.7 / (1 / i )
    return (Ki_red_CMS)

Kival = 0.7
Ki_red_perc = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1]  #np.random.uniform(0,0.5, 10)
Ki_red_CMS = [getKiredCMS(x) for x in Ki_red_perc]
socialDistance_start = 22


nscen = generateScenarios(Kivalues,  socialDistance_start,Ki_red=Ki_red_CMS, sub_samples=50, modelname=emodlname )
generateSubmissionFile(nscen, exp_name, Location='Local')  # 'NUCLUSTER'

if Location == 'Local' :
    runExp(Location='Local')
    # Once the simulations are done
    combineTrajectories(nscen)
    #cleanup()
    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    #df.params.unique()
    #df= df[df['params'] == 9.e-05]
    # Plots for quick check of simulation results
    first_day = date(2020, 2, 22)
    plot(df, allchannels=master_channel_list, plot_fname='main_channels.png')
    plot(df, allchannels=detection_channel_list, plot_fname='detection_channels.png')
    plot(df, allchannels=custom_channel_list, plot_fname='cumulative_channels.png')