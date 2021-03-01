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


def plot_vaccinations(adf, channel, add_mean_lines=False):

    max_all = np.max(adf[channel])
    mean_all = np.mean(adf[channel])

    fig = plt.figure(figsize=(14, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.5, wspace=0.3, top=0.90, bottom=0.08)
    palette = sns.color_palette('coolwarm', 8)
    k = 1
    channel_title = channel
    if channel == 'persons_fully_vaccinated_perc' or channel == 'daily_perc_vacc':
        channel_title =  f'{channel} (%)'
    fig.suptitle(x=0.5, y=0.98, t=channel_title, size=14)

    for e, ems_num in enumerate(adf['region'].unique()):
        ax = fig.add_subplot(3, 4, e + 1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        mdf = adf[adf['region'] == ems_num]
        mean_reg = np.mean(mdf[channel])

        if 'daily' in channel :
            ax.bar(mdf['date'], mdf[channel]*100, color=palette[k], label=channel)
        else :
            ax.plot(mdf['date'], mdf[channel]*100, color=palette[k], label=channel)

        if add_mean_lines:
            ax.axhline(y=mean_all*100, color='#737373', linestyle='-')
            ax.axhline(y=mean_reg*100, color=palette[k], linestyle='--')

        plotsubtitle = f'COVID-19 Region {str(int(ems_num))}'
        if ems_num == 0:
            plotsubtitle = 'Illinois'
        ax.set_title(plotsubtitle)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%d'))
        if channel == 'persons_fully_vaccinated_perc' or channel == 'daily_perc_vacc' :
            ax.set_ylim(0, (max_all+(max_all *0.1))*100)

        plt.savefig(os.path.join(plot_path, f'{channel}_by_covidregion.png'))
        plt.savefig(os.path.join(plot_path, 'pdf', f'{channel}_by_covidregion.pdf'), format='PDF')

def plot_vaccinations_compare(adf, channels):

    pdf = adf[adf['date']== max(adf['date'])]
    pdf = pdf.groupby(['date'])[['persons_fully_vaccinated','population']].agg(np.sum).reset_index()
    maxdate = max(pdf['date']).strftime('%b-%d-%Y')
    pdf['persons_fully_vaccinated_perc'] = pdf['persons_fully_vaccinated'] / pdf['population']
    IL_fully_vaccinated = int(pdf['persons_fully_vaccinated'])
    IL_fully_vaccinated_perc = float(pdf['persons_fully_vaccinated_perc'])
    IL_fully_vaccinated_perc = str(round(IL_fully_vaccinated_perc*100,3))

    fig = plt.figure(figsize=(14, 6))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.5, wspace=0.3, top=0.90, bottom=0.08)
    fig.suptitle(x=0.5, y=0.98, t=f'Fully vaccinated in IL by {maxdate} {IL_fully_vaccinated_perc} % (n={IL_fully_vaccinated})', size=14)
    palette = sns.color_palette('coolwarm', len(adf['region'].unique()))
    for c, channel in enumerate(channels):
        ax = fig.add_subplot(1, len(channels), c+1)
        ax.grid(b=True, which='major', color='#999999', linestyle='-', alpha=0.3)
        ax.set_title(f'{channel} (%)')

        yvalues = adf.groupby(['date'])[channel].agg(np.sum).reset_index()[channel].values
        for e, ems_num in enumerate(adf['region'].unique()):
            mdf = adf[adf['region'] == ems_num]
            if channel =='daily_perc_vacc':
                if e >0 :
                    yvalues = yvalues - mdf[channel].values
                ax.bar(mdf['date'], yvalues*100, color=palette[e], label=f'Region {str(int(ems_num))}')
                ax.set_ylabel('Stacked daily region vaccinations (%)')
            else:
                ax.plot(mdf['date'], mdf[channel]*100, color=palette[e], label=f'Region {str(int(ems_num))}')
                ax.set_ylabel('Persons fully vaccinated per region (%)')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%d'))
        ax.legend()
        plt.savefig(os.path.join(plot_path, f'compare_covidregions.png'))
        plt.savefig(os.path.join(plot_path, 'pdf', f'compare_covidregions.pdf'), format='PDF')

if __name__ == '__main__':

    datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
    plot_path = os.path.join(projectpath, 'Plots + Graphs', 'vaccinations')

    df = pd.read_csv(os.path.join(datapath, 'covid_IDPH','Corona virus reports','vaccinations.csv'))
    df.columns
    df['date'] = pd.to_datetime(df['report_date'])
    df['breakout_type'].unique()
    df['breakout_group'].unique()
    df = df[df['breakout_type']=='gender']
    ## Aggregate per county
    df = df.groupby(['date','geography_name','breakout_type'])[['persons_fully_vaccinated','administered_count','allocated_doses']].agg(np.sum).reset_index()

    df = merge_county_covidregions(df,key_x= 'geography_name')
    df.columns
    df['region'] = df['covid_region']
    df['region'].unique()
    df = df.dropna(subset=["region"])

    ## Aggregate per region
    adf = df.groupby(['date','region'])[['persons_fully_vaccinated','population']].agg(np.nansum).reset_index()
    adf.groupby('region')['population'].agg(np.max).reset_index()

    inc_df = pd.DataFrame()
    for region, df in adf.groupby('region'):
        print(region)
        df = df.sort_values('date')
        sdf = pd.DataFrame({'date': df['date'],
                            'population': df['population'],
                            'persons_fully_vaccinated': df['persons_fully_vaccinated'],
                            'daily_full_vaccinated': count_new(df, 'persons_fully_vaccinated')})
        sdf['region'] = region
        inc_df = pd.concat([inc_df, sdf])

    inc_df['persons_fully_vaccinated_perc'] = inc_df['persons_fully_vaccinated'] / inc_df['population']
    inc_df['daily_perc_vacc'] = inc_df['daily_full_vaccinated'] / inc_df['population']
    inc_df.to_csv(os.path.join(datapath, 'covid_IDPH','Corona virus reports','vaccinations_by_covidregion.csv'), index=False)

    ## Daily vaccinations
    #inc_df.groupby(['region'])[['daily_perc_vacc']].agg(np.mean)
    #np.mean(inc_df['daily_perc_vacc'])

    """Plots per COVID-19 region"""
    plot_vaccinations(adf=inc_df, channel = 'daily_perc_vacc')
    plot_vaccinations(adf=inc_df, channel = 'daily_full_vaccinated')
    plot_vaccinations(adf=inc_df, channel = 'persons_fully_vaccinated_perc')
    plot_vaccinations(adf=inc_df, channel = 'persons_fully_vaccinated')

    """Comparing COVID-19 region"""
    plot_vaccinations_compare(adf=inc_df, channels = ['daily_perc_vacc','persons_fully_vaccinated_perc'])

