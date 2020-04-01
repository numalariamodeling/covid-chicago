import os
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.dates as mdates
from datetime import date, timedelta
from load_paths import load_box_paths

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')
cfg_dir = os.path.join(git_dir, 'cfg')

temp_dir = os.path.join(git_dir,'_temp')
if not os.path.exists(temp_dir):
    os.makedirs(os.path.join(temp_dir))

def define_and_replaceParameters(inputfile , outputfile):
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
    Ki = np.random.uniform(1e-6, 9e-5)

    fin = open(os.path.join(emodl_dir,inputfile), "rt")
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
    fin.close()

    fin = open(os.path.join(temp_dir,outputfile), "wt")
    fin.write(data)
    fin.close()

def runExp_simple(modelname) :

    define_and_replaceParameters(inputfile = modelname, outputfile= "simulation_i.emodl")

    file = open('runModel_testing.bat', 'w')
    file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(cfg_dir, "simplemodel_testing.cfg") +
                  '"' + ' -m ' + '"' + os.path.join(temp_dir, "simulation_i.emodl") + '"')
    file.close()
    subprocess.call([r'runModel_testing.bat'])

    return()

def reprocess(output_fname=None) :

    fname = os.path.join('trajectories.csv')
    df = pd.read_csv(fname, skiprows=1)
    df = df.set_index('sampletimes').transpose()
    df = df.reset_index(drop=False)
    df = df.rename(columns={'index' : 'time'})
    df['time'] = df['time'].astype(float)

    channels = [x for x in df.columns.values if '{' in x]
    df = df.rename(columns={
        x : x.split('{')[0] for x in channels
    })

    if output_fname :
        df.to_csv(os.path.join(temp_dir, output_fname))
    return df


def plot(df) :

    plotchannels = [x for x in df.columns.values if 'time' not in x]

    fig = plt.figure()
    ax = fig.gca()
    for channel in plotchannels :
            ax.plot(df['time'], df[channel], label=channel)
    ax.set_xlim(0,60)
    ax.legend()
    #plt.savefig(os.path.join(sim_output_path, 'sample_plot.png'))
    plt.show()


def plot_by_channel(adf) :

    fig = plt.figure(figsize=(8,6))
    allchannels = [x for x in df.columns.values if 'time' not in x]
    palette = sns.color_palette('Set1', len(allchannels))

    axes = [fig.add_subplot(3,3,x+1) for x in range(len(allchannels))]
    fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
    for c, channel in enumerate(allchannels) :

        mdf = adf.groupby('time')[channel].agg([np.mean]).reset_index()
        ax = axes[c]
        #dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
        ax.plot(df['time'], mdf['mean'], label=channel, color=palette[c])
        ax.set_title(channel, y=0.8)

        #formatter = mdates.DateFormatter("%m-%d")
        #ax.xaxis.set_major_formatter(formatter)
        #ax.xaxis.set_major_locator(mdates.MonthLocator())
        #ax.set_xlim(first_day, )
    plt.show()

if __name__ == '__main__' :

    runExp_simple(modelname="simplemodel_testing.emodl")
    df = reprocess()
    first_day = date(2020, 3, 1)  # arbitrary selection of starting date
    plot(df)
    plot_by_channel(df)


