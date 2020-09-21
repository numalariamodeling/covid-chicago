import os
import sys
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

def plot(adf, plot_path, channels = None ) :

    if channels == None :
        channels = ['susceptible','exposed','infectious','recovered']
        
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(1, 1,  1)
    palette = sns.color_palette('Set1', len(channels))

    for c, channel in enumerate(channels) :
        mdf = adf.groupby('time')[channel].agg([np.mean]).reset_index()
        ax.plot(mdf['time'], mdf['mean'], linewidth=1, alpha=1, color=palette[c], label=channel)
    ax.legend()
    ax.set_xlabel('Time in days')
    plt.savefig(os.path.join(plot_path, 'sample_plot.png'))
    plt.show()

def reprocess(test_dir, input_fname='trajectories.csv') :

    fname = os.path.join(test_dir, input_fname)
    row_df = pd.read_csv(fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    num_channels = len([x for x in df.columns.values if '{0}' in x])
    num_samples = int((len(row_df)-1)/num_channels)

    df = df.reset_index(drop=False)
    df = df.rename(columns={'index' : 'time'})
    df['time'] = df['time'].astype(float)

    adf = pd.DataFrame()
    for sample_num in range(num_samples) :
        channels = [x for x in df.columns.values if '{%d}' % sample_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x : x.split('{')[0] for x in channels
        })
        sdf['sample_num'] = sample_num
        adf = pd.concat([adf, sdf])

    adf = adf.reset_index()
    del adf['index']
    return adf

if __name__ == '__main__':

    test_dir = sys.argv[1]
    df = reprocess(test_dir=test_dir)
    plot(adf=df, plot_path=test_dir)
