import argparse
import numpy as np
import pandas as pd
import os
import sys
sys.path.append('../')
from processing_helpers import *
from load_paths import load_box_paths

##plotting
import matplotlib as mpl
import matplotlib.pyplot as plt
#mpl.use('Agg')
#import seaborn as sns
import matplotlib.dates as mdates

def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-exp",
        "--exp_name",
        type=str,
        help="Name of simulation experiments"
    )

    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default="Local"
    )
    return parser.parse_args()


def plot_sim(df,grp, first_day, last_day):
    palette = ('#913058', "#F6851F", "#00A08A", "#D61B5A", "#5393C3", "#F1A31F", "#98B548", "#8971B3", "#969696")


    fig = plt.figure(figsize=(6, 4))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    ax = fig.add_subplot(1, 1, 1)

    for k, scen in enumerate(list(df['scen_num'].unique())):
        mdf = df[df['scen_num'] == scen]
        ax.plot(mdf['date'], mdf['new_symp_mild'], color=palette[0])

    ax.set_ylabel('new_symp_mild')
    ax.set_title(grp)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))

    plotname = f'new_symp_mild_{grp}'
    plt.suptitle('Daily new mild symptomatic infections\nper trajectory', x=0.5, y=0.999, fontsize=14)
    plt.tight_layout()

    plt.savefig(os.path.join(plot_path, plotname + '.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', plotname + '.pdf'), format='PDF')



if __name__ == '__main__':

    testrun=True
    if testrun:
        exp_name ='20210406_IL_locale__test_rn25_vaccine'
        Location = 'LOCAL'
    else:
        args = parse_args()
        exp_name = args.exp_name
        Location = args.Location

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    print(exp_name)
    exp_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = os.path.join(exp_path, '_plots')

    """Get group names"""
    grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=exp_path)

    column_list = ['startdate', 'time', 'scen_num', 'sample_num','run_num']
    channel = 'symp_mild_cumul'

    for grp in grp_list:
        column_list.append(channel + f'_{grp}')

    """Example wide format all regions, region name in column name"""
    df = load_sim_data(exp_name, region_suffix=None, fname='trajectoriesDat.csv',column_list=column_list, add_incidence=True)
    columns_to_keep = [col for col in df.columns if '_cumul' not in col]
    df = df[columns_to_keep]
    df.to_csv(os.path.join(exp_path, 'new_symp_mild.csv'), index=False)

    """Example each region single csv, additional region column"""
    for grp in grp_list:
        print(f'Processing for {grp}')
        grp_nr = grp.replace(grp_suffix,'')
        df = load_sim_data(exp_name, region_suffix=f'_{grp}', fname='trajectoriesDat.csv',column_list=column_list, add_incidence=True)
        df['region'] = grp
        columns_to_keep = [col for col in df.columns if '_cumul' not in col]
        df = df[columns_to_keep]
        df.to_csv(os.path.join(exp_path, f'new_symp_mild_region{grp_nr}.csv'), index=False)

        first_day = pd.Timestamp.today() - pd.Timedelta(60, 'days')
        last_day = pd.Timestamp.today() + pd.Timedelta(15, 'days')

        plot_sim(df, grp,first_day,last_day)



