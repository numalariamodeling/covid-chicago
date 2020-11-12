import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import seaborn as sns
from processing_helpers import *
from data_comparison import load_sim_data
from copy import copy

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

first_day = date(2020, 2, 13) # IL
first_plot_day = date(2020, 9, 1)
#last_plot_day = date(2020, 4, 30)

def plot_main(param, channel = 'crit_det',time_param=False) :

    column_list = ['scen_num', param]
    sampled_df = pd.read_csv(os.path.join(sim_output_path, "sampled_parameters.csv"), usecols=column_list)
    column_list = ['scen_num', 'time', 'startdate']
    for ems_region in range(1, 12):
        column_list.append('crit_det_EMS-' + str(ems_region))
        column_list.append('hosp_det_EMS-' + str(ems_region))
    df = load_sim_data(exp_name, fname="trajectoriesDat.csv", column_list=column_list)
    df = df.dropna()
    df = pd.merge(how='left', left=df, left_on='scen_num', right=sampled_df, right_on='scen_num')
    df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))

    fig = plt.figure(figsize=(10, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
    axes = [fig.add_subplot(4, 3, x + 1) for x in range(0,11)]

    if channel=="hosp_det":
        capacitychannel = 'hospitalized'
    if channel=="crit_det":
        capacitychannel = 'critical'


    for c, ems in enumerate(range(1,12)):

        mdf = df[(df['date'] >= first_plot_day) & (df['date'] <= max(df['date']))]

        region_suffix = '_EMS-' + str(ems)
        mdf.columns = mdf.columns.str.replace(region_suffix, '')
        mdf = mdf.groupby(['date',  param])[channel].agg(
            [CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        ax = axes[c]
        ax.set_title(str(ems) , y=0.85)
        palette = sns.color_palette('Set1', len(df[param].unique()))

        capacity = load_capacity(ems)
        ax.plot([np.min(mdf['date']), np.max(mdf['date'])], [capacity[capacitychannel], capacity[capacitychannel]],
                '--', linewidth=1, color='black')
        ax.plot([np.min(mdf['date']), np.max(mdf['date'])],
                [capacity[capacitychannel] * 0.75, capacity[capacitychannel] * 0.75], '--', linewidth=0.8, color='grey')

        for d, param_value in enumerate(df[param].unique()):
            adf = mdf[mdf[param]== param_value]

            if time_param:
                param_value = first_day + timedelta(days=int(param_value))

            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
            ax.plot(adf['date'], adf['CI_50'], color=palette[d], label=param_value)
            # ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
            #                 color=color, linewidth=0, alpha=0.2)
            ax.fill_between(adf['date'].values, adf['CI_25'], adf['CI_75'],
                            color=palette[d], linewidth=0, alpha=0.4)
            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            #ax.set_ylim(0, max(mdf['CI_75']))
    axes[-1].legend()

    fig.suptitle(x=0.5, y=0.999,t=channel + ' by ' + str(param))
    fig.tight_layout()

    fig.savefig(os.path.join(sim_output_path,'_plots',f'plot_by_{param}_{channel}.png'))
    fig.savefig(os.path.join(sim_output_path,'_plots', f'plot_by_{param}_{channel}.pdf'), format='PDF')
    #plt.show()



if __name__ == '__main__' :

    exp_name = '20201030_IL_rollback_toki8_small_reopen'
    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    #channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']
    #channels = ['crit_det', 'hosp_det']
    plot_main(channel= 'crit_det', param= 'socialDistance_reopen_time', time_param=True)