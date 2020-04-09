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


def replace_Species_initial(data, df, sample_nr):
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


def define_Ki_contact_matrix(df):
    ##  20200318_EMODKingCountyCovidInterventions.docx
    ##  Aggregated mean estimates from MUestimates_all_locations_2.xlsx
    df['sKi1_1'] = 2.518895202
    df['sKi1_2'] = 0.648295899
    df['sKi1_3'] = 0.403854826
    df['sKi1_4'] = 0.922508934
    df['sKi1_5'] = 0.504057076
    df['sKi1_6'] = 0.412414524
    df['sKi1_7'] = 0.259550957
    df['sKi1_8'] = 0.05073959
    df['sKi2_1'] = 0.648295899
    df['sKi2_2'] = 5.857925743
    df['sKi2_3'] = 0.887561841
    df['sKi2_4'] = 0.727965387
    df['sKi2_5'] = 1.04261901
    df['sKi2_6'] = 0.684837537
    df['sKi2_7'] = 0.269607763
    df['sKi2_8'] = 0.042566135
    df['sKi3_1'] = 0.403854826
    df['sKi3_2'] = 0.887561841
    df['sKi3_3'] = 2.859730063
    df['sKi3_4'] = 1.235840304
    df['sKi3_5'] = 0.990130401
    df['sKi3_6'] = 0.859039248
    df['sKi3_7'] = 0.228935133
    df['sKi3_8'] = 0.033866765
    df['sKi4_1'] = 0.922508934
    df['sKi4_2'] = 0.727965387
    df['sKi4_3'] = 1.235840304
    df['sKi4_4'] = 2.193732214
    df['sKi4_5'] = 1.367833626
    df['sKi4_6'] = 0.898917596
    df['sKi4_7'] = 0.364703817
    df['sKi4_8'] = 0.045544761
    df['sKi5_1'] = 0.504057076
    df['sKi5_2'] = 1.04261901
    df['sKi5_3'] = 0.990130401
    df['sKi5_4'] = 1.367833626
    df['sKi5_5'] = 1.860524535
    df['sKi5_6'] = 1.034551661
    df['sKi5_7'] = 0.365736948
    df['sKi5_8'] = 0.061597604
    df['sKi6_1'] = 0.412414524
    df['sKi6_2'] = 0.684837537
    df['sKi6_3'] = 0.859039248
    df['sKi6_4'] = 0.898917596
    df['sKi6_5'] = 1.034551661
    df['sKi6_6'] = 1.409059589
    df['sKi6_7'] = 0.372508504
    df['sKi6_8'] = 0.076732159
    df['sKi7_1'] = 0.259550957
    df['sKi7_2'] = 0.269607763
    df['sKi7_3'] = 0.228935133
    df['sKi7_4'] = 0.364703817
    df['sKi7_5'] = 0.365736948
    df['sKi7_6'] = 0.372508504
    df['sKi7_7'] = 0.707152426
    df['sKi7_8'] = 0.146860318
    df['sKi8_1'] = 0.259550957
    df['sKi8_2'] = 0.269607763
    df['sKi8_3'] = 0.228935133
    df['sKi8_4'] = 0.364703817
    df['sKi8_5'] = 0.365736948
    df['sKi8_6'] = 0.372508504
    df['sKi8_7'] = 0.339232089
    df['sKi8_8'] = 0.386823814
    return df


def replace_Ki_contact_param(data, df, sample_nr) :
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


def makeExperimentFolder():
    sim_output_path = os.path.join(wdir, 'simulation_output_age', exp_name)
    plot_path = sim_output_path
    temp_exp_dir = os.path.join(git_dir, 'age_model', '_temp', exp_name)
    temp_dir = os.path.join(temp_exp_dir, 'simulations')
    trajectories_dir = os.path.join(temp_exp_dir, 'trajectories')
    if not os.path.exists(os.path.join(git_dir, '_temp')):
        os.makedirs(os.path.join(os.path.join(git_dir, '_temp')))
    if not os.path.exists(temp_exp_dir):
        os.makedirs(temp_exp_dir)
        os.makedirs(temp_dir)
        os.makedirs(trajectories_dir)
        os.makedirs(os.path.join(temp_exp_dir, 'log'))
        os.makedirs(os.path.join(trajectories_dir, 'log'))

    ## Copy emodl and cfg file  to experiment folder
    shutil.copyfile(os.path.join(emodl_dir, emodlname), os.path.join(temp_exp_dir, emodlname))
    shutil.copyfile(os.path.join(cfg_dir, 'model.cfg'), os.path.join(temp_exp_dir, 'model.cfg'))

    return temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path


# parameter samples
def generateParameterSamples(samples, pop, age_dic):
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

    df['socialDistance_time1'] = 24
    df['socialDistance_time2'] = 29
    df['socialDistance_time3'] = 33

    df = define_Ki_contact_matrix(df)
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

    data = replace_Ki_contact_param(data, df, sample_nr)
    data = replace_Species_initial(data, df, sample_nr)

    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_" + str(scen_num) + ".emodl"), "wt")
    fin.write(data)
    fin.close()


def generateScenarios(simulation_population, Kivalues, duration, monitoring_samples, nruns, sub_samples, modelname, age_dic,):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population,  age_dic=age_dic)
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

    exp_name = today.strftime("%Y%m%d") + '_TEST_8grp_rn' + str(int(np.random.uniform(10, 99)))

    # Simlation setup
    simulation_population = 315000  # 1000  # 12830632 Illinois   # 2700000  Chicago ## 315000 NMH catchment
    number_of_samples = 20
    number_of_runs = 3
    duration = 365
    monitoring_samples = 365  # needs to be smaller than duration

    ## Specify age population
    emodlname = 'extendedmodel_cobey_age_8grp.emodl'

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder()

    ### NMH catchment area population  age distribution
    ageGroups_grp = ["0to9", "10to19", "20to29", "30to39", "40to49", "50to59", "60to69", "70to100"]
    ageGroupScale_grp = [0.1256, 0.1233, 0.1404, 0.1652, 0.1338, 0.1196, 0.1012, 0.0909]

    ### Cook county age distribution
    #ageGroupScale_grp = [0.1211, 0.1204, 0.1487, 0.1513, 0.1269, 0.1260, 0.1070, 0.09863]

    initialAs_grp = [3, 3, 3, 3, 3, 3, 3, 3]

    age_dic = define_group_dictionary(totalPop=simulation_population,  # 2700000
                                      ageGroups=ageGroups_grp,
                                      ageGroupScale=ageGroupScale_grp,
                                      initialAs=initialAs_grp)


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
    Kivalues = np.linspace(1.5e-6, 2e-6, 3)  # np.linspace(2.e-7,2.5e-7,5) # np.logspace(-8, -4, 4)

    nscen = generateScenarios(simulation_population,
                              Kivalues,
                              nruns=number_of_runs,
                              sub_samples=number_of_samples,
                              duration=duration,
                              monitoring_samples=monitoring_samples,
                              modelname=emodlname,
                              age_dic=age_dic)

    generateSubmissionFile(nscen, exp_name)

if Location == 'Local':

    runExp(trajectories_dir=trajectories_dir, Location='Local')

    # Once the simulations are done
    #combineTrajectories(nscen)
    #cleanup(delete_temp_dir=False)
