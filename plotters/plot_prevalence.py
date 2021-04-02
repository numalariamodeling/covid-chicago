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

# from plotting.colors import load_color_palette

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

def get_prev_df(exp_name, channels, region_list):

    df = pd.DataFrame()
    for ems_region in region_list:
        print(ems_region)
        ems_nr = ems_region.replace("EMS-","")
        if ems_region== "All": ems_nr = 0
        get_det =0
        for ch in channels:
            if 'det' in ch: get_det = get_det + 1

        column_list = ['time', 'startdate', 'scen_num', 'run_num', 'sample_num']
        column_list.append('N_' + str(ems_region.replace("-", "_")))
        column_list.append('infected_' + str(ems_region))
        column_list.append('infected_cumul_' + str(ems_region))
        column_list.append('recovered_' + str(ems_region))
        column_list.append('deaths_' + str(ems_region))
        if get_det >0:
            column_list.append('infected_det_' + str(ems_region))
            column_list.append('infected_det_cumul_' + str(ems_region))
            column_list.append('recovered_det_' + str(ems_region))
            column_list.append('deaths_det_' + str(ems_region))

        df_i = load_sim_data(exp_name, region_suffix=f'_{ems_region}', column_list=column_list, add_incidence=True)
        if ems_region !="All" :
            df_i['N'] = df_i['N_' + str(ems_region.replace("-", "_"))]

        df_i = calculate_prevalence(df_i)
        df_i['region'] = ems_nr
        df_i = df_i[['region','date','scen_num','sample_num']+channels]

        if df.empty:
            df= df_i
        else:
            df = pd.concat([df,df_i])
    #df.to_csv(os.path.join(wdir, 'simulation_output', exp_name, "prevalenceDat.csv"), index=False, date_format='%Y-%m-%d')
    return df

def plot_prevalences(df, first_day, last_day, channels):

    df = df[(df['date'] >= first_day) & (df['date'] <= last_day)]
    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.05)
    palette = sns.color_palette('husl', 8)
    for e, ems_num in enumerate(df['region'].unique()):
        ax = fig.add_subplot(3, 4, e + 1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        adf = df[df['region'] == ems_num]
        for k, channel in enumerate(channels):
            plot_label = ''
            if len(channels) > 1:
                plot_label = channel
            channel_label = channel + str(ems_num)
            mdf = adf.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
            ax.plot(mdf['date'], mdf['CI_50'], color=palette[k], label=plot_label)
            ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
                            color=palette[k], linewidth=0, alpha=0.2)
            ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                            color=palette[k], linewidth=0, alpha=0.4)
        if ems_num == len(df['region'].unique()):
            ax.legend()
        plotsubtitle = f'COVID-19 Region {ems_num}'
        if ems_num == 0:
            plotsubtitle = 'Illinois'
        ax.set_title(plotsubtitle)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
        ax.set_xlim(first_day, last_day)
        ax.axvline(x=pd.Timestamp.today(), color='#666666', linestyle='--')

    if len(channels) == 1:
        fig.suptitle(x=0.5, y=0.999, t=channel_label)

    fig_name = channels[0]
    if len(channels) == 2:
        fig_name = channels[0] + '-' + channels[1]

    plt.savefig(os.path.join(plot_path, f'{fig_name}_by_covidregion.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{fig_name}_by_covidregion.pdf'), format='PDF')


if __name__ == '__main__':

    args = parse_args()
    stem = args.stem
    Location = args.Location

    first_plot_day = pd.Timestamp('2020-02-13')
    last_plot_day = pd.Timestamp.today()+ pd.Timedelta(30,'days')

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    for exp_name in exp_names:
        print(exp_name)
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        plot_path = os.path.join(sim_output_path, '_plots')
        """Get group names"""
        grp_list, grp_suffix, grp_numbers = get_group_names(exp_path=sim_output_path)
        
        channels = ['prevalence','seroprevalence','IFR','IFR_t']
        #channels = ['prevalence','prevalence_det' ,'seroprevalence','seroprevalence_det' ,'IFR','IFR_t','IFR_det']
        df = get_prev_df(exp_name, channels=channels, region_list = grp_list)
        plot_prevalences(df, channels=['prevalence'], first_day=first_plot_day, last_day=last_plot_day)
        plot_prevalences(df, channels=['seroprevalence'], first_day=first_plot_day,last_day=last_plot_day)
        plot_prevalences(df, channels=['IFR'],first_day=first_plot_day,last_day=last_plot_day)
        #plot_prevalences(df, channels=['IFR_t'], first_day=first_plot_day,last_day=last_plot_day)
        #plot_prevalences(df, channels=['IFR', 'IFR_det'], first_day=first_plot_day, last_day=last_plot_day)
        #plot_prevalences(df, channels=['seroprevalence', 'seroprevalence_det'], first_day=first_plot_day, last_day=last_plot_day)
        #plot_prevalences(df, channels=['prevalence', 'prevalence_det'], first_day=first_plot_day, last_day=last_plot_day)
