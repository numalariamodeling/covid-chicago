import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
from scipy.interpolate import interp1d

mpl.rcParams['pdf.fonttype'] = 42

user_path = '/Users/jlg1657'
# user_path = '/Users/mrung'

wdir = os.path.join(user_path, 'Box/NU-malaria-team/projects/covid_chicago/cms_sim')
sim_output_path = os.path.join(wdir, 'sample_trajectories')
plot_path = os.path.join(wdir, 'sample_plots')


master_channel_list = ['susceptible', 'exposed', 'infectious', 'symptomatic', 'detected',
                       'hospitalized', 'critical', 'death', 'recovered']
first_day = date(2020, 3, 1)


def calculate_other_channels(df, CFR, fraction_symptomatic, fraction_hospitalized,
                             fraction_critical, time_to_hospitalization,
                             time_to_critical, time_to_death, sample_num=0) :

    fraction_death = CFR/(fraction_hospitalized * fraction_critical)

    h_time = int(time_to_hospitalization)
    pre_h_t_steps = len(df[df['time'] < h_time])
    c_time = h_time + int(time_to_critical)
    pre_c_t_steps = len(df[df['time'] < c_time])
    d_time = c_time + int(time_to_death)
    pre_d_t_steps = len(df[df['time'] < d_time])

    df['symptomatic'] = df['infectious'] * fraction_symptomatic

    df.loc[:, 'hospitalized'] = 0
    if pre_h_t_steps > 0 :
        hosp = list(df['symptomatic'] * fraction_hospitalized)[:-1*pre_h_t_steps]
    else :
        hosp = list(df['symptomatic'] * fraction_hospitalized)
    df.loc[df['time'] >= h_time, 'hospitalized'] = hosp

    df.loc[:, 'critical'] = 0
    crit = list(df['hospitalized'] * fraction_critical)[:-1*pre_c_t_steps]
    df.loc[df['time'] >= c_time, 'critical'] = crit

    df.loc[:, 'death'] = 0
    death = list(df['critical'] * fraction_death)[:-1*pre_d_t_steps]
    df.loc[df['time'] >= d_time, 'death'] = death

    df.loc[:, 'downstream_sample_num'] = sample_num
    return df


def CI_5(x) :

    return np.percentile(x, 5)


def CI_95(x) :

    return np.percentile(x, 95)


def CI_25(x) :

    return np.percentile(x, 25)


def CI_75(x) :

    return np.percentile(x, 75)


def sample_downstream_populations(master_df, sub_samples=1) :

    # CFR = 0.016
    # fraction_symptomatic = 0.7
    # fraction_hospitalized = 0.3
    # fraction_critical = 0.8
    # time_to_hospitalization = 6
    # time_to_critical = 6
    # time_to_death = 2


    adf = pd.DataFrame()

    master_df = master_df[master_df['Ki'] == 0.0009]

    for (sim_sample, scen), df in master_df.groupby(['sample_num', 'scen_num']) :

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

    return estimate_surveilled_cases(adf)


def estimate_surveilled_cases(adf) :

    prob_symptomatic_detected = 0.2
    prob_hospitalized_detected = 1

    adf['detected'] = adf['symptomatic'] * prob_symptomatic_detected + adf['hospitalized'] * prob_hospitalized_detected

    return adf


def plot(adf) :

    fig = plt.figure(figsize=(8,6))
    palette = sns.color_palette('Set1', 10)

    allchannels = master_channel_list
    axes = [fig.add_subplot(3,3,x+1) for x in range(len(allchannels))]
    fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
    for c, channel in enumerate(allchannels) :

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

    plt.savefig(os.path.join(plot_path, 'sample_plot.png'))
    plt.show()


if __name__ == '__main__' :

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    adf = sample_downstream_populations(df, 1)
    plot(adf)
