import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import sys
sys.path.append('../')
from processing_helpers import *
from load_paths import load_box_paths

mpl.rcParams['pdf.fonttype'] = 42
testMode = True

exp_name = '20200412_TEST_simplemodel_4grp__rn44'
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

if testMode == True :
    sim_output_path = os.path.join(git_dir,'age_model', '_temp',exp_name)
    plot_path = sim_output_path
else :
    sim_output_path = os.path.join(wdir, 'simulation_output_age', exp_name)
    plot_path = sim_output_path

if not os.path.exists(sim_output_path):
    os.makedirs(sim_output_path)

if not os.path.exists(plot_path):
    os.makedirs(plot_path)

master_channel_list = ['susceptible', 'exposed', 'infectious', 'recovered']
custom_channel_list = ['susceptible', 'exposed', 'infectious', 'recovered']

first_day = date(2020, 2, 28)


def count_new(df, curr_ch) :

    ch_list = list(df[curr_ch].values)
    diff = [0] + [ch_list[x] - ch_list[x - 1] for x in range(1, len(df))]
    return diff



def calculate_mean_and_CI(adf, channel, output_filename=None) :

    mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
    if output_filename :
        mdf.to_csv(os.path.join(sim_output_path, output_filename), index=False)


def plot(adf,age_group,filename) :

    fig = plt.figure(figsize=(8,10))

    plotchannels = [ '%s_%s' % (x, age_group) for x in [
        'susceptible', 'exposed', 'infectious', 'recovered']]
    palette = sns.color_palette('muted', len(plotchannels))
    axes = [fig.add_subplot(4,1,x+1) for x in range(len(plotchannels))]
    fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
    for c, channel in enumerate(plotchannels) :

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

    plt.savefig(os.path.join(plot_path, '%s.png' % filename))


if __name__ == '__main__' :

    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    suffix_names = [x.split('_')[1] for x in df.columns.values if 'susceptible' in x]
    base_names = [x.split('_%s' % suffix_names[0])[0] for x in df.columns.values if suffix_names[0] in x]
    sample_index_names = [x for x in df.columns.values if ('num' in x or 'time' in x)]

    df = df[df['Ki'] == df.Ki.unique()[13]]  #mdf= mdf[mdf['Ki'] == mdf.Ki.unique()[2]]
    df.Ki.unique()

    for col in base_names :
        df['%s_%s' % (col, 'all')] = sum([df['%s_%s' % (col, age_group)] for age_group in suffix_names])

    suffix_names.append('all')
    for age_group in suffix_names :
        cols = sample_index_names + [ "%s_%s" % (channel, age_group) for channel in base_names]
        adf = df[cols]
        #adf = calculate_incidence(adf, age_group, output_filename='trajectoriesDat_withIncidence_%s.csv' % age_group)
        #adf['infections_cumul_%s' % age_group] = adf['asymp_cumul_%s' % age_group] + adf['symp_cumul_%s' % age_group]
        #for channel in ['infections_cumul_%s' % age_group, 'detected_cumul_%s' % age_group] :
        #    calculate_mean_and_CI(adf, channel, output_filename='%s.csv' % (channel, age_group))

        plot(adf, age_group, 'plot_withIncidence_Ki_0.15789816_%s' % age_group)

    # plt.show()

