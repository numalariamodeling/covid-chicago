import numpy as np
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import itertools
from scipy.interpolate import interp1d
import os
import shutil
from load_paths import load_box_paths

mpl.rcParams['pdf.fonttype'] = 42
testMode = False
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'age_model', 'emodl')
cfg_dir = os.path.join(git_dir, 'age_model', 'cfg')

today =  date.today()
exp_name = today.strftime("%Y%m%d") + '_extendedModel_cook_fitKi'

#emodlname = 'age_model_covid_noContactMix.emodl'
#emodlname = 'age_model_covid_homogeneousMixing_lowerPop.emodl'
#emodlname = 'age_extendedmodel_covid_pop5000.emodl'
emodlname = 'age_extendedmodel_covid_Pop1000.emodl'

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
temp_dir = os.path.join(git_dir,'age_model','_temp')
if not os.path.exists(temp_dir):
    os.makedirs(os.path.join(temp_dir))

## Copy emodl file  to experiment folder
if not os.path.exists(os.path.join(sim_output_path,emodlname)):
    shutil.copyfile(os.path.join(emodl_dir, emodlname) , os.path.join(sim_output_path,emodlname))

if not os.path.exists(os.path.join(sim_output_path, 'model.cfg')):
    shutil.copyfile(os.path.join(cfg_dir, 'model.cfg'), os.path.join(sim_output_path, 'model.cfg'))

# Select range for fitting parameter
Kivalues = np.random.uniform(5e-03, 1e-06, 10)

# Define scaling factors for the contact mixing between groups
#### ALL LOCATIONS
def define_Ki_contact_matrix(df):
    ##  20200318_EMODKingCountyCovidInterventions.docx
    ##  Aggregated mean estimates from MUestimates_all_locations_2.xlsx
	##  Estimates rescaled to that the sum of scaling factors is 1 (maintains Ki for total population)
    df['sKi1_4'] = 0.209526849
    df['sKi1_3'] = 0.039466462
    df['sKi1_2'] = 0.037694265
    df['sKi1_1'] = 0.015909742
    df['sKi2_4'] = 0.051521569
    df['sKi2_3'] = 0.293093246
    df['sKi2_2'] = 0.066737714
    df['sKi2_1'] = 0.02740285
    df['sKi3_4'] = 0.042740507
    df['sKi3_3'] = 0.046714807
    df['sKi3_2'] = 0.092046263
    df['sKi3_1'] = 0.027158353
    df['sKi4_4'] = 0.006685113
    df['sKi4_3'] = 0.004914879
    df['sKi4_2'] = 0.007194698
    df['sKi4_1'] = 0.031192683
    return df

def replace_Ki_contact_param(data, df, sample_nr) :
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
    return data


def define_intervention_param(df, startDate, reduction):
    df['socialDistance_start'] = startDate
    df['contactReduction'] = reduction
    return df

def replace_intervention_param(data, df, sample_nr) :
    data = data.replace('@socialDistance_start@', str(df.socialDistance_start[sample_nr]))
    data = data.replace('@contactReduction@', str(df.contactReduction[sample_nr]))
    return data

def generateParameterSamples(samples, pop=10000, Ki_contact_matrix = True, addIntervention=True ,interventionStart=10, coverage=0.4):
    df = pd.DataFrame()
    df['sample_num'] = range(samples)
    df['speciesS'] = pop
    df['initialAs'] = np.random.uniform(1, 5, samples)
    df['incubation_pd'] = np.random.uniform(4.2, 6.63, samples)
    df['time_to_infectious'] = np.random.uniform(0, df['incubation_pd'] , samples)  # placeholder and  time_to_infectious <= incubation_pd
    df['time_to_hospitalization'] = np.random.normal(5.76, 4.22, samples)
    df['time_to_critical'] = np.random.uniform(4, 9, samples)
    df['time_to_death'] = np.random.uniform(3, 11, samples)
    df['recovery_rate'] = np.random.uniform(6, 16, samples)
    df['fraction_hospitalized'] = np.random.uniform(0.1, 5, samples)
    df['fraction_symptomatic'] = np.random.uniform(0.5, 0.8, samples)
    df['fraction_critical'] = np.random.uniform(0.1, 5, samples)
    df['reduced_inf_of_det_cases'] = np.random.uniform(0.2, 0.3, samples)
    df['cfr'] = np.random.uniform(0.008, 0.022, samples)  #
    df['d_Sy'] = np.random.uniform(0.2, 0.3, samples)
    df['d_H'] = np.random.uniform(1, 1, samples)
    df['d_As'] = np.random.uniform(0, 0, samples)
    # df['Ki'] = Ki_i
    if Ki_contact_matrix==True :
         df = define_Ki_contact_matrix(df)

    if addIntervention==True :
         df = define_intervention_param(df, startDate=interventionStart, reduction=coverage)
    df.to_csv(os.path.join(sim_output_path, "sampled_parameters.csv"))
    return (df)


def replaceParameters(df, Ki_i, sample_nr, emodlname, Ki_contact_matrix = True, addIntervention=True):
    fin = open(os.path.join(emodl_dir,emodlname), "rt")
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

    if Ki_contact_matrix==True :
         data = replace_Ki_contact_param(data, df, sample_nr)

    if addIntervention==True :
         data = replace_intervention_param(data, df, sample_nr)

    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_i.emodl"), "wt")
    fin.write(data)
    fin.close()


def runExp(Kivalues, sub_samples, modelname) :
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=10000)
    for sample in range(sub_samples):
        for i in Kivalues:
            scen_num += 1
            print(i)
            lst.append([sample, scen_num, i])
            replaceParameters(df=dfparam, Ki_i=i, sample_nr=sample, emodlname=modelname)
            # adjust simplemodel.cfg
            fin = open(os.path.join(cfg_dir,"model.cfg"), "rt")
            data_cfg = fin.read()
            data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
            fin.close()
            fin = open(os.path.join(temp_dir,"model_i.cfg"), "wt")
            fin.write(data_cfg)
            fin.close()

            file = open('runModel_i.bat', 'w')
            file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(temp_dir,
                                                                                                             "model_i.cfg") +
                       '"' + ' -m ' + '"' + os.path.join(temp_dir, "simulation_i.emodl" ) + '"')
            file.close()

            subprocess.call([r'runModel_i.bat'])


    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki'])
    df.to_csv(os.path.join(sim_output_path,"scenarios.csv"))
    return (scen_num)


def reprocess(input_fname='trajectories.csv', output_fname=None):
    fname = os.path.join(git_dir, 'age_model',input_fname)
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
        adf.to_csv(os.path.join(sim_output_path,output_fname))
    return adf


def combineTrajectories(Nscenarios):
    scendf = pd.read_csv(os.path.join(sim_output_path,"scenarios.csv"))
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

    dfc = pd.concat(df_list)
    dfc.to_csv(os.path.join(sim_output_path,"trajectoriesDat.csv"))

    return dfc


def cleanup(Nscenarios) :
    if os.path.exists(os.path.join(sim_output_path,"trajectoriesDat.csv")):
        for scen_i in range(1, Nscenarios):
            input_name = "trajectories_scen" + str(scen_i) + ".csv"
            try:
                os.remove(os.path.join(git_dir, input_name))
            except:
                continue
    os.remove(os.path.join(temp_dir, "simulation_i.emodl"))
    os.remove(os.path.join(temp_dir, "model_i.cfg"))

# if __name__ == '__main__' :
nscen = runExp(Kivalues, sub_samples=10, modelname=emodlname)
combineTrajectories(nscen)
cleanup(nscen)
