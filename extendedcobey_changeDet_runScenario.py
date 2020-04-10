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
datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()

emodl_dir = os.path.join(git_dir, 'emodl')
cfg_dir = os.path.join(git_dir, 'cfg')

today = date.today()


# parameter samples
def generateParameterSamples(samples, pop):
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
    df['fraction_critical'] = np.random.uniform(0.2, 0.5, samples)
    df['cfr'] = np.random.uniform(0.002675, 0.007775, samples)
    df['fraction_dead'] = df.apply(lambda x: x['cfr'] / x['fraction_severe'], axis=1)
    df['fraction_hospitalized'] = df.apply(
        lambda x: 1 - x['fraction_critical'] - x['fraction_dead'] , axis=1)
    df['reduced_inf_of_det_cases'] = np.random.uniform(0.5, 0.9, samples)
    df['d_Sym'] = np.random.uniform(0.2, 0.3, samples)
    df['d_Sys'] = np.random.uniform(0.7, 0.9, samples)
    df['d_As'] = np.random.uniform(0, 0, samples)
    # df['Ki'] = np.random.uniform(2.e-7, 2.5e-7, samples)

    df['social_multiplier_1'] = np.random.uniform(0.9, 1, samples)
    df['social_multiplier_2'] = np.random.uniform(0.6, 0.9, samples)
    df['social_multiplier_3'] = np.random.uniform(0.005, 0.3, samples)  # 0.2, 0.6

    df['socialDistance_time1'] = 32  # 24  ## (+8 for NMH)
    df['socialDistance_time2'] = 37  # 29  ## (+8 for NMH)
    df['socialDistance_time3'] = 41  # 33  ## (+8 for NMH)

    df['detection_multiplier_1'] = np.random.uniform(0.00170516612048064, 0.00170516612048064, samples)
    df['detection_multiplier_1'] = np.random.uniform(0.00170516612048064, 0.00170516612048064, samples)
    df['detection_multiplier_2'] = np.random.uniform(0.00226467375376335, 0.00226467375376335, samples)
    df['detection_multiplier_3'] = np.random.uniform(0.00246449790850718, 0.00246449790850718, samples)
    df['detection_multiplier_4'] = np.random.uniform(0.00262435723230224, 0.00262435723230224, samples)
    df['detection_multiplier_5'] = np.random.uniform(0.00262435723230224, 0.00262435723230224, samples)
    df['detection_multiplier_6'] = np.random.uniform(0.0026376788426185, 0.0026376788426185, samples)
    df['detection_multiplier_7'] = np.random.uniform(0.00350358351317507, 0.00350358351317507, samples)
    df['detection_multiplier_8'] = np.random.uniform(0.00350358351317507, 0.00350358351317507, samples)
    df['detection_multiplier_9'] = np.random.uniform(0.00387658860203021, 0.00387658860203021, samples)
    df['detection_multiplier_10'] = np.random.uniform(0.00434284496309914, 0.00434284496309914, samples)
    df['detection_multiplier_11'] = np.random.uniform(0.00482242293448432, 0.00482242293448432, samples)
    df['detection_multiplier_12'] = np.random.uniform(0.00683398609223883, 0.00683398609223883, samples)
    df['detection_multiplier_13'] = np.random.uniform(0.0136546505741614, 0.0136546505741614, samples)
    df['detection_multiplier_14'] = np.random.uniform(0.0199690938640663, 0.0199690938640663, samples)
    df['detection_multiplier_15'] = np.random.uniform(0.0273226227586391, 0.0273226227586391, samples)
    df['detection_multiplier_16'] = np.random.uniform(0.0419231076652546, 0.0419231076652546, samples)
    df['detection_multiplier_17'] = np.random.uniform(0.0570298137638878, 0.0570298137638878, samples)
    df['detection_multiplier_18'] = np.random.uniform(0.0831401699837476, 0.0831401699837476, samples)
    df['detection_multiplier_19'] = np.random.uniform(0.110835797831242, 0.110835797831242, samples)
    df['detection_multiplier_20'] = np.random.uniform(0.13129779127701, 0.13129779127701, samples)
    df['detection_multiplier_21'] = np.random.uniform(0.152785548717129, 0.152785548717129, samples)
    df['detection_multiplier_22'] = np.random.uniform(0.189286760983668, 0.189286760983668, samples)
    df['detection_multiplier_23'] = np.random.uniform(0.221551701169637, 0.221551701169637, samples)
    df['detection_multiplier_24'] = np.random.uniform(0.286974129432766, 0.286974129432766, samples)
    df['detection_multiplier_25'] = np.random.uniform(0.339581168571657, 0.339581168571657, samples)
    df['detection_multiplier_26'] = np.random.uniform(0.369834545599872, 0.369834545599872, samples)
    df['detection_multiplier_27'] = np.random.uniform(0.405589747688701, 0.405589747688701, samples)
    df['detection_multiplier_28'] = np.random.uniform(0.469253723390083, 0.469253723390083, samples)
    df['detection_multiplier_29'] = np.random.uniform(0.537979911011643, 0.537979911011643, samples)
    df['detection_multiplier_30'] = np.random.uniform(0.581568219966429, 0.581568219966429, samples)
    df['detection_multiplier_31'] = np.random.uniform(0.640076732475422, 0.640076732475422, samples)
    df['detection_multiplier_32'] = np.random.uniform(0.713785202355261, 0.713785202355261, samples)
    df['detection_multiplier_33'] = np.random.uniform(0.78574854128367, 0.78574854128367, samples)
    df['detection_multiplier_34'] = np.random.uniform(0.838488796525724, 0.838488796525724, samples)
    df['detection_multiplier_35'] = np.random.uniform(0.915620920256841, 0.915620920256841, samples)
    df['detection_multiplier_36'] = np.random.uniform(1, 1, samples)

    df['detection_time_1'] = 14
    df['detection_time_2'] = 15
    df['detection_time_3'] = 16
    df['detection_time_4'] = 17
    df['detection_time_5'] = 18
    df['detection_time_6'] = 19
    df['detection_time_7'] = 20
    df['detection_time_8'] = 21
    df['detection_time_9'] = 22
    df['detection_time_10'] = 23
    df['detection_time_11'] = 24
    df['detection_time_12'] = 25
    df['detection_time_13'] = 26
    df['detection_time_14'] = 27
    df['detection_time_15'] = 28
    df['detection_time_16'] = 29
    df['detection_time_17'] = 30
    df['detection_time_18'] = 31
    df['detection_time_19'] = 32
    df['detection_time_20'] = 33
    df['detection_time_21'] = 34
    df['detection_time_22'] = 35
    df['detection_time_23'] = 36
    df['detection_time_24'] = 37
    df['detection_time_25'] = 38
    df['detection_time_26'] = 39
    df['detection_time_27'] = 40
    df['detection_time_28'] = 41
    df['detection_time_29'] = 42
    df['detection_time_30'] = 43
    df['detection_time_31'] = 44
    df['detection_time_32'] = 45
    df['detection_time_33'] = 46
    df['detection_time_34'] = 47
    df['detection_time_35'] = 48
    df['detection_time_36'] = 49

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

    data = data.replace('@detection_multiplier_1@', str(df.detection_multiplier_1[sample_nr]))
    data = data.replace('@detection_multiplier_2@', str(df.detection_multiplier_2[sample_nr]))
    data = data.replace('@detection_multiplier_3@', str(df.detection_multiplier_3[sample_nr]))
    data = data.replace('@detection_multiplier_4@', str(df.detection_multiplier_4[sample_nr]))
    data = data.replace('@detection_multiplier_5@', str(df.detection_multiplier_5[sample_nr]))
    data = data.replace('@detection_multiplier_6@', str(df.detection_multiplier_6[sample_nr]))
    data = data.replace('@detection_multiplier_7@', str(df.detection_multiplier_7[sample_nr]))
    data = data.replace('@detection_multiplier_8@', str(df.detection_multiplier_8[sample_nr]))
    data = data.replace('@detection_multiplier_9@', str(df.detection_multiplier_9[sample_nr]))
    data = data.replace('@detection_multiplier_10@', str(df.detection_multiplier_10[sample_nr]))
    data = data.replace('@detection_multiplier_11@', str(df.detection_multiplier_11[sample_nr]))
    data = data.replace('@detection_multiplier_12@', str(df.detection_multiplier_12[sample_nr]))
    data = data.replace('@detection_multiplier_13@', str(df.detection_multiplier_13[sample_nr]))
    data = data.replace('@detection_multiplier_14@', str(df.detection_multiplier_14[sample_nr]))
    data = data.replace('@detection_multiplier_15@', str(df.detection_multiplier_15[sample_nr]))
    data = data.replace('@detection_multiplier_16@', str(df.detection_multiplier_16[sample_nr]))
    data = data.replace('@detection_multiplier_17@', str(df.detection_multiplier_17[sample_nr]))
    data = data.replace('@detection_multiplier_18@', str(df.detection_multiplier_18[sample_nr]))
    data = data.replace('@detection_multiplier_19@', str(df.detection_multiplier_19[sample_nr]))
    data = data.replace('@detection_multiplier_20@', str(df.detection_multiplier_20[sample_nr]))
    data = data.replace('@detection_multiplier_21@', str(df.detection_multiplier_21[sample_nr]))
    data = data.replace('@detection_multiplier_22@', str(df.detection_multiplier_22[sample_nr]))
    data = data.replace('@detection_multiplier_23@', str(df.detection_multiplier_23[sample_nr]))
    data = data.replace('@detection_multiplier_24@', str(df.detection_multiplier_24[sample_nr]))
    data = data.replace('@detection_multiplier_25@', str(df.detection_multiplier_25[sample_nr]))
    data = data.replace('@detection_multiplier_26@', str(df.detection_multiplier_26[sample_nr]))
    data = data.replace('@detection_multiplier_27@', str(df.detection_multiplier_27[sample_nr]))
    data = data.replace('@detection_multiplier_28@', str(df.detection_multiplier_28[sample_nr]))
    data = data.replace('@detection_multiplier_29@', str(df.detection_multiplier_29[sample_nr]))
    data = data.replace('@detection_multiplier_30@', str(df.detection_multiplier_30[sample_nr]))
    data = data.replace('@detection_multiplier_31@', str(df.detection_multiplier_31[sample_nr]))
    data = data.replace('@detection_multiplier_32@', str(df.detection_multiplier_32[sample_nr]))
    data = data.replace('@detection_multiplier_33@', str(df.detection_multiplier_33[sample_nr]))
    data = data.replace('@detection_multiplier_34@', str(df.detection_multiplier_34[sample_nr]))
    data = data.replace('@detection_multiplier_35@', str(df.detection_multiplier_35[sample_nr]))
    data = data.replace('@detection_multiplier_36@', str(df.detection_multiplier_36[sample_nr]))
    data = data.replace('@detection_time_1@', str(df.detection_time_1[sample_nr]))
    data = data.replace('@detection_time_2@', str(df.detection_time_2[sample_nr]))
    data = data.replace('@detection_time_3@', str(df.detection_time_3[sample_nr]))
    data = data.replace('@detection_time_4@', str(df.detection_time_4[sample_nr]))
    data = data.replace('@detection_time_5@', str(df.detection_time_5[sample_nr]))
    data = data.replace('@detection_time_6@', str(df.detection_time_6[sample_nr]))
    data = data.replace('@detection_time_7@', str(df.detection_time_7[sample_nr]))
    data = data.replace('@detection_time_8@', str(df.detection_time_8[sample_nr]))
    data = data.replace('@detection_time_9@', str(df.detection_time_9[sample_nr]))
    data = data.replace('@detection_time_10@', str(df.detection_time_10[sample_nr]))
    data = data.replace('@detection_time_11@', str(df.detection_time_11[sample_nr]))
    data = data.replace('@detection_time_12@', str(df.detection_time_12[sample_nr]))
    data = data.replace('@detection_time_13@', str(df.detection_time_13[sample_nr]))
    data = data.replace('@detection_time_14@', str(df.detection_time_14[sample_nr]))
    data = data.replace('@detection_time_15@', str(df.detection_time_15[sample_nr]))
    data = data.replace('@detection_time_16@', str(df.detection_time_16[sample_nr]))
    data = data.replace('@detection_time_17@', str(df.detection_time_17[sample_nr]))
    data = data.replace('@detection_time_18@', str(df.detection_time_18[sample_nr]))
    data = data.replace('@detection_time_19@', str(df.detection_time_19[sample_nr]))
    data = data.replace('@detection_time_20@', str(df.detection_time_20[sample_nr]))
    data = data.replace('@detection_time_21@', str(df.detection_time_21[sample_nr]))
    data = data.replace('@detection_time_22@', str(df.detection_time_22[sample_nr]))
    data = data.replace('@detection_time_23@', str(df.detection_time_23[sample_nr]))
    data = data.replace('@detection_time_24@', str(df.detection_time_24[sample_nr]))
    data = data.replace('@detection_time_25@', str(df.detection_time_25[sample_nr]))
    data = data.replace('@detection_time_26@', str(df.detection_time_26[sample_nr]))
    data = data.replace('@detection_time_27@', str(df.detection_time_27[sample_nr]))
    data = data.replace('@detection_time_28@', str(df.detection_time_28[sample_nr]))
    data = data.replace('@detection_time_29@', str(df.detection_time_29[sample_nr]))
    data = data.replace('@detection_time_30@', str(df.detection_time_30[sample_nr]))
    data = data.replace('@detection_time_31@', str(df.detection_time_31[sample_nr]))
    data = data.replace('@detection_time_32@', str(df.detection_time_32[sample_nr]))
    data = data.replace('@detection_time_33@', str(df.detection_time_33[sample_nr]))
    data = data.replace('@detection_time_34@', str(df.detection_time_34[sample_nr]))
    data = data.replace('@detection_time_35@', str(df.detection_time_35[sample_nr]))
    data = data.replace('@detection_time_36@', str(df.detection_time_36[sample_nr]))


    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_" + str(scen_num) + ".emodl"), "wt")
    fin.write(data)
    fin.close()


def generateScenarios(simulation_population, Kivalues, duration, monitoring_samples, nruns, sub_samples, modelname):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population)
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
    master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild',
                           'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
    detection_channel_list = ['detected', 'detected_cumul', 'asymp_det_cumul', 'hosp_det_cumul']
    custom_channel_list = ['detected_cumul', 'symp_severe_cumul', 'asymp_det_cumul', 'hosp_det_cumul',
                           'symp_mild_cumul', 'asymp_cumul', 'hosp_cumul', 'crit_cumul']

    # ============================================================
    # Experiment design, fitting parameter and population
    # =============================================================

    exp_name = today.strftime("%Y%m%d") + '_TEST_detection_change' + '_rn' + str(int(np.random.uniform(10, 99)))

    # Selected SEIR model
    emodlname = 'extendedmodel_cobey_changeDetection.emodl'

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder()

    # Simlation setup
    simulation_population = 315000  # 1000  # 12830632 Illinois   # 2700000  Chicago  ## 315000 NMH catchment
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
    Kivalues = np.linspace(1.5e-6, 2e-6, 5)

    nscen = generateScenarios(simulation_population,
                              Kivalues,
                              nruns=number_of_runs,
                              sub_samples=number_of_samples,
                              duration=duration,
                              monitoring_samples=monitoring_samples,
                              modelname=emodlname)

    generateSubmissionFile(nscen, exp_name)

if Location == 'Local':
    runExp(trajectories_dir=trajectories_dir, Location='Local')

    # Once the simulations are done
    combineTrajectories(nscen)
    cleanup(delete_temp_dir=False)
    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))

    first_day = date(2020, 2, 28)
    sampleplot(df, allchannels=master_channel_list, plot_fname='main_channels.png')
    sampleplot(df, allchannels=detection_channel_list, plot_fname='detection_channels.png')
    sampleplot(df, allchannels=custom_channel_list, plot_fname='cumulative_channels.png')
