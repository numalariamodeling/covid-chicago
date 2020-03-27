import os
import subprocess
import matplotlib.pyplot as plt
import pandas as pd


## directories
user_path = os.path.expanduser('~')
exe_dir = os.path.join(user_path, 'Box/NU-malaria-team/projects/binaries/compartments/')

if "mrung" in user_path :
    git_dir = os.path.join(user_path, 'gitrepos/covid-chicago/age_structured')
    sim_output_path = os.path.join(user_path, 'Box/NU-malaria-team/projects/covid_chicago/cms_sim')

def runExp_simple() :

    file = open('runModel_testing.bat', 'w')
    file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(git_dir, "simplemodel_testing.cfg") +
                  '"' + ' -m ' + '"' + os.path.join( git_dir, "simplemodel_testing.emodl", ) + '"')
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
    offset_channels = ['hospitalized', 'critical', 'death']

    fig = plt.figure()
    ax = fig.gca()
    for channel in plotchannels :
            ax.plot(df['time'], df[channel], label=channel)
    ax.set_xlim(0,60)
    ax.legend()
    #plt.savefig(os.path.join(sim_output_path, 'sample_plot.png'))
    plt.show()


if __name__ == '__main__' :

    runExp_simple()
    df = reprocess()
    plot(df)


