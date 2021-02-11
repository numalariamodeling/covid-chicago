import os
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta, datetime

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns
from plotting.colors import load_color_palette


mpl.rcParams['pdf.fonttype'] = 42


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()


if __name__ == '__main__' :

    scen_dirs = ['20210203_IL_quest_baseline',
                 '20210205_IL_locale_uniform_range_mr_bvariant_infectivity_0.10_bvariant',
                 '20210204_IL_locale_uniform_range_ae_bvariant_infectivity_0.25_bvariant',
                 '20210204_IL_locale_uniform_range_ae_bvariant_infectivity_0.5_bvariant',
                 '20210204_IL_locale_uniform_range_ae_bvariant_infectivity_0.75_bvariant']
    labels = ['baseline', '10%', '25%', '50%', '75%']

    col = 'deaths'

    plot_first_day = date(2021, 2, 1)
    plot_last_day = date(2021, 5, 1)

    fig = plt.figure(figsize=(6,4))
    fig.subplots_adjust(left=0.2)
    ax = fig.gca()
    p = load_color_palette('wes')
    palette = [p[x] for x in [8, 4, 2, 1, 3]]

    for s, scen in enumerate(scen_dirs) :
        simpath = os.path.join(projectpath, 'cms_sim', 'simulation_output', scen)
        fname = 'nu_%s_All.csv' % scen.split('_')[0]
        df = pd.read_csv(os.path.join(simpath, fname))
        df['date'] = pd.to_datetime(df['date'])
        df = df[(df['date'] >= plot_first_day) & (df['date'] <= plot_last_day)]
        ax.bar([s], np.sum(df['%s_median' % col]), align='center', color=palette[s], label=labels[s])
        ax.plot([s,s], [np.sum(df['%s_lower' % col]), np.sum(df['%s_upper' % col])], color='k', linewidth=0.5)
    ax.legend()
    ax.set_ylabel('cumulative deaths Feb 1 - May 1')
    plt.savefig(os.path.join(projectpath, 'project_notes', 'figures', '210205_bvariant_deaths_barplot.png'))
    plt.savefig(os.path.join(projectpath, 'project_notes', 'figures', '210205_bvariant_deaths_barplot.pdf'), format='PDF')
    plt.show()