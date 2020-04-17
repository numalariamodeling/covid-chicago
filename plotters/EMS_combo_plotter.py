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
from data_comparison import load_sim_data


mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
plotdir = os.path.join(wdir, 'simulation_output', '_plots')


def load_ems(ems) :

    ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'emresource_by_region.csv'))
    if ems > 0 :
        ref_df = ref_df[ref_df['region'] == ems]
    else :
        ref_df = ref_df.groupby('date_of_extract').agg(np.sum).reset_index()
    ref_df['suspected_and_confirmed_covid_icu'] = ref_df['suspected_covid_icu'] + ref_df['confirmed_covid_icu']
    data_channel_names = ['suspected_and_confirmed_covid_icu', 'confirmed_covid_deaths_prev_24h',
                          'confirmed_covid_icu', 'confirmed_covid_on_vents']
    ref_df = ref_df.groupby('date_of_extract')[data_channel_names].agg(np.sum).reset_index()
    ref_df['date'] = pd.to_datetime(ref_df['date_of_extract'])
    return ref_df


def load_capacity(ems) :

    ems_fname = os.path.join(datapath, 'covid_IDPH/Corona virus reports/EMS_report_2020_03_21.xlsx')
    ems_df = pd.read_excel(ems_fname)
    ems_df = ems_df[ems_df['Date'] == '3/27/20']
    ems_df['ems'] = ems_df['Region'].apply(lambda x : int(x.split('-')[0]))
    ems_df = ems_df.set_index('ems')
    if ems > 0 :
        capacity = {
            'hospitalized' : ems_df.at[ems, 'Total_Med/_Surg_Beds'],
            'critical' : ems_df.at[ems, 'Total_Adult_ICU_Beds'],
            'ventilators' : ems_df.at[ems, 'Total_Vents']
        }
    else :
        capacity = {
            'hospitalized' : np.sum(ems_df['Total_Med/_Surg_Beds']),
            'critical' : np.sum(ems_df['Total_Adult_ICU_Beds']),
            'ventilators' : np.sum(ems_df['Total_Vents'])
        }
    return capacity


def plot_on_fig(df, channels, axes, color, ems) :

    capacity = load_capacity(ems)

    for c, channel in enumerate(channels) :
        ax = axes[c]
        mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

        ax.plot(mdf['date'], mdf['CI_50'], color=color, label='EMS %d' % ems)
        # ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
        #                 color=color, linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=color, linewidth=0, alpha=0.4)

        if channel in capacity.keys() :
            ax.plot([np.min(mdf['date']), np.max(mdf['date'])],
                    [capacity[channel], capacity[channel]], '--', linewidth=2, color=color)

        ax.set_title(' '.join(channel.split('_')), y=0.85)
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())


if __name__ == '__main__' :

    stem = '20200416_EMS'
    plot_name = '200416_TEST'
    plot_first_day = date(2020,3,1)
    plot_last_day = date(2020,6,1)

    exp_names = [x for x in os.listdir(os.path.join(wdir, 'simulation_output')) if stem in x]
    channels = ['infected', 'new_detected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']

    fig = plt.figure(figsize=(8, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
    palette = sns.color_palette('hls', len(exp_names))
    axes = [fig.add_subplot(3, 2, x + 1) for x in range(len(channels))]

    adf = pd.DataFrame()
    days_to_plot = plot_last_day - plot_first_day
    last = {x: [0] * (days_to_plot.days+1) for x in channels}
    for d, exp_name in enumerate(exp_names) :
        sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
        ems = int(exp_name.split('_')[2])
        df = load_sim_data(exp_name)

        df['ventilators'] = df['critical']*0.8
        first_day = datetime.strptime(df['first_day'].unique()[0], '%Y-%m-%d')

        df['date'] = df['time'].apply(lambda x: first_day + timedelta(days=int(x)))
        df = df[(df['date'] >= plot_first_day) & (df['date'] <= plot_last_day)]
        df['ems'] = ems

        fig_exp = plt.figure(figsize=(8, 8))
        fig_exp.subplots_adjust(right=0.97, wspace=0.2, left=0.1, hspace=0.25, top=0.95, bottom=0.07)
        axes_exp = [fig_exp.add_subplot(3, 2, x + 1) for x in range(len(channels))]

        plot_on_fig(df, channels, axes_exp, color=palette[d], ems=ems)
        fig_exp.savefig(os.path.join(plotdir, '%s_EMS%d.png' % (plot_name, ems)))
        fig_exp.savefig(os.path.join(plotdir, '%s_EMS%d.pdf' % (plot_name, ems)), format='PDF')
        plt.close(fig_exp)

        adf = pd.concat([adf, df[channels + ['date', 'ems']]])

        for c, channel in enumerate(channels) :
            ax = axes[c]
            mdf = df.groupby('date')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()

            ax.fill_between(mdf['date'].values, last[channel],
                            [x + y for x, y in zip(last[channel], mdf['CI_50'].values)],
                            color=palette[d], label='EMS %d' % ems,
                            linewidth=0)
            last[channel] = [x + y for x, y in zip(last[channel], mdf['CI_50'].values)]

            if d == 0 :
                ax.set_title(' '.join(channel.split('_')), y=0.85)
                formatter = mdates.DateFormatter("%m-%d")
                ax.xaxis.set_major_formatter(formatter)
                ax.xaxis.set_major_locator(mdates.MonthLocator())

    axes[-1].legend()
    fig.savefig(os.path.join(plotdir, '%s_all.png' % plot_name))
    fig.savefig(os.path.join(plotdir, '%s_all.pdf' % plot_name), format='PDF')

    plt.show()

