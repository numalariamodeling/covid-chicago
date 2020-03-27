import os
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
from datetime import date, timedelta

## directories
user_path = os.path.expanduser('~')
exe_dir = os.path.join(user_path, 'Box/NU-malaria-team/projects/binaries/compartments/')

if "mrung" in user_path :
    git_dir = os.path.join(user_path, 'gitrepos/covid-chicago/')
    sim_output_path = os.path.join(user_path, 'Box/NU-malaria-team/projects/covid_chicago/cms_sim')

def runExp_simple(modelname="extendedmodel_covid.emodl") :

    file = open('runModel_testing.bat', 'w')
    file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(git_dir, "simplemodel_testing.cfg") +
                  '"' + ' -m ' + '"' + os.path.join( git_dir, modelname  ) + '"')
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
        df.to_csv(output_fname)
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


first_day = date(2020, 3, 1)

def plot_by_channel(adf) :

    fig = plt.figure(figsize=(8,6))
    palette = sns.color_palette('Set1', 10)
    allchannels = [x for x in df.columns.values if 'time' not in x]

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

    runExp_simple(modelname="extendedmodel_covid.emodl")
    runExp_simple(modelname="simplemodel_covid.emodl")
    df = reprocess()
    plot(df)
    plot_by_channel(df)


