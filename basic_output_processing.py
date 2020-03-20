import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

sim_output_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago/cms_sim'


def reprocess(output_fname=None) :

    fname = os.path.join(sim_output_path, 'trajectories.csv')
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


def calculate_other_channels(df, CFR, fraction_symptomatic, fraction_hospitalized,
                             fraction_critical, time_to_hospitalization,
                             time_to_critical, time_to_death) :

    fraction_death = CFR/(fraction_hospitalized * fraction_critical)

    df['time_hospitalized'] = df['time'] + time_to_hospitalization
    df['time_critical'] = df['time_hospitalized'] + time_to_critical
    df['time_death'] = df['time_critical'] + time_to_death

    df['symptomatic'] = df['infectious'] * fraction_symptomatic
    df['hospitalized'] = df['symptomatic'] * fraction_hospitalized
    df['critical'] = df['hospitalized'] * fraction_critical
    df['death'] = df['critical'] * fraction_death

    return df


def plot(df) :

    plotchannels = [x for x in df.columns.values if 'time' not in x]
    offset_channels = ['hospitalized', 'critical', 'death']

    fig = plt.figure()
    ax = fig.gca()
    for channel in plotchannels :
        if channel in offset_channels :
            ax.plot(df['time_%s' % channel], df[channel], label=channel)
        else :
            ax.plot(df['time'], df[channel], label=channel)
    ax.set_xlim(0,60)
    ax.legend()
    plt.savefig(os.path.join(sim_output_path, 'sample_plot.png'))
    plt.show()


def sample_and_plot(df) :

    CFR = 0.016
    fraction_symptomatic = 0.7
    fraction_hospitalized = 0.3
    fraction_critical = 0.8
    time_to_hospitalization = 6
    time_to_critical = 6
    time_to_death = 2

    df = calculate_other_channels(df, CFR, fraction_symptomatic, fraction_hospitalized,
                             fraction_critical, time_to_hospitalization,
                             time_to_critical, time_to_death)
    plot(df)


if __name__ == '__main__' :

    df = reprocess()
    sample_and_plot(df)