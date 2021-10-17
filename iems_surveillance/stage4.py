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
    '''
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle(x=0.5, y=0.989, t='Estimated time-varying reproductive number (Rt)')
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.93, bottom=0.05)
    palette = sns.color_palette('husl', 8)

    df['date'] = pd.to_datetime(df['date'])
    
    rt_min = df['rt_lower'].min()
    rt_max = df['rt_upper'].max()
    if rt_max > 4:
        rt_max = 4
    if rt_max < 1.1:
        rt_max = 1.1
    if rt_min > 0.9:
        rt_min = 0.9

    ax = fig.add_subplot(3, 4, 1) #e + 1
    ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
    ax.plot(df['date'], df['rt_median'], color=palette[0])
    ax.fill_between(df['date'].values, df['rt_lower'], df['rt_upper'],
                        color=palette[0], linewidth=0, alpha=0.3)

    plt.savefig(f'{plotname}.png')
    #plt.savefig(os.path.join(plot_path, 'pdf', f'{plotname}.pdf'), format='PDF')
    '''


def estimate_rt(df) :
    #df = pd.read_csv('datacopy.csv', index_col=5, parse_dates=True)['new_symp_mild_All']
    
    # CODE TO RUN MULTIPLE TRAJECTORIES
    #df2 = pd.read_csv('data.csv')
    print('df \n', df.head())
    #df was df2q

    scenario_nums = np.unique(df['scen_num'].values)

    #list of timeSeries each with the data for a different trajectory
    trajectories = []
    #list of RTs to be returned at the ended
    RTs = []
    df_rt_scen = pd.DataFrame()

    '''
    for num in scenario_nums :
        #print('### num ### \n', num)
        single_df = df[df['scen_num'] == num]
        #print('### new df ### ', num, '\n')
        single_df.loc[:, 'date'] = pd.to_datetime(single_df['date'])
        #single_df['cases'] = df['downsampled_EMS11']
        series = single_df.set_index('date')['downsampled_EMS11']

        trajectories.append(series)
    '''
    #print('trajectories \n', trajectories[1])
    #set optional epyestim parameters for our sentinel surveillance 
    my_continuous_distrb = scipy.stats.gamma(a=5.807, scale=0.948)
    my_discrete_distrb = epyestim.discrete_distrb(my_continuous_distrb)
    sc_distrb = my_discrete_distrb

    for s, scen in enumerate(df.scen_num.unique()):
            mdf = df[df['scen_num'] == scen]
            mdf.loc[:, 'date'] = pd.to_datetime(mdf.loc[:,'date'])
            mdf = mdf.set_index('date')['downsampled_EMS11']
            df_rt = covid19.r_covid(mdf[:-1], delay_distribution=sc_distrb, r_window_size=14, auto_cutoff=False)
            df_rt.reset_index(inplace=True)
            df_rt['scen_num'] = scen
            df_rt_scen = df_rt_scen.append(df_rt)
    """
    for traj in trajectories : 
        r_series = covid19.r_covid(traj[:-1], delay_distribution=sc_distrb, r_window_size=14, auto_cutoff=False)
        RTs.append(r_series)
    """
    return df_rt_scen
    
    '''
    #turn date strings into dateTime objects
    df['date'] = pd.to_datetime(df['date'])

    df['cases'] = df['11']
    #df['cases'] = df['downsampled_EMS11']

    series = df.set_index('date')['cases']
    
    #generate sentinel surveillance distribution to load into epyEstim
    my_continuous_distrb = scipy.stats.gamma(a=5.807, scale=0.948)
    my_discrete_distrb = epyestim.discrete_distrb(my_continuous_distrb)
    sc_distrb = my_discrete_distrb

    #run epyestim
    r_series = covid19.r_covid(series[:-1], delay_distribution=sc_distrb, r_window_size=14, auto_cutoff=False)

    return r_series
    '''
def main(path) :
    #load in downsampled data to a dataframe
    #df = pd.read_csv('datacopy.csv')
    #df = pd.read_csv('downsampled_cases.csv')
    df = pd.read_csv(os.path.join('../../projects','covid_chicago', 'cms_sim','simulation_output', path, 'downsampled_cases.csv'))
    
    #run rt function
    rt = estimate_rt(df)

    #add a date column that mirrors the index
    rt['date'] = rt['index']

    #write out to a csv
    #rt.to_csv('step5_input.csv')
    rt.to_csv(os.path.join('../../projects','covid_chicago', 'cms_sim','simulation_output', path, 'step5_input.csv'),index=False)
    
    #graph the Rt over time
    #graph_rt(rt, 'graph_of_rt')


if __name__ == '__main__': 
    main(*sys.argv[1:])


    '''
    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        print(exp_name)
        exp_dir = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(exp_dir, '_plots')
        """Get group names"""
        grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=exp_dir)
        if plot_only==False:
            if use_pre_aggr:
                run_Rt_estimation(exp_name,grp_numbers,smoothing_window=28, r_window_size=3)
            else:
                try:
                    print("Running use_Rt_trajectories")
                    use_Rt_trajectories(exp_name,exp_dir,grp_numbers)
                    print("Successfully ran use_Rt_trajectories")
                except:
                    print("Memory or run time error in use_Rt_trajectories\n"
                                     "Estimate Rt based on aggregated median new infections")
                    run_Rt_estimation(exp_name,grp_numbers, smoothing_window=28, r_window_size=3)

        df_rt_all = pd.read_csv(os.path.join(exp_dir, f'nu_{exp_name.split("_")[0]}.csv'))
        plot_rt_aggr(df=df_rt_all,grp_numbers=grp_numbers, plot_path=plot_path,plotname='estimated_rt_by_covidregion_full')
        plot_rt_aggr(df=df_rt_all,grp_numbers=grp_numbers, first_day=pd.Timestamp.today() - pd.Timedelta(90, 'days'),
                     last_day=last_plot_day, plot_path=plot_path, plotname='rt_by_covidregion_truncated')  
    '''
