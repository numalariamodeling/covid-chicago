import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
from scipy import signal
import matplotlib.colors as colors
from plotting.colors import load_color_palette

mpl.rcParams['pdf.fonttype'] = 42


LL_date = '210216'

box_data_path = '/Users/jlg1657/Box/NU-malaria-team/data/covid_IDPH'
project_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago'
plot_path = os.path.join(project_path, 'Plots + Graphs', '_trend_tracking')


def crosscorr(datax, datay, lag=0, wrap=False):
    """ Lag-N cross correlation.
    Shifted data filled with NaNs

    Parameters
    ----------
    lag : int, default 0
    datax, datay : pandas.Series objects of equal length
    Returns
    ----------
    crosscorr : float
    """
    if wrap:
        shiftedy = datay.shift(lag)
        shiftedy.iloc[:lag] = datay.iloc[-lag:].values
        return datax.corr(shiftedy)
    else:
        return datax.corr(datay.shift(lag))


if __name__ == '__main__' :

    public_df = pd.read_csv(os.path.join(box_data_path, 'Corona virus reports', 'IDPH_public_county.csv'))
    d_df = pd.read_csv(os.path.join(box_data_path, 'Cleaned Data', '210216_jg_deceased_date_covidregion.csv'))

    public_df = public_df[public_df['county'] == 'Illinois']
    public_df['test_date'] = pd.to_datetime(public_df['test_date'])
    public_df['by_reported_date'] = np.insert(np.diff(public_df['deaths']), 0, 0)

    d_df['date'] = pd.to_datetime(d_df['date'])
    d_df = d_df[d_df['date'] > date(2020, 3, 1)]
    d_df = d_df.groupby('date')['cases'].agg(np.sum).reset_index()

    df = pd.merge(left=d_df, right=public_df[['test_date', 'by_reported_date']], left_on='date', right_on='test_date', how='outer')
    df = df.fillna(0)
    df = df.rename(columns={'cases' : 'by_deceased_date'})
    firstday = np.min(df['date'])
    df['day'] = df['date'].apply(lambda x: (x - firstday).days)
    df = df[df['date'] <= date(2020, 12, 31)]

    lags = range(-20, 15)
    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    palette = load_color_palette('wes')
    fig = plt.figure()
    ax = fig.gca()

    rs = [crosscorr(df['by_deceased_date'], df['by_reported_date'], lag) for lag in lags]
    ax.plot(lags, rs)
    ax.set_xlabel('lag')
    ax.set_ylabel('corr')
    fig.savefig(os.path.join(project_path, 'project_notes', 'publications', 'mobility_part_2', 'death_reporting_lag.png'))
    plt.show()
