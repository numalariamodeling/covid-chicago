import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
from processing_helpers import *
#from plotting.colors import load_color_palette

mpl.rcParams['pdf.fonttype'] = 42
today = datetime.today()

first_plot_day = pd.to_datetime(date(2020, 7, 15))
last_plot_day = pd.to_datetime(today)

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--cdph_date",
        type=str,
        help="i.e 20201026",
        default=None
    )
    return parser.parse_args()

def plot_emresource(ems_list, scale=''):

    ref_df = pd.DataFrame()
    for ems_nr in ems_list :
        ref_df_t = load_ref_df(ems_nr=int(ems_nr))
        ref_df = ref_df.append(ref_df_t)

    ref_df = ref_df.sort_values('date')
    ref_df = ref_df[(ref_df['date'] >= first_plot_day) & (ref_df['date'] <= last_plot_day)]

    ref_df = ref_df.rename(columns={
        'confirmed_covid_deaths_prev_24h' : 'deaths',
        'confirmed_covid_icu' : 'ICU conf',
        'confirmed_covid_on_vents' : 'vents conf',
        'suspected_and_confirmed_covid_icu' : 'ICU conf+susp',
        'covid_non_icu' : 'non ICU',
        'inpatient': 'CLI admissions'
    })

    channels = ['ICU conf', 'non ICU','CLI admissions']
    ref_df = ref_df[['date', 'covid_region'] + channels]

    palette = ("#913058", "#F6851F","#00A08A")  # sns.color_palette('Set1', len(channels))
    fig = plt.figure(figsize=(12, 5))
    fig.subplots_adjust(left=0.07, right=0.97, top=0.95, bottom=0.1, hspace=0.25)

    for ei, ems in enumerate(ems_list):
        ax = fig.add_subplot(len(ems_list)/2, 4-len(ems_list), ei + 1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        df = ref_df[ref_df['covid_region'] == ems]

        for (c, name) in enumerate(channels):
            df['moving_ave'] = df[name].rolling(window=7, center=True).mean()
            ax.plot(df['date'].values, df['moving_ave'], color=palette[c], label=name)
            ax.scatter(df['date'].values, df[name], s=10, linewidth=0, color=palette[c], alpha=0.7, label='')
        ax.set_title('covid region %d' % ems)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))

        if scale == 'log':
            ax.set_yscale('log')

    if ei+1 == len(ems_list):
        ax.legend(loc='upper left', shadow=False, ncol=1)

    regions = '-'.join(map(str, ems_list))
    fig.savefig(os.path.join(plot_path, f'EMResource_and_CLI_covidregion_{regions}_{scale}.png'))
    fig.savefig(os.path.join(plot_path, f'EMResource_and_CLI_covidregion_{regions}_{scale}.pdf'), format='PDF')

if __name__ == '__main__' :

    args = parse_args()
    datetoday = args.cdph_date
    if datetoday == None :
        datetoday = (str(today.year) + str(today.month) + str(today.day))

    # plot_path = os.path.join(projectpath, 'Plots + Graphs', 'Emresource Plots')
    plot_path = os.path.join(projectpath, 'NU_cdph_outputs', datetoday)

    if not os.path.exists(plot_path):
        os.makedirs(plot_path)

    plot_emresource(ems_list=[10, 11], scale='nolog')
    plot_emresource(ems_list=[10, 11],scale='log')
    #plt.show()

