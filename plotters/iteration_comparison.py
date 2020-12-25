"""
Compare COVID-19 simulation outputs to data.
Estimate Rt using epyestim
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns

sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *

mpl.rcParams['pdf.fonttype'] = 42

def comparison_plot(reg_nr=0, channels=None, n_iter=3):
    if reg_nr == 0:
        region = "illinois"
    else:
        region = f'covidregion_{reg_nr}'

    if channels == None:
        channels = ['cases', 'cases_new', 'deaths', 'deaths_det', 'recovered',
                    'hosp_bed','icu', 'vent'] #'hosp_det_bed',  'icu_det'

    capacity = load_capacity(ems=reg_nr)
    new_keys = ['hosp_det_bed', 'icu_det', 'vent']
    for key, n_key in zip(capacity.keys(), new_keys):
        capacity[n_key] = capacity.pop(key)

    fig = plt.figure(figsize=(16, 8))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.07, hspace=0.15)
    palette = sns.color_palette('Set1', n_iter)

    NU_civis_path = os.path.join(projectpath, 'NU_civis_outputs')
    exp_simdates = os.listdir(NU_civis_path)[-n_iter:]
    print(exp_simdates)

    for i, simdate in enumerate(exp_simdates):
        df = pd.read_csv(os.path.join(NU_civis_path, simdate, 'csv', f'nu_{simdate}.csv'), parse_dates=['date'])
        df = df[df['geography_modeled'] == region]
        df = df[df['scenario_name'] == 'baseline']

        for c, channel in enumerate(channels):
            ax = fig.add_subplot(2, 5, c + 1)
            ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
            ax.plot(df['date'], df['%s_median' % channel], color=palette[i], label=simdate)
            ax.fill_between(df['date'].values, df['%s_lower' % channel], df['%s_upper' % channel],
                            color=palette[i], linewidth=0, alpha=0.2)

            if channel in capacity.keys():
                ax.plot([np.min(df['date']), np.max(df['date'])],
                        [capacity[channel], capacity[channel]], '--', linewidth=2, color='black')

            ax.set_title(channel, y=0.85)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        axes[-1].legend()

    plotname = f'iteration_comparison_{region}'

    plt.savefig(os.path.join(NU_civis_path, simdate, plotname + '.png'))
    #plt.savefig(os.path.join(NU_civis_path, simdate, 'pdf', plotname + '.pdf'), format='PDF')


if __name__ == '__main__':

    Location = 'Local'
    first_plot_day = date.today() - timedelta(30)
    last_plot_day = date.today() + timedelta(30)

    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)
    comparison_plot()
