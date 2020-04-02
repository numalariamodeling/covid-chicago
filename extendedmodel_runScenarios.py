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

mpl.rcParams['pdf.fonttype'] = 42
testMode = False
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

emodl_dir = os.path.join(git_dir, 'emodl')
cfg_dir = os.path.join(git_dir, 'cfg')

today = date.today()
exp_name = today.strftime("%Y%m%d") + '_extendedModel_withIntervention'

#emodlname = 'extendedmodel_covid.emodl'
emodlname = 'extendedmodel_covid_timeevent.emodl'


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
temp_dir = os.path.join(git_dir, '_temp')
if not os.path.exists(temp_dir):
    os.makedirs(os.path.join(temp_dir ))

## Copy emodl file  to experiment folder
if not os.path.exists(os.path.join(sim_output_path, emodlname)):
    shutil.copyfile(os.path.join(emodl_dir, emodlname), os.path.join(sim_output_path, emodlname))
if not os.path.exists(os.path.join(sim_output_path, 'model.cfg')):
    shutil.copyfile(os.path.join(cfg_dir, 'model.cfg'), os.path.join(sim_output_path, 'model.cfg'))

master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
detection_channel_list = ['detected', 'detected_cumul',  'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul',  'crit_det_cumul']
custom_channel_list = ['detected_cumul', 'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul', 'crit_det_cumul', 'symp_cumul',  'asymp_cumul','hosp_cumul', 'crit_cumul']

# Selected range values from SEIR Parameter Estimates.xlsx

Kivalues = np.random.uniform(0,0.3, 30)
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
        df['initialAs'] = np.random.uniform(1, 5,samples )
        df['incubation_pd'] = np.random.uniform(4.2, 6.63, samples)
        df['time_to_infectious'] = np.random.uniform(0, df['incubation_pd'], samples)  # placeholder and  time_to_infectious <= incubation_pd
        df['time_to_hospitalization'] = np.random.normal(5.9, 2,samples )
        df['time_to_critical'] = np.random.normal(5.9, 2,samples )
        df['time_to_death'] = np.random.uniform(1, 3,samples )
        df['recovery_rate'] = np.random.uniform(6, 16,samples )
        df['fraction_hospitalized'] = np.random.uniform(0.1, 5,samples )
        df['fraction_symptomatic'] = np.random.uniform(0.5, 0.8,samples )
        df['fraction_critical'] = np.random.uniform(0.1, 5,samples )
        df['reduced_inf_of_det_cases'] = np.random.uniform(0.2, 0.3,samples )
        df['cfr'] = np.random.uniform(0.008, 0.022,samples )
        df['d_Sy'] = np.random.uniform(0.2, 0.3,samples )
        df['d_H'] =  np.random.uniform(1, 1,samples )
        df['d_As'] = np.random.uniform(0, 0,samples )
        #df['Ki'] = Ki_i

        if addIntervention == True:
            df = define_intervention_param(df, startDate=interventionStart, reduction=coverage)

        df.to_csv(os.path.join(sim_output_path, "sampled_parameters.csv"))
        return(df)

def replaceParameters(df, Ki_i, sample_nr, emodlname, addIntervention=True) :
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
    # data = data.replace('@Ki@', str(df.Ki[sub_sample]))
    if addIntervention==True :
         data = replace_intervention_param(data, df, sample_nr)

    fin.close()
    fin = open(os.path.join(temp_dir, "simulation_i.emodl"), "wt")
    fin.write(data)
    fin.close()


def runExp(Kivalues, sub_samples, modelname):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=10000)
    for sample in range(sub_samples):
        for i in Kivalues:
            scen_num += 1
            print(i)

            lst.append([sample, scen_num, i])
            replaceParameters(df=dfparam, Ki_i=i, sample_nr= sample, emodlname=modelname )

            # adjust model.cfg
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

        if deleteFiles == True: os.remove(os.path.join(git_dir, input_name))

    dfc = pd.concat(df_list)
    dfc.to_csv( os.path.join(sim_output_path,"trajectoriesDat.csv"))

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
nscen = runExp(Kivalues, sub_samples=3, modelname=emodlname)
combineTrajectories(nscen)
cleanup(nscen)

df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
#df.params.unique()
#df= df[df['params'] == 9.e-05]

# Plots for quick check of simulation results
first_day = date(2020, 3, 1)
plot(df, allchannels=master_channel_list, plot_fname='main_channels.png')
plot(df, allchannels=detection_channel_list, plot_fname='detection_channels.png')
plot(df, allchannels=custom_channel_list, plot_fname='cumulative_channels.png')
