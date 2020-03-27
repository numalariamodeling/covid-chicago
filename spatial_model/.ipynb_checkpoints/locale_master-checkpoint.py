import numpy as np
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import itertools
from scipy.interpolate import interp1d
import csv
import sys

mpl.rcParams['pdf.fonttype'] = 42
user_path = os.path.expanduser('~')

if "mrung" in user_path : 
    exe_dir = os.path.join(user_path, 'Box/NU-malaria-team/projects/binaries/compartments/')
    git_dir = os.path.join(user_path, 'gitrepos/covid-chicago/')
    #plot_path= os.path.join(project_dir,'fitting/') ###need to specify this for yourself
    ###adding these so we can import functions from other python files
    sys.path.append(git_dir)
    sys.path.append(os.path.join(git_dir, 'spatial_model/'))
elif 'geickelb1' in user_path:
    project_dir= os.path.join(user_path,'Box/covid_chicago/cms_sim/')
    exe_dir = os.path.join(user_path,'Desktop/compartments/')
    git_dir = os.path.join(user_path, 'Documents/Github/covid-chicago/')
    plot_path= os.path.join(project_dir,'fitting/')
    sys.path.append(git_dir)
    sys.path.append(os.path.join(git_dir, 'spatial_model/'))
    

    
master_channel_list = ['susceptible', 'exposed', 'infectious', 'symptomatic', 'detected',
                       'hospitalized', 'critical', 'death', 'recovered']

first_day = date(2020, 2, 24)

#### EMODL GENERATION###
from locale_emodl_generator import generate_locale_emodl, generate_locale_cfg

county_dic={}
county_n_limit=5 #just limits size for processing speed as we develop
cfg_filename='locale_test.CFG'
nruns= 3

###running with only first 10 counties (county_dic2):
with open('county_dic.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    i=0
    for row in reader:
        if i<county_n_limit:
            county_dic[row['county']]= [int(x) for x in row['val_list'].strip('][').split(', ')] 
            i+=1
        else:
            pass

param_dic={'ki':4.45e-6,
           'incubation_pd':6.63,
           'recovery_rate':16,
           'waning':180}

file_output='locale_covid.emodl'

# generating locale_covid.emodl
generate_locale_emodl(county_dic, param_dic,file_output, verbose=False)

# generate the CFG file
generate_locale_cfg(cfg_filename,nruns, filepath=cfg_filename)

#### most of this is Manuela's code from here on, some of the plot functions are mine, or modified by me

def runExp(Kivalues, sub_samples):
    lst = []
    scen_num = 0
    for sample in range(sub_samples):
        for i in Kivalues:
            scen_num += 1
            print(i)

            lst.append([sample, scen_num, i])
            define_and_replaceParameters(Ki_i=i)

            # adjust simplemodel.cfg
            fin = open("simplemodel.cfg", "rt")
            data_cfg = fin.read()
            data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
            fin.close()
            fin = open("simplemodel_i.cfg", "wt")
            fin.write(data_cfg)
            fin.close()

            file = open('runModel_i.bat', 'w')
            file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(git_dir,
                                                                                                             "simplemodel_i.cfg") +
                       '"' + ' -m ' + '"' + os.path.join(git_dir, "extendedmodel_covid_i.emodl", ) + '"')
            file.close()

            subprocess.call([r'runModel_i.bat'])

    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki'])
    df.to_csv("scenarios.csv")
    return (scen_num)

def reprocess(input_fname='trajectories.csv', output_fname=None):
    fname = os.path.join(git_dir, input_fname)
    row_df = pd.read_csv(fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    num_channels = len([x for x in df.columns.values if '{0}' in x])
    num_samples = int((len(row_df) - 1) / num_channels)

    df = df.reset_index(drop=False)
    df = df.rename(columns={'index': 'time'})
    df['time'] = df['time'].astype(float)

    adf = pd.DataFrame()
    for sample_num in range(num_samples):
        channels = [x for x in df.columns.values if '{%d}' % sample_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x: x.split('{')[0] for x in channels
        })
        sdf['sample_num'] = sample_num
        adf = pd.concat([adf, sdf])

    adf = adf.reset_index()
    del adf['index']
    if output_fname:
        adf.to_csv(output_fname)
    return adf

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
    
    
    def detected_plot(df, allchannels='detected', chicago=True, save=False, plotname="detected_plot"):
    
    """
    plotting function for plotting the detected channel from a trajectories_dat.
    
    inputs:
    df: trajectoriesDat dataframe (pd.dataframe)
    allchannels: single channel name to plot (string, optional)
    chicago: boolean to compare to the chicago_df data (bool, optional)
    save: boolean to save resulting plot (bool, optional)
        plotname: name of saved plot
    """
    #copy dataset and define pallet/fig
    adf= df.copy()
    fig = plt.figure(figsize=(8,6))
    palette = sns.color_palette('Set1', 10)
    
    #make composite key (time,Ki) aggregation for mean and confidence intervals
    mdf = adf.groupby(['time','Ki'])[allchannels].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
    #convert time to dates based off firstday
    mdf['dates']= pd.to_datetime([first_day + timedelta(days=int(x)) for x in mdf['time']])
    
    ## boolean logic to merge chicago dataset in
    if chicago==True:
        mdf=pd.merge(mdf,
                     chicago_df[["Date",'confirmed_cases','cumulative_cases_calc']],
                     left_on='dates',
                     right_on='Date',how='left' )

    ##automating accounting if Ki is >1. if so, plot each Ki independnely, and don't fill in confidence intervals
    if len(df['Ki'].unique())>1:
        
        for element in range(0, len(mdf['Ki'].unique())):
            plt.plot(mdf.loc[(mdf['Ki']==mdf['Ki'].unique()[element]),'dates'],
                     mdf.loc[(mdf['Ki']==mdf['Ki'].unique()[element]),'mean'],
                     label='detected_SEIR_Ki={}'.format(mdf['Ki'].unique()[element]),
                     color=palette[element])
    
    else:
        plt.plot(mdf['dates'], mdf['mean'], label='detected_SEIR', color=palette[0])
        plt.fill_between(mdf['dates'], mdf['CI_5'], mdf['CI_95'],
                        color=palette[0], linewidth=0, alpha=0.2)
        plt.fill_between(mdf['dates'], mdf['CI_25'], mdf['CI_75'],
                        color=palette[0], linewidth=0, alpha=0.4)
        plt.plot(mdf['dates'], mdf['cumulative_cases_calc'], label='detected_reported', color=palette[1])


    #if chicago is true, plot the chicago data
    if chicago==True:
        plt.plot(mdf['dates'], mdf['cumulative_cases_calc'], label='detected_reported')#, color=palette[element+1])

    plt.title('confirmed_cases')#, y=0.8)
    plt.legend()

    ax = plt.gca()

    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_xlim(first_day, )
    
    if save==True:
        plt.savefig(os.path.join(plot_path, '{}.png'.format(plotname)))
    plt.show()

    
    
def plot(adf, allchannels = master_channel_list, save=False) :
    """
    Manuela's origional plotting function
    """
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
        
        if save==True:
            plt.savefig(os.path.join(plot_path, 'sample_plot.png'))
    plt.show()