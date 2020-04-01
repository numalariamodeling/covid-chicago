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


def import_and_merge_chicago(mdf, chicago_filepath):
    
    #import and format chicago df
    chicago_df= df= pd.read_csv(chicago_filepath,index_col=0)
    chicago_df= chicago_df.reset_index()#.head()
    chicago_df['Date']=pd.to_datetime(chicago_df['Date'])
    
    mdf=pd.merge(mdf,
                 chicago_df[["Date",'confirmed_cases','cumulative_cases_calc']],
                 left_on='dates',
                 right_on='Date',how='left' )
    
    return(mdf)
    
    
def detection_plot(df,first_day, allchannels='detected_cumul', chicago=True, chicago_filepath=os.path.join(wdir,'chicago/chicago_cases.csv'), save=False, plotname="detected_plot"):
    
    """
    plotting function for plotting the detected channel from a trajectories_dat.
    
    inputs:
    df: trajectoriesDat dataframe (pd.dataframe)
    allchannels: single channel name to plot (string, optional)
    chicago: boolean to compare to the chicago_df data (bool, optional)
    save: boolean to save resulting plot (bool, optional)
        plotname: name of saved plot

    """
    
    #copy dataset (ensures we don't overwrite any data)
    adf= df.copy()
       
    # define pallet/fig
    fig = plt.figure(figsize=(8,6))
    palette = sns.color_palette('Set1', 10)
    
    #make composite key (time,Ki) aggregation for mean and confidence intervals
    mdf = adf.groupby(['time','Ki'])[allchannels].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
    #convert time to dates based off firstday
    dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
    mdf['dates']= pd.to_datetime(dates)
    
    ## boolean logic to merge chicago dataset in
    if chicago==True:
        mdf=import_and_merge_chicago(mdf,chicago_filepath )

    ##automating accounting if Ki is >1. if so, plot each Ki independnely, and don't fill in confidence intervals
    if len(df['Ki'].unique())>1:

        for element in range(0, len(mdf['Ki'].unique())):
            plt.plot(mdf.loc[(mdf['Ki']==mdf['Ki'].unique()[element]),'dates'],
                     mdf.loc[(mdf['Ki']==mdf['Ki'].unique()[element]),'mean'],
                     label='detected_SEIR_Ki={}'.format(mdf['Ki'].unique()[element]),
                     color=palette[element])
    
    else:
        plt.plot(mdf['dates'], mdf['mean'], label='detected_SEIR', color=palette[0])
        plt.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                        color=palette[0], linewidth=0, alpha=0.2)
        plt.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                        color=palette[0], linewidth=0, alpha=0.4)

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

    
   
   