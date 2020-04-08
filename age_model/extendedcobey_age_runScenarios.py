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
import sys
sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *
from simulation_helpers import *

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

    if ageGroupSet == '4grp':
        df['speciesS_age0to19'] = age_dic[0][0]
        df['speciesS_age20to39'] = age_dic[1][0]
        df['speciesS_age40to59'] = age_dic[2][0]
        df['speciesS_age60to100'] = age_dic[3][0]

        df['initialAs_age0to19'] = age_dic[0][1]
        df['initialAs_age20to39'] = age_dic[1][1]
        df['initialAs_age40to59'] = age_dic[2][1]
        df['initialAs_age60to100'] = age_dic[3][1]

    elif ageGroupSet == '8grp':
        df['speciesS_age0to9'] = age_dic[0][0]
        df['speciesS_age10to19'] = age_dic[1][0]
        df['speciesS_age20to29'] = age_dic[2][0]
        df['speciesS_age30to39'] = age_dic[3][0]
        df['speciesS_age40to49'] = age_dic[4][0]
        df['speciesS_age50to59'] = age_dic[5][0]
        df['speciesS_age60to69'] = age_dic[6][0]
        df['speciesS_age70to100'] = age_dic[7][0]

        df['initialAs_age0to9'] = age_dic[0][1]
        df['initialAs_age10to19'] = age_dic[1][1]
        df['initialAs_age20to29'] = age_dic[2][1]
        df['initialAs_age30to39'] = age_dic[3][1]
        df['initialAs_age40to49'] = age_dic[4][1]
        df['initialAs_age50to59'] = age_dic[5][1]
        df['initialAs_age60to69'] = age_dic[6][1]
        df['initialAs_age70to100'] = age_dic[7][1]

    return df

def replace_Species_initial(data, df, sample_nr, ageGroupSet) :

    if ageGroupSet == '4grp':
        data = data.replace('@speciesS_age0to19@', str(df.speciesS_age0to19[sample_nr]))
        data = data.replace('@speciesS_age20to39@', str(df.speciesS_age20to39[sample_nr]))
        data = data.replace('@speciesS_age40to59@', str(df.speciesS_age40to59[sample_nr]))
        data = data.replace('@speciesS_age60to100@', str(df.speciesS_age60to100[sample_nr]))

        data = data.replace('@initialAs_age0to19@', str(df.initialAs_age0to19[sample_nr]))
        data = data.replace('@initialAs_age20to39@', str(df.initialAs_age20to39[sample_nr]))
        data = data.replace('@initialAs_age40to59@', str(df.initialAs_age40to59[sample_nr]))
        data = data.replace('@initialAs_age60to100@', str(df.initialAs_age60to100[sample_nr]))

    if ageGroupSet == '8grp':
        data = data.replace('@speciesS_age0to9@', str(df.speciesS_age0to9[sample_nr]))
        data = data.replace('@speciesS_age10to19@', str(df.speciesS_age10to19[sample_nr]))
        data = data.replace('@speciesS_age20to29@', str(df.speciesS_age20to29[sample_nr]))
        data = data.replace('@speciesS_age30to39@', str(df.speciesS_age30to39[sample_nr]))
        data = data.replace('@speciesS_age40to49@', str(df.speciesS_age40to49[sample_nr]))
        data = data.replace('@speciesS_age50to59@', str(df.speciesS_age50to59[sample_nr]))
        data = data.replace('@speciesS_age60to69@', str(df.speciesS_age60to69[sample_nr]))
        data = data.replace('@speciesS_age70to100@', str(df.speciesS_age70to100[sample_nr]))

        data = data.replace('@initialAs_age0to9@', str(df.initialAs_age0to9[sample_nr]))
        data = data.replace('@initialAs_age10to19@', str(df.initialAs_age10to19[sample_nr]))
        data = data.replace('@initialAs_age20to29@', str(df.initialAs_age20to29[sample_nr]))
        data = data.replace('@initialAs_age30to39@', str(df.initialAs_age30to39[sample_nr]))
        data = data.replace('@initialAs_age40to49@', str(df.initialAs_age40to49[sample_nr]))
        data = data.replace('@initialAs_age50to59@', str(df.initialAs_age50to59[sample_nr]))
        data = data.replace('@initialAs_age60to69@', str(df.initialAs_age60to69[sample_nr]))
        data = data.replace('@initialAs_age70to100@', str(df.initialAs_age70to100[sample_nr]))
    return data

def define_Ki_contact_matrix(df, ageGroupSet):
    ##  20200318_EMODKingCountyCovidInterventions.docx
    ##  Aggregated mean estimates from MUestimates_all_locations_2.xlsx
	##  Estimates rescaled to that the sum of scaling factors is 1 (maintains Ki for total population)

    if ageGroupSet == '4grp':
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

    elif ageGroupSet == '8grp' :
        df['sKi1_1'] = 0.0761629361427651
        df['sKi1_2'] = 0.0196022919639728
        df['sKi1_3'] = 0.0122112143720089
        df['sKi1_4'] = 0.0278935737177406
        df['sKi1_5'] = 0.0152409941053062
        df['sKi1_6'] = 0.0124700309317769
        df['sKi1_7'] = 0.00784794976124784
        df['sKi1_8'] = 0.00153419488422333
        df['sKi2_1'] = 0.0196022919639728
        df['sKi2_2'] = 0.177124012111205
        df['sKi2_3'] = 0.0268368909430618
        df['sKi2_4'] = 0.0220112298667518
        df['sKi2_5'] = 0.0315252992632548
        df['sKi2_6'] = 0.0207071884435741
        df['sKi2_7'] = 0.00815203379191477
        df['sKi2_8'] = 0.00128705705722352
        df['sKi3_1'] = 0.0122112143720089
        df['sKi3_2'] = 0.0268368909430618
        df['sKi3_3'] = 0.0864686382964874
        df['sKi3_4'] = 0.0373676626539042
        df['sKi3_5'] = 0.0299382199193964
        df['sKi3_6'] = 0.0259744634520253
        df['sKi3_7'] = 0.00692222999265651
        df['sKi3_8'] = 0.00102401728907355
        df['sKi4_1'] = 0.0278935737177406
        df['sKi4_2'] = 0.0220112298667518
        df['sKi4_3'] = 0.0373676626539042
        df['sKi4_4'] = 0.0663310988174002
        df['sKi4_5'] = 0.0413586976604434
        df['sKi4_6'] = 0.0271802508663495
        df['sKi4_7'] = 0.011027419288813
        df['sKi4_8'] = 0.00137712068721345
        df['sKi5_1'] = 0.0152409941053062
        df['sKi5_2'] = 0.0315252992632548
        df['sKi5_3'] = 0.0299382199193964
        df['sKi5_4'] = 0.0413586976604434
        df['sKi5_5'] = 0.0562560170141427
        df['sKi5_6'] = 0.031281369718711
        df['sKi5_7'] = 0.0110586577096286
        df['sKi5_8'] = 0.00186250480319021
        df['sKi6_1'] = 0.0124700309317769
        df['sKi6_2'] = 0.0207071884435741
        df['sKi6_3'] = 0.0259744634520253
        df['sKi6_4'] = 0.0271802508663495
        df['sKi6_5'] = 0.031281369718711
        df['sKi6_6'] = 0.042605232407188
        df['sKi6_7'] = 0.0112634068366254
        df['sKi6_8'] = 0.00232012294128771
        df['sKi7_1'] = 0.00784794976124784
        df['sKi7_2'] = 0.00815203379191477
        df['sKi7_3'] = 0.00692222999265651
        df['sKi7_4'] = 0.011027419288813
        df['sKi7_5'] = 0.0110586577096286
        df['sKi7_6'] = 0.0112634068366254
        df['sKi7_7'] = 0.021381915764784
        df['sKi7_8'] = 0.00444056307897012
        df['sKi8_1'] = 0.00784794976124784
        df['sKi8_2'] = 0.00815203379191477
        df['sKi8_3'] = 0.00692222999265651
        df['sKi8_4'] = 0.011027419288813
        df['sKi8_5'] = 0.0110586577096286
        df['sKi8_6'] = 0.0112634068366254
        df['sKi8_7'] = 0.0102572397143531
        df['sKi8_8'] = 0.0116962537313286
    return df

def replace_Ki_contact_param(data, df, sample_nr, ageGroupSet) :

    if ageGroupSet == '4grp':
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

    if ageGroupSet == '8grp' :
        data = data.replace('@sKi1_1@', str(df.sKi1_1[sample_nr]))
        data = data.replace('@sKi1_2@', str(df.sKi1_2[sample_nr]))
        data = data.replace('@sKi1_3@', str(df.sKi1_3[sample_nr]))
        data = data.replace('@sKi1_4@', str(df.sKi1_4[sample_nr]))
        data = data.replace('@sKi1_5@', str(df.sKi1_5[sample_nr]))
        data = data.replace('@sKi1_6@', str(df.sKi1_6[sample_nr]))
        data = data.replace('@sKi1_7@', str(df.sKi1_7[sample_nr]))
        data = data.replace('@sKi1_8@', str(df.sKi1_8[sample_nr]))
        data = data.replace('@sKi2_1@', str(df.sKi2_1[sample_nr]))
        data = data.replace('@sKi2_2@', str(df.sKi2_2[sample_nr]))
        data = data.replace('@sKi2_3@', str(df.sKi2_3[sample_nr]))
        data = data.replace('@sKi2_4@', str(df.sKi2_4[sample_nr]))
        data = data.replace('@sKi2_5@', str(df.sKi2_5[sample_nr]))
        data = data.replace('@sKi2_6@', str(df.sKi2_6[sample_nr]))
        data = data.replace('@sKi2_7@', str(df.sKi2_7[sample_nr]))
        data = data.replace('@sKi2_8@', str(df.sKi2_8[sample_nr]))
        data = data.replace('@sKi3_1@', str(df.sKi3_1[sample_nr]))
        data = data.replace('@sKi3_2@', str(df.sKi3_2[sample_nr]))
        data = data.replace('@sKi3_3@', str(df.sKi3_3[sample_nr]))
        data = data.replace('@sKi3_4@', str(df.sKi3_4[sample_nr]))
        data = data.replace('@sKi3_5@', str(df.sKi3_5[sample_nr]))
        data = data.replace('@sKi3_6@', str(df.sKi3_6[sample_nr]))
        data = data.replace('@sKi3_7@', str(df.sKi3_7[sample_nr]))
        data = data.replace('@sKi3_8@', str(df.sKi3_8[sample_nr]))
        data = data.replace('@sKi4_1@', str(df.sKi4_1[sample_nr]))
        data = data.replace('@sKi4_2@', str(df.sKi4_2[sample_nr]))
        data = data.replace('@sKi4_3@', str(df.sKi4_3[sample_nr]))
        data = data.replace('@sKi4_4@', str(df.sKi4_4[sample_nr]))
        data = data.replace('@sKi4_5@', str(df.sKi4_5[sample_nr]))
        data = data.replace('@sKi4_6@', str(df.sKi4_6[sample_nr]))
        data = data.replace('@sKi4_7@', str(df.sKi4_7[sample_nr]))
        data = data.replace('@sKi4_8@', str(df.sKi4_8[sample_nr]))
        data = data.replace('@sKi5_1@', str(df.sKi5_1[sample_nr]))
        data = data.replace('@sKi5_2@', str(df.sKi5_2[sample_nr]))
        data = data.replace('@sKi5_3@', str(df.sKi5_3[sample_nr]))
        data = data.replace('@sKi5_4@', str(df.sKi5_4[sample_nr]))
        data = data.replace('@sKi5_5@', str(df.sKi5_5[sample_nr]))
        data = data.replace('@sKi5_6@', str(df.sKi5_6[sample_nr]))
        data = data.replace('@sKi5_7@', str(df.sKi5_7[sample_nr]))
        data = data.replace('@sKi5_8@', str(df.sKi5_8[sample_nr]))
        data = data.replace('@sKi6_1@', str(df.sKi6_1[sample_nr]))
        data = data.replace('@sKi6_2@', str(df.sKi6_2[sample_nr]))
        data = data.replace('@sKi6_3@', str(df.sKi6_3[sample_nr]))
        data = data.replace('@sKi6_4@', str(df.sKi6_4[sample_nr]))
        data = data.replace('@sKi6_5@', str(df.sKi6_5[sample_nr]))
        data = data.replace('@sKi6_6@', str(df.sKi6_6[sample_nr]))
        data = data.replace('@sKi6_7@', str(df.sKi6_7[sample_nr]))
        data = data.replace('@sKi6_8@', str(df.sKi6_8[sample_nr]))
        data = data.replace('@sKi7_1@', str(df.sKi7_1[sample_nr]))
        data = data.replace('@sKi7_2@', str(df.sKi7_2[sample_nr]))
        data = data.replace('@sKi7_3@', str(df.sKi7_3[sample_nr]))
        data = data.replace('@sKi7_4@', str(df.sKi7_4[sample_nr]))
        data = data.replace('@sKi7_5@', str(df.sKi7_5[sample_nr]))
        data = data.replace('@sKi7_6@', str(df.sKi7_6[sample_nr]))
        data = data.replace('@sKi7_7@', str(df.sKi7_7[sample_nr]))
        data = data.replace('@sKi7_8@', str(df.sKi7_8[sample_nr]))
        data = data.replace('@sKi8_1@', str(df.sKi8_1[sample_nr]))
        data = data.replace('@sKi8_2@', str(df.sKi8_2[sample_nr]))
        data = data.replace('@sKi8_3@', str(df.sKi8_3[sample_nr]))
        data = data.replace('@sKi8_4@', str(df.sKi8_4[sample_nr]))
        data = data.replace('@sKi8_5@', str(df.sKi8_5[sample_nr]))
        data = data.replace('@sKi8_6@', str(df.sKi8_6[sample_nr]))
        data = data.replace('@sKi8_7@', str(df.sKi8_7[sample_nr]))
        data = data.replace('@sKi8_8@', str(df.sKi8_8[sample_nr]))
    return data


def makeExperimentFolder() :
    sim_output_path = os.path.join(wdir, 'simulation_output_age', exp_name)
    plot_path = sim_output_path
    # Create temporary folder for the simulation files
    # currently allowing to run only 1 experiment at a time locally
    temp_exp_dir = os.path.join(git_dir, 'age_model','_temp', exp_name)
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
    return (scen_num)

if __name__ == '__main__' :


    #============================================================
    # Experiment design, fitting parameter and population
    #=============================================================

    ageGroupSet = '8grp'
    ageGroupSet = '4grp'
    exp_name = today.strftime("%Y%m%d") + '_NMH_age_homogeneous_' + ageGroupSet + '_rn' + str(int(np.random.uniform(10, 99)))
    exp_description = " "

    # Simlation setup
    simulation_population = 2700000 #  1000  # 12830632 Illinois   # 2700000  Chicago ## 315000 NMH catchment
    number_of_samples = 20
    number_of_runs = 3
    duration = 365
    monitoring_samples = 365  # needs to be smaller than duration

    ## Specify age population
    if ageGroupSet == '4grp':
        emodlname =  'extendedmodel_cobey_age_4grp_homogeneous.emodl' #'extendedmodel_cobey_age_4grp_noS.emodl' #'extendedmodel_cobey_age_4grp.emodl'
        ageGroups_4grp = ["0to19","20to39","40to59","60to100"]
        ageGroupScale_4grp = [0.249, 0.306, 0.253,  0.192]  ## NMH catchment area population age distribution
        # ageGroupScale_4grp = []  ## Update with cook county age distribution for same age group
        initialAs_4grp = [3, 3, 3, 3, 3, 3]

        age_dic = define_group_dictionary(totalPop=simulation_population,  # 2700000
                                          ageGroups=ageGroupScale_4grp,
                                          ageGroupScale=ageGroupScale_4grp,
                                          initialAs=initialAs_4grp)


    elif ageGroupSet == '8grp':
        emodlname = 'extendedmodel_cobey_age_8grp.emodl'
        ageGroups_8grp = ["0to9" , "10to19" , "20to29", "30to39", "40to49", "50to59", "60to69", "70to100"]
        ageGroupScale_8grp = [0.1256 , 0.1233 , 0.1404 , 0.1652 , 0.1338 , 0.1196 , 0.1012 , 0.0909 ]  ## NMH catchment area population age distribution
        #ageGroupScale_8grp = []  ## Update with cook county age distribution for same age group
        initialAs_8grp = [3, 3, 3, 3, 3, 3, 3, 3]

        age_dic = define_group_dictionary(totalPop=simulation_population,  # 2700000
                                          ageGroups=ageGroupScale_8grp,
                                          ageGroupScale=ageGroupScale_8grp,
                                          initialAs=initialAs_8grp)

    # Time event
    #startDate = '02.20.2020'
    #socialDistance_time = [24, 29, 33]  # 22 ,  27 , 31

    # Parameter values
    Kivalues =  np.linspace(2.e-7,2.5e-7,5)# np.linspace(2.e-7,2.5e-7,5) # np.logspace(-8, -4, 4)

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder()

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
    runExp(trajectories_dir=trajectories_dir, Location='Local')

    # Once the simulations are done
    combineTrajectories(nscen)
    cleanup(delete_temp_dir=False)
