import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import copy
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
from processing_helpers import *
from plotting.colors import load_color_palette
from statsmodels.stats.proportion import proportion_confint

mpl.rcParams['pdf.fonttype'] = 42
today = datetime.today()

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
datapath = os.path.join(datapath, 'covid_IDPH')
plotdir = os.path.join(projectpath, 'project_notes', 'publications', 'labor_and_delivery_surveillance', 'figures')


def plot_number_tested_timeseries(adf) :

    cols = ['num_delivered', 'num_tested']
    df = adf.groupby('delivery_date')[cols].agg(np.sum).reset_index()
    df = df.sort_values(by='delivery_date')
    df['excess_delivered'] = df['num_delivered'] - df['num_tested']

    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(8,4))
    ax = fig.gca()
    palette = [load_color_palette('wes')[x] for x in [3, 4]]
    formatter = mdates.DateFormatter("%m-%d")

    ax.bar(df['delivery_date'], df['num_tested'], color=palette[1],
           align='center', linewidth=0, alpha=0.5)
    ax.bar(df['delivery_date'], df['excess_delivered'], bottom=df['num_tested'], color=palette[0],
           align='center', linewidth=0, alpha=0.5)
    for c, col in enumerate(cols) :
        df['moving_ave'] = df[col].rolling(window=7, center=True).mean()
        ax.plot(df['delivery_date'], df['moving_ave'], '-', color=palette[c], label=col.split('_')[-1])
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.legend()
    ax.set_ylabel('number of individuals')
    ax.set_xlabel('date of delivery')
    fig.savefig(os.path.join(plotdir, 'daily_number_tested.png'))
    fig.savefig(os.path.join(plotdir, 'daily_number_tested.pdf'), format='PDF')


def plot_fraction_asymptomatic(adf) :

    cols = ['num_positive', 'num_asymptomatic']
    df = adf.groupby('delivery_date')[cols].agg(np.sum).reset_index()
    df = df.sort_values(by='delivery_date')
    df = df[df['num_positive'] > 0]
    df['fraction_asymptomatic'] = df['num_asymptomatic']/df['num_positive']

    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(8,4))
    ax = fig.gca()
    palette = sns.color_palette('Set1')
    formatter = mdates.DateFormatter("%m-%d")

    # ax.scatter(df['delivery_date'].values, df['fraction_asymptomatic'].values, df['num_positive'], color=palette[1],
    #            label='daily')

    df['moving_ave_frac'] = df['fraction_asymptomatic'].rolling(window=7, center=True).mean()
    ax.plot(df['delivery_date'], df['moving_ave_frac'], '-', color=palette[1])

    df['moving_ave_asymp'] = df['num_asymptomatic'].rolling(window=7, center=True).sum()
    df['moving_ave_pos'] = df['num_positive'].rolling(window=7, center=True).sum()
    lows, highs = [], []
    for r, row in df.iterrows() :
        low, high = proportion_confint(row['moving_ave_asymp'], row['moving_ave_pos'])
        lows.append(low)
        highs.append(high)

    ax.fill_between(df['delivery_date'].values, lows, highs, color=palette[1], linewidth=0, alpha=0.3)

    ax.set_ylabel('percent of positives who were asymptomatic at time of test')
    ax.set_xlabel('date of delivery')
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    fig.savefig(os.path.join(plotdir, 'percent_asymptomatic.png'))
    fig.savefig(os.path.join(plotdir, 'percent_asymptomatic.pdf'), format='PDF')


def plot_tpr(adf) :

    cols = ['num_positive', 'num_tested']
    df = adf[adf['covid_region'] == 11].groupby('delivery_date')[cols].agg(np.sum).reset_index()
    df = df.sort_values(by='delivery_date')
    df = df[df['num_tested'] > 0]
    df['fraction_positive'] = df['num_positive']/df['num_tested']

    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(8,4))
    ax = fig.add_subplot(2,1,1)
    palette = [load_color_palette('wes')[x] for x in [5, 4]]
    formatter = mdates.DateFormatter("%m-%d")

    # ax.scatter(df['delivery_date'].values, df['fraction_positive'].values, df['num_tested'], color=palette[0],
    #            label='daily')
    df['moving_ave_frac'] = df['fraction_positive'].rolling(window=7, center=True).mean()
    ax.plot(df['delivery_date'], df['moving_ave_frac'], '-', color=palette[0], label='moving average')

    df['moving_ave_test'] = df['num_tested'].rolling(window=7, center=True).sum()
    df['moving_ave_pos'] = df['num_positive'].rolling(window=7, center=True).sum()
    lows, highs = [], []
    for r, row in df.iterrows() :
        low, high = proportion_confint(row['moving_ave_pos'], row['moving_ave_test'])
        lows.append(low)
        highs.append(high)

    ax.fill_between(df['delivery_date'].values, lows, highs, color=palette[0], linewidth=0, alpha=0.3)

    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_ylabel('percent positive')
    ax.set_title('Region 11')
    ax.set_xlim(date(2020, 6, 10), date(2021, 1, 15))

    ax = fig.add_subplot(2,1,2)
    cdf = pd.read_csv(os.path.join(datapath, 'Corona virus reports', 'CLI_admissions.csv'))
    cdf = cdf[cdf['region'] == 'Chicago']
    cdf['date'] = pd.to_datetime(cdf['date'])
    cdf = cdf[(cdf['date'] >= np.min(df['delivery_date']) - timedelta(days=3)) & (cdf['date'] <= np.max(df['delivery_date'] + timedelta(days=3)))]
    cdf = cdf.groupby('date')['inpatient'].agg(np.sum).reset_index()
    cdf = cdf.sort_values(by='date')
    cdf['moving_ave_cli'] = cdf['inpatient'].rolling(window=7, center=True).mean()
    ax.plot(cdf['date'], cdf['moving_ave_cli'], '-', color=palette[1])
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_ylabel('CLI admissions')
    ax.set_xlabel('date')
    ax.set_ylim(0,)
    ax.set_xlim(date(2020, 6, 10), date(2021, 1, 15))

    fig.savefig(os.path.join(plotdir, 'TPR_and_CLI.png'))
    fig.savefig(os.path.join(plotdir, 'TPR_and_CLI.pdf'), format='PDF')


def plot_fraction_tested_by_region(adf) :

    cols = ['num_delivered', 'num_tested']
    df = adf.groupby('delivery_date')[cols].agg(np.sum).reset_index()
    df = df.sort_values(by='delivery_date')
    df['excess_delivered'] = df['num_delivered'] - df['num_tested']

    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(8,4))
    ax = fig.gca()
    palette = [load_color_palette('wes')[x] for x in [3, 4]]
    formatter = mdates.DateFormatter("%m-%d")

    pdf = copy.copy(df[df['covid_region'] == 11])
    pdf['fraction_tested'] = pdf['num_tested']/pdf['num_delivered']
    df['moving_ave'] = df[col].rolling(window=7, center=True).mean()
    ax.plot(df['delivery_date'], df['moving_ave'], '-', color=palette[c], label=col.split('_')[-1])

    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.legend()
    ax.set_ylabel('number of individuals')
    ax.set_xlabel('date of delivery')
    fig.savefig(os.path.join(plotdir, 'daily_number_tested.png'))


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


def plot_lag(adf) :

    cols = ['num_positive', 'num_tested']
    df = adf[adf['covid_region'] == 11].groupby('delivery_date')[cols].agg(np.sum).reset_index()
    df = df.sort_values(by='delivery_date')
    df = df[df['num_tested'] > 0]
    df['fraction_positive'] = df['num_positive']/df['num_tested']

    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(5,4))
    ax = fig.gca()
    df['moving_ave_frac'] = df['fraction_positive'].rolling(window=7, center=True).mean()

    cdf = pd.read_csv(os.path.join(datapath, 'Corona virus reports', 'CLI_admissions.csv'))
    cdf = cdf[cdf['region'] == 'Chicago']
    cdf['date'] = pd.to_datetime(cdf['date'])
    cdf = cdf[(cdf['date'] >= np.min(df['delivery_date']) - timedelta(days=3)) & (cdf['date'] <= np.max(df['delivery_date'] + timedelta(days=3)))]
    cdf = cdf.groupby('date')['inpatient'].agg(np.sum).reset_index()
    cdf = cdf.sort_values(by='date')
    cdf['moving_ave_cli'] = cdf['inpatient'].rolling(window=7, center=True).mean()

    df = pd.merge(left=df[['delivery_date', 'moving_ave_frac']],
                  right=cdf[['date', 'moving_ave_cli']],
                  left_on='delivery_date', right_on='date', how='inner')

    lags = range(-20,30)
    rs = [crosscorr(df['moving_ave_frac'], df['moving_ave_cli'], lag) for lag in lags]
    ax.plot(lags, rs)
    ax.set_xlabel('days LD TPR lags CLI')
    ax.set_ylabel('cross correlation')
    fig.savefig(os.path.join(plotdir, 'TPR_and_CLI_cross_corr.png'))
    fig.savefig(os.path.join(plotdir, 'TPR_and_CLI_cross_corr.pdf'), format='PDF')


if __name__ == '__main__' :

    adf = pd.read_csv(os.path.join(datapath, 'perinatal', '210324_labor_delivery_clean.csv'))
    adf['delivery_date'] = pd.to_datetime(adf['delivery_date'])
    # plot_number_tested_timeseries(adf)
    # plot_fraction_asymptomatic(adf)
    # plot_tpr(adf)
    # plot_fraction_tested_by_region(adf)
    # plot_lag(adf)
    # plt.show()

    ems_regions = {
        'northcentral' : [1, 2],
        'northeast' : [7, 8, 9, 10, 11],
        'central' : [3, 6],
        'southern' : [4, 5]
    }

    for region in ems_regions :
        df = adf[adf['covid_region'].isin(ems_regions[region])]
        df = df[(df['delivery_date'] >= date(2020,8,15)) & (df['delivery_date'] <= date(2021,1,1))]
        gdf = df.groupby(['delivery_date'])['num_tested'].agg(np.sum).reset_index()
        print(region, np.mean(gdf['num_tested']))