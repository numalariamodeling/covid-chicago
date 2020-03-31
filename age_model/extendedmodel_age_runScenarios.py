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
from load_paths import load_box_paths
from processing_helpers import *
import shutil

mpl.rcParams['pdf.fonttype'] = 42
testMode = False
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

today =  date.today()
exp_name = today.strftime("%d%m%Y") + '_TEST_extendedModel_age_4grp'

#emodlname = 'age_model_covid_noContactMix.emodl'
emodlname = 'age_extendedmodel_covid.emodl'

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

## Copy emodl file  to experiment folder
if not os.path.exists(os.path.join(sim_output_path,emodlname)):
    shutil.copyfile(os.path.join(git_dir, 'age_model', emodlname) , os.path.join(sim_output_path,emodlname))

# Selected range values from SEIR Parameter Estimates.xlsx
# speciesS = [360980]   ## Chicago population + NHS market share 2705994 * 0.1334  - in infect
Kivalues = np.random.uniform(3.23107e-06, 4.7126e-06 , 3)   # [9e-05, 7e-06, 8e-06, 9e-06, 9e-077]

### Contact rates (scale factors)

#def defineContactScalingParameters () :


#plt.hist(Kivalues, bins=100)
#plt.show()

def define_Ki_contact_matrix(data) :
    ## placeholder values
    sKi1_4 = np.random.uniform(0.2, 0.3)
    sKi1_3 = np.random.uniform(0.4, 0.5)
    sKi1_2 = np.random.uniform(0.8, 0.9)
    sKi1_1 = np.random.uniform(0.9, 1)
    sKi2_4 = np.random.uniform(0.6, 0.8)
    sKi2_3 = np.random.uniform(0.8, 0.9)
    sKi2_2 = np.random.uniform(0.9, 1)
    sKi2_1 = sKi1_2
    sKi3_4 = np.random.uniform(0.8, 0.9)
    sKi3_3 = np.random.uniform(0.9, 1)
    sKi3_2 = sKi2_3
    sKi3_1 = sKi1_3
    sKi4_4 = np.random.uniform(0.9, 1)
    sKi4_3 = sKi3_4
    sKi4_2 = sKi2_4
    sKi4_1 = sKi1_4

    data = data.replace('@sKi1_4@', str(sKi1_4))
    data = data.replace('@sKi1_3@', str(sKi1_3))
    data = data.replace('@sKi1_2@', str(sKi1_2))
    data = data.replace('@sKi1_1@', str(sKi1_1))
    data = data.replace('@sKi2_4@', str(sKi2_4))
    data = data.replace('@sKi2_3@', str(sKi2_3))
    data = data.replace('@sKi2_2@', str(sKi2_2))
    data = data.replace('@sKi2_1@', str(sKi2_1))
    data = data.replace('@sKi3_4@', str(sKi3_4))
    data = data.replace('@sKi3_3@', str(sKi3_3))
    data = data.replace('@sKi3_2@', str(sKi3_2))
    data = data.replace('@sKi3_1@', str(sKi3_1))
    data = data.replace('@sKi4_4@', str(sKi4_4))
    data = data.replace('@sKi4_3@', str(sKi4_3))
    data = data.replace('@sKi4_2@', str(sKi4_2))
    data = data.replace('@sKi4_1@', str(sKi4_1))

    return data



def define_and_replaceParameters(inputfile , outputfile, Ki_i, Ki_contact_matrix = True):
    speciesS = 360980
    initialAs = np.random.uniform(1, 5)
    incubation_pd = np.random.uniform(4.2, 6.63)
    time_to_hospitalization = np.random.normal(5.9, 2)
    time_to_critical = np.random.normal(5.9, 2)
    time_to_death = np.random.uniform(1, 3)
    recovery_rate = np.random.uniform(6, 16)
    fraction_hospitalized = np.random.uniform(0.1, 5)
    fraction_symptomatic = np.random.uniform(0.5, 0.8)
    fraction_critical = np.random.uniform(0.1, 5)
    reduced_inf_of_det_cases = np.random.uniform(0,1)
    cfr = np.random.uniform(0.008, 0.022)
    d_Sy = np.random.uniform(0.2, 0.3)
    d_H = 1
    d_As = 0
    Ki = Ki_i

    fin = open(os.path.join(git_dir, 'age_model', inputfile), "rt")
    data = fin.read()
    data = data.replace('@speciesS@', str(speciesS))
    data = data.replace('@initialAs@', str(initialAs))
    data = data.replace('@incubation_pd@', str(incubation_pd))
    data = data.replace('@time_to_hospitalization@', str(time_to_hospitalization))
    data = data.replace('@time_to_critical@', str(time_to_critical))
    data = data.replace('@time_to_death@', str(time_to_death))
    data = data.replace('@fraction_hospitalized@', str(fraction_hospitalized))
    data = data.replace('@fraction_symptomatic@', str(fraction_symptomatic))
    data = data.replace('@fraction_critical@', str(fraction_critical))
    data = data.replace('@reduced_inf_of_det_cases@', str(reduced_inf_of_det_cases))
    data = data.replace('@cfr@', str(cfr))
    data = data.replace('@d_As@', str(d_As))
    data = data.replace('@d_Sy@', str(d_Sy))
    data = data.replace('@d_H@', str(d_H))
    data = data.replace('@recovery_rate@', str(recovery_rate))
    data = data.replace('@Ki@', str(Ki))

    if Ki_contact_matrix==True :
         data = define_Ki_contact_matrix(data)
    fin.close()

    fin = open(os.path.join(git_dir, 'age_model', outputfile), "wt")
    fin.write(data)
    fin.close()


def runExp(Kivalues, sub_samples, modelname):

    lst = []
    scen_num = 0
    for sample in range(sub_samples):
        for i in Kivalues:
            scen_num += 1
            print(i)

            lst.append([sample, scen_num, i])
            define_and_replaceParameters(Ki_i=i, inputfile = modelname, outputfile= "temp_i.emodl")

            # adjust simplemodel.cfg
            fin = open(os.path.join(git_dir,'age_model',"model.cfg"), "rt")
            data_cfg = fin.read()
            data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
            fin.close()
            fin = open(os.path.join(git_dir, 'age_model',"model_i.cfg"), "wt")
            fin.write(data_cfg)
            fin.close()

            file = open('runModel_i.bat', 'w')
            file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(git_dir, 'age_model', "model_i.cfg") +
                       '"' + ' -m ' + '"' + os.path.join(git_dir, 'age_model', "temp_i.emodl" ) + '"')
            file.close()

            subprocess.call([r'runModel_i.bat'])

    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki'])
    df.to_csv("scenarios.csv")
    return (scen_num)


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
        adf.to_csv(os.path.join(sim_output_path,output_fname))
    return adf


def combineTrajectories(Nscenarios, deleteFiles=False):
    scendf = pd.read_csv(os.path.join(git_dir,"scenarios.csv"))
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
    dfc.to_csv( os.path.join(sim_output_path,"trajectoriesDat.csv"))

    return dfc


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


# if __name__ == '__main__' :

nscen = runExp(Kivalues, sub_samples=3, modelname=emodlname)
combineTrajectories(nscen)

df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
#df.params.unique()
#df= df[df['params'] == 9.e-05]
first_day = date(2020, 10, 1)

#plot(df, allchannels=master_channel_list, plot_fname='main_channels.png')
#plot(df, allchannels=detection_channel_list, plot_fname='detection_channels.png')

plot(df, allchannels=['susceptible_age0to19','susceptible_age20to59','susceptible_age60to100',
                      'exposed_age0to19', 'exposed_age20to59', 'exposed_age60to100',
                       'detected_cumul_age0to19', 'detected_cumul_age20to59', 'detected_cumul_age60to100'], plot_fname='main_channels.png')

plot(df, allchannels=['hosp_cumul_age0to19','hosp_cumul_age20to59','hosp_cumul_age60to100',
                      'crit_cumul_age0to19', 'crit_cumul_age20to59', 'crit_cumul_age60to100',
                       'deaths_age0to19', 'deaths_age20to59', 'deaths_age60to100'], plot_fname='hosp_channels.png')


# generating a list of base names in cols we might want to keep:
base_names=set([x.split('_')[0] for x in list(df) if len(x.split('_'))>1 and x not in ['scen','sample']])
# generating a list of suffix names in cols we might want to keep:
suffix_names= list(set([x.split('_')[-1] for x in list(df) if len(x.split('_'))>1 and x not in['sample_num', 'scen_num']]))


#### automated wrangling columns wanted for melt
col_bools= []
for element in list(df):
    col_bools.append(any(substring in element for substring in suffix_names))
### melting from wide to long
dfm = pd.melt(df, id_vars=[x for x in list(df) if x not in list(df.loc[:,col_bools])], value_vars=list(df.loc[:,col_bools]), var_name='channels')

# dropping null value columns to avoid errors
dfm.dropna(inplace=True)

# new data frame with split value columns
new = dfm["Name"].str.split(" ", n=1, expand=True)

# making separate first name column from new data frame
dfm["First Name"] = new[0]

# making separate last name column from new data frame
dfm["Last Name"] = new[1]

# Dropping old Name columns
dfm.drop(columns=["Name"], inplace=True)
