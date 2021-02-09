"""
Compare COVID-19 simulation outputs to data.
Estimate Rt using epyestim
"""
import os
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import sys
import matplotlib.dates as mdates
import seaborn as sns

sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *

mpl.rcParams['pdf.fonttype'] = 42


def comparison_plot(reg_nr=0, channels=None, n_iter=3):
    if reg_nr == 0:
        region = "illinois"
        region_label = "Illinois"
    else:
        region = f'covidregion_{reg_nr}'
        region_label = f'COVID-19 Region {reg_nr}'

    if channels == None:
        channels = ['cases', 'deaths_det', 'recovered', 'hosp_bed', 'icu', 'vent']
        #channels = ['cases', 'deaths_det', 'recovered','hosp_det_bed', 'icu_det', 'vent']
        channel_labels = ['Cases', 'Daily deaths', 'Recovered','Med/surg beds', 'ICU beds', 'Ventilators']

    capacity = load_capacity(ems=reg_nr)
    new_keys = ['hosp_det_bed', 'icu_det', 'vent']
    #new_keys = ['hosp_bed', 'icu', 'vent']
    for key, n_key in zip(capacity.keys(), new_keys):
        capacity[n_key] = capacity.pop(key)

    fig = plt.figure(figsize=(12, 8))
    fig.suptitle(x=0.07, y=0.982, t=f"Predicted COVID-19 outcomes in {region_label}", ha='left')
    axes = [fig.add_subplot(2, 3, x + 1) for x in range(len(channels))]
    fig.subplots_adjust(right=0.96, left=0.07, hspace=0.25, wspace=0.3, top=0.92, bottom=0.07)
    palette = sns.color_palette('husl', n_iter)

    NU_civis_path = os.path.join(projectpath, 'NU_civis_outputs')
    exp_simdates = os.listdir(NU_civis_path)[-n_iter:]
    print(exp_simdates)

    for i, simdate in enumerate(exp_simdates):
        df = pd.read_csv(os.path.join(NU_civis_path, simdate, 'csv', f'nu_{simdate}.csv'))
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['geography_modeled'] == region]
        #df = df[df['scenario_name'] == 'baseline']

        for c, channel in enumerate(channels):
            ax = axes[c]
            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
            ax.plot(df['date'], df['%s_median' % channel], color=palette[i], label=simdate)
            ax.fill_between(df['date'].values, df['%s_lower' % channel], df['%s_upper' % channel],
                            color=palette[i], linewidth=0, alpha=0.3)

            if channel in capacity.keys():
                ax.plot([np.min(df['date']), np.max(df['date'])],
                        [capacity[channel], capacity[channel]], '--', linewidth=1, color='black')

            ax.set_title(channel_labels[c], y=0.978)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
    axes[-1].legend(loc='upper right')
    plotname = f'iteration_comparison_{region}'

    plt.savefig(os.path.join(NU_civis_path, simdate, plotname + '.png'))
    # plt.savefig(os.path.join(NU_civis_path, simdate, 'pdf', plotname + '.pdf'), format='PDF')


def region_rt_plot(reg_nr=0, n_iter=2, rt_min=0.8, rt_max=2):
    if reg_nr == 0:
        region = "illinois"
        region_label = "Illinois"
    else:
        region = f'covidregion_{reg_nr}'
        region_label = f'COVID-19 Region {reg_nr}'
        if reg_nr == 11:
            region_label = f'Chicago'

    NU_civis_path = os.path.join(projectpath, 'NU_civis_outputs')
    exp_simdates = os.listdir(NU_civis_path)[-n_iter:]
    print(exp_simdates)

    fig = plt.figure(figsize=(10, 6))
    fig.subplots_adjust(right=0.97, left=0.08, hspace=0.4, wspace=0.2, top=0.87, bottom=0.17)
    palette = ['#595959', '#1696D2']
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
    #ax.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)

    for i, simdate in enumerate(exp_simdates):
        df = pd.read_csv(os.path.join(NU_civis_path, simdate, 'csv', f'nu_{simdate}.csv'))
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['geography_modeled'] == region]
        #df = df[df['scenario_name'] == 'baseline']

        simdate_label = "this weeks's fit"
        if i == 0:
            simdate_label = "last weeks's fit"

        ax.plot(df['date'], df['rt_median'], color=palette[i], label=simdate_label)
        ax.fill_between(df['date'], df['rt_lower'], df['rt_upper'], color=palette[i], linewidth=0, alpha=0.2)

        if i + 1 == len(exp_simdates):
            df_today = df[df['date'] == pd.Timestamp.today()]
            df_initial = df[df['date'] == df['date'].min()]
            rt_median_today = df_today.iloc[0]['rt_median'].round(decimals=3)
            rt_lower_today = df_today.iloc[0]['rt_lower'].round(decimals=3)
            rt_upper_today = df_today.iloc[0]['rt_upper'].round(decimals=3)
            rt_median_initial = df_initial.iloc[0]['rt_median'].round(decimals=3)
            rt_lower_initial = df_initial.iloc[0]['rt_lower'].round(decimals=3)
            rt_upper_initial = df_initial.iloc[0]['rt_upper'].round(decimals=3)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
    ax.axvline(x=pd.Timestamp.today(), color='#737373', linestyle='--')
    ax.axhline(y=1, color='black', linestyle='-')
    ax.set_ylim(rt_min, rt_max)
    ax.set_ylabel('Rt')
    ax.legend()

    caption_text = "\nModel fitted to hospital inpatient census, intensive care unit census data and reported deaths. " \
                   "\nRt estimated based on predicted new infections using EpiEstim (epyestim)." \
                   "\nThe lag time between infections and hospitalizations and fitting points in the simulations " \
                   "affect estimated Rt for the previous weeks\n" \
                   "Plot truncated at Rt=2, initial Rt is estimated at " \
                   f"{rt_median_initial} (95%CI{rt_lower_initial} - {rt_upper_initial})"
    text_top = "Estimated Rt using NU's COVID-19 model"
    text_bottom = f"Estimated Rt for {pd.Timestamp.today().strftime('%Y-%b-%d')}:" \
                  f" {str(rt_median_today)} (95%CI {str(rt_lower_today)} - {str(rt_upper_today)})"
    fig.suptitle(x=0.07, y=0.969, t=f"{region_label}\n{text_top}\n{text_bottom}", ha='left')
    fig.text(0.07, 0.02, caption_text, wrap=True, horizontalalignment='left', fontsize=8)

    plotname = f'{exp_simdates[-1]}_Rt_{region}'

    plt.savefig(os.path.join(NU_civis_path, simdate, 'plots', plotname + '.png'))
    if reg_nr == 10 or reg_nr ==11:
        plt.savefig(os.path.join(projectpath, 'NU_cdph_outputs', simdate, plotname + '.png'))


if __name__ == '__main__':
    
    Location = 'Local'
    first_plot_day = pd.Timestamp.today()- pd.Timedelta(30,'days')
    last_plot_day = pd.Timestamp.today()+ pd.Timedelta(30,'days')

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)
    comparison_plot()
    for reg_nr in [0,10,11]:
        region_rt_plot(reg_nr=reg_nr)

