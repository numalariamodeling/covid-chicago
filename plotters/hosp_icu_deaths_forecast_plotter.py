import argparse
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
    return parser.parse_args()


def plot_sim_and_ref(df, ems_nr, ref_df, channels, data_channel_names, titles, plot_name, region_label, first_day, last_day,
                     ymax=1000,  logscale=False):

    fig = plt.figure(figsize=(13, 4))
    fig.subplots_adjust(left=0.07, right=0.97, top=2.95, bottom=0.05, hspace=0.25)
    axes = [fig.add_subplot(1,3, x + 1) for x in range(len(channels))]
    palette = sns.color_palette('husl', 8)
    k = 0

    for c, channel in enumerate(channels):
        ax = axes[c]
        mdf = df.groupby('date')[channel].agg([np.min, CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75, np.max]).reset_index()
        ax.plot(mdf['date'], mdf['CI_50'], color=palette[k])
        ax.fill_between(mdf['date'], mdf['CI_2pt5'], mdf['CI_97pt5'],
                        color=palette[k], linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'], mdf['CI_25'], mdf['CI_75'],
                        color=palette[k], linewidth=0, alpha=0.4)
        ax.fill_between(mdf['date'], mdf['amin'], mdf['amax'],
                        color=palette[k], linewidth=0, alpha=0.1)

        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        ax.set_title(titles[c],  fontsize=12)
        # ax.legend()

        if logscale:
            ax.set_ylim(0.1, ymax)
            ax.set_yscale('log')

        ax.plot(ref_df['date'], ref_df[data_channel_names[c]], 'o', color='#303030', linewidth=0, ms=1)
        ax.plot(ref_df['date'], ref_df[data_channel_names[c]].rolling(window=7, center=True).mean(), c='k', alpha=1.0)

        if channel == "hosp_det" or channel == "crit_det":
            capacity = load_capacity(ems_nr)
            if channel == "hosp_det":
                capacitychannel = 'hosp_det'
            if channel == "crit_det":
                capacitychannel = 'crit_det'

            ax.plot([first_plot_day,last_plot_day ], [capacity[capacitychannel], capacity[capacitychannel]], '--', linewidth=1, color='black')
            ax.plot([first_plot_day,last_plot_day ], [capacity[capacitychannel] * 0.75, capacity[capacitychannel] * 0.75], '--', linewidth=0.8, color='grey')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        ax.set_xlim(first_day, last_day)

    fig.suptitle(region_label,  y=1.0, fontsize=14)
    fig.tight_layout()
    plot_name_full = plot_name + '_covidregion_' + str(ems_nr)
    fig.subplots_adjust(top=0.8)

    if logscale == False:
        plot_name_full = plot_name_full + "_nolog"

    plt.savefig(os.path.join(plot_path, plot_name_full + '.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', plot_name_full + '.pdf'), format='PDF')

def compare_ems(exp_name, plot_name, ems_nr, first_day , last_day):

    if ems_nr == 0:
        region_suffix = "_All"
        region_label = 'Illinois'
    else:
        region_suffix = "_EMS-" + str(ems_nr)
        region_label = region_suffix.replace('_EMS-', 'COVID-19 Region ')

    column_list = ['time', 'startdate', 'scen_num', 'sample_num', 'run_num']

    outcome_channels = ['hosp_det_cumul', 'hosp_cumul', 'hosp_det', 'hospitalized',
                        'crit_det_cumul', 'crit_cumul', 'crit_det', 'critical',
                        'deaths_det_cumul', 'deaths']


    for channel in outcome_channels:
        column_list.append(channel + region_suffix)

    df = load_sim_data(exp_name, region_suffix=region_suffix, column_list=column_list)
    df = df[df['date'].between(first_day, last_day)]

    ref_df = load_ref_df(ems_nr)
    ref_df = ref_df[ref_df['date'].between(first_day, last_day)]
    channels = ['crit_det', 'hosp_det', 'new_deaths']
    data_channel_names = ['confirmed_covid_icu', 'covid_non_icu', 'deaths']
    titles = ['ICU census\n(EMR)', 'non-ICU inpatient census\n(EMR)','daily deaths\n(LL)']

    #plot_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,plot_name=plot_name,
    #                first_day=first_day, last_day=last_day, logscale=True)
    plot_sim_and_ref(df, ems_nr, ref_df, channels=channels, data_channel_names=data_channel_names, titles=titles,plot_name=plot_name,
                     region_label=region_label, first_day=first_day, last_day=last_day, logscale=False)

    # return ref_df_emr, ref_df_ll


if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    Location = args.Location

    first_plot_day = pd.Timestamp.today()- pd.Timedelta(60,'days')
    last_plot_day = pd.Timestamp.today()+ pd.Timedelta(150,'days')

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')
        """Get group names"""
        grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=sim_output_path)
        
        for grp_nr in grp_numbers:
            print("Start processing region " + str(grp_nr))
            compare_ems(exp_name, ems_nr=int(grp_nr), plot_name='forward_projection',
                        first_day=first_plot_day, last_day=last_plot_day)