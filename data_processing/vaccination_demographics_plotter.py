import pandas as pd
import numpy as np
#import geopandas as gpd
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


def get_pop_by_age(adjust_for_chicago=True):
    """Population by age per covid region"""
    pop_df = pd.read_csv(os.path.join(datapath, "covid_IDPH/population/cc-est2019-agesex-17.csv"))
    pop_df = pop_df[pop_df['YEAR']==12] # corresponds to 2019
    pop_df['AGE16BELOW_TOT'] = pop_df['POPESTIMATE'] - pop_df['AGE16PLUS_TOT']
    pop_df['AGE65BELOW_TOT'] = pop_df['POPESTIMATE'] - pop_df['AGE65PLUS_TOT']
    pop_df['16-64'] = pop_df['AGE65BELOW_TOT'] - pop_df['AGE16BELOW_TOT']
    pop_df['65+'] = pop_df['AGE65PLUS_TOT']
    pop_df['county'] = pop_df['CTYNAME'].str.replace(' County','')
    pop_df = pop_df[['county','POPESTIMATE','65+','16-64','MEDIAN_AGE_TOT','AGE16BELOW_TOT']]

    if adjust_for_chicago:
        chicago_pop = 2456274
        chicago_perc_pop_below16 = 0.1758 # below 15 due to agebins..
        chicago_perc_pop_16to65 = 0.70174  # estimated from https://www.chicagohealthatlas.org/indicators/total-population
        chicago_perc_pop_above65 = 0.1224
        chicago_pop_below16 = int(round(chicago_pop * chicago_perc_pop_below16,0))
        chicago_pop_16to65 = int(round(chicago_pop * chicago_perc_pop_16to65,0))
        chicago_pop_above65 = int(round(chicago_pop * chicago_perc_pop_above65,0))

        pop_df[pop_df['county'] == 'Cook']
        chicago_df = {'county': ['Chicago'], 'POPESTIMATE': [chicago_pop],
                      '65+': [chicago_pop_above65], '16-64': [chicago_pop_16to65],
                      'MEDIAN_AGE_TOT' : [-9],'AGE16BELOW_TOT':[chicago_pop_below16] }
        chicago_df = pd.DataFrame(data=chicago_df)
        cook_df = pop_df[pop_df['county'] == 'Cook']

        cook_df['POPESTIMATE'] = cook_df['POPESTIMATE'] - chicago_pop
        cook_df['65+'] = cook_df['65+'] - chicago_pop_above65
        cook_df['16-64'] = cook_df['16-64']  - chicago_pop_16to65
        cook_df['AGE16BELOW_TOT'] = cook_df['AGE16BELOW_TOT']  - chicago_pop_below16
        cook_chicago_df = cook_df.append(chicago_df)

        pop_df = pop_df[pop_df['county'] != 'Cook']
        pop_df = pop_df.append(cook_chicago_df).reset_index()


    ### Chicgo (region 11 missing)
    pop_df = merge_county_covidregions(pop_df, key_x='county', add_pop=False)
    #pop_df.groupby(['covid_region'])[['MEDIAN_AGE_TOT']].agg([np.min, np.mean, np.max] ).reset_index()
    pop_df = pop_df.groupby(['covid_region'])[['POPESTIMATE','AGE16BELOW_TOT', '65+', '16-64']].agg(np.nansum).reset_index()

    pop_df_i = pd.melt(pop_df, id_vars=['covid_region'], value_vars=['65+', '16-64'])
    pop_df_i.rename(columns={"variable": "agegrp"}, inplace=True)
    pop_df_i.rename(columns={"value": "population"}, inplace=True)

    pop_df['16-64']  = pop_df['16-64'] / pop_df['POPESTIMATE']
    pop_df['65+']  = pop_df['65+'] / pop_df['POPESTIMATE']
    pop_df_ii = pd.melt(pop_df, id_vars=['covid_region'], value_vars=['65+', '16-64'])
    pop_df_ii.rename(columns={"variable": "agegrp"}, inplace=True)
    pop_df_ii.rename(columns={"value": "pop_perc"}, inplace=True)

    df = pd.merge(pop_df_i, pop_df_ii)

    return df


def plot_by_age_region(df, channel,plot_title='',plot_name=None):

    fig = plt.figure(figsize=(14, 8))
    fig.subplots_adjust(right=0.97, left=0.05, hspace=0.5, wspace=0.3, top=0.91, bottom=0.08)
    palette = ('#913058', "#F6851F", "#00A08A", "#D61B5A", "#5393C3", "#F1A31F", "#98B548", "#8971B3", "#969696")
    # sns.color_palette('husl', len(channels))
    fig.suptitle(x=0.5, y=0.98, t=plot_title, size=14)

    for e, ems_num in enumerate(df['covid_region'].unique()):
        plotsubtitle = f'COVID-19 Region {str(int(ems_num))}'
        if ems_num == 0:
            plotsubtitle = 'Illinois'

        ax = fig.add_subplot(3, 4, e + 1)
        ax.grid(b=True, which='major', axis='y',color='#999999', linestyle='-', alpha=0.3)
        mdf = df[df['covid_region'] == ems_num]
        ax.bar(mdf['agegrp'], mdf[channel], color=palette[c], label=age)
        ax.set_title(plotsubtitle)
        if channel=='fully_vaccinated_perc':
            ax.set_ylim(0, 0.25)
    ax.legend()

    if plot_name is None:
        plot_name =f'{channel}_by_age_region'

    plt.savefig(os.path.join(plot_path, f'{plot_name}.png'))
    plt.savefig(os.path.join(plot_path, 'pdf', f'{plot_name}.pdf'), format='PDF')

if __name__ == '__main__':

    datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
    plot_path = os.path.join(projectpath, 'Plots + Graphs', 'vaccinations')

    df = pd.read_csv(os.path.join('R:/PrevMed/Covid-19-Modeling/IDPH line list', 'vaccinations_by_zip_210303.csv'))
    df['extract_date'].unique()
    df['date'] = pd.to_datetime(df['extract_date'])

    df.groupby(['date', 'covid_region'])[['fully_vaccinated', 'doses']].agg( np.nansum).reset_index()
    df.groupby(['date', 'agegrp'])[['fully_vaccinated', 'doses']].agg(np.nansum).reset_index()
    df.groupby(['date','covid_region', 'agegrp'])[['fully_vaccinated', 'doses']].agg(np.nansum).reset_index()

    df = df.groupby(['date', 'covid_region','agegrp'])[['fully_vaccinated', 'doses']].agg(np.nansum).reset_index()

    """Population by age per covid region"""
    pop_df = get_pop_by_age()

    """Merge vaccination and age population data and plot"""
    df = pd.merge(how='left', left=df, right=pop_df, on=['covid_region','agegrp'])
    df['fully_vaccinated_perc'] = df['fully_vaccinated'] / df['population']


    plot_by_age_region(df=df, channel='fully_vaccinated_perc',
                       plot_title='Fraction of population vaccinated per age and region (2021-02-19)')
    plot_by_age_region(df=df, channel='pop_perc',
                       plot_title='Fraction of population in age group by region  (2019)')



