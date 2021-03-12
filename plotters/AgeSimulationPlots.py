import os
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib.dates as mdates
import seaborn as sns
from processing_helpers import *

mpl.rcParams['pdf.fonttype'] = 42


def plot_on_fig(df, c, axes,channel, color,panel_heading, label=None, addgrid=True) :
    ax = axes[c]
    mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

    if addgrid:
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
    ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
    ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                color=color, linewidth=0, alpha=0.4)
    ax.set_title(panel_heading, y=0.85)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

   # ref_df  = compare_ems(ems=ems, channel=channel)

    if channel=="hosp_det":
        datachannel = 'covid_non_icu'
    if channel=="crit_det":
        datachannel = 'confirmed_covid_icu'

    #ax.plot(ref_df['date'], ref_df[datachannel], 'o', color='#303030', linewidth=0, ms=3)
    #ax.plot(ref_df['date'], ref_df[datachannel].rolling(window=7, center=True).mean(), c='k', alpha=1.0)
    #ax.set_yscale('log')
    #ax.set_ylim(0, 55000)
    #ax.set_yscale('log')
    #ax.set_ylim(0, max(mdf['CI_75']))


def plot_covidregions(exp_names,channel,subgroups, psuffix) :

    fig = plt.figure(figsize=(14, 8))
    fig.suptitle(f' {channel}', y=1, fontsize=14)
    plt.tight_layout(rect=[0, 0, 0, .95])
    fig.subplots_adjust(top=0.88)
    fig.subplots_adjust(right=0.97, wspace=0.20, left=0.05, hspace=0.4, top=0.95, bottom=0.01)
    palette = sns.color_palette('Set1', len(exp_names))
    axes = [fig.add_subplot(3, 3, x + 1) for x in range(len(subgroups))]

    for c, age_suffix in enumerate(subgroups) :

        region_label= age_suffix.replace('_age', 'age ')
        region_label= region_label.replace('_All', 'all ')

        for d, exp_name in enumerate(exp_names) :
            df = load_sim_data(exp_name, region_suffix=age_suffix, add_incidence=True)
            df = df[df['date'].between(first_plot_day, last_plot_day)]
            
            version = exp_name.split("_")[-1]
            exp_name_label = version
            if exp_name == "20201015_EMS_1_ms_age_cdc_v1":
                exp_name_label = "original"
            if exp_name == "20201021_EMS_1_testrun_ct_2ndWave_run2":
                exp_name_label = "new"
            plot_on_fig(df, c, axes, channel=channel, color=palette[d], panel_heading = region_label, label=exp_name_label)

        axes[-1].legend()
        #fig.suptitle(x=0.5, y=0.999,t=channel)
        #plt.tight_layout(rect=[0, 0, 0, .95])

    plt.savefig(os.path.join(plot_path, f'covidregion_{psuffix}_{channel}.png'))
    plt.savefig(os.path.join(plot_path,'pdf', f'covidregion_{psuffix}_{channel}.pdf'))



if __name__ == '__main__' :

    datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

    exp_names = ['20200923_EMS_11_ms_age_testhosp_v1','20200925_EMS_11_ms_age_testhosp_v6']
    plot_path = os.path.join(wdir, 'simulation_output', exp_names[len(exp_names) - 1], '_plots')

    ageGroup_list = ['_All',"_age0to9", "_age10to19", "_age20to29", "_age30to39", "_age40to49", "_age50to59", "_age60to69", "_age70to100"]
    first_plot_day = pd.Timestamp('2020-02-13')
    last_plot_day = pd.Timestamp.today() + pd.Timedelta(30, 'days')
    
    psuffix = 'FebToToday'
    #plot_covidregions(exp_names,channel='crit_det', subgroups = ageGroup_list, psuffix =psuffix)
    #plot_covidregions(exp_names,channel='hosp_det', subgroups = ageGroup_list,  psuffix =psuffix)
    #plot_covidregions(exp_names,channel='hospitalized', subgroups = ageGroup_list,  psuffix =psuffix)
    #plot_covidregions(exp_names,channel='deaths_det_cumul', subgroups = ageGroup_list,  psuffix =psuffix)
    plot_covidregions(exp_names,channel='infected', subgroups = ageGroup_list,  psuffix =psuffix)
    #plot_covidregions(exp_names,channel='asymptomatic', subgroups = ageGroup_list,  psuffix =psuffix)