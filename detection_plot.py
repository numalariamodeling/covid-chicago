import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
from scipy.interpolate import interp1d
from load_paths import load_box_paths
from processing_helpers import CI_5, CI_95, CI_25, CI_75


## directories
user_path = os.path.expanduser('~')
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

testMode=True
#exp_name = '29032020_extendedModel_base_chicago'

if 'geickelb1' in user_path:
    wdir = os.path.join(user_path,'Box/covid_chicago/cms_sim/')
    exe_dir = os.path.join(user_path,'Desktop/compartments/')
    git_dir = os.path.join(user_path, 'Documents/Github/covid-chicago/')


if testMode == True :
    sim_output_path = os.path.join(wdir, 'sample_trajectories')
    plot_path= os.path.join(wdir ,'fitting/')
else :
    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = sim_output_path

if not os.path.exists(sim_output_path):
    os.makedirs(sim_output_path)

if not os.path.exists(plot_path):
    os.makedirs(plot_path)

master_channel_list = ['susceptible', 'exposed', 'infectious', 'symptomatic', 'detected',
                       'hospitalized', 'critical', 'death', 'recovered']

first_day = date(2020, 2, 24)

#specified_channels=['susceptible', 'exposed']

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
    origional plotting function
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
    
    
### data reading
chicago_df= df= pd.read_csv(
        os.path.join( wdir,'chicago/chicago_cases.csv'),
        index_col=0)
chicago_df= chicago_df.reset_index()#.head()
chicago_df['Date']=pd.to_datetime(chicago_df['Date'])

df= pd.read_csv(
        os.path.join( sim_output_path,'trajectoriesDat_v5.csv'),
        index_col=0)


###run the plot function:

detected_plot(df, allchannels='detected', chicago=True, save=True, plotname='detection_plot')



