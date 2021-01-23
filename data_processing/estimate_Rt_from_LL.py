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
import epyestim
import epyestim.covid19 as covid19
import seaborn as sns

sys.path.append('../')
from load_paths import load_box_paths
from processing_helpers import *

mpl.rcParams['pdf.fonttype'] = 42


def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-exp",
        "--exp_name",
        type=str,
        help="Name of simulation experiment"
    )
    parser.add_argument(
        "-loc",
        "--Location",
        type=str,
        help="Local or NUCLUSTER",
        default="Local"
    )
    return parser.parse_args()


def get_distributions(show_plot=False):
    si_distrb = covid19.generate_standard_si_distribution()
    delay_distrb = covid19.generate_standard_infection_to_reporting_distribution()

    if show_plot:
        fig, axs = plt.subplots(1, 2, figsize=(12, 3))
        axs[0].bar(range(len(si_distrb)), si_distrb, width=1)
        axs[1].bar(range(len(delay_distrb)), delay_distrb, width=1)
        axs[0].set_title('Default serial interval distribution')
        axs[1].set_title('Default infection-to-reporting delay distribution')

    return si_distrb, delay_distrb


def rt_plot(df, first_day=None, last_day=None):
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle(x=0.5, y=0.989, t='Estimated time varying reproductive number (Rt)')
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.4, wspace=0.2, top=0.93, bottom=0.05)
    palette = sns.color_palette('husl', 8)

    df['date'] = pd.to_datetime(df['date'])
    if first_day != None:
        df = df[df['date'].between(first_day, last_day)]

    rt_min = df['rt_lower'].min()
    rt_max = df['rt_upper'].max()
    if rt_max > 4:
        rt_max = 4
    if rt_max < 1.1:
        rt_max = 1.1
    if rt_min > 0.9:
        rt_min = 0.9

    for e, reg in enumerate(df['geography_modeled'].unique()):
        ax = fig.add_subplot(3, 4, e + 1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        mdf = df.loc[df['geography_modeled'] == reg]
        ax.plot(mdf['date'], mdf['rt_median'], color=palette[0])
        ax.fill_between(mdf['date'].values, mdf['rt_lower'], mdf['rt_upper'],
                        color=palette[0], linewidth=0, alpha=0.3)
        plotsubtitle = reg.replace('covidregion_', f'COVID-19 Region ')
        if reg == 'illinois':
            plotsubtitle = 'Illinois'
        ax.set_title(plotsubtitle)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d\n%b'))
        if first_day != None:
            ax.set_xlim(first_day, last_day)
        ax.axvline(x=pd.Timestamp.today(), color='#737373', linestyle='--')
        ax.axhline(y=1, color='black', linestyle='-')
        ax.set_ylim(rt_min, rt_max)

    plotname = 'rt_from_LLdata_by_covidregion_full'
    if not first_day == None:
        plotname = 'rt_from_LLdata_by_covidregion_truncated'
    plt.savefig(os.path.join(plot_path, f'{plotname}.png'))
    # plt.savefig(os.path.join(plot_path, f'{plotname}.pdf'), format='PDF')


def run_Rt_estimation(smoothing_window=14, r_window_size=7):
    """Code following online example:
    https://github.com/lo-hfk/epyestim/blob/main/notebooks/covid_tutorial.ipynb
    """

    LL_file_date = get_latest_LLfiledate(file_path=os.path.join(datapath, 'covid_IDPH', 'Cleaned Data'))
    df = pd.read_csv(
        os.path.join(datapath, 'covid_IDPH', 'Cleaned Data', f'{LL_file_date}_jg_aggregated_covidregion.csv'))
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'].between(pd.Timestamp('2020-04-01'), pd.Timestamp.today())]

    df_rt_all = pd.DataFrame()
    for ems_nr in range(1, 12):
        mdf = df.loc[df['covid_region'] == ems_nr]
        mdf.cases = mdf.cases.astype(int)
        mdf = mdf.set_index('date')['cases']

        """Use default distributions (for covid-19)"""
        si_distrb, delay_distrb = get_distributions(show_plot=False)
        df_rt = covid19.r_covid(mdf[:-1], smoothing_window=smoothing_window, r_window_size=r_window_size)

        df_rt['geography_modeled'] = f'covidregion_{ems_nr}'
        df_rt.reset_index(inplace=True)
        df_rt = df_rt.rename(columns={'index': 'date',
                                      'Q0.5': 'rt_median',
                                      'Q0.025': 'rt_lower',
                                      'Q0.975': 'rt_upper'})
        df_rt = df_rt[['date', 'geography_modeled', 'rt_median', 'rt_lower', 'rt_upper']]
        df_rt['smoothing_window'] = smoothing_window
        df_rt['r_window_size'] = r_window_size
        df_rt_all = df_rt_all.append(df_rt)

    df_rt_all.to_csv(os.path.join(plot_path, f'rt_from_LLdata.csv'), index=False)
    rt_plot(df=df_rt_all, first_day=None, last_day=None)
    rt_plot(df=df_rt_all, first_day=first_plot_day, last_day=last_plot_day)

    return df_rt


if __name__ == '__main__':
    
    first_plot_day = pd.Timestamp(pd.Timestamp.today()) - pd.Timedelta(30,'days')
    last_plot_day = pd.Timestamp(pd.Timestamp.today()) 


    datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()

    plot_path = os.path.join(projectpath, 'Plots + Graphs/Rt_plots')
    #run_Rt_estimation(smoothing_window=14, r_window_size=7)
    run_Rt_estimation(smoothing_window=28, r_window_size=3)
