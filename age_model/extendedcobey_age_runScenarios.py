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

emodl_dir = os.path.join(git_dir,'age_model', 'emodl')
cfg_dir = os.path.join(git_dir,'age_model', 'cfg')

today = date.today()


def define_group_dictionary(totalPop, ageGroups, ageGroupScale, initialAs):
    age_dic = {}
    for i, grp in enumerate(ageGroups):
        print(i, grp)
        age_dic[i] = [totalPop * ageGroupScale[i], initialAs[i]]
    return age_dic


def define_Species_initial(df, age_dic, ageGroupSet):
    ##  20200318_EMODKingCountyCovidInterventions.docx
    ##  Aggregated mean estimates from MUestimates_all_locations_2.xlsx
    ##  Estimates rescaled to that the sum of scaling factors is 1 (maintains Ki for total population)

    if ageGroupSet == 'Set1':
        df['speciesS_ageU5'] = age_dic[0][0]
        df['speciesS_age5to17'] = age_dic[1][0]
        df['speciesS_age18to64'] = age_dic[2][0]
        df['speciesS_age64to100'] = age_dic[3][0]

        df['initialAs_age0to19'] = age_dic[0][1]
        df['initialAs_age5to17'] = age_dic[1][1]
        df['initialAs_age18to64'] = age_dic[2][1]
        df['initialAs_age64to100'] = age_dic[3][1]

    ## COPIED VALUES FROM SET1 - they do not scale to 1 and for testing only, update with new extractions from contact matrix when available
    elif ageGroupSet == 'Set2':
        df['speciesS_age0to19'] = age_dic[0][0]
        df['speciesS_age20to44'] = age_dic[1][0]
        df['speciesS_age45to54'] = age_dic[2][0]
        df['speciesS_age55to64'] = age_dic[3][0]
        df['speciesS_age65to74'] = age_dic[4][0]
        df['speciesS_age75to84'] = age_dic[5][0]

        df['initialAs_age0to19'] = age_dic[0][1]
        df['initialAs_age20to44'] = age_dic[1][1]
        df['initialAs_age45to54'] = age_dic[2][1]
        df['initialAs_age55to64'] = age_dic[3][1]
        df['initialAs_age65to74'] = age_dic[4][1]
        df['initialAs_age75to84'] = age_dic[5][1]

    return df

def replace_Species_initial(data, df, sample_nr, ageGroupSet) :

    if ageGroupSet == 'Set1':
        data = data.replace('@speciesS_ageU5@', str(df.speciesS_ageU5[sample_nr]))
        data = data.replace('@speciesS_age5to17@', str(df.speciesS_age5to17[sample_nr]))
        data = data.replace('@speciesS_age18to64@', str(df.speciesS_age18to64[sample_nr]))
        data = data.replace('@speciesS_age64to100@', str(df.speciesS_age64to100[sample_nr]))

        data = data.replace('@initialAs_ageU5@', str(df.initialAs_ageU5[sample_nr]))
        data = data.replace('@initialAs_age5to17@', str(df.initialAs_age5to17[sample_nr]))
        data = data.replace('@initialAs_age18to64@', str(df.initialAs_age18to64[sample_nr]))
        data = data.replace('@initialAs_age64to100@', str(df.initialAs_age64to100[sample_nr]))

    if ageGroupSet == 'Set2':
        data = data.replace('@speciesS_age0to19@', str(df.speciesS_age0to19[sample_nr]))
        data = data.replace('@speciesS_age20to44@', str(df.speciesS_age20to44[sample_nr]))
        data = data.replace('@speciesS_age45to54@', str(df.speciesS_age45to54[sample_nr]))
        data = data.replace('@speciesS_age55to64@', str(df.speciesS_age55to64[sample_nr]))
        data = data.replace('@speciesS_age65to74@', str(df.speciesS_age65to74[sample_nr]))
        data = data.replace('@speciesS_age75to84@', str(df.speciesS_age75to84[sample_nr]))

        data = data.replace('@initialAs_age0to19@', str(df.initialAs_age0to19[sample_nr]))
        data = data.replace('@initialAs_age20to44@', str(df.initialAs_age20to44[sample_nr]))
        data = data.replace('@initialAs_age45to54@', str(df.initialAs_age45to54[sample_nr]))
        data = data.replace('@initialAs_age55to64@', str(df.initialAs_age55to64[sample_nr]))
        data = data.replace('@initialAs_age65to74@', str(df.initialAs_age65to74[sample_nr]))
        data = data.replace('@initialAs_age75to84@', str(df.initialAs_age75to84[sample_nr]))
    return data

def define_Ki_contact_matrix(df, ageGroupSet):
    ##  20200318_EMODKingCountyCovidInterventions.docx
    ##  Aggregated mean estimates from MUestimates_all_locations_2.xlsx
	##  Estimates rescaled to that the sum of scaling factors is 1 (maintains Ki for total population)

    if ageGroupSet == 'Set1':
        df['sKi1_1'] = 0.257686875216915
        df['sKi1_2'] = 0.0559508758329188
        df['sKi1_3'] = 0.0494614061407881
        df['sKi1_4'] = 0.013894156574477
        df['sKi2_1'] = 0.0559508758329188
        df['sKi2_2'] = 0.360461121322605
        df['sKi2_3'] = 0.0697648677126865
        df['sKi2_4'] = 0.0198730010097838
        df['sKi3_1'] = 0.0494614061407881
        df['sKi3_2'] = 0.0697648677126865
        df['sKi3_3'] = 0.113203219876234
        df['sKi3_4'] = 0.021342113533092
        df['sKi4_1'] = 0.013894156574477
        df['sKi4_2'] = 0.0198730010097838
        df['sKi4_3'] = 0.021342113533092
        df['sKi4_4'] = 0.0383623627804992


    ## COPIED VALUES FROM SET1 - they do not scale to 1 and for testing only, update with new extractions from contact matrix when available
    elif ageGroupSet == 'Set2' :
        df['sKi1_6'] = 0.209526849
        df['sKi1_5'] = 0.039466462
        df['sKi1_4'] = 0.209526849
        df['sKi1_3'] = 0.039466462
        df['sKi1_2'] = 0.037694265
        df['sKi1_1'] = 0.015909742

        df['sKi2_6'] = 0.051521569
        df['sKi2_5'] = 0.293093246
        df['sKi2_4'] = 0.051521569
        df['sKi2_3'] = 0.293093246
        df['sKi2_2'] = 0.066737714
        df['sKi2_1'] = 0.02740285

        df['sKi3_6'] = 0.042740507
        df['sKi3_5'] = 0.046714807
        df['sKi3_4'] = 0.042740507
        df['sKi3_3'] = 0.046714807
        df['sKi3_2'] = 0.092046263
        df['sKi3_1'] = 0.027158353

        df['sKi4_6'] = 0.006685113
        df['sKi4_5'] = 0.004914879
        df['sKi4_4'] = 0.006685113
        df['sKi4_3'] = 0.004914879
        df['sKi4_2'] = 0.007194698
        df['sKi4_1'] = 0.031192683

        df['sKi5_6'] = 0.006685113
        df['sKi5_5'] = 0.004914879
        df['sKi5_4'] = 0.006685113
        df['sKi5_3'] = 0.004914879
        df['sKi5_2'] = 0.007194698
        df['sKi5_1'] = 0.031192683

        df['sKi6_6'] = 0.006685113
        df['sKi6_5'] = 0.004914879
        df['sKi6_4'] = 0.006685113
        df['sKi6_3'] = 0.004914879
        df['sKi6_2'] = 0.007194698
        df['sKi6_1'] = 0.031192683
    return df

def replace_Ki_contact_param(data, df, sample_nr, ageGroupSet) :

    if ageGroupSet == 'Set1':
        data = data.replace('@sKi1_4@', str(df.sKi1_4[sample_nr]))
        data = data.replace('@sKi1_3@', str(df.sKi1_3[sample_nr]))
        data = data.replace('@sKi1_2@', str(df.sKi1_2[sample_nr]))
        data = data.replace('@sKi1_1@', str(df.sKi1_1[sample_nr]))
        data = data.replace('@sKi2_4@', str(df.sKi2_4[sample_nr]))
        data = data.replace('@sKi2_3@', str(df.sKi2_3[sample_nr]))
        data = data.replace('@sKi2_2@', str(df.sKi2_2[sample_nr]))
        data = data.replace('@sKi2_1@', str(df.sKi2_1[sample_nr]))
        data = data.replace('@sKi3_4@', str(df.sKi3_4[sample_nr]))
        data = data.replace('@sKi3_3@', str(df.sKi3_3[sample_nr]))
        data = data.replace('@sKi3_2@', str(df.sKi3_2[sample_nr]))
        data = data.replace('@sKi3_1@', str(df.sKi3_1[sample_nr]))
        data = data.replace('@sKi4_4@', str(df.sKi4_4[sample_nr]))
        data = data.replace('@sKi4_3@', str(df.sKi4_3[sample_nr]))
        data = data.replace('@sKi4_2@', str(df.sKi4_2[sample_nr]))
        data = data.replace('@sKi4_1@', str(df.sKi4_1[sample_nr]))

    if ageGroupSet == 'Set2':
        data = data.replace('@sKi1_6@', str(df.sKi1_6[sample_nr]))
        data = data.replace('@sKi1_5@', str(df.sKi1_5[sample_nr]))
        data = data.replace('@sKi1_4@', str(df.sKi1_4[sample_nr]))
        data = data.replace('@sKi1_3@', str(df.sKi1_3[sample_nr]))
        data = data.replace('@sKi1_2@', str(df.sKi1_2[sample_nr]))
        data = data.replace('@sKi1_1@', str(df.sKi1_1[sample_nr]))
        data = data.replace('@sKi2_6@', str(df.sKi2_6[sample_nr]))
        data = data.replace('@sKi2_5@', str(df.sKi2_5[sample_nr]))
        data = data.replace('@sKi2_4@', str(df.sKi2_4[sample_nr]))
        data = data.replace('@sKi2_3@', str(df.sKi2_3[sample_nr]))
        data = data.replace('@sKi2_2@', str(df.sKi2_2[sample_nr]))
        data = data.replace('@sKi2_1@', str(df.sKi2_1[sample_nr]))
        data = data.replace('@sKi3_6@', str(df.sKi3_6[sample_nr]))
        data = data.replace('@sKi3_5@', str(df.sKi3_5[sample_nr]))
        data = data.replace('@sKi3_4@', str(df.sKi3_4[sample_nr]))
        data = data.replace('@sKi3_3@', str(df.sKi3_3[sample_nr]))
        data = data.replace('@sKi3_2@', str(df.sKi3_2[sample_nr]))
        data = data.replace('@sKi3_1@', str(df.sKi3_1[sample_nr]))
        data = data.replace('@sKi4_6@', str(df.sKi4_6[sample_nr]))
        data = data.replace('@sKi4_5@', str(df.sKi4_5[sample_nr]))
        data = data.replace('@sKi4_4@', str(df.sKi4_4[sample_nr]))
        data = data.replace('@sKi4_3@', str(df.sKi4_3[sample_nr]))
        data = data.replace('@sKi4_2@', str(df.sKi4_2[sample_nr]))
        data = data.replace('@sKi4_1@', str(df.sKi4_1[sample_nr]))
        data = data.replace('@sKi5_6@', str(df.sKi5_6[sample_nr]))
        data = data.replace('@sKi5_5@', str(df.sKi5_5[sample_nr]))
        data = data.replace('@sKi5_4@', str(df.sKi5_4[sample_nr]))
        data = data.replace('@sKi5_3@', str(df.sKi5_3[sample_nr]))
        data = data.replace('@sKi5_2@', str(df.sKi5_2[sample_nr]))
        data = data.replace('@sKi5_1@', str(df.sKi5_1[sample_nr]))
        data = data.replace('@sKi6_6@', str(df.sKi6_6[sample_nr]))
        data = data.replace('@sKi6_5@', str(df.sKi6_5[sample_nr]))
        data = data.replace('@sKi6_4@', str(df.sKi6_4[sample_nr]))
        data = data.replace('@sKi6_3@', str(df.sKi6_3[sample_nr]))
        data = data.replace('@sKi6_2@', str(df.sKi6_2[sample_nr]))
        data = data.replace('@sKi6_1@', str(df.sKi6_1[sample_nr]))
    return data


def makeExperimentFolder() :
    sim_output_path = os.path.join(wdir, 'simulation_output_age', exp_name)
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
def generateParameterSamples(samples, pop, age_dic, ageGroupSet):
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
        #df['fraction_critical'] = np.random.uniform(0.2, 0.5, samples)
        #df['fraction_critical'] = np.random.uniform(0.15, 0.35, samples)
        df['fraction_critical'] = np.random.uniform(0.15, 0.45, samples)
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

        df['social_multiplier_1'] = np.random.uniform(0.9, 1, samples)
        df['social_multiplier_2'] = np.random.uniform(0.6, 0.9, samples)
        df['social_multiplier_3'] = np.random.uniform( 0.005 , 0.3, samples) #0.2, 0.6

        df['socialDistance_time1'] = 24
        df['socialDistance_time2'] = 29
        df['socialDistance_time3'] = 33
        
        df = define_Ki_contact_matrix(df, ageGroupSet=ageGroupSet)
        df = define_Species_initial(df, age_dic, ageGroupSet=ageGroupSet )

        df.to_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"), index=False)
        return(df)

def replaceParameters(df, Ki_i,  sample_nr, emodlname,  scen_num, ageGroupSet) :
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

    data = replace_Ki_contact_param(data, df, sample_nr, ageGroupSet=ageGroupSet)
    data = replace_Species_initial(data, df, sample_nr, ageGroupSet=ageGroupSet)

    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_"+str(scen_num)+".emodl"), "wt")
    fin.write(data)
    fin.close()

def writeTxt(txtdir, filename, textstring) :
    file = open(os.path.join(txtdir, filename), 'w')
    file.write(textstring)
    file.close()
    
def generateScenarios(simulation_population, Kivalues, duration, monitoring_samples, nruns, sub_samples,  modelname, age_dic, ageGroupSet):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population, ageGroupSet=ageGroupSet, age_dic=age_dic)
    for sample in range(sub_samples):
        for i in Kivalues:
            scen_num += 1
            #print(i)

            #lst.append([simulation_population, sample, nruns, scen_num, i, Kval])
            lst.append([sample, scen_num, i])
            replaceParameters(df=dfparam, Ki_i=i, sample_nr= sample, emodlname=modelname, scen_num=scen_num, ageGroupSet = ageGroupSet)

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
    if not exp_description == None :
        writeTxt(temp_exp_dir, 'exp_description.txt', exp_description )
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


if __name__ == '__main__' :

    master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild',
                           'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
    detection_channel_list = ['detected', 'detected_cumul', 'asymp_det_cumul', 'hosp_det_cumul']
    custom_channel_list = ['detected_cumul', 'symp_severe_cumul', 'asymp_det_cumul', 'hosp_det_cumul',
                           'symp_mild_cumul', 'asymp_cumul', 'hosp_cumul', 'crit_cumul']

    #============================================================
    # Experiment design, fitting parameter and population
    #=============================================================

    exp_name = today.strftime("%Y%m%d") + '_mr_test_age_6grp' + '_rn' + str(int(np.random.uniform(10, 99)))
    exp_description = "Test running time for full age model and 6 grp (contact matrix placeholders)"

    # Selected SEIR model
    emodlname = "age_cobeymodel_covid_6grp.emodl"
    ageGroupSet = 'Set2'

    #emodlname =  'age_cobeymodel_covid_6agegrp_pop1000.emodl' # 'age_colbeymodel_covid_4agegrp_pop1000.emodl'
    #ageGroupSet = 'Set2'

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder()

    # Simlation setup
    simulation_population = 2700000 #2700000  #  1000  # 12830632 Illinois   # 2700000  Chicago
    number_of_samples = 3
    number_of_runs = 2
    duration = 365
    monitoring_samples = 365  # needs to be smaller than duration

    # Age specification
    ageGroups_4grp=['ageU5', 'age5to17', 'age18to64', 'age64to100']
    ageGroupScale_4grp = [0.062, 0.203, 0.606, 0.129]
    initialAs_4grp = [3, 3, 3, 3, 3, 3]

    ageGroups_6grp = ['age0to19', 'age20to44', 'age45to54', 'age55to64', 'age65to74','age75to84']
    ageGroupScale_6grp = [0.226, 0.412, 0.120, 0.112, 0.075, 0.038]
    initialAs_6grp = [3, 3, 3, 3, 3, 3]

    age_dic = define_group_dictionary(totalPop=simulation_population,  # 2700000
                                      ageGroups=ageGroupScale_6grp,
                                      ageGroupScale=ageGroupScale_6grp,
                                      initialAs=initialAs_6grp)

    # Time event
    #startDate = '02.20.2020'
    #socialDistance_time = [24, 29, 33]  # 22 ,  27 , 31

    # Parameter values
    Kivalues =  np.linspace(2.e-7,2.5e-7,5)# np.linspace(2.e-7,2.5e-7,5) # np.logspace(-8, -4, 4)

    nscen = generateScenarios(simulation_population,
                              Kivalues,
                              nruns=number_of_runs,
                              sub_samples=number_of_samples,
                              duration = duration,
                              monitoring_samples = monitoring_samples,
                              modelname=emodlname,
                              age_dic = age_dic,
                              ageGroupSet =ageGroupSet)

    generateSubmissionFile(nscen, exp_name)
  
  if Location == 'Local' :
    runExp(Location='Local')

    # Once the simulations are done
    combineTrajectories(500)
    cleanup(delete_temp_dir=False)
