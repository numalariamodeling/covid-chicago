import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns
from processing_helpers import *

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

first_plot_day = pd.Timestamp('2020-02-13')
last_plot_day = pd.Timestamp.today()+ pd.Timedelta(30,'days')

def load_sim_data(exp_name,channel, ageGroup_list,age_suffix ='_All', input_wdir=None,fname='trajectoriesDat.csv', input_sim_output_path =None) :
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    column_list = ['scen_num',  'time', 'startdate']
    for grp in ageGroup_list:
        column_list.append(channel + str(grp))
        column_list.append('N' + str(grp))

    df = pd.read_csv(os.path.join(sim_output_path, fname), usecols=column_list)
    df.columns = df.columns.str.replace(age_suffix, '')

    return df

def plot_covidregions(exp_name,channel,ageGroup_list,ageGroups, perPop=True) :

    fig = plt.figure(figsize=(7, 3))
    fig.tight_layout()
    fig.subplots_adjust(top=0.88)
    fig.subplots_adjust(right=0.97, wspace=0.5, left=0.1, hspace=0.9, top=0.90, bottom=0.07)
    palette = sns.color_palette('Set1', 2)
    axes = [fig.add_subplot(1, 2, x + 1) for x in range(len(exp_names))]

    for p, exp_name in enumerate(exp_names) :
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        df = load_sim_data(exp_name, channel=channel, ageGroup_list=ageGroup_list,age_suffix="")

        exp_name_label = ''
        if exp_name == "20201015_EMS_1_ms_age_cdc_v1":
            exp_name_label = "Before age-adjustment 2nd Wave"
        if exp_name == "20201021_EMS_1_testrun_ct_2ndWave_run2":
            exp_name_label = "After age-adjustment 2nd Wave"

        for i in range(len(ageGroups)) :
            column_list = []
            column_list2 = []
            for grp in ageGroups[list(ageGroups.keys())[i]]:
                column_list.append(channel + str(grp))
                column_list2.append('N' + str(grp))
            df[f'{channel}_grp{i+1}'] = df[column_list].sum(axis=1)
            df[f'Npop_grp{i+1}'] = df[column_list2].sum(axis=1)
            df[f'{channel}_perPop_grp{i + 1}'] = df[f'{channel}_grp{i+1}'] / df[f'Npop_grp{i+1}']

        channels_new =  [x for x in df.columns.values if 'grp' in x]
        ytitle = "Total infected"
        if perPop == True :
            channels_new =  [x for x in df.columns.values if 'perPop_grp' in x]
            ytitle = "N infected / Population"

        for c, grp_channel in enumerate(channels_new) :

            grp_label =grp_channel #f'{channel} {list(ageGroups.keys())[c-1]}'

            if grp_channel == f'{channel}_perPop_grp1':
                grp_label = ' younger age group (<60)'
            if grp_channel == f'{channel}_perPop_grp2':
                grp_label = ' older age group (>60)'

            ax = axes[p]
            first_day = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
            df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
            df = df[(df['date'] >= first_plot_day) & (df['date'] <= last_plot_day)]
            mdf = df.groupby('date')[grp_channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
            ax.plot(mdf['date'], mdf['CI_50']*100, color=palette[c], label=grp_label)
            ax.fill_between(mdf['date'].values, mdf['CI_25']*100, mdf['CI_75']*100,
                            color=palette[c], linewidth=0, alpha=0.4)
            formatter = mdates.DateFormatter("%b")
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.set_ylabel(ytitle)
            ax.set_title(exp_name_label, y=0.98,size=10)

            axes[-1].legend()
            plt.tight_layout()

    plt.savefig(os.path.join(sim_output_path, 'age_comparison_plot_%s.png' % channel))
    plt.savefig(os.path.join(sim_output_path, 'age_comparison_plot_%s.pdf' % channel))


if __name__ == '__main__' :

    exp_names = ['20201015_EMS_1_ms_age_cdc_v1','20201021_EMS_1_testrun_ct_2ndWave_run2']

    ageGroup_list = ["_age0to9", "_age10to19", "_age20to29", "_age30to39", "_age40to49", "_age50to59", "_age60to69", "_age70to100"]
    ageGroups = {'young' : ['_age0to9', '_age10to19', '_age20to29', '_age30to39', '_age40to49', '_age50to59'],
                  'elderly' : ['_age60to69', '_age70to100']}

    #plot_covidregions(exp_names,channel='new_exposures', ageGroup_list=ageGroup_list,ageGroups = ageGroups)
    #plot_covidregions(exp_names,channel='new_infected', ageGroup_list=ageGroup_list,ageGroups = ageGroups)
    plot_covidregions(exp_names,channel='infected', ageGroup_list=ageGroup_list,ageGroups = ageGroups)

