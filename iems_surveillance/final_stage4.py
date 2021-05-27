import pandas as pd
import numpy as np
import os
import sys
import scipy
import epyestim 
import epyestim.covid19 as covid19
import matplotlib.pyplot as plt
import seaborn as sns
from seaborn.palettes import color_palette

def graph_rt(df, plotname) :
    plt.figure(figsize=(12,8))

    #df['date'] = pd.to_datetime(df.index())
    #df['date'] = df.index
    #pd.Index(df, name = 'date')
    #df.index(name='date')

    plt.plot(df['date'], df['Q0.025'], label='Q0.025') 
    plt.plot(df['date'], df['Q0.975'], label='Q0.975') 

    plt.fill_between(df['date'],df['Q0.025'],df['Q0.975'], alpha=0.3)

    plt.title('Graph of Rt Predictive Interval over time')
    plt.xlabel('Date')
    plt.ylabel('Rt')
    plt.legend()
    plt.show()
    #plt.savefig(f'{plotname}.png')
    #plt.savefig(f'{plotname}.png') path

def estimate_rt(df) :
    #scenario_nums = np.unique(df['scen_num'].values)

    #list of RTs to be returned at the ended
    df_rt_scen = pd.DataFrame()

    #probability array
    date = '2020-11-15'
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
        print(scen)
        for d, down in enumerate(df.downsample_num.unique()) :
            step5_count = 0

            #for each replication of that downsample size
            for r, rep in enumerate(df.replication_num.unique()) :
                mdf = df[(df['scen_num'] == scen) & (df['downsample_num'] == down) & (df['replication_num'] == rep)]
                mdf.loc[:, 'date'] = pd.to_datetime(mdf.loc[:,'date'])
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
                print(df_rt.at[date, 'R_mean'])
                if df_rt.at[date, 'R_mean']> 1.0 : step5_count += 1 
                print(step5_count)
                #row = df_rt[df_rt['index'] == '2020-11-01']
                #if row.R_mean > 1.0 : step5_count += 1
            #step 5 stuff 
            step5_arr[s][d] = step5_count / x3 

    return step5_arr

df = pd.read_csv('downsampled_cases.csv')
p_arr = estimate_rt(df)



    
# def main(path) :
#     #load in downsampled data to a dataframe
#     #df = pd.read_csv('datacopy.csv')
#     df = pd.read_csv('new_data_format.csv')
#     #df = pd.read_csv(os.path.join('../../projects','covid_chicago', 'cms_sim','simulation_output', path, 'downsampled_cases.csv'))
    
#     #run rt function
#     rt = estimate_rt(df)

#     #add a date column that mirrors the index
#     rt['date'] = rt['index']

#     #write out to a csv
#     rt.to_csv('new_step5_format.csv')
#     #rt.to_csv(os.path.join('../../projects','covid_chicago', 'cms_sim','simulation_output', path, 'step5_input.csv'),index=False)
    
#     #graph the Rt over time
#     #graph_rt(rt, 'graph_of_rt')


# if __name__ == '__main__': 
#     main('path')
#     #main(*sys.argv[1:])