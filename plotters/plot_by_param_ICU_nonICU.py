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

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

first_day = date(2020, 2, 13) # IL
first_plot_day = date(2020, 8, 1)
last_plot_day = date(2020, 12, 30)


def load_sim_data(exp_name, region_suffix ='_All', input_wdir=None,fname='trajectoriesDat_trim.csv', input_sim_output_path =None) :
    input_wdir = input_wdir or wdir
    sim_output_path_base = os.path.join(input_wdir, 'simulation_output', exp_name)
    sim_output_path = input_sim_output_path or sim_output_path_base

    column_list = ['scen_num',  'time', 'startdate']
    for ems_region in range(1, 12):
        column_list.append('crit_det_EMS-' + str(ems_region))
        column_list.append('hosp_det_EMS-' + str(ems_region))

    df = pd.read_csv(os.path.join(sim_output_path, fname), usecols=column_list)
    df.columns = df.columns.str.replace(region_suffix, '')

    return df

def plot_on_fig(df, c, axes,channel, color,panel_heading, ems, label=None, addgrid=True) :
    ax = axes[c]
    df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
    df = df[(df['date'] >= first_plot_day) & (df['date'] <= last_plot_day)]
    mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

    if addgrid:
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
    ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
    ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                color=color, linewidth=0, alpha=0.4)
    ax.set_title(panel_heading, y=0.85)
    formatter = mdates.DateFormatter("%d\n%b")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())

    ref_df  = compare_ems(ems=ems, channel=channel)

    if channel=="hosp_det":
        datachannel = 'covid_non_icu'
    if channel=="crit_det":
        datachannel = 'confirmed_covid_icu'

    ax.plot(ref_df['date'], ref_df[datachannel], 'o', color='#303030', linewidth=0, ms=3)
    ax.plot(ref_df['date'], ref_df[datachannel].rolling(window=7, center=True).mean(), c='k', alpha=1.0)
   #ax.set_yscale('log')
   # ax.set_ylim(0, max(mdf['CI_75']))

def compare_ems( ems,channel):
    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'emresource_by_region.csv'))
    ref_df = ref_df[ref_df['covid_region'] == ems]
    ref_df['suspected_and_confirmed_covid_icu'] = ref_df['suspected_covid_icu'] + ref_df['confirmed_covid_icu']

    if channel == "hosp_det":
        data_channel_names = ['covid_non_icu']
    if channel == "crit_det":
        data_channel_names = ['confirmed_covid_icu']

    ref_df = ref_df.groupby('date_of_extract')[data_channel_names].agg(np.sum).reset_index()
    ref_df['date'] = pd.to_datetime(ref_df['date_of_extract'])
    ref_df = ref_df[(ref_df['date'] >= pd.to_datetime(first_plot_day)) & (ref_df['date'] <= pd.to_datetime(last_plot_day))]

    return ref_df

def plot_covidregions(channel,subgroups, psuffix) :

    fig = plt.figure(figsize=(14, 12))
    fig.subplots_adjust(right=0.97, wspace=0.5, left=0.1, hspace=0.9, top=0.95, bottom=0.07)
    palette = sns.color_palette('Set1', len(exp_names))
    #axes = [fig.add_subplot(3, 4, x + 1) for x in range(len(subgroups))]
    axes = [fig.add_subplot(4, 3, x + 1) for x in range(len(subgroups))]

    for c, region_suffix in enumerate(subgroups) :

        region_label= region_suffix.replace('_EMS-', 'covid region ')
        ems = int(region_suffix.replace('_EMS-', ''))

        for d, exp_name in enumerate(exp_names) :
            sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
            df = load_sim_data(exp_name, region_suffix=region_suffix)
            exp_name_label =  int(exp_name.split('_')[0])
            plot_on_fig(df, c, axes, channel=channel, color=palette[d],ems=ems, panel_heading = region_label, label="")

        axes[-1].legend()
        #fig.suptitle(x=0.5, y=0.999,t=channel)
        plt.tight_layout()

    plt.savefig(os.path.join(sim_output_path, 'covidregion_'+psuffix+'_%s.png' % channel))
    plt.savefig(os.path.join(sim_output_path, 'covidregion'+psuffix+'_%s.pdf' % channel))

def plot_covidregions_both(subgroups, plot_name) :

    fig = plt.figure(figsize=(10, 4))
    fig.subplots_adjust(right=0.97, wspace=0.5, left=0.1, hspace=0.9, top=0.6, bottom=0.07)
    axes = [fig.add_subplot(1, 2, x + 1) for x in range(2)]

    region_suffix =subgroups[0]
    region_label= region_suffix.replace('_EMS-', 'covid region ')
    ems_nr = int(region_suffix.replace('_EMS-', ''))

    for d, exp_name in enumerate(exp_names) :
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        df = load_sim_data(exp_name, region_suffix=region_suffix)
        exp_name_label =  int(exp_name.split('_')[0])
        plot_on_fig2(df, axes, ems_nr=ems_nr,  label=exp_name_label)

    #axes[-1].legend()
    fig.suptitle(f'{region_label}\n', x=0.5, y=0.990)
    #plt.tight_layout(rect=[0, 0, 0, .95])
    plt.tight_layout()

    plt.savefig(os.path.join(sim_output_path, plot_name))
    plt.savefig(os.path.join(sim_output_path, plot_name))


if __name__ == '__main__' :

    exp_names = ['20201020_IL_mr_baseline']

    covidregionlist = ['_EMS-1', '_EMS-2', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-6', '_EMS-7', '_EMS-8', '_EMS-9', '_EMS-10', '_EMS-11']
    #covidregionlist = ['_EMS-1', '_EMS-3', '_EMS-4', '_EMS-5', '_EMS-9']

    plot_covidregions(channel='crit_det', subgroups = covidregionlist, psuffix ='AugDec')
    plot_covidregions(channel='hosp_det', subgroups = covidregionlist,  psuffix ='AugDec')
    #plot_covidregions_both(subgroups = ['_EMS-10'],  plot_name ='covidregion_10_ICU_nonICU_AugDec')
    #plot_covidregions_both(subgroups = ['_EMS-11'],  plot_name ='covidregion_11_ICU_nonICU_AugDec')
    #plt.show()