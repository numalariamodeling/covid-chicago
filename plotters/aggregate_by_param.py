import argparse
import numpy as np
import pandas as pd
import os
import sys
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
sys.path.append('../')
from processing_helpers import *
from load_paths import load_box_paths

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
    parser.add_argument(
        "-p",
        "--param",
        type=str,
        #nargs='+',
        help="Name of parameter to keep when aggregating simulations. I.e. intervention coverage parameter",
        default='time_to_detection_Sym'
    )
    parser.add_argument(
        "-plot",
        "--plot_only",
        action='store_true',
        help="If specified, only generates the plot, given that trajectoriesDat_aggr is available.",
    )
    return parser.parse_args()

def plot_sim(exp_name,exp_path,grp_list, param, channel):

    first_day = pd.Timestamp.today() - pd.Timedelta(60,'days')
    last_day = pd.Timestamp.today() + pd.Timedelta(15,'days')

    column_list =['date', 'grp']
    for stat in ['_median','_50CI_upper','_50CI_lower','_95CI_upper','_95CI_lower']:
        column_list.append(channel + stat)

    if param is not None:
        column_list = column_list + [param]

    df = pd.read_csv(os.path.join(exp_path, 'trajectoriesDat_aggr.csv'), usecols=column_list)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'].between(pd.Timestamp(first_day), pd.Timestamp(last_day))]

    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    palette = sns.color_palette('Set1', len(df[param].unique()))

    for c, grp in enumerate(list(df['grp'].unique())):
        mdf = df[df['grp']==grp]
        ax = fig.add_subplot(3, 4, c + 1)

        for k, p in enumerate(list(mdf[param].unique())):
            pdf = mdf[mdf[param] == p]
            ax.plot(pdf['date'], pdf['%s_median' % channel], color=palette[k], label=p)
            ax.fill_between(pdf['date'].values, pdf['%s_95CI_lower' % channel], pdf['%s_95CI_upper' % channel],
                            color=palette[k], linewidth=0, alpha=0.2)
            ax.fill_between(pdf['date'].values, pdf['%s_50CI_lower' % channel], pdf['%s_50CI_upper' % channel],
                            color=palette[k], linewidth=0, alpha=0.4)
        ax.set_title(grp)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
    ax.legend(title=param)
    plotname = f'{exp_name.split("_")[-1]}_{channel}'
    plt.suptitle(channel, x=0.5, y=0.999, fontsize=14)
    plt.tight_layout()

    plt.savefig(os.path.join(plot_path, plotname + '.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', plotname + '.pdf'), format='PDF')


def aggregate_trajectories(grp, param=None, channels=None):

    if grp is not None:
        region_suffix =  f'_{grp}'
    else:
        grp=''
        region_suffix=''

    column_list = ['startdate', 'time', 'scen_num', 'sample_num','run_num']
    if channels is None:
        channels = ['susceptible', 'infected', 'recovered', 'infected_cumul', 'asymp_cumul','asymp_det_cumul',
                    'symp_mild_cumul', 'symp_severe_cumul', 'symp_mild_det_cumul','symp_severe_det_cumul',
                    'hosp_det_cumul', 'hosp_cumul', 'detected_cumul', 'crit_cumul', 'crit_det_cumul',
                    'deaths_det_cumul', 'deaths', 'crit_det',  'critical', 'hosp_det', 'hospitalized','Ki_t']

    if grp =='All':
        channels = [ch for ch in channels if ch != "Ki_t"]

    if len(region_suffix)>0:
        for channel in channels:
            column_list.append(channel + region_suffix)

    df = load_sim_data(exp_name,region_suffix = region_suffix,column_list=column_list,  add_incidence=True)
    df['grp'] = grp
    if param is not None:
        sampled_df = pd.read_csv(os.path.join(exp_path, "sampled_parameters.csv"), usecols=['scen_num', param])
        df = pd.merge(how='left', left=df, left_on='scen_num', right=sampled_df, right_on='scen_num')
    else :
        """Create dummy column"""
        df['param'] = 1
        param = 'param'

    groupby_channels = ['date', 'startdate', 'time', 'grp',param]
    groupby_channels = list(set(groupby_channels))
    channels = [ch for ch in list(df.columns) if ch not in
                list(set(groupby_channels + ['scen_num','sample_num','run_num','N',f'N_{grp}']))]

    metrics = (np.min, CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75, np.max)
    adf = pd.DataFrame()
    for c, channel in enumerate(channels):
        mdf = df.groupby(groupby_channels)[channel].agg(metrics).reset_index()

        mdf = mdf.rename(columns={'amin': '%s_min' % channel,
                                  'CI_50': '%s_median' % channel,
                                  'CI_2pt5': '%s_95CI_lower' % channel,
                                  'CI_97pt5': '%s_95CI_upper' % channel,
                                  'CI_25': '%s_50CI_lower' % channel,
                                  'CI_75': '%s_50CI_upper' % channel,
                                  'amax': '%s_max' % channel})
        if adf.empty:
            adf = mdf
        else:
            adf = pd.merge(left=adf, right=mdf, on=groupby_channels)

    return adf


if __name__ == '__main__':

    args = parse_args()
    exp_name = args.exp_name
    Location = args.Location
    param = args.param
    plot_only = args.plot_only

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    print(exp_name)
    exp_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = os.path.join(exp_path, '_plots')

    """Get group names"""
    grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=exp_path)

    if not plot_only:
        """Channels to keep (might change depending on simulation and focus"""
        outcome_channels = ['recovered', 'infected_cumul','hosp_det_cumul','detected_cumul',
                            'crit_det_cumul', 'deaths_det_cumul', 'deaths', 'crit_det', 'hosp_det','Ki_t']

        if len(grp_list) >1:
            dfAll = pd.DataFrame()
            for grp in grp_list:
                print(f'Start aggregating trajectories for {grp}')
                df = aggregate_trajectories(grp, param=param, channels=outcome_channels)
                df['scenario_name'] = exp_name.split("_")[-1]
                df['simdate'] = exp_name.split("_")[0]
                df['processdate'] = pd.Timestamp.today().date()
                filename = f'trajectoriesDat_aggr_{grp}.csv'
                df.to_csv(os.path.join(exp_path, filename), index=False)
                dfAll = pd.concat([dfAll, df])
                del df
            dfAll.to_csv(os.path.join(exp_path, 'trajectoriesDat_aggr.csv'), index=False)
        else:
            df = aggregate_trajectories(grp=grp_list[0], param=param,channels=outcome_channels)
            df['scenario_name'] = exp_name.split("_")[-1]
            df['simdate'] = exp_name.split("_")[0]
            df['processdate'] = pd.Timestamp.today()
            filename = f'trajectoriesDat_aggr.csv'
            df.to_csv(os.path.join(exp_path, filename), index=False)

    plot_sim(exp_name,exp_path,grp_list, param, channel='new_crit_det')
