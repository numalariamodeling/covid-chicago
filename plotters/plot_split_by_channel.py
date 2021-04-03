import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('Agg')
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib.dates as mdates
import seaborn as sns
from processing_helpers import *
import re

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
        "-g",
        "--channelGrp",
        type=str,
        choices=['symp','infect','hospCrit','Vaccinated'], #'bvariant'
        help="Name of channels to compare",
        default="Vaccinated"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default="Local"
    )
    return parser.parse_args()

def plot_on_fig(df, channels, axes, color, label,logscale=False, ymax=10000) :

    for c, channel in enumerate(channels) :

        channeltitle = re.sub('_detected', '', str(channel), count=1)
        channeltitle = re.sub('_det','', str(channeltitle), count=1)

        ax = axes[c]
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)

        mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
        ax.plot(mdf['date'], mdf['CI_50'], color=color, label=label)
        ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
                        color=color, linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=color, linewidth=0, alpha=0.4)

        if channel=="vaccinated_cumul":
            if grp =='All':
                ems_nr= 0
            else:
                ems_nr=int(grp.replace('EMS-', ''))
            adf = load_vacc_df(ems_nr=ems_nr)
            ax.plot(adf['date'], adf['persons_first_vaccinated'], 'o', color='#303030', linewidth=0, ms=1.1)

        ax.set_title(' '.join(channeltitle.split('_')), y=0.985)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        if logscale :
            ax.set_ylim(0.1, ymax)
            ax.set_yscale('log')



def get_channels(channelGrp):
    nchannels_symp = {'channels1': ['symp_severe_cumul', 'symp_mild_cumul', 'symptomatic_severe', 'symptomatic_mild'],
                      'channels2': ['symp_severe_det_cumul', 'symp_mild_det_cumul', 'symptomatic_severe_det',
                                    'symptomatic_mild_det']}

    nchannels_infect = {'channels1': ['infected', 'presymptomatic', 'infectious_undet', 'asymp', 'asymp_cumul'],
                        'channels2': ['infected_det', 'presymptomatic_det', 'infectious_det', 'asymptomatic_det',
                                      'asymp_det_cumul']}

    nchannels_hospCrit = {
        'channels1': ['hospitalized', 'new_hospitalized', 'hosp_cumul', 'critical', 'new_critical', 'crit_cumul'],
        'channels2': ['hosp_det', 'new_hosp_det', 'hosp_det_cumul', 'crit_det', 'new_crit_det',
                      'crit_det_cumul']}

    nchannels_Vacc = {
        'channels1': ['vaccinated_cumul', 'new_infected', 'new_asymp_det', 'crit_det', 'new_deaths', 'new_recovered'],
        'channels2': ['vaccinated_cumul', 'new_infected_V', 'new_asymp_det_V', 'crit_det_V', 'new_deaths_V', 'new_recovered_V']}

    nchannels_B = {
        'channels1': ['B_prev','new_infected',  'new_hosp',  'new_crit', 'new_deaths', 'new_recovered'],
        'channels2': ['B_prev','new_Binfect',  'new_hosp_B', 'new_crit_B', 'new_deaths_B', 'new_recovered_B']}

    if channelGrp == "symp":
        nchannels = nchannels_symp
        label0 = "detected + undetected"
        label1 = "detected"
    if channelGrp == "infect":
        nchannels = nchannels_infect
        label0 = "detected + undetected"
        label1 = "detected"
    if channelGrp == "hospCrit":
        nchannels = nchannels_hospCrit
        label0 = "detected + undetected"
        label1 = "detected"
    if channelGrp == "Vaccinated":
        nchannels = nchannels_Vacc
        label0 = "vaccinated + not vaccinated"
        label1 = "vaccinated"
    if channelGrp == "bvariant":
        nchannels = nchannels_B
        label0 = "bvariant + not bvariant"
        label1 = "bvariant"

    return  nchannels, label0, label1


def compare_channels(channelGrp,grp="All",logscale=False):

    nchannels, label0, label1 = get_channels(channelGrp)

    trajectories_cols = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'), index_col=0, nrows=0).columns.tolist()
    cols = list(set([ch.replace('new_','').replace('_V','') for ch in nchannels['channels1']+nchannels['channels2']]))
    column_list=[]
    for col in cols:
        column_list = column_list + [x for x in trajectories_cols if x.startswith(col)]

    df = load_sim_data(exp_name, region_suffix=f'_{grp}',fname='trajectoriesDat.csv',column_list=column_list, add_incidence=True)
    df = df[df['date'].between(pd.Timestamp(first_day), pd.Timestamp(last_day))]
    if channelGrp =='bvariant':
        df['B_prev'] = df['infected_B'] / df['infected']

    palette = sns.color_palette('Set1', len(nchannels))
    fig = plt.figure(figsize=(12, 6))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.3, wspace=0.2, top=0.92, bottom=0.08)
    if channelGrp == "Vaccinated":
        fig.suptitle(x=0.5, y=0.99, t=f'{grp} - based on 1st dose vaccine coverage shifted by 21 days')
    else:
        fig.suptitle(x=0.5, y=0.99, t=grp)
    axes = [fig.add_subplot(2, 3, x + 1) for x in range(len(nchannels['channels1']))]

    for d, key in enumerate(nchannels.keys()):
        channels = nchannels[key]
        if len([col for col in channels if not col in df.columns])>0:
            raise ValueError("Not all columns in dataframe")
        else:
            if d == 0:
                label = label0
            if d == 1:
                label = label1
        plot_on_fig(df, channels, axes, color=palette[d], label=label,logscale=logscale)

    axes[-1].legend()

    plot_name = f'{channelGrp}_comparison_{grp}'
    if logscale :
        plot_name = plot_name + "_log"

    plt.savefig(os.path.join(plot_path, plot_name + '.png'))
    plt.savefig(os.path.join(plot_path,'pdf', plot_name + '.pdf'), format='PDF')
    plt.show()

if __name__ == '__main__' :

    args = parse_args()
    stem = args.stem
    channelGrp = args.channelGrp
    Location = args.Location

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    first_day = pd.Timestamp.today()- pd.Timedelta(60,'days')
    last_day = pd.Timestamp.today()+ pd.Timedelta(150,'days')
    if channelGrp == 'Vaccinated':
        first_day = pd.Timestamp('2021-01-01')

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')
        grp_list, grp_suffix, grp_numbers = get_group_names(exp_path = sim_output_path)

        for grp in grp_list:
            print(f'Process started for {grp}')
            compare_channels(channelGrp=channelGrp, grp=grp)
            #compare_channels(channelGrp=channelGrp, grp=grp,logscale=True)
