import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from plotting.colors import load_color_palette

sim_output_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago/cms_sim'
raw_palette = load_color_palette('wes')
palette = { x : raw_palette[y] for (y,x) in enumerate([
    'susceptible',
    'exposed',
    'infectious',
    'recovered',
    'symptomatic',
    'hospitalized',
    'critical',
    'death'
])}

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


def calculate_other_channels(adf, CFR, fraction_symptomatic, fraction_hospitalized,
                             fraction_critical, time_to_hospitalization,
                             time_to_critical, time_to_death, sample_num=0) :

    fraction_death = CFR/(fraction_hospitalized * fraction_critical)

    df['time_hospitalized'] = df['time'] + time_to_hospitalization
    df['time_critical'] = df['time_hospitalized'] + time_to_critical
    df['time_death'] = df['time_critical'] + time_to_death

    df['symptomatic'] = df['infectious'] * fraction_symptomatic
    df['hospitalized'] = df['symptomatic'] * fraction_hospitalized
    df['critical'] = df['hospitalized'] * fraction_critical
    df['death'] = df['critical'] * fraction_death

    df['sample_num'] = sample_num
    return df


def plot(ax, df, channels=None, linewidth=1.0, alpha=1.0, label=False) :

    plotchannels = channels or [x for x in df.columns.values if 'time' not in x]
    plotchannels = [x for x in plotchannels if x != 'sample_num']
    offset_channels = ['hospitalized', 'critical', 'death']

    for channel in plotchannels :
        label = channel if label else ''
        if channel in offset_channels :
            ax.plot(df['time_%s' % channel], df[channel], label=label, linewidth=linewidth, alpha=alpha,
                    color=palette[channel])
        else :
            ax.plot(df['time'], df[channel], label=label, linewidth=linewidth, alpha=alpha,
                    color=palette[channel])


def sample_and_plot(df, samples) :

    CFR = 0.016
    fraction_symptomatic = 0.7
    fraction_hospitalized = 0.3
    fraction_critical = 0.8
    time_to_hospitalization = 6
    time_to_critical = 6
    time_to_death = 2

    offset_channels = ['hospitalized', 'critical', 'death']

    fig = plt.figure()
    ax = fig.gca()

    adf = pd.DataFrame()

    for sample in range(samples) :

        CFR = np.random.uniform(0.008, 0.022)
        fraction_symptomatic = np.random.uniform(0.5, 0.9)
        fraction_hospitalized = np.random.uniform(0.1, 0.5)
        fraction_critical = np.random.uniform(0.5, 1)

        time_to_hospitalization = np.random.normal(5.9, 2)
        time_to_critical = np.random.normal(5.9, 2)
        time_to_death = np.random.uniform(1, 3)

        df = calculate_other_channels(df, CFR, fraction_symptomatic, fraction_hospitalized,
                                      fraction_critical, time_to_hospitalization,
                                      time_to_critical, time_to_death)
        plot(ax, df, alpha=0.3, linewidth=0.5, channels=offset_channels, label=False)
        adf = pd.concat([adf, df])

    mdf = adf.groupby('time').agg(np.mean)
    plotchannels = [x for x in df.columns.values if 'time' not in x]
    plotchannels = [x for x in plotchannels if x not in offset_channels]
    plot(ax, df, channels=plotchannels, label=True)
    plot(ax, mdf, channels=offset_channels, label=True)

    ax.set_xlim(0,60)
    ax.legend()
    plt.savefig(os.path.join(sim_output_path, 'sample_plot.png'))
    plt.show()


if __name__ == '__main__' :

    df = reprocess()
    sample_and_plot(df, 10)
