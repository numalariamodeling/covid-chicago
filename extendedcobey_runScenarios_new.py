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

def gen_samples(sample_params_csv_base = './sampled_parameters', samples=20, pop=12830632):
    
    #Function generates csv and DataFrame of sampled_parameters,
    #specified below. Samples specifies number of samples used.
    #Population specified by 'pop'.
    
    df =  pd.DataFrame()
    df['sample_index'] = range(samples) #Be sure that your index contains the substring 'index!'
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

    df.to_csv(sample_params_csv_base + '.csv', index=False) #Writing to csv...
    
    return df

def gen_scenarios(scenarios_csv_base='./scenarios', nscenarios=5, log=False):
    
    #Function generates csv and DataFrame of scenarios, varying
    #the parameters specified below in either a linear space
    #with nscenarios instances or a logspace with nscenarios
    #instances. This function only determines K_i right now,
    #where the lowest K_i and highest K_i are specified below.
    
    #Specify min and max of K_i to iterate over.
    K_i_low = 3.5e-8
    K_i_high = 5.3e-8
    
    df = pd.DataFrame()
    df['scenario_index'] = range(nscenarios) #Be sure that your index contains the substring 'index!'
    
    if log: #Log Space (Probably only use if K_i_low << K_i_high)
        df['Ki'] = np.logspace(start=np.log10(K_i_low), stop=np.log10(K_i_high), num=nscenarios)
    else: #Linear Space (Default)
        df['Ki'] = np.linspace(start=K_i_low, stop=K_i_high, num=nscenarios)
        
    df.to_csv(scenarios_csv_base + '.csv', index=False) #Writing to csv...
    
    return df

def gen_combos(csv_base_list=['./sampled_parameters', './scenarios'], output_base='./master_input'):
    
    #Function takes list of csv bases, generates a master
    #csv file with all combinations of parameters contained therein.
    #Ensure that all parameters have unique names in input files
    #and that multiple input files are supplied.
    
    dfs_list = ['']*(len(csv_base_list)) #Initialize list to store DataFrames
    
    #Importing data...
    base_index = 0
    for base in csv_base_list:
        fullname = './' + base + '.csv'
        csv_df = pd.read_csv(fullname, header=0).dropna(axis='columns') #Import csv
        dfs_list[base_index] = csv_df.copy()
        base_index += 1
        
    #Restructuring data in lists with all possible combinations...    
    cool_list = np.array(list(itertools.product(dfs_list[0].to_numpy(),dfs_list[1].to_numpy())))
    cool_list = np.array(list(np.concatenate(x) for x in cool_list))
    for i in range(2,len(dfs_list)):
        cool_list = np.array(list(itertools.product(cool_list,dfs_list[i].to_numpy())))
        cool_list = np.array(list(np.concatenate(x) for x in cool_list))
    
    #Creating a list of columns for use in the final DataFrame...
    master_columns = []
    for df in dfs_list:
        master_columns.extend(np.array(df.columns))
    
    #Isolating index columns...
    index_columns = []
    for col in master_columns:
        if 'index' in col:
            index_columns.append(col)
    
    #Writing all data to master DataFrame...
    master_df = pd.DataFrame(data=cool_list, columns=master_columns)
    
    #Restructuring master DataFrame to bring index columns to front...
    master_df = master_df[[c for c in master_df if c in index_columns]+[c for c in master_df if c not in index_columns]]
    
    #Writing master dataframe to output csv.
    master_df.to_csv(output_base+'.csv')
    
    return master_df

def make_folders(emodl_and_cfg_folder='emodls', trajectories_folder='trajectories'):
    
    #This function makes the emodls and cfg directory,
    #as well as the trajectories_folder.
    #No other functions call this function, so if
    #you decide to manually make your emodl files,
    #you do not need to call this funciton.
    
    if not (os.path.isdir(emodl_and_cfg_folder)):
        os.mkdir(emodl_and_cfg_folder)
    if not (os.path.isdir(trajectories_folder)):
        os.mkdir(trajectories_folder)

def gen_emodls(emodl_base='./emodl_', cfg_base='./cfg_', master_input_base='./master_input_4grps', template_emodl_base='./extendedmodel_cobey_age_4grp', \
               duration=365, nruns=3, monitoring_samples=365, prefix='trajectories_', \
               template_cfg_base='./extendedmodel_cobey_age_4grp'):
    
    #Function takes master csv file (output of gen_combos from
    #combine_to_master_input_csv.py) and creates an emodl file
    #and corresponding cfg file for each line for each line.
    #Everything that goes in the emodl is contained within the
    #master csv file, whereas everything that goes in the cfg
    #file is determined at call (duration, nruns, nsamples,
    #etc...). Prefix emodl_base will also be used as the prefix
    #for the output cfg files.
    
    #Read in master input csv to DataFrame...
    master_df = pd.read_csv(master_input_base + '.csv', index_col=0)
    columns = list(master_df.columns)         
    
    #Read in template emodl and cfg as strings...
    template_emodl = open(template_emodl_base + '.emodl', 'r') 
    template_e_txt = template_emodl.read() #Read in template emodl as string
    template_emodl.close()
    
    template_cfg = open(template_cfg_base + '.cfg', 'r') 
    template_c_txt = template_cfg.read() #Read in template emodl as string
    template_cfg.close()
    
    
    #Create an emodl file and cfg file with specified base for each row...
    for index, row in master_df.iterrows():
        template_e = template_e_txt #Writing to output emodl
        for col in columns:
            if ('@' + col + '@') in template_e:
                template_e = template_e.replace('@' + col + '@', str(row[col]))
        output_emodl = open(emodl_base + str(index) + '.emodl', 'w')
        output_emodl.write(template_e)
        output_emodl.close()
        
        template_c = template_c_txt #Writing to output cfg
        template_c = template_c.replace('@duration@', str(duration))
        template_c = template_c.replace('@nruns@', str(nruns))
        template_c = template_c.replace('@monitoring_samples@', str(duration))
        template_c = template_c.replace('@prefix@', prefix + str(index))
        output_cfg = open(cfg_base + str(index) + '.cfg', 'w')
        output_cfg.write(template_c)
        output_cfg.close()
        
def gen_batch(compartments_path='..\CMS\compartments.exe', emodl_base='.\emodl_', cfg_base='.\cfg_', \
              nsims=100, bat_file_base='run_simulations'):
    
    #Function generates batch file which can be run from
    #Windows Explorer (click 'Run as Administrator').
    #NOTE that the .bat file uses windows file structure, so
    #make sure your emodl_base and cfg_base contain '\'s, not
    #'/'s!
    #You can also specify the path to the CMS binary via
    #compartments_path.
    
    file = open(bat_file_base + '.bat', 'w')
    file.write("ECHO start" + "\n" + "FOR /L %%i IN (0,1,{}) DO ( {} -c {} -m {})".format(
        str(nsims-1),
        compartments_path,
        cfg_base+'%%i'+'.cfg',
        emodl_base+'%%i'+'.emodl') + "\n ECHO end")
    
    file.close()

def gen_quest(emodl_base='./emodl_', cfg_base='./cfg_', nsims=100, quest_file_base='run_simulations'):
    
    #Function generates batch file which can be run on
    #Quest (sbatch run_simulations.sh)! To change any
    #of the parameters in the header, simply modify
    #'header' below.
    
    file = open(quest_file_base + '.sh', 'w')
    header = """#!/bin/bash
#SBATCH -A p30781                               # Allocation
#SBATCH -p normal                               # Queue
#SBATCH -t 04:00:00                             # Walltime/duration of the job
#SBATCH -N 1                                    # Number of Nodes
#SBATCH --mem=18G                               # Memory per node in GB needed for a job. Also see --mem-per-cpu
#SBATCH --ntasks-per-node=1                     # Number of Cores (Processors)
#SBATCH --mail-user=rakr@u.northwestern.edu     # Designate email address for job communications
#SBATCH --mail-type=END                         # Events options are job BEGIN, END, NONE, FAIL, REQUEUE
#SBATCH --output=./output.txt                   # Path for output must already exist
#SBATCH --error=./error.txt                     # Path for errors must already exist
#SBATCH --job-name="CMS_simulation"             # Name of job\n\n\n"""
    file.write(header)
    
    file.write('module load singularity\n\n\n')
    
    #The loop below is written such that each
    #simulation requires a line in the submission text.
    #This is a bad way to code it, but not inherently
    #harmful. Will update once I am on Quest (4-9-20).
    
    for i in range(nsims):
        file.write('singularity exec ../singwine-v1.img wine ../CMS/compartments.exe -c ' \
                   + cfg_base + str(i) + '.cfg ' + '-m ' + emodl_base + str(i) + '.emodl\n')
    file.close()

def reprocess_new(input_fname='trajectories.csv', output_fname=None):
    
    #Function combines the trajectories of each run
    #in a single simulation into a DataFrame. 
    #"Run Number" is stored as run_index.
    #Called by combine_trajectories.
    
    row_df = pd.read_csv(input_fname, skiprows=1)
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
        sdf['run_index'] = run_num
        adf = pd.concat([adf, sdf])

    adf = adf.reset_index()
    del adf['index']
    if output_fname:
        adf.to_csv(os.path.join(temp_exp_dir,output_fname), index=False)
    return adf

def combine_trajectories(trajectories_base_name='./trajectories_', master_input_base='./master_input', \
                         output_name='./trajectoriesDat', summary_name_base='./summary', columns_to_include=['Ki']):
    
    #Function combines processed trajectories into output_name.csv.
    #Summary of how many runs successfully completed for each
    #simulations is written out in summary_name_base.txt.
    #Indices are decided based upon what is in master_input.csv.
    #Be sure that every index name in both the master_input.csv
    #and the trajectories.csv is unique!
    #The columns_to_include input is a list of columns in the
    #master_input_csv which you would like to include. The default
    #is Ki, but you could choose any column that you like!
    
    master_df = pd.read_csv(master_input_base + '.csv', index_col=0)
    master_columns = list(master_df.columns)
    
    #Isolating index columns...
    master_index_columns = []
    for col in master_columns:
        if 'index' in col:
            master_index_columns.append(col)
    
    summary = open(summary_name_base + '.txt', 'w')
    #Populating the list of dfs and writing to summary.txt
    df_list = []
    for index, row in master_df.iterrows():
        try:
            df_i = reprocess_new(trajectories_base_name + str(index) + '.csv')
            for index_col in master_index_columns:
                df_i[index_col] = row[index_col]
            for col in columns_to_include:
                df_i[col] = row[col]
            df_list.append(df_i)
            n_runs_successful = np.max(df_i['run_index'].values)+1
            summary.write(trajectories_base_name + str(index) + '.csv runs successfully completed: ' \
                      + str(n_runs_successful) + '\n') #Write to summary csv
        except:
            n_runs_successful = 0
            summary.write(trajectories_base_name + str(index) + '.csv runs successfully completed: ' \
                      + str(n_runs_successful) + '\n') #Write to summary csv
            continue
    summary.close()
    
    df_final = pd.concat(df_list)
    df_final.to_csv(output_name + '.csv', index=True)
    return df_final

### Credible interval shortcut functions.

def CI_5(x) :
    return np.percentile(x, 5)

def CI_95(x) :
    return np.percentile(x, 95)

def CI_25(x) :
    return np.percentile(x, 25)

def CI_75(x) :
    return np.percentile(x, 75)

def CI_2pt5(x) :
    return np.percentile(x, 2.5)

def CI_97pt5(x) :
    return np.percentile(x, 97.5)

def CI_50(x) :
    return np.percentile(x, 50)

def sample_plot(adf, allchannels, plot_fname=None, first_day=date(2020,2,20)):
    
    #Function plots whichever 'channels' you would like to see
    #in your data.
    
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

        ax.set_title(channel, y=1.05)

        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)) #bymonthday=first_day.day,
        ax.set_xlim(first_day, )
        
    fig.tight_layout()
    if plot_fname :
        plt.savefig(plot_fname)
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
