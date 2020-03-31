import numpy as np
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
from load_paths import load_box_paths
import shutil

mpl.rcParams['pdf.fonttype'] = 42
testMode = False
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

today =  date.today()
exp_name = today.strftime("%d%m%Y") + '_extendedModel_base_Kirange'

#emodlname = 'age_model_covid_noContactMix.emodl'
emodlname = 'extendedmodel_covid.emodl'

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
if not os.path.exists(os.path.join(sim_output_path, emodlname)):
    shutil.copyfile(os.path.join(git_dir, emodlname), os.path.join(sim_output_path, emodlname))
if not os.path.exists(os.path.join(sim_output_path, 'simplemodel.cfg')):
    shutil.copyfile(os.path.join(git_dir, 'simplemodel.cfg'), os.path.join(sim_output_path, 'simplemodel.cfg'))




master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
detection_channel_list = ['detected', 'detected_cumul',  'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul',  'crit_det_cumul']
custom_channel_list = ['detected_cumul', 'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul', 'crit_det_cumul', 'symp_cumul',  'asymp_cumul','hosp_cumul', 'crit_cumul']

# Selected range values from SEIR Parameter Estimates.xlsx
# speciesS = [360980]   ## Chicago population + NHS market share 2705994 * 0.1334  - in infect
Kivalues = np.random.uniform(4e-02, 5e-06, 20)  # [9e-05, 7e-06, 8e-06, 9e-06, 9e-077]

#plt.hist(Kivalues, bins=100)
#plt.show()

def generateParameterSamples( samples, pop=10000):
        df =  pd.DataFrame()
        df['sample_num'] = range(samples)
        df['speciesS'] = pop
        df['initialAs'] = np.random.uniform(1, 5,samples )
        df['incubation_pd'] = np.random.uniform(4.2, 6.63, samples)
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
        df.to_csv(os.path.join(sim_output_path, "sampled_parameters.csv"))
        return(df)

def replaceParameters(df, Ki_i, sample_nr, emodlname="extendedmodel_covid.emodl") :
    fin = open(os.path.join(sim_output_path,emodlname), "rt")
    data = fin.read()
    data = data.replace('@speciesS@', str(df.speciesS[sample_nr]))
    data = data.replace('@initialAs@', str(df.initialAs[sample_nr]))
    data = data.replace('@incubation_pd@', str(df.incubation_pd[sample_nr]))
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
    fin.close()
    fin = open(os.path.join(sim_output_path, "simulation_i.emodl"), "wt")
    fin.write(data)
    fin.close()



def runExp(Kivalues, sub_samples):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=10000)
    for sample in range(sub_samples):
        for i in Kivalues:
            scen_num += 1
            print(i)

            lst.append([sample, scen_num, i])
            replaceParameters(df=dfparam, Ki_i=i, sample_nr= sample )

            # adjust simplemodel.cfg
            fin = open(os.path.join(sim_output_path,"simplemodel.cfg"), "rt")
            data_cfg = fin.read()
            data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
            fin.close()
            fin = open(os.path.join(sim_output_path,"simplemodel_i.cfg"), "wt")
            fin.write(data_cfg)
            fin.close()

            file = open('runModel_i.bat', 'w')
            file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(sim_output_path,
                                                                                                             "simplemodel_i.cfg") +
                       '"' + ' -m ' + '"' + os.path.join(sim_output_path, "simulation_i.emodl" ) + '"')
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

def CI_5(x) :

    return np.percentile(x, 5)


def CI_95(x) :

    return np.percentile(x, 95)


def CI_25(x) :

    return np.percentile(x, 25)


def CI_75(x) :

    return np.percentile(x, 75)

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

nscen = runExp(Kivalues, sub_samples=20)
combineTrajectories(nscen)

df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
#df.params.unique()
#df= df[df['params'] == 9.e-05]
first_day = date(2020, 3, 1)

plot(df, allchannels=master_channel_list, plot_fname='main_channels.png')
plot(df, allchannels=detection_channel_list, plot_fname='detection_channels.png')
plot(df, allchannels=custom_channel_list, plot_fname='cumulative_channels.png')
