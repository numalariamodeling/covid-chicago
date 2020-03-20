import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def reprocess(output_fname=None) :

    fname = 'trajectories.csv'
    df = pd.read_csv(fname, skiprows=1)
    df = df.set_index('sampletimes').transpose()
    df = df.reset_index(drop=False)
    df = df.rename(columns={'index' : 'time'})

    if output_fname :
        df.to_csv(output_fname)
    return df


def plot(df) :

    plotchannels = [x for x in df.columns.values if '{' in x]

    fig = plt.figure()
    ax = fig.gca()
    for channel in plotchannels :
        ax.plot(df['time'], df[channel], label=channel.split('{')[0])
    ax.legend()
    plt.show()


if __name__ == '__main__' :


    df = reprocess()
    plot(df)
