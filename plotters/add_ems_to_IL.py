import os
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns

mpl.rcParams['pdf.fonttype'] = 42


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

mixed_scenarios = True
simdate = '20200506'

scen_dir = os.path.join(projectpath, 'NU_civis_outputs', simdate)
if mixed_scenarios == True :
    scen_dir = os.path.join(wdir, 'simulation_output', simdate + '_mixed_reopening')

csv_dir = os.path.join(scen_dir, 'csv')
plot_dir = os.path.join(scen_dir, 'plots')

if __name__ == '__main__' :


    col_names = civis_colnames(reverse=True)
    channels = ['infected', 'new_symptomatic', 'new_deaths', 'hospitalized', 'critical', 'ventilators']
    plot_first_day = date(2020, 3, 1)
    plot_last_day = date(2020, 10, 1)

    ems_fnames = [x for x in os.listdir(csv_dir) if 'ems' in x]
    for fname in ems_fnames :
        il_fname = fname.replace('ems', 'illinois')
        adf = pd.read_csv(os.path.join(csv_dir, fname))
        adf['Date'] = pd.to_datetime(adf['Date'])
        adf = adf[(adf['Date'] >= plot_first_day) & (adf['Date'] <= plot_last_day)]

        df = adf.groupby('Date').agg(np.sum).reset_index()
        del df['ems']

        df.to_csv(os.path.join(csv_dir, il_fname), index=False)
        adf.to_csv(os.path.join(csv_dir, fname), index=False)

        df = df.rename(columns=col_names)

        fig = plt.figure(figsize=(18,12))
        fig.subplots_adjust(right=0.97, wspace=0.2, left=0.07, hspace=0.15)
        palette = sns.color_palette('Set1', len(channels))

        for c, channel in enumerate(channels) :
            ax = fig.add_subplot(4,2,c+1)

            ax.plot(df['Date'], df['%s_median' % channel], color=palette[c])
            ax.fill_between(df['Date'].values, df['%s_95CI_lower' % channel],
                            df['%s_95CI_upper' % channel],
                            color=palette[c], linewidth=0, alpha=0.2)

            #lower_bound = 0
            #if channel == "infected": upper_bound = 5500000
            #if channel == "new_deaths": upper_bound = 10000
            #if channel == "critical": upper_bound = 110000
            #if channel == "new_symptomatic": upper_bound = 460000
            #if channel == "hospitalized": upper_bound = 150000
            #if channel == "ventilators": upper_bound = 86000
            #plt.ylim([lower_bound, upper_bound])

            ax.set_title(channel, y=0.85)
            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_major_locator(mdates.MonthLocator())

        plt.savefig(os.path.join(plot_dir, il_fname.replace('csv', 'pdf')), format='PDF')
        plt.close(fig)




