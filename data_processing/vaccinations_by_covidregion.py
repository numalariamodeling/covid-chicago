import pandas as pd
import numpy as np
import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib.dates as mdates
import sys
sys.path.append('../')
from processing_helpers import *
from load_paths import load_box_paths

mpl.rcParams['pdf.fonttype'] = 42

def plot_vaccinations(adf, channels,channel_title, plot_name=None):

    fig = plt.figure(figsize=(14, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.5, wspace=0.3, top=0.91, bottom=0.08)
    palette = ('#913058', "#F6851F", "#00A08A", "#D61B5A", "#5393C3", "#F1A31F", "#98B548", "#8971B3", "#969696")
    # sns.color_palette('husl', len(channels))
    fig.suptitle(x=0.5, y=0.98, t=channel_title, size=14)

    for e, ems_num in enumerate(adf['covid_region'].unique()):
        plotsubtitle = f'COVID-19 Region {str(int(ems_num))}'
        if ems_num == 0:
            plotsubtitle = 'Illinois'

        ax = fig.add_subplot(3, 4, e + 1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        mdf = adf[adf['covid_region'] == ems_num]
        for c, channel in enumerate(channels):
            if 'daily' in channel :
                ax.bar(mdf['date'], mdf[channel], color=palette[c], label=channel, alpha=0.6)
            else :
                ax.plot(mdf['date'], mdf[channel], color=palette[c], label=channel)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        ax.set_title(plotsubtitle)
        if 'perc' in channels[0]:
            ax.set_ylim(0, 0.5)

    ax.legend()

    if plot_name is None:
        plot_name = f'{channels[0]}_by_covidregion'

    plt.savefig(os.path.join(plot_path, f'{plot_name}.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{plot_name}.pdf'), format='PDF')

def plot_vaccinations_compare(adf, channels,type):
    channel_daily = channels[0]
    channel_cumul = channels[1]
    channel_cumul_perc = channels[2]
    pdf = adf[adf['date']== max(adf['date'])]
    pdf = pdf.groupby(['date'])[[channel_cumul,'population']].agg(np.sum).reset_index()
    maxdate = max(pdf['date']).strftime('%b-%d-%Y')
    pdf[f'{channel_cumul}_perc'] = pdf[channel_cumul] / pdf['population']
    IL_vaccinated = int(pdf[channel_cumul])
    IL_vaccinated_perc = float(    pdf[f'{channel_cumul}_perc'])
    IL_vaccinated_perc = str(round(IL_vaccinated_perc*100,3))

    fig = plt.figure(figsize=(16, 6))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.5, wspace=0.3, top=0.90, bottom=0.08)
    fig.suptitle(x=0.5, y=0.98, t=f'Population {type} vaccinated in IL by {maxdate} {IL_vaccinated_perc} % (n={IL_vaccinated})', size=14)
    palette = sns.color_palette('coolwarm', len(adf['covid_region'].unique()))
    for c, channel in enumerate(channels):
        ax = fig.add_subplot(1, len(channels), c+1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        ax.set_title(channel)
        yvalues = adf.groupby(['date'])[channel_daily].agg(np.sum).reset_index()[channel_daily].values
        for e, ems_num in enumerate(adf['covid_region'].unique()):
            mdf = adf[adf['covid_region'] == ems_num]
            if channel ==channel_daily:
                ax.bar(mdf['date'], yvalues, color=palette[e], label=f'Region {str(int(ems_num))}')
                yvalues = yvalues - mdf[channel_daily].values
                ax.set_ylabel(channel_daily)
            elif channel == channel_cumul_perc:
                ax.plot(mdf['date'], mdf[channel]*100, color=palette[e], label=f'Region {str(int(ems_num))}')
                ax.set_ylabel(f'Persons {type} vaccinated per region (%)')
            else:
                ax.plot(mdf['date'], mdf[channel], color=palette[e], label=f'Region {str(int(ems_num))}')
                ax.set_ylabel(f'Persons {type} vaccinated per region')

            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        ax.legend()
        plt.savefig(os.path.join(plot_path, f'compare_covidregions_{type}.png'))
        plt.savefig(os.path.join(plot_path, 'pdf', f'compare_covidregions_{type}.pdf'), format='PDF')

if __name__ == '__main__':

    datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
    plot_path = os.path.join(projectpath, 'Plots + Graphs', 'vaccinations')

    fname = 'vaccinations_historical.csv' #'vaccinations.csv'
    df = pd.read_csv(os.path.join(datapath, 'covid_IDPH','Corona virus reports',fname))
    df.columns
    df['date'] = pd.to_datetime(df['report_date'])
    min( df['date'])

    df = merge_county_covidregions(df,key_x= 'geography_name')
    df.columns
    df['covid_region'].unique()
    df = df.dropna(subset=["covid_region"])

    ## Aggregate per region
    adf = df.groupby(['date','covid_region'])[['persons_fully_vaccinated','population','administered_count','allocated_doses']].agg(np.nansum).reset_index()
    adf.groupby('covid_region')['population'].agg(np.max).reset_index()

    inc_df = pd.DataFrame()
    for region, df in adf.groupby('covid_region'):
        print(region)
        df = df.sort_values('date')
        sdf = pd.DataFrame({'date': df['date'],
                            'population': df['population'],
                            'persons_fully_vaccinated': df['persons_fully_vaccinated'],
                            'administered_count': df['administered_count'],
                            'daily_full_vaccinated': count_new(df, 'persons_fully_vaccinated'),
                            'daily_new_administered_count': count_new(df, 'administered_count')})
        sdf['covid_region'] = region

        """Replace first entry (backlog)"""
        sdf.loc[sdf['date'] == min(sdf['date']),'daily_full_vaccinated'] = sdf.loc[sdf['date'] == min(sdf['date']),'persons_fully_vaccinated']
        sdf.loc[sdf['date'] == min(sdf['date']),'daily_new_administered_count'] = sdf.loc[sdf['date'] == min(sdf['date']),'administered_count']
        inc_df = pd.concat([inc_df, sdf])

    inc_df['persons_fully_vaccinated_perc'] = inc_df['persons_fully_vaccinated'] / inc_df['population']
    inc_df['daily_fully_vacc_perc'] = inc_df['daily_full_vaccinated'] / inc_df['population']

    inc_df['persons_first_vaccinated'] = inc_df['administered_count'] - inc_df['persons_fully_vaccinated']
    inc_df['persons_first_vaccinated_perc'] = inc_df['persons_first_vaccinated'] / inc_df['population']

    inc_df['daily_first_vacc'] = inc_df['daily_new_administered_count'] - inc_df['daily_full_vaccinated']
    inc_df['daily_first_vacc_perc'] = inc_df['daily_first_vacc'] / inc_df['population']
    #inc_df.groupby('covid_region')['population'].agg(np.max).reset_index()
    inc_df.to_csv(os.path.join(datapath, 'covid_IDPH','Corona virus reports','vaccinations_by_covidregion.csv'), index=False)

    ## Daily vaccinations
    """Plots per COVID-19 region"""
    plot_vaccinations(adf=inc_df,
                      channels = ['daily_first_vacc_perc','daily_fully_vacc_perc'],
                      channel_title="Daily vaccinated population 1st or 2nd (fully) dose (proportion)")

    plot_vaccinations(adf=inc_df,
                      channels = ['daily_first_vacc','daily_full_vaccinated'],
                      channel_title="Daily vaccinated population 1st or 2nd (fully) dose (population)")

    plot_vaccinations(adf=inc_df,
                      channels = ['persons_first_vaccinated_perc','persons_fully_vaccinated_perc'],
                      channel_title="Total vaccinated population (proportion)",
                      plot_name='fraction_vaccinated_by_covidregion')

    plot_vaccinations(adf=inc_df,
                      channels = ['persons_first_vaccinated','persons_fully_vaccinated'],
                      channel_title="Total vaccinated population",
                      plot_name = 'population_vaccinated_by_covidregion')

    """Comparing COVID-19 region"""
    plot_vaccinations_compare(adf=inc_df, channels = ['daily_full_vaccinated','persons_fully_vaccinated','persons_fully_vaccinated_perc'],type='fully')
    plot_vaccinations_compare(adf=inc_df, channels = ['daily_first_vacc','persons_first_vaccinated','persons_first_vaccinated_perc'],type='first')
