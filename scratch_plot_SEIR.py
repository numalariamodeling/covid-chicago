import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
from scipy.interpolate import interp1d

## directories
user_path = os.path.expanduser('~')
exe_dir = os.path.join(user_path, 'Box/NU-malaria-team/projects/binaries/compartments/')

if "mrung" in user_path :
    git_dir = os.path.join(user_path, 'gitrepos/covid-chicago/')
    sim_output_path = os.path.join(user_path, 'Box/NU-malaria-team/projects/covid_chicago/cms_sim')

master_channel_list = ['susceptible', 'exposed', 'infectious', 'symptomatic', 'detected',
                       'hospitalized', 'critical', 'death', 'recovered']
first_day = date(2020, 3, 1)


def CI_5(x) :

    return np.percentile(x, 5)


def CI_95(x) :

    return np.percentile(x, 95)


def CI_25(x) :

    return np.percentile(x, 25)


def CI_75(x) :

    return np.percentile(x, 75)

def plot(adf, allchannels = master_channel_list) :

    fig = plt.figure(figsize=(8,6))
    palette = sns.color_palette('Set1', 10)

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

    #plt.savefig(os.path.join(plot_path, 'sample_plot.png'))
    plt.show()


df = pd.read_csv(os.path.join(git_dir,'trajectoriesDat.csv'))
#f = df[df['Ki'] == 0.0009]
plot(df, allchannels=[ 'hospitalized','detected', 'critical', 'deaths'])
