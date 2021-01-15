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

mpl.rcParams['pdf.fonttype'] = 42


def plot_over_time(df, time_var):
    fig = plt.figure(figsize=(10, 5))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.95, bottom=0.09)
    palette = sns.color_palette('husl', 8)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(df[time_var], df['median_f_inf_det'], color=palette[0])
    ax.fill_between(df[time_var].values, df['p25_f_inf_det'], df['p975_f_inf_det'], color=palette[0], linewidth=0, alpha=0.2)
    ax.set_title('d_Sys')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
    ax.set_ylim(0, 1.5)
    fig.savefig(os.path.join(wdir, 'inputs', 'testing', f'dSym_by_{time_var}_levincsv.png'))


if __name__ == '__main__':

    fname_levin = 'f_inf_det_Illinois_201124_excessdeaths_and_nonstationary.csv'
    fname_odriscoll = 'f_inf_det_Illinois_201124_excessdeaths_and_nonstationary_odriscoll.csv'
    fname=fname_levin

    df = pd.read_csv(os.path.join(projectpath, 'Plots + Graphs', 'detection_estimation', fname))
    df.columns
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['month'] = pd.to_datetime(df['date']).dt.month
    df[['median_f_inf_det', 'p25_f_inf_det', 'p975_f_inf_det']].describe()

    df_aggr = df.groupby('month')[['median_f_inf_det', 'p25_f_inf_det', 'p975_f_inf_det']].agg(np.mean).reset_index()
    df_aggr['source_dat'] = fname
    df_aggr.to_csv(os.path.join(wdir, 'inputs', 'testing', f"{str(date.today()).replace('-', '')}_dSym.csv"))

    plot_over_time(df=df, time_var='date')
    plot_over_time(df=df_aggr, time_var='month')
