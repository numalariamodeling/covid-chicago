"""
Compare COVID-19 simulation outputs to data.
Estimate Rt using epyestim, per trajectory
"""
import argparse
import os
import pandas as pd
import matplotlib as mpl

mpl.use('Agg')
import matplotlib.pyplot as plt
import sys
import matplotlib.dates as mdates
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
        "-stem",
        "--stem",
        type=str,
        help="Name of simulation experiment"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default="Local"
    )
    parser.add_argument(
        "-sr",
        "--subregion",
        type=str,
        help="Number of covid region if running script in parallel (i.e. on Quest) If none, will run for all regions",
        default=None
    )
    parser.add_argument(
        "--combine_and_plot",
        action='store_true',
        help="combine_and_plot",
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


def plot_rt_aggr(df, grp_numbers, plot_path, plotname, first_day=None, last_day=None,stats=None):
    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.93, bottom=0.05)
    palette = sns.color_palette('husl', 8)

    if stats=='minmax':
        channel = 'CI_50'
        channel_lo ='amin'
        channel_up = 'amax'
    elif stats == '95% CI' :
        channel = 'CI_50'
        channel_lo ='CI_2pt5'
        channel_up = 'CI_97pt5'
    else:
        channel = 'rt_median'
        channel_lo ='rt_lower'
        channel_up = 'rt_upper'

    df['date'] = pd.to_datetime(df['date'])
    if first_day != None:
        df = df[df['date'].between(first_day, last_day)]

    for e, ems_nr in enumerate(grp_numbers):
        if ems_nr == 0:
            region_label = "illinois"
        else:
            region_label = f'covidregion_{str(ems_nr)}'

        ax = fig.add_subplot(3, 4, e + 1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        mdf = df.loc[df['geography_modeled'] == region_label]
        ax.plot(mdf['date'], mdf[channel], color=palette[0])
        ax.fill_between(mdf['date'].values, mdf[channel_lo], mdf[channel_up],
                        color=palette[0], linewidth=0, alpha=0.3)
        plotsubtitle = region_label.replace('covidregion_', f'COVID-19 Region ')
        ax.set_title(plotsubtitle)

        if first_day != None:
            ax.set_xlim(first_day, last_day)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
        ax.axvline(x=pd.Timestamp.today(), color='#737373', linestyle='--')
        ax.axhline(y=1, color='black', linestyle='-')

    fig.suptitle(x=0.5, y=0.989, t='Estimated time-varying reproductive number (Rt)' +f' ({stats} range)' )
    plt.savefig(os.path.join(plot_path, f'{plotname}.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{plotname}.pdf'), format='PDF')


def plot_rt(df, grp_numbers, plot_path, plotname, first_day=None, last_day=None):
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle(x=0.5, y=0.989, t='Estimated time-varying reproductive number (Rt)')
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.93, bottom=0.05)
    palette = sns.color_palette('husl', 8)

    df['date'] = pd.to_datetime(df['date'])
    df = df.dropna(subset=["date"])
    if first_day != None:
        df = df[df['date'].between(first_day, last_day)]

    for e, ems_nr in enumerate(grp_numbers):
        if ems_nr == 0:
            region_label = "illinois"
        else:
            region_label = f'covidregion_{str(ems_nr)}'
        ax = fig.add_subplot(3, 4, e + 1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        mdf = df.loc[df['geography_modeled'] == region_label]
        for t, scen in enumerate(mdf['scen_num'].unique()):
            tdf = mdf.loc[mdf['scen_num'] == scen]
            ax.plot(tdf['date'], tdf['rt_median'], color=palette[0])

        plotsubtitle = region_label.replace('covidregion_', f'COVID-19 Region ')
        ax.set_title(plotsubtitle)

        if first_day != None:
            ax.set_xlim(first_day, last_day)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
        ax.axvline(x=pd.Timestamp.today(), color='#737373', linestyle='--')
        ax.axhline(y=1, color='black', linestyle='-')

    plt.savefig(os.path.join(plot_path, f'{plotname}.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{plotname}.pdf'), format='PDF')


def run_Rt_estimation_trajectories(exp_name,exp_dir,grp_numbers, smoothing_window, r_window_size,min_date=None):
    """Code following online example:
    https://github.com/lo-hfk/epyestim/blob/main/notebooks/covid_tutorial.ipynb
    smoothing_window of 28 days was found to be most comparable to EpiEstim in this case
    r_window_size default is 3 if not specified, increasing r_window_size narrows the uncertainity bounds
    """
    simdate = exp_name.split("_")[0]

    df_rt_all = pd.DataFrame()
    for e, ems_nr in enumerate(grp_numbers):
        if ems_nr == 0:
            region_suffix = '_All'
            region_label = "illinois"
        else:
            region_suffix = f'_EMS-{ems_nr}'
            region_label = f'covidregion_{str(ems_nr)}'
        print(region_suffix)
        df = load_sim_data(exp_name, region_suffix=region_suffix)
        df['date'] = pd.to_datetime(df['date'])

        if min_date is not None:
            df = df[df['date'] >= min_date ]

        """Use default distributions (for covid-19)"""
        si_distrb, delay_distrb = get_distributions(show_plot=False)

        df_rt_scen = pd.DataFrame()
        for s, scen in enumerate(df.scen_num.unique()):
            print(scen)
            mdf = df[df['scen_num'] == scen]
            mdf = mdf.set_index('date')['new_infected']
            df_rt = covid19.r_covid(mdf[:-1], smoothing_window=smoothing_window, r_window_size=r_window_size)
            df_rt.reset_index(inplace=True)
            df_rt = df_rt.rename(columns={'index': 'date',
                                          'Q0.5': 'rt_median',
                                          'Q0.025': 'rt_lower',
                                          'Q0.975': 'rt_upper'})
            df_rt['model_date'] = pd.Timestamp(simdate)
            df_rt['geography_modeled'] = region_label
            df_rt['scen_num'] = scen
            df_rt['scen_enumerator'] = s
            df_rt_scen = df_rt_scen.append(df_rt)
        df_rt_scen.to_csv(os.path.join(exp_dir, 'rt_trajectories' + region_label + '.csv'), index=False)

def run_combine_and_plot(exp_dir, grp_numbers, last_plot_day):
    plot_path = os.path.join(exp_dir, '_plots')
    df_rt_all = pd.DataFrame()
    for ems_nr in grp_numbers:
        if ems_nr == 0:
            region_label = "illinois"
        else:
            region_label = f'covidregion_{str(ems_nr)}'
        try:
            df_rt = pd.read_csv(os.path.join(exp_dir, 'rt_trajectories' + region_label + '.csv'))
            df_rt_all = df_rt_all.append(df_rt)
        except:
            print('rt_trajectories' + region_label + '.csv not included')

    df_rt_all.to_csv(os.path.join(exp_dir, 'rt_trajectories.csv'), index=False)

    """Plot """
    plot_rt(df=df_rt_all,grp_numbers=grp_numbers,plot_path=plot_path, plotname=f'rt_trajectories_full')
    plot_rt(df=df_rt_all,grp_numbers=grp_numbers, first_day=pd.Timestamp.today() - pd.Timedelta(90, 'days'), last_day=last_plot_day,
            plot_path=plot_path,plotname=f'rt_trajectories_truncated')

    """Aggregate rt estimates per date and region """
    df_rt_aggr = df_rt_all.groupby(['model_date', 'date', 'geography_modeled'])['rt_median'].agg(
        [CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75, np.min, np.max]).reset_index()
    df_rt_aggr.to_csv(os.path.join(exp_dir, 'rt_trajectories_aggr.csv'), index=False)

    """Plot """
   # plot_rt_aggr(df=df_rt_aggr, grp_numbers=grp_numbers, plot_path=plot_path, plotname=f'rt_full', stats='minmax')
   # plot_rt_aggr(df=df_rt_aggr, grp_numbers=grp_numbers, first_day=pd.Timestamp.today() - pd.Timedelta(90, 'days'),
   #              last_day=last_plot_day, plot_path=plot_path, plotname=f'rt_truncated', stats='minmax')

    return df_rt_aggr

if __name__ == '__main__':

    test_mode = False
    if test_mode:
        stem = "20210402_IL_locale_sub_ae_test_v7_vaccine"
        Location = 'Local'
        subregion = None
        combine_and_plot = True
    else:
        args = parse_args()
        stem = args.stem
        Location = args.Location
        subregion = args.subregion
        combine_and_plot = args.combine_and_plot

    first_plot_day = pd.Timestamp('2020-03-01')
    last_plot_day = pd.Timestamp.today() + pd.Timedelta(90, 'days')

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        print(exp_name)
        exp_dir = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(exp_dir, '_plots')
        """Get group names"""
        grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=exp_dir)
        if subregion is not None:
            grp_numbers = [int(subregion)]

        if not combine_and_plot :
            run_Rt_estimation_trajectories(exp_name,exp_dir,grp_numbers, smoothing_window=28, r_window_size=3, min_date = first_plot_day )
        """Process needs to be separated when running same script in parallel versus all in one go, depending on simulation size"""
        if  combine_and_plot or subregion is None:
            run_combine_and_plot(exp_dir,grp_numbers, last_plot_day)



