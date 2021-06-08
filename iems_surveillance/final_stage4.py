import pandas as pd
import numpy as np
import os
import sys
import scipy
import epyestim 
import epyestim.covid19 as covid19
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from seaborn.palettes import color_palette

def estimate_rt(df) :
    #scenario_nums = np.unique(df['scen_num'].values)

    #list of RTs to be returned at the ended
    df_rt_scen = pd.DataFrame()
    

    #probability array
    date = '2020-10-05'
    x1 = len(df.scen_num.unique())
    x2 = len(df.downsample_num.unique())
    x3 = len(df.replication_num.unique())
    step5_arr = np.empty((x1,x2))

    #set optional epyestim parameters for our sentinel surveillance 
    my_continuous_distrb = scipy.stats.gamma(a=5.807, scale=0.948)
    my_discrete_distrb = epyestim.discrete_distrb(my_continuous_distrb)
    sc_distrb = my_discrete_distrb
    '''
    for s, scen in enumerate(df.scen_num.unique()):
            mdf = df[df['scen_num'] == scen]
            mdf.loc[:, 'date'] = pd.to_datetime(mdf.loc[:,'date'])
            mdf = mdf.set_index('date')['downsampled_EMS11']
            df_rt = covid19.r_covid(mdf[:-1], delay_distribution=sc_distrb, r_window_size=14, auto_cutoff=False)
            df_rt.reset_index(inplace=True)
            df_rt['scen_num'] = scen
            df_rt_scen = df_rt_scen.append(df_rt)
    '''
    #for each trajetory
    for s, scen in enumerate(df.scen_num.unique()) :
        #for each different downsample size
        #print(scen)
        for d, down in enumerate(df.downsample_num.unique()) :
            step5_count = 0

            #for each replication of that downsample size
            for r, rep in enumerate(df.replication_num.unique()) :
                mdf = df[(df['scen_num'] == scen) & (df['downsample_num'] == down) & (df['replication_num'] == rep)]
                mdf.loc[:, 'date'] = pd.to_datetime(mdf.loc[:,'date'])
                #print(mdf.head())
                #print(df.date.unique())
                #print(mdf.loc[:,'date'])
                mdf = mdf.set_index('date')['downsampled_EMS11']
                #print(mdf)
                df_rt = covid19.r_covid(mdf[:-1], delay_distribution=sc_distrb, r_window_size=14, auto_cutoff=False)
                df_rt.reset_index(inplace=True)
                #add indexing columns
                df_rt['scen_num'] = scen 
                df_rt['downsample_num'] = down
                df_rt['replication_num'] = rep
                #append to larger dataframe that is returned
                df_rt_scen = df_rt_scen.append(df_rt)
                
                df_rt = df_rt.set_index('index')
                print(df_rt)
                #print(df_rt['index']==date)
                
                #step 5 stuff
                print(scen, down, rep)
                print(df_rt.at[date, 'R_mean'])
                if df_rt.at[date, 'R_mean']> 1.0 : step5_count += 1 
                print(step5_count)
                #row = df_rt[df_rt['index'] == '2020-11-01']
                #if row.R_mean > 1.0 : step5_count += 1
            #step 5 stuff 
            step5_arr[s][d] = step5_count / x3 

    return df_rt_scen, step5_arr

# Confidence interval functions for plotting
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

# plotting function
def graph_rt(df, path='title') :
    #df = pd.read_csv('graph_data.csv')
    num_dist = len(df.downsample_num.unique())
    last_day = df.iloc[-1].loc['index']

    #Graph uncertainty in the Rt estimate aggregated across all trajectories  
    fig1, axs1 = plt.subplots(num_dist, figsize=(12,8), sharex=True)
    fig1.suptitle('Graph of uncertainty in mean Rt estimate for each distribution')
    fig1.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)

    rdf = df.groupby(['index','downsample_num', 'replication_num'])['R_mean'].agg(np.mean).reset_index()

    for d, dist in enumerate(rdf.downsample_num.unique()) :
        #grab a subset of the dataframe that is the distribution currently being plotted of the first trajectory and first replication
        mdf = rdf[(rdf['downsample_num'] == dist)]
        mdf = mdf.groupby(['index'])['R_mean'].agg([CI_50, CI_25, CI_75]).reset_index()
        mdf['date'] = pd.to_datetime(mdf.loc[:,'index'])
        axs1[d].plot(mdf['date'], mdf['CI_50'], label='Median')
        axs1[d].fill_between(mdf['date'],mdf['CI_25'],mdf['CI_75'], alpha=0.3)
        axs1[d].set_title(f'Downsample Dist {dist}')
        axs1[d].xaxis.set_major_formatter(mdates.DateFormatter('%m\n%Y'))
    #plt.savefig('Figure3.png')
    plt.savefig(f'{path/Figure3}.png') #put correct path in 

    fig2, axs2 = plt.subplots(num_dist, figsize=(12,8), sharex=True)
    fig2.suptitle('Graph of uncertainty in mean Rt estimate for each distribution')
    fig2.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)

    #Graph uncertainty in the Rt estimate 
    #Shows the Rt trajectory and credible interval for one replication of on trajectory across all distributions
    for d, dist in enumerate(rdf.downsample_num.unique()) :
        mdf = df[(df['downsample_num'] == dist) & (df['scen_num'] == 1) & (df['replication_num'] == 1)]
        mdf['date'] = pd.to_datetime(mdf.loc[:,'index'])
        axs2[d].plot(mdf['date'], mdf['R_mean'], label='Rt Mean')
        axs2[d].fill_between(mdf['date'],mdf['Q0.025'],mdf['Q0.975'], alpha=0.3)
        axs2[d].set_title(f'Downsample Dist {dist}')

    plt.savefig(f'{path/Figure1}.png') #put correct path in  

    #Graph of uncertainty in the mean Rt estimate
    #histogram of the mean Rt values with 5 panels one for each downsampling option
    fig, axs = plt.subplots(num_dist, figsize=(12,8), sharex=True)
    
    fig.suptitle('Graph of uncertainty in mean Rt estimate for each distribution')
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)

    for d, dist in enumerate(df.downsample_num.unique()) :
        #grab a subset of the dataframe that is the distribution currently being plotted and the last Rt estimate calculated
        mdf = df[(df['downsample_num'] == dist) & (df['index'] == last_day)]
        #mdf.loc[:, 'date'] = pd.to_datetime(mdf.loc[:,'date'])
        axs[d].hist(mdf['R_mean'], bins=25, density=True, alpha=0.5) #could add an array of colors and make each one a different color
        axs[d].set_title(f'Downsample Dist {dist}')

    plt.savefig(f'{path/Figure2}.png') #put correct path in 



    
def main(path) :
    #load in downsampled data to a dataframe
    #df = pd.read_csv('downsampled_cases.csv')
    df = pd.read_csv(os.path.join('../../projects','covid_chicago', 'cms_sim','simulation_output', path, 'downsampled_cases.csv'))
    
    #run rt function
    step4, step5 = estimate_rt(df)
    #print('### Step 4 Ouput ### \n', step4.head())
    #print('### Step 5 Ouput ### \n', step5)

    #add a date column that mirrors the index
    #rt['date'] = rt['index']

    #write out to a csv
    #step4.to_csv('graph_data.csv')
    #step5.to_csv('step5_matrix.csv')
    step5.to_csv(os.path.join('../../projects','covid_chicago', 'cms_sim','simulation_output', path, 'prob.csv'),index=False)
    
    #graph the Rt over time
    #step4 = pd.DataFrame()
    graph_rt(step4, path)


if __name__ == '__main__': 
    #main('path')
    main(*sys.argv[1:])
