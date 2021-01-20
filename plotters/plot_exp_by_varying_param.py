import argparse
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

def parse_args():

    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-s",
        "--stem",
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
    parser.add_argument(
        "-p", "--param",
        type=str,
        help="Name of parameter with varying levels to plot",
        default='capacity_multiplier',
    )
    parser.add_argument(
        "-c", "--channel",
        type=str,
        help="Name of output channel to plot",
        default='crit_det',
    )
    return parser.parse_args()

def plot_main(param, channel, first_day, last_day,time_param=False) :

    sampled_df = pd.read_csv(os.path.join(sim_output_path, "sampled_parameters.csv"), usecols=['scen_num', param])

    fig = plt.figure(figsize=(16,8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    axes = [fig.add_subplot(3, 4, x + 1) for x in range(12)]

    capacitychannel = channel

    for c, ems_nr in enumerate(range(0,12)):

        if ems_nr == 0:
            region_suffix = "_All"
            region_label = 'Illinois'
        else:
            region_suffix = "_EMS-" + str(ems_nr)
            region_label = region_suffix.replace('_EMS-', 'COVID-19 Region ')

        column_list = ['scen_num', 'sample_num','run_num', 'time', 'startdate', f'{channel}{region_suffix}']
        df = load_sim_data(exp_name, region_suffix=region_suffix,  column_list=column_list, add_incidence=False)
        df = df[(df['date'] >= first_day) & (df['date'] <= last_day)]
        df = pd.merge(how='left', left=df, left_on='scen_num', right=sampled_df, right_on='scen_num')

        mdf = df.groupby(['date', param])[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        ax = axes[c]
        ax.set_title(region_label)
        palette = sns.color_palette('Set1', len(df[param].unique()))

        capacity = load_capacity(ems_nr)
        ax.plot([np.min(mdf['date']), np.max(mdf['date'])], [capacity[capacitychannel], capacity[capacitychannel]],
                '--', linewidth=1, color='black')
        ax.plot([np.min(mdf['date']), np.max(mdf['date'])],
                [capacity[capacitychannel] * 0.75, capacity[capacitychannel] * 0.75], '--', linewidth=0.8, color='grey')

        for d, param_value in enumerate(df[param].unique()):
            adf = mdf[mdf[param]== param_value]

            if time_param:
                startdate = datetime.strptime(df['startdate'].unique()[0], '%Y-%m-%d')
                param_value = startdate + timedelta(days=int(param_value))

            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
            ax.plot(adf['date'], adf['CI_50'], color=palette[d], label=param_value)
            # ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
            #                 color=color, linewidth=0, alpha=0.2)
            ax.fill_between(adf['date'].values, adf['CI_25'], adf['CI_75'],
                            color=palette[d], linewidth=0, alpha=0.4)

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
            #ax.set_ylim(0, max(mdf['CI_75']))
    axes[-1].legend()

    fig.suptitle(x=0.5, y=0.999,t=channel + ' by ' + str(param))
    fig.tight_layout()

    fig.savefig(os.path.join(plot_path, f'plot_by_{param}_{channel}.png'))
    fig.savefig(os.path.join(plot_path, 'pdf', f'plot_by_{param}_{channel}.pdf'), format='PDF')

if __name__ == '__main__' :

    args = parse_args()
    stem = args.stem
    Location = args.Location
    param = args.param
    channel = args.channel

    first_plot_day = date.today() - timedelta(60)
    last_plot_day = date.today() + timedelta(15)

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(wdir, 'simulation_output', exp_name, '_plots')
        #channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']
        #channels = ['crit_det', 'hosp_det']
        plot_main(channel=channel, param=param, time_param=True, first_day=first_plot_day, last_day=last_plot_day)