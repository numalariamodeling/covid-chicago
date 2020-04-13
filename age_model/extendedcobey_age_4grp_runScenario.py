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
from simulation_setup import *

mpl.rcParams['pdf.fonttype'] = 42
testMode = False
Location = 'Local'  # 'NUCLUSTER'
datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()

emodl_dir = os.path.join(git_dir, 'age_model', 'emodl')
cfg_dir = os.path.join(git_dir, 'age_model', 'cfg')

today = date.today()


def define_group_dictionary(totalPop, ageGroups, ageGroupScale, initialAs):
    age_dic = {}
    for i, grp in enumerate(ageGroups):
        print(i, grp)
        age_dic[i] = [totalPop * ageGroupScale[i], initialAs[i]]
    return age_dic


def define_Species_initial(df, age_dic):
    df['speciesS_age0to19'] = age_dic[0][0]
    df['speciesS_age20to39'] = age_dic[1][0]
    df['speciesS_age40to59'] = age_dic[2][0]
    df['speciesS_age60to100'] = age_dic[3][0]

    df['initialAs_age0to19'] = age_dic[0][1]
    df['initialAs_age20to39'] = age_dic[1][1]
    df['initialAs_age40to59'] = age_dic[2][1]
    df['initialAs_age60to100'] = age_dic[3][1]

    df['N_age0to19'] = df['speciesS_age0to19'] + df['initialAs_age0to19']
    df['N_age20to39'] =df['speciesS_age20to39'] + df['initialAs_age20to39']
    df['N_age40to59'] = df['speciesS_age40to59'] + df['initialAs_age40to59']
    df['N_age60to100'] = df['speciesS_age60to100'] + df['initialAs_age60to100']

    return df


def replace_Species_initial(data, df, sample_nr):
    data = data.replace('@speciesS_age0to19@', str(df.speciesS_age0to19[sample_nr]))
    data = data.replace('@speciesS_age20to39@', str(df.speciesS_age20to39[sample_nr]))
    data = data.replace('@speciesS_age40to59@', str(df.speciesS_age40to59[sample_nr]))
    data = data.replace('@speciesS_age60to100@', str(df.speciesS_age60to100[sample_nr]))

    data = data.replace('@initialAs_age0to19@', str(df.initialAs_age0to19[sample_nr]))
    data = data.replace('@initialAs_age20to39@', str(df.initialAs_age20to39[sample_nr]))
    data = data.replace('@initialAs_age40to59@', str(df.initialAs_age40to59[sample_nr]))
    data = data.replace('@initialAs_age60to100@', str(df.initialAs_age60to100[sample_nr]))

    data = data.replace('@N_age0to19@', str(df.N_age0to19[sample_nr]))
    data = data.replace('@N_age20to39@', str(df.N_age20to39[sample_nr]))
    data = data.replace('@N_age40to59@', str(df.N_age40to59[sample_nr]))
    data = data.replace('@N_age60to100@', str(df.N_age60to100[sample_nr]))
    return data


def define_contact_matrix(df):
    ##  20200318_EMODKingCountyCovidInterventions.docx
    ##  Aggregated mean estimates from MUestimates_all_locations_2.xlsx
    df['C1_1'] = 0.425
    df['C1_2'] = 0.109
    df['C1_3'] = 0.068
    df['C1_4'] = 0.155
    df['C2_1'] = 0.109
    df['C2_2'] = 0.989
    df['C2_3'] = 0.150
    df['C2_4'] = 0.122
    df['C3_1'] = 0.068
    df['C3_2'] = 0.150
    df['C3_3'] = 0.483
    df['C3_4'] = 0.208
    df['C4_1'] = 0.155
    df['C4_2'] = 0.122
    df['C4_3'] = 0.208
    df['C4_4'] = 0.369
    return df


def replace_contact_param(data, df, sample_nr) :
    data = data.replace('@C1_4@', str(df.C1_4[sample_nr]))
    data = data.replace('@C1_3@', str(df.C1_3[sample_nr]))
    data = data.replace('@C1_2@', str(df.C1_2[sample_nr]))
    data = data.replace('@C1_1@', str(df.C1_1[sample_nr]))
    data = data.replace('@C2_4@', str(df.C2_4[sample_nr]))
    data = data.replace('@C2_3@', str(df.C2_3[sample_nr]))
    data = data.replace('@C2_2@', str(df.C2_2[sample_nr]))
    data = data.replace('@C2_1@', str(df.C2_1[sample_nr]))
    data = data.replace('@C3_4@', str(df.C3_4[sample_nr]))
    data = data.replace('@C3_3@', str(df.C3_3[sample_nr]))
    data = data.replace('@C3_2@', str(df.C3_2[sample_nr]))
    data = data.replace('@C3_1@', str(df.C3_1[sample_nr]))
    data = data.replace('@C4_4@', str(df.C4_4[sample_nr]))
    data = data.replace('@C4_3@', str(df.C4_3[sample_nr]))
    data = data.replace('@C4_2@', str(df.C4_2[sample_nr]))
    data = data.replace('@C4_1@', str(df.C4_1[sample_nr]))
    return data

# parameter samples
def generateParameterSamples(samples, pop, age_dic, first_day):
    df = pd.DataFrame()
    df['sample_num'] = range(samples)
    df['speciesS'] = pop
    df['initialAs'] = 10  # np.random.uniform(1, 5, samples)

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
    # df['fraction_critical'] = np.random.uniform(0.2, 0.5, samples)
    # df['fraction_critical'] = np.random.uniform(0.15, 0.35, samples)
    df['fraction_critical'] = np.random.uniform(0.15, 0.45, samples)
    # df['cfr'] = np.random.uniform(0.008, 0.022, samples)
    # df['cfr'] = np.random.uniform(0.0009, 0.0017, samples)
    # df['cfr'] = np.random.uniform(0.00445, 0.01185, samples)
    df['cfr'] = np.random.uniform(0.002675, 0.007775, samples)
    df['fraction_dead'] = df.apply(lambda x: x['cfr'] / x['fraction_severe'], axis=1)
    df['fraction_hospitalized'] = df.apply(lambda x: 1 - x['fraction_critical'] - x['fraction_dead'], axis=1)
    df['reduced_inf_of_det_cases'] = np.random.uniform(0.5, 0.9, samples)
    df['d_Sym'] = np.random.uniform(0.2, 0.3, samples)
    df['d_Sys'] = np.random.uniform(0.7, 0.9, samples)
    df['d_As'] = np.random.uniform(0, 0, samples)

    df['social_multiplier_1'] = np.random.uniform(0.9, 1, samples)
    df['social_multiplier_2'] = np.random.uniform(0.6, 0.9, samples)
    df['social_multiplier_3'] = np.random.uniform(0.005, 0.3, samples)  # 0.2, 0.6

    df['socialDistance_time1'] = DateToTimestep(date(2020, 3, 13), startdate=first_day)
    df['socialDistance_time2'] = DateToTimestep(date(2020, 3, 18), startdate=first_day)
    df['socialDistance_time3'] = DateToTimestep(date(2020, 3, 22), startdate=first_day)
    df = define_contact_matrix(df)
    df = define_Species_initial(df, age_dic)

    df.to_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"), index=False)
    return (df)


def replaceParameters(df, Ki_i, sample_nr, emodlname, scen_num):
    fin = open(os.path.join(temp_exp_dir, emodlname), "rt")
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
    data = data.replace('@Ki@', '%.09f' % Ki_i)
    data = data.replace('@social_multiplier_1@', str(df.social_multiplier_1[sample_nr]))
    data = data.replace('@social_multiplier_2@', str(df.social_multiplier_2[sample_nr]))
    data = data.replace('@social_multiplier_3@', str(df.social_multiplier_3[sample_nr]))
    data = data.replace('@socialDistance_time1@', str(df.socialDistance_time1[sample_nr]))
    data = data.replace('@socialDistance_time2@', str(df.socialDistance_time2[sample_nr]))
    data = data.replace('@socialDistance_time3@', str(df.socialDistance_time3[sample_nr]))

    data = replace_contact_param(data, df, sample_nr)
    data = replace_Species_initial(data, df, sample_nr)

    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_" + str(scen_num) + ".emodl"), "wt")
    fin.write(data)
    fin.close()


def generateScenarios(simulation_population, Kivalues, duration, monitoring_samples, nruns, sub_samples, modelname, age_dic,first_day):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population,  age_dic=age_dic,first_day=first_day)
    for sample in range(sub_samples):
        for i in Kivalues:
            scen_num += 1
            # print(i)

            # lst.append([simulation_population, sample, nruns, scen_num, i, Kval])
            lst.append([sample, scen_num, i])
            replaceParameters(df=dfparam, Ki_i=i, sample_nr=sample, emodlname=modelname, scen_num=scen_num)

            # adjust model.cfg
            fin = open(os.path.join(temp_exp_dir, "model.cfg"), "rt")
            data_cfg = fin.read()
            data_cfg = data_cfg.replace('@duration@', str(duration))
            data_cfg = data_cfg.replace('@monitoring_samples@', str(monitoring_samples))
            data_cfg = data_cfg.replace('@nruns@', str(nruns))
            data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
            fin.close()
            fin = open(os.path.join(temp_dir, "model_" + str(scen_num) + ".cfg"), "wt")
            fin.write(data_cfg)
            fin.close()

    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki'])
    df.to_csv(os.path.join(temp_exp_dir, "scenarios.csv"), index=False)
    return (scen_num)


if __name__ == '__main__':

    # ============================================================
    # Experiment design, fitting parameter and population
    # =============================================================

    region = 'NMH_catchment'

    exp_name = today.strftime("%Y%m%d") + '_%s_TEST_4grp_normalizedContacts_rn' % region + '_rn' + str(int(np.random.uniform(10, 99)))

    # Simlation setup (function in simulation_setup.py)
    populations, Kis, startdate = load_setting_parameter()

    simulation_population = populations[region]
    number_of_samples = 20
    number_of_runs = 3
    duration = 365
    monitoring_samples = 365  # needs to be smaller than duration


    emodlname = 'extendedmodel_cobey_age_4grp.emodl'

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder(
        cfg_dir=cfg_dir,
        exp_name=exp_name,
        emodl_dir=emodl_dir,
        emodlname=emodlname,
        temp_exp_dir = os.path.join(git_dir, 'age_model', '_temp', exp_name))

    ## Specify age population
    ageGroups_grp = ["0to19", "20to39", "40to59", "60to100"]
    ageGroupScale_grp = [0.249, 0.306, 0.253, 0.192]  ## NMH catchment area population age distribution
    initialAs_grp = [3, 3, 3, 3, 3, 3]

    age_dic = define_group_dictionary(totalPop=simulation_population,
                                      ageGroups=ageGroups_grp,
                                      ageGroupScale=ageGroupScale_grp,
                                      initialAs=initialAs_grp)


    # Parameter values
    Kivalues = np.linspace(0.005, 0.015, 5)   # Kis[region]
    first_day = startdate[region]


    nscen = generateScenarios(simulation_population,
                              Kivalues,
                              nruns=number_of_runs,
                              sub_samples=number_of_samples,
                              duration=duration,
                              monitoring_samples=monitoring_samples,
                              modelname=emodlname,
                              age_dic=age_dic,
                              first_day=first_day)


    generateSubmissionFile(trajectories_dir=trajectories_dir,temp_dir=temp_dir, temp_exp_dir=temp_exp_dir,scen_num=nscen, exp_name=exp_name)

if Location == 'Local':

    runExp(trajectories_dir=trajectories_dir, Location='Local')

    # Once the simulations are done
    #combineTrajectories(nscen)
    #cleanup(delete_temp_dir=False)
    #run postprocessing script
