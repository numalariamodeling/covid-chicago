### Extended Cobey Condensed Simulation Processor
### Runs everything after actually running the simulations with CMS.
### extendedcobey_condensed_pt1.py handles everything prior-simulation.
### Reese Richardson 4-10-20

import numpy as np
import pandas as pd
import itertools
import os

from datetime import date, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

def reprocess(input_fname='trajectories.csv', output_fname=None):
    
    #Function combines the trajectories of each run
    #in a single simulation into a DataFrame. 
    #"Run Number" is stored as run_index.
    #Called by combine_trajectories.
    
    row_df = pd.read_csv(input_fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    run_time = len([x for x in df.columns.values if '{0}' in x])
    num_runs = int((len(row_df)) / run_time)

    df = df.reset_index(drop=False)
    df = df.rename(columns={'index': 'time'})
    df['time'] = df['time'].astype(float)

    adf = pd.DataFrame()
    for run_num in range(num_runs):
        channels = [x for x in df.columns.values if '{%d}' % run_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x: x.split('{')[0] for x in channels
        })
        sdf['run_index'] = run_num
        adf = pd.concat([adf, sdf])

    adf = adf.reset_index()
    del adf['index']
    if output_fname:
        adf.to_csv(os.path.join(temp_exp_dir,output_fname), index=False)
    return adf

def combine_trajectories(trajectories_base_name='./trajectories_', master_input_base='./master_input', \
                         output_name='./trajectoriesDat', summary_name_base='./summary', columns_to_include=['Ki']):
    
    #Function combines processed trajectories into output_name.csv.
    #Summary of how many runs successfully completed for each
    #simulations is written out in summary_name_base.txt.
    #Indices are decided based upon what is in master_input.csv.
    #Be sure that every index name in both the master_input.csv
    #and the trajectories.csv is unique!
    #The columns_to_include input is a list of columns in the
    #master_input_csv which you would like to include. The default
    #is Ki, but you could choose any column that you like!
    
    master_df = pd.read_csv(master_input_base + '.csv', index_col=0)
    master_columns = list(master_df.columns)
    
    #Isolating index columns...
    master_index_columns = []
    for col in master_columns:
        if 'index' in col:
            master_index_columns.append(col)
    
    summary = open(summary_name_base + '.txt', 'w')
    #Populating the list of dfs and writing to summary.txt
    df_list = []
    for index, row in master_df.iterrows():
        try:
            df_i = reprocess(trajectories_base_name + str(index) + '.csv')
            for index_col in master_index_columns:
                df_i[index_col] = row[index_col]
            for col in columns_to_include:
                df_i[col] = row[col]
            df_list.append(df_i)
            n_runs_successful = np.max(df_i['run_index'].values)+1
            summary.write(trajectories_base_name + str(index) + '.csv runs successfully completed: ' \
                      + str(n_runs_successful) + '\n') #Write to summary csv
        except:
            n_runs_successful = 0
            summary.write(trajectories_base_name + str(index) + '.csv runs successfully completed: ' \
                      + str(n_runs_successful) + '\n') #Write to summary csv
            continue
    summary.close()
    
    df_final = pd.concat(df_list)
    df_final.to_csv(output_name + '.csv', index=True)
    return df_final

### Credible interval shortcut functions.

def CI_5(x) :
    return np.percentile(x, 5)

def CI_95(x) :
    return np.percentile(x, 95)

def CI_25(x) :
    return np.percentile(x, 25)

def CI_75(x) :
    return np.percentile(x, 75)

def CI_2pt5(x) :
    return np.percentile(x, 2.5)

def CI_97pt5(x) :
    return np.percentile(x, 97.5)

def CI_50(x) :
    return np.percentile(x, 50)

def sampleplot(adf, allchannels, plot_fname=None, first_day=date(2020,2,20)):
    
    #Function plots whichever 'channels' you would like to see
    #in your data.
    
    fig = plt.figure(figsize=(8, 6))
    palette = sns.color_palette('Set1', 10)

    axes = [fig.add_subplot(3, 3, x + 1) for x in range(len(allchannels))]
    fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
    for c, channel in enumerate(allchannels):
        mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
        ax = axes[c]
        dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
        ax.plot(dates, mdf['mean'], label=channel, color=palette[c])
        ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                        color=palette[c], linewidth=0, alpha=0.2)
        ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                        color=palette[c], linewidth=0, alpha=0.4)

        ax.set_title(channel, y=1.05)

        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3)) #bymonthday=first_day.day,
        ax.set_xlim(first_day, )
        
    fig.tight_layout()
    if plot_fname :
        plt.savefig(plot_fname)
    plt.show()

#Running combine_trajectories...
df_final = combine_trajectories(master_input_base='master_input', trajectories_base_name='./trajectories/trajectories_')
#Running plot function...
master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild', \
                           'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
first_day = date(2020, 2, 20)
sampleplot(df_final, allchannels=master_channel_list, first_day=first_day, plot_fname='main_channels.png')