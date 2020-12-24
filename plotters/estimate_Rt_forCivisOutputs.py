"""
Compare COVID-19 simulation outputs to data.
Estimate Rt using epyestim
"""
import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import epyestim
import epyestim.covid19 as covid19
import seaborn as sns
sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *

mpl.rcParams['pdf.fonttype'] = 42

def parse_args():

    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-exp",
        "--exp_name",
        type=str,
        help="Name of simulation experiment"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default = "Local"
    )
    return parser.parse_args()


def get_distributions(show_plot=False):
    si_distrb = covid19.generate_standard_si_distribution()
    delay_distrb = covid19.generate_standard_infection_to_reporting_distribution()

    if show_plot:
        fig, axs = plt.subplots(1, 2, figsize=(12, 3))
        axs[0].bar(range(len(si_distrb)), si_distrb, width=1)
        axs[1].bar(range(len(delay_distrb)), delay_distrb, width=1)
        axs[0].set_title('Default serial interval distribution')
        axs[1].set_title('Default infection-to-reporting delay distribution')

    return si_distrb, delay_distrb

def rt_plot(df, first_day=None, last_day=None):
    fig = plt.figure(figsize=(16,8))
    fig.suptitle(x=0.5, y=0.999, t='Estimated time varying reproductive number (Rt)')
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    palette = sns.color_palette('husl', 8)

    df['date'] = pd.to_datetime(df['date']).dt.date
    if first_day != None:
        df = df[(df['date'] >= first_day) & (df['date'] <= last_day)]
    for e, reg in enumerate(df['geography_modeled'].unique()):
        ax = fig.add_subplot(3,4,e+1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        mdf = df[df['geography_modeled'] == reg]
        plot_label =''
        ax.plot(mdf['date'], mdf['rt_median'], color=palette[0], label=plot_label)
        ax.fill_between(mdf['date'].values, mdf['rt_lower'], mdf['rt_upper'],
                        color=palette[0], linewidth=0, alpha=0.3)
        if e == len(df['geography_modeled'].unique())-1:
            ax.legend()
        plotsubtitle = reg.replace('covidregion_',f'COVID-19 Region ')
        if reg == 'illinois' :
            plotsubtitle = 'Illinois'
        ax.set_title(plotsubtitle)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        if first_day != None:
            ax.set_xlim(first_day, last_day)
        #ax.axvline(x=date.today(), color='#666666', linestyle='--')
        ax.axhline(y=1, color='#666666', linestyle='-')

    plotname = 'estimated_rt_by_covidregion_full'
    if not first_day == None:
        plotname = 'estimated_rt_by_covidregion_truncated'
    plt.savefig(os.path.join(plot_path, f'{plotname}.png'))
    plt.savefig(os.path.join(plot_path,'pdf', f'{plotname}.pdf'), format='PDF')


def run_Rt_estimation():
    """Code following online example:
    https://github.com/lo-hfk/epyestim/blob/main/notebooks/covid_tutorial.ipynb
    """
    simdate = exp_name.split("_")[0]
    df = pd.read_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'),parse_dates=['date'])

    df_rt_all = pd.DataFrame()
    for ems_nr in range(1,12):

        if ems_nr == 0:
            region_suffix = "illinois"
        else:
            region_suffix = f'covidregion_{str(ems_nr)}'

        mdf = df[df["geography_modeled"] == region_suffix]
        mdf.cases_new_median = mdf.cases_new_median.astype(int)
        mdf = mdf.set_index('date')['cases_new_median']

        """Use default distributions (for covid-19)"""
        get_distributions()

        df_rt = covid19.r_covid(mdf[:-1])
        #df_rt.tail()
        df_rt['geography_modeled'] = region_suffix
        df_rt.reset_index(inplace=True)
        df_rt = df_rt.rename(columns={'index':'date',
                                      'R_mean':'rt_mean',
                                      'Q0.5':'rt_median',
                                      'Q0.025':'rt_lower',
                                      'Q0.975':'rt_upper'})
        df_rt = df_rt[['date','geography_modeled','rt_mean','rt_median','rt_lower','rt_upper']]
        df_rt_all = df_rt_all.append(df_rt)

    if not 'rt_median' in df.columns:
        df_withRt = pd.merge(left=df, right=df_rt_all,
                             left_on=['date','geography_modeled'],
                             right_on=['date','geography_modeled'])
        df_withRt.to_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'), index=False)
    else :
        del df[['rt_median','rt_mean','rt_lower','rt_upper']]
        df_withRt = pd.merge(left=df, right=df_rt_all,
                             left_on=['date','geography_modeled'],
                             right_on=['date','geography_modeled'])
        df_withRt.to_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'), index=False)

    rt_plot(df=df_rt_all)
    rt_plot(df=df_rt_all, first_day = first_plot_day , last_day = last_plot_day)

    return df_rt

if __name__ == '__main__':

    test_mode=True
    if test_mode:
        exp_name = '20201215_IL_mr_test_run'
        Location = 'Local'
    else:
        args = parse_args()
        exp_name = args.exp_name
        Location = args.Location

    first_plot_day = date.today() - timedelta(30)
    last_plot_day = date.today() + timedelta(30)

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_dir = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = os.path.join(exp_dir, '_plots')
    run_Rt_estimation()
