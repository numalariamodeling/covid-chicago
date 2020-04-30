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

scen_dir = os.path.join(projectpath, 'NU_civis_outputs', '20200429')
csv_dir = os.path.join(scen_dir, 'csv')
plot_dir = os.path.join(scen_dir, 'plots')

if __name__ == '__main__' :

    col_names = {
        "infected_median": "Number of Covid-19 infections",
        "infected_95CI_lower": "Lower error bound of covid-19 infections",
        "infected_95CI_upper": "Upper error bound of covid-19 infections",
        "new_deaths_median": "Number of new covid-19 deaths",
        "new_deaths_95CI_lower": "Lower error bound of new covid-19 deaths",
        "new_deaths_95CI_upper": "Upper error bound of new covid-19 deaths",
        "hospitalized_median": "Number of hospital beds occupied",
        "hospitalized_95CI_lower": "Lower error bound of number of hospital beds occupied",
        "hospitalized_95CI_upper": "Upper error bound of number of hospital beds occupied",
        "critical_median": "Number of ICU beds occupied",
        "critical_95CI_lower": "Lower error bound of number of ICU beds occupied",
        "critical_95CI_upper": "Upper error bound of number of ICU beds occupied",
        "ventilators_median": "Number of ventilators used",
        "ventilators_95CI_lower": "Lower error bound of number of ventilators used",
        "ventilators_95CI_upper": "Upper error bound of number of ventilators used"
    }
    col_names = {value: key for key, value in col_names.items()}
    channels = ['infected', 'new_deaths', 'hospitalized', 'critical', 'ventilators']
    plot_first_day = date(2020, 3, 13)
    plot_last_day = date(2020, 7, 31)

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
            ax.set_title(channel, y=0.85)
            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_major_locator(mdates.MonthLocator())

        plt.savefig(os.path.join(plot_dir, il_fname.replace('csv', 'pdf')), format='PDF')
        plt.close(fig)


