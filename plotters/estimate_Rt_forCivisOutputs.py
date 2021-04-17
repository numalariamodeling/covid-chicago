"""
Compare COVID-19 simulation outputs to data.
Estimate Rt using epyestim
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
        "--plot_only",
        action='store_true',
        help="If specified only Rt plots will be generated, given Rt was already estimated",
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


def rt_plot(df, plotname,first_day=None, last_day=None):
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle(x=0.5, y=0.989, t='Estimated time-varying reproductive number (Rt)')
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.93, bottom=0.05)
    palette = sns.color_palette('husl', 8)

    df['date'] = pd.to_datetime(df['date'])
    if first_day != None:
        df = df[df['date'].between(first_day, last_day)]

    rt_min = df['rt_lower'].min()
    rt_max = df['rt_upper'].max()
    if rt_max > 4:
        rt_max = 4
    if rt_max < 1.1:
        rt_max = 1.1
    if rt_min > 0.9:
        rt_min = 0.9

    for e, reg in enumerate(df['geography_modeled'].unique()):
        ax = fig.add_subplot(3, 4, e + 1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        mdf = df.loc[df['geography_modeled'] == reg]
        ax.plot(mdf['date'], mdf['rt_median'], color=palette[0])
        ax.fill_between(mdf['date'].values, mdf['rt_lower'], mdf['rt_upper'],
                        color=palette[0], linewidth=0, alpha=0.3)
        plotsubtitle = reg.replace('covidregion_', f'COVID-19 Region ')
        if reg == 'illinois':
            plotsubtitle = 'Illinois'
        ax.set_title(plotsubtitle)

        if first_day != None:
            ax.set_xlim(first_day, last_day)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        else:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
        ax.axvline(x=pd.Timestamp.today(), color='#737373', linestyle='--')
        ax.axhline(y=1, color='black', linestyle='-')
        ax.set_ylim(rt_min, rt_max)

    plt.savefig(os.path.join(plot_path, f'{plotname}.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{plotname}.pdf'), format='PDF')


def run_Rt_estimation(grp_numbers,smoothing_window, r_window_size):
    """Code following online example:
    https://github.com/lo-hfk/epyestim/blob/main/notebooks/covid_tutorial.ipynb
    smoothing_window of 28 days was found to be most comparable to EpiEstim in this case
    r_window_size default is 3 if not specified, increasing r_window_size narrows the uncertainity bounds
    """
    simdate = exp_name.split("_")[0]
    df = pd.read_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'))
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['date'] > pd.Timestamp('2020-03-01'))]

    df_rt_all = pd.DataFrame()
    for ems_nr in grp_numbers:

        if ems_nr == 0:
            region_suffix = "illinois"
        else:
            region_suffix = f'covidregion_{str(ems_nr)}'

        if region_suffix not in df["geography_modeled"].unique():
            continue
        mdf = df[df['geography_modeled'] == region_suffix]
        mdf = mdf.set_index('date')['cases_new_median']

        """Use default distributions (for covid-19)"""
        si_distrb, delay_distrb = get_distributions(show_plot=False)
        df_rt = covid19.r_covid(mdf[:-1], smoothing_window=smoothing_window, r_window_size=r_window_size)

        df_rt['geography_modeled'] = region_suffix
        df_rt.reset_index(inplace=True)
        df_rt = df_rt.rename(columns={'index': 'date',
                                      'Q0.5': 'rt_median',
                                      'Q0.025': 'rt_lower',
                                      'Q0.975': 'rt_upper'})
        df_rt['model_date'] = pd.Timestamp(simdate)
        df_rt = df_rt[['model_date', 'date', 'geography_modeled', 'rt_median', 'rt_lower', 'rt_upper']]
        # df_rt['smoothing_window'] =smoothing_window
        # df_rt['r_window_size'] = r_window_size
        df_rt_all = df_rt_all.append(df_rt)

    df_rt_all.to_csv(os.path.join(exp_dir, 'rtNU.csv'), index=False)

    if not 'rt_median' in df.columns:
        df_with_rt = pd.merge(how='left', left=df, right=df_rt_all,
                              left_on=['date', 'geography_modeled'],
                              right_on=['date', 'geography_modeled'])
        df_with_rt.to_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'), index=False)
    else:
        print("Warning: Overwriting already present Rt estimates")
        df = df.drop(['rt_median', 'rt_lower', 'rt_upper'], axis=1)
        df_with_rt = pd.merge(how='left', left=df, right=df_rt_all,
                              left_on=['date', 'geography_modeled'],
                              right_on=['date', 'geography_modeled'])
        df_with_rt.to_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'), index=False)


    return df_rt


if __name__ == '__main__':

    test_mode = False
    if test_mode:
        stem = "20210203_IL_quest_baseline"
        Location = 'Local'
    else:
        args = parse_args()
        stem = args.stem
        Location = args.Location

    first_plot_day = pd.Timestamp('2020-03-01')
    last_plot_day = pd.Timestamp.today() + pd.Timedelta(90,'days')

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        print(exp_name)
        exp_dir = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(exp_dir, '_plots')
        """Get group names"""
        grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=exp_dir)
        if args.plot_only==False:
            run_Rt_estimation(grp_numbers,smoothing_window=28, r_window_size=3)

        df_rt_all = pd.read_csv(os.path.join(exp_dir, f'nu_{exp_name.split("_")[0]}.csv'))
        rt_plot(df=df_rt_all, plotname='estimated_rt_by_covidregion_full')
        rt_plot(df=df_rt_all, first_day=pd.Timestamp.today() - pd.Timedelta(90, 'days'), last_day=last_plot_day,
                plotname='rt_by_covidregion_truncated')

