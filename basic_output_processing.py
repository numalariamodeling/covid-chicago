import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

sim_output_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago/cms_sim/sample_trajectories'
#sim_output_path = '/Users/mrung/Box/NU-malaria-team/projects/covid_chicago/cms_sim'


def reprocess(input_fname='trajectories.csv', output_fname=None) :

    fname = os.path.join(sim_output_path, input_fname)
    df = pd.read_csv(fname, skiprows=1)
    num_samples = int((len(df)-1)/4)
    df = df.set_index('sampletimes').transpose()
    df = df.reset_index(drop=False)
    df = df.rename(columns={'index' : 'time'})
    df['time'] = df['time'].astype(float)

    adf = pd.DataFrame()
    for sample_num in range(num_samples) :
        channels = [x for x in df.columns.values if '{%d}' % sample_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x : x.split('{')[0] for x in channels
        })
        sdf['sample_num'] = sample_num
        adf = pd.concat([adf, sdf])

    adf = adf.reset_index()
    del adf['index']
    if output_fname :
        adf.to_csv(output_fname)
    return adf


def calculate_other_channels(df, CFR, fraction_symptomatic, fraction_hospitalized,
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

    df['downstream_sample_num'] = sample_num
    return df


def CI_5(x) :

    return np.percentile(x, 5)


def CI_95(x) :

    return np.percentile(x, 95)


def sample_and_plot(master_df, sub_samples) :

    # CFR = 0.016
    # fraction_symptomatic = 0.7
    # fraction_hospitalized = 0.3
    # fraction_critical = 0.8
    # time_to_hospitalization = 6
    # time_to_critical = 6
    # time_to_death = 2

    offset_channels = ['hospitalized', 'critical', 'death']

    fig = plt.figure()
    ax = fig.gca()
    palette = sns.color_palette('Set1', 8)

    adf = pd.DataFrame()
    for sim_sample, df in master_df.groupby('sample_num') :

        for sample in range(sub_samples) :

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
            adf = pd.concat([adf, df])

    allchannels = [x for x in adf.columns.values if ('time' not in x and 'sample' not in x)]
    for c, channel in enumerate(allchannels) :
        x_name = 'time' if channel not in offset_channels else 'time_%s' % channel
        mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95]).reset_index()
        x_data = mdf['time'] if channel not in offset_channels else adf.groupby('time')[x_name].agg(np.mean).reset_index()[x_name]
        ax.plot(x_data, mdf['mean'], label=channel, color=palette[c])
        ax.fill_between(x_data, mdf['CI_5'], mdf['CI_95'],
                        color=palette[c], linewidth=0, alpha=0.3)

    ax.set_xlim(0,60)
    ax.legend()
    plt.savefig(os.path.join(sim_output_path, 'sample_plot.png'))
    plt.show()


if __name__ == '__main__' :

    df = reprocess(input_fname='trajectories_multipleSeeds.csv')
    sample_and_plot(df, 1)
