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

from estimate_Rt_trajectores import *
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
    parser.add_argument(
        "--use_pre_aggr",
        action='store_true',
        help="If specified uses pre-aggregated new_infections instead of new_infections per trajectory to estimate Rt",
    )
    return parser.parse_args()


def run_Rt_estimation(exp_name,grp_numbers,smoothing_window, r_window_size):
    """
    Rt estimation using median new_infections, aggregated from the trajectoriesDat.csv
    Code following online example:
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

    df_rt_all['rt_pre_aggr'] = use_pre_aggr
    df_rt_all.to_csv(os.path.join(exp_dir, 'rtNU.csv'), index=False)

    if not 'rt_median' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df_rt_all['date'] = pd.to_datetime(df_rt_all['date'])

        df_with_rt = pd.merge(how='left', left=df, right=df_rt_all,
                              left_on=['date', 'geography_modeled'],
                              right_on=['date', 'geography_modeled'])
        df_with_rt.to_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'), index=False)
    else:
        print("Warning: Overwriting already present Rt estimates")
        df = df.drop(['rt_median', 'rt_lower', 'rt_upper'], axis=1)
        df['date'] = pd.to_datetime(df['date'])
        df_rt_all['date'] = pd.to_datetime(df_rt_all['date'])
        df_with_rt = pd.merge(how='left', left=df, right=df_rt_all,
                              left_on=['date', 'geography_modeled'],
                              right_on=['date', 'geography_modeled'])
        df_with_rt.to_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'), index=False)

    return df_rt

def use_Rt_trajectories(exp_name,exp_dir,grp_numbers, min_date = None, use_pre_aggr=True ):
    """
    If exist load rt_trajectories_aggr, otherwise rerun rt estimation for new_infections per trajectory:
    Note: estimation per trajectory may take >1 hour or may run out of memory, depending on date and scenarios
    estimate_Rt_trajectories.py (separate script) allows to run in parallel per region on NUCLUSTER.
    """
    simdate = exp_name.split("_")[0]
    if min_date is None:
        min_date = pd.Timestamp('2021-01-01')

    if os.path.exists(os.path.join(exp_dir, 'rt_trajectories_aggr.csv')):
        df = pd.read_csv(os.path.join(exp_dir, 'rt_trajectories_aggr.csv'))
        df['date'] = pd.to_datetime(df['date'])
    else:
        run_Rt_estimation_trajectories(exp_name,exp_dir,grp_numbers, smoothing_window=28, r_window_size=3, min_date = min_date)
        df = run_combine_and_plot(exp_dir,grp_numbers=grp_numbers, last_plot_day=min_date )

    df.rename(columns={"CI_50": "rt_median", "amin": "rt_lower", "amax": "rt_upper"}, inplace=True)
    df = df.drop(['CI_2pt5', 'CI_97pt5', 'CI_25','CI_75'], axis=1)

    if df['date'].min() > pd.Timestamp('2020-03-01') :

        if use_pre_aggr:
            rt_name = 'rt_trajectories_aggr.csv'
            rdf = pd.read_csv(os.path.join(wdir, 'simulation_saved', rt_name))
            rdf.rename(columns={"CI_50": "rt_median", "amin": "rt_lower", "amax": "rt_upper"}, inplace=True)
            rdf = rdf.drop(['CI_2pt5', 'CI_97pt5', 'CI_25', 'CI_75'], axis=1)
        else:
            rt_name = 'rtNU.csv'
            rdf = pd.read_csv(os.path.join(wdir, 'simulation_saved', rt_name))

        """Read saved historical Rt estimates"""
        rdf = rdf[df.columns]
        rdf['date'] = pd.to_datetime(rdf['date'])
        rdf = rdf[rdf['date'] < df['date'].min()]
        df_rt_all = rdf.append(df)
        del rdf, df
    else:
        df_rt_all = df
        del df

    df_rt_all['rt_pre_aggr'] = use_pre_aggr
    df_rt_all.to_csv(os.path.join(exp_dir, 'rtNU.csv'), index=False)

    """ Add to civis deliverables """
    df = pd.read_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'))
    df['date'] = pd.to_datetime(df['date'])
    df_rt_all['date'] = pd.to_datetime(df_rt_all['date'])
    df_rt_all = df_rt_all.drop(['model_date'], axis=1)

    if not 'rt_median' in df.columns:
        df_with_rt = pd.merge(how='left', left=df, right=df_rt_all,
                              left_on=['date', 'geography_modeled'],
                              right_on=['date', 'geography_modeled'])
        df_with_rt.to_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'), index=False)
    else:
        print("Warning: Overwriting already present Rt estimates")
        df = df.drop(['rt_median', 'rt_lower', 'rt_upper','rt_pre_aggr'], axis=1)
        df_with_rt = pd.merge(how='left', left=df, right=df_rt_all,
                              left_on=['date', 'geography_modeled'],
                              right_on=['date', 'geography_modeled'])
        df_with_rt.to_csv(os.path.join(exp_dir, f'nu_{simdate}.csv'), index=False)



if __name__ == '__main__':

    test_mode = False
    if test_mode:
        stem = "20210423_IL_localeEMS_1_testRtnew_baseline"
        Location = 'Local'
        plot_only=False
        use_pre_aggr= False
    else:
        args = parse_args()
        stem = args.stem
        Location = args.Location
        plot_only = args.plot_only
        use_pre_aggr = args.use_pre_aggr


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

