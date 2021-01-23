import os
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import calculate_incidence
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns

mpl.rcParams['pdf.fonttype'] = 42


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

if __name__ == '__main__' :

    plot_dir = os.path.join(projectpath, 'Plots + Graphs', 'simulated_scenarios')
    output_dir = os.path.join(wdir, '..', 'NU_civis_outputs', '20200506', 'trajectories')
    exp_name = 'Trajectories_set7'
    ems = 5

    adf = pd.read_csv(os.path.join(output_dir, '%s.csv' % exp_name))
    adf['date'] = pd.to_datetime(adf['date'])
    adf = adf[adf['ems'] == ems]

    adf = calculate_incidence(adf)
    adf = adf[adf['date'] >= pd.Timestamp('2020-10-01')]
    # print(adf.columns.values)

    channels = ['infected', 'new_detected_hospitalized']

    gdf = adf.groupby(['run_num', 'sample_num'])
    palette = sns.color_palette('rainbow', len(gdf))

    fig = plt.figure()
    ax = [fig.add_subplot(2,1,x+1) for x in range(len(channels))]

    for i, ((s, r), df) in enumerate(gdf) :
        for c, channel in enumerate(channels) :
            ax[c].plot(df['date'], df[channel], linewidth=1, alpha=1, color=palette[i])
    for c, channel in enumerate(channels):
        ax[c].set_title(channel)

    plt.savefig(os.path.join(plot_dir, 'ems5_individual_trajectories.pdf'), format='PDF')
    plt.show()

