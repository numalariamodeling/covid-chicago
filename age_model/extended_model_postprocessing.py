import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
from processing_helpers import *
from load_paths import load_box_paths

mpl.rcParams['pdf.fonttype'] = 42
testMode = False

exp_name = '31032020_extendedModel_base_varyingKi'
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

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

master_channel_list = ['susceptible', 'exposed', 'infectious', 'symptomatic', 'detected',
                       'hospitalized', 'critical', 'deaths', 'recovered']
first_day = date(2020, 3, 1)


def count_new(df, curr_ch) :

    ch_list = list(df[curr_ch].values)
    diff = [0] + [ch_list[x] - ch_list[x - 1] for x in range(1, len(df))]
    return diff


def calculate_incidence(adf, age_group, output_filename=None) :

    inc_df = pd.DataFrame()
    for (samp, scen), df in adf.groupby(['sample_num', 'scen_num']) :

        sdf = pd.DataFrame( { 'time' : df['time'],
                              'new_exposures_%s' % age_group : [-1*x for x in count_new(df, 'susceptible_%s' % age_group)],
                              'new_asymptomatic_%s' % age_group : count_new(df, 'asymp_cumul_%s' % age_group),
                              'new_asymptomatic_detected_%s' % age_group : count_new(df, 'asymp_det_cumul_%s' % age_group),
                              'new_symptomatic_%s' % age_group : count_new(df, 'symp_cumul_%s' % age_group),
                              'new_symptomatic_detected_%s' % age_group : count_new(df, 'symp_det_cumul_%s' % age_group),
                              'new_hospitalized_%s' % age_group : count_new(df, 'hosp_cumul_%s' % age_group),
                              'new_detected_%s' % age_group : count_new(df, 'detected_cumul_%s' % age_group),
                              'new_critical_%s' % age_group : count_new(df, 'crit_cumul_%s' % age_group),
                              'new_deaths_%s' % age_group : count_new(df, 'deaths_%s' % age_group)
                              })
        sdf['sample_num'] = samp
        sdf['scen_num'] = scen
        inc_df = pd.concat([inc_df, sdf])
    adf = pd.merge(left=adf, right=inc_df, on=['sample_num', 'scen_num', 'time'])
    if output_filename :
        adf.to_csv(os.path.join(sim_output_path, output_filename), index=False)
    return adf


def calculate_mean_and_CI(adf, channel, output_filename=None) :

    mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
    if output_filename :
        mdf.to_csv(os.path.join(sim_output_path, output_filename), index=False)


def melter(df):
    """
    overview: melts columns of the grouped
    it woulda been fairly straight forward, but i wanted to automate the finding of columns we want to keep so we dont need ot specify which columns have the prefex and suffix, and which we want to keep.
    it should be all automatic now base_names splits a string into a list based on the "_" delimiter, and takes the first entry, but only if the entry list is longer than 1 and i do that for all column names
​
    suffix_list does same thing but takes the last entry and excludes a few suffixes (sample_num and scen_num).
    so it does a pretty good job at finding the "channels" (base_names) and the channel groups (suffix_names).
    i then make a list of booleans that loops over all column names and makes it true if any of the suffix_names match the col name.
    so the final result is a bool list of all columns we want to pivot.
​
    """

    # generating a list of base names in cols we might want to keep:
    # base_names = set([x.split('_')[0] for x in list(df) if len(x.split('_')) > 1 and x not in ['scen', 'sample']])
    # generating a list of suffix names in cols we might want to keep:
    # suffix_names = list(set([x.split('_')[-1] for x in list(df) if len(x.split('_')) > 1 and x not in ['sample_num', 'scen_num']]))
    #### automated wrangling columns wanted for melt
    col_bools = []
    for element in list(df):
        col_bools.append(any(substring in element for substring in suffix_names))
    ### melting from wide to long
    df_melted = pd.melt(df, id_vars=[x for x in list(df) if x not in list(df.loc[:, col_bools])],
                        value_vars=list(df.loc[:, col_bools]), var_name='channels')

    df_melted['base_channel'] = df_melted['channels'].apply(lambda x: "_".join(str(x).split('_')[:-1]))
    df_melted['base_group'] = df_melted['channels'].apply(lambda x: str(x).split('_')[-1])

    return (df_melted)


def plot(adf,age_group,filename) :

    fig = plt.figure(figsize=(12,6))

    plotchannels = [ '%s_%s' % (x, age_group) for x in [
        'susceptible', 'exposed', 'asymptomatic', 'symptomatic',
                    'detected', 'hospitalized', 'critical', 'deaths', 'recovered',
                    'new_detected', 'new_hospitalized', 'new_deaths']]
    palette = sns.color_palette('muted', len(plotchannels))
    axes = [fig.add_subplot(3,4,x+1) for x in range(len(plotchannels))]
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

    for col in base_names :
        df['%s_%s' % (col, 'all')] = sum([df['%s_%s' % (col, age_group)] for age_group in suffix_names])

    suffix_names.append('all')
    for age_group in suffix_names :
        cols = sample_index_names + [ "%s_%s" % (channel, age_group) for channel in base_names]
        adf = df[cols]
        adf = calculate_incidence(adf, age_group, output_filename='trajectoresDat_withIncidence_%s.csv' % age_group)
        adf['infections_cumul_%s' % age_group] = adf['asymp_cumul_%s' % age_group] + adf['symp_cumul_%s' % age_group]
        for channel in ['infections_cumul_%s' % age_group, 'detected_cumul_%s' % age_group] :
            calculate_mean_and_CI(adf, channel, output_filename='%s_%s.csv' % (channel, age_group))
        plot(adf, age_group, 'plot_withIncidence_%s' % age_group)

    # plt.show()
