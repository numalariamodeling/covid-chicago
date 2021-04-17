import os
import pandas as pd
import numpy as np
import sys
import seaborn as sns
import matplotlib.pyplot as plt
sys.path.append('../')
from load_paths import load_box_paths
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
from processing_helpers import *

"""Define function methods"""
def load_data(column_list=None, remove_nas=False):
    """Read in only relevant columns """
    if column_list == None:
        column_list =['icu_length',    'hosp_length', 'age_group','res_county','res_state','hosp_yn', 'icu_yn', 'death_yn']
    df_full = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'il_cdc_thru_0811.csv'),
                          usecols=column_list)
    df = df_full.copy()
    """Remove Missings and Unknowns """
    if remove_nas:
        df = df.dropna(subset=["hosp_length"])
        df = df.dropna(subset=["age_group"])
        df = df.dropna(subset=["death_yn"])
        df = df[df['age_group'] != 'Unknown' ]
        df = df[df['icu_yn'] != 'Unknown' ]
        df = df[df['icu_yn'] != 'Missing' ]
        #print(df)
    return df

def LOS_descriptive_tables(groupList, channel='hosp_length', sortByList=None, fname=None):
    df_summary = df.groupby(groupList)[channel].agg(
        [np.mean, CI_2pt5, CI_25, CI_50, CI_75, CI_97pt5]).reset_index()
    if sortByList != None:
        df_summary = df_summary.sort_values(by=sortByList)

    if fname is not None:
        df_summary.to_csv(os.path.join(plot_path,f'summary_{"_".join(groupList)}_{channel}_{fname}.csv'))
    return df_summary

### Simple histogram, not age structured\
def plot_hist(df, channel='hosp_length') :
    plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':100})
    x = df[channel]
    plt.hist(x, bins=50)
    plt.gca().set(title=channel, ylabel='Frequency');
    return plt

### Function for age structured plot
def plot_hist_by_grp(df, channel='hosp_length',groups = None, grp_name = None, truncate_at=20) :
    ## Get age groups
    if groups == None:
        groups =  ['0 - 9 Years', '10 - 19 Years', '20 - 29 Years', '30 - 39 Years', '40 - 49 Years', '50 - 59 Years',
                  '60 - 69 Years', '70 - 79 Years', '80+ Years']
    if grp_name == None:
        grp_name = 'age_group'

    palette = sns.color_palette('husl', len(groups))
    fig = plt.figure(figsize=(10, 6))
    fig.subplots_adjust(right=0.97, left=0.1, hspace=0.4, wspace=0.3, top=0.90, bottom=0.05)
    fig.suptitle(x=0.5, y=0.999, t='Hospital LOS')

    for c, grp in enumerate(groups):
        if len(groups)==9:
            ax = fig.add_subplot(3, 3, c + 1)
        else:
            ax = fig.add_subplot(4, 4, c + 1)
        mdf = df[df[grp_name] == grp]
        if truncate_at is not None:
            mdf.loc[mdf[channel] >truncate_at, channel] = truncate_at
        median = np.median(mdf[channel])
        ax.hist(mdf[channel], bins=50, color=palette[0])
        ax.set_title(groups[c])
        ax.axvline(x=median, color='#737373', linestyle='--')
        ax.set(xlabel='', ylabel='Frequency')

    plt.savefig(os.path.join(plot_path, f'{channel}_by_{grp_name}.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{channel}_by_{grp_name}.pdf'), format='PDF')

    return plt


def plot_hist_by_grp_2(df, channel='hosp_length',color_channel = "icu_yn", groups = None, grp_name = None,truncate_at=None) :
    ## Get age groups
    if groups == None:
        groups =  ['0 - 9 Years', '10 - 19 Years', '20 - 29 Years', '30 - 39 Years', '40 - 49 Years', '50 - 59 Years',
                  '60 - 69 Years', '70 - 79 Years', '80+ Years']
    if grp_name == None:
        grp_name = 'age_group'

    palette = sns.color_palette('Set1', len(groups))
    fig = plt.figure(figsize=(10, 6))
    fig.subplots_adjust(right=0.97, left=0.1, hspace=0.4, wspace=0.3, top=0.90, bottom=0.05)
    fig.suptitle(x=0.5, y=0.999, t='Hospital LoS by ICU admission status ')

    for c, grp in enumerate(groups):
        if len(groups)==9:
            ax = fig.add_subplot(3, 3, c + 1)
        else:
            ax = fig.add_subplot(4, 4, c + 1)

        mdf = df[df[grp_name] == grp]
        if truncate_at is not None:
            mdf.loc[mdf[channel] > truncate_at, channel] = truncate_at

        ax.hist(mdf[mdf[color_channel]=='Yes'][channel], bins=50, color=palette[0], label="ICU yes", alpha=0.6)
        ax.hist(mdf[mdf[color_channel]=='No'][channel], bins=50, color=palette[1], label="ICU no", alpha=0.6)
        ax.axvline(x=np.median(mdf[mdf[color_channel]=='Yes'][channel]), color=palette[0], linestyle='--')
        ax.axvline(x=np.median(mdf[mdf[color_channel]=='No'][channel]), color=palette[1], linestyle='--')
        ax.set(xlabel='', ylabel='Frequency')
        ax.set_title(groups[c] ) #,fontweight="bold"
    ax.legend()

    plotname =  f'{channel}_colorby_{color_channel}_by_{grp_name}'
    if truncate_at is not None:
        plotname = plotname +'_truncated'

    plt.savefig(os.path.join(plot_path, f'{plotname}.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{plotname}.pdf'), format='PDF')

    return plt


if __name__ == '__main__':
    """Basic descriptive tables"""
    plot_path = os.path.join(projectpath, 'Plots + Graphs','Age Model - MS')

    df=load_data(remove_nas=True)
    pd.crosstab(index=df['age_group'], columns='count')
    LOS_descriptive_tables(channel='hosp_length',groupList=['age_group', 'death_yn'])
    LOS_descriptive_tables(channel='hosp_length',groupList=['age_group', 'icu_yn'], sortByList=['icu_yn','age_group'])
    df = df[df['hosp_length'] !=0 ]
    LOS_descriptive_tables(groupList=['age_group', 'death_yn'])
    LOS_descriptive_tables(groupList=['age_group', 'death_yn'], sortByList=['death_yn','age_group'],fname='_by_death_yn')
    LOS_descriptive_tables(groupList=['age_group', 'icu_yn'], sortByList=['icu_yn','age_group'],fname='icu_yn')

    ## Same histogra, with colors by ICU_yn
    plot_hist_by_grp_2(df, channel='hosp_length',color_channel = "icu_yn")
    plot_hist_by_grp_2(df, channel='hosp_length',color_channel = "icu_yn", truncate_at=20)

    """Compare by region"""
    df = load_data(remove_nas=True)
    df = df.dropna(subset=["res_county"])
    df = merge_county_covidregions(df_x=df, key_x='res_county', key_y='County')

    pd.crosstab(index=df['covid_region'], columns='count')
    LOS_descriptive_tables(channel='hosp_length',groupList=['covid_region', 'death_yn'])
    LOS_descriptive_tables(channel='hosp_length',groupList=['covid_region', 'icu_yn'], sortByList=['icu_yn','covid_region'])
    df = df[df['hosp_length'] !=0 ]
    LOS_descriptive_tables(groupList=['covid_region', 'death_yn'])
    LOS_descriptive_tables(groupList=['covid_region', 'death_yn'], sortByList=['death_yn','covid_region'],fname='_by_death_yn')
    LOS_descriptive_tables(groupList=['covid_region', 'icu_yn'], sortByList=['icu_yn','covid_region'],fname='icu_yn')

    plot_hist_by_grp(df=df, grp_name='covid_region', groups=list(range(1,12)))
    plot_hist_by_grp_2(df=df, grp_name='covid_region', groups=list(range(1,12)))