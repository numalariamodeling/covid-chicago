import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
import geopandas as gpd
import matplotlib.colors as colors
from plotting.colors import load_color_palette

mpl.rcParams['pdf.fonttype'] = 42


LL_date = '201020'

idph_data_path = '/Volumes/fsmresfiles/PrevMed/Covid-19-Modeling/IDPH line list'
cleaned_line_list_fname = os.path.join(idph_data_path,
                                       'LL_%s_JGcleaned_no_race.csv' % LL_date)
box_data_path = '/Users/jlg1657/Box/NU-malaria-team/data/covid_IDPH'
project_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago'
plot_path = os.path.join(project_path, 'Plots + Graphs', '_trend_tracking')
emr_fname = os.path.join(box_data_path, 'emresource_by_region.csv')
spec_coll_fname = os.path.join(box_data_path, 'Corona virus reports', '%s_LL_cases_by_EMS_spec_collection.csv' % LL_date)
shp_path = os.path.join(box_data_path, 'shapefiles')


def load_cleaned_line_list() :

    df = pd.read_csv(cleaned_line_list_fname)
    return df


def make_heatmap(ax, adf, col) :

    palette = sns.color_palette('RdYlBu_r', 101)

    df = adf.dropna(subset=[col])
    df = df.groupby([col, 'EMS'])['id'].agg(len).reset_index()
    df = df.rename(columns={'id' : col,
                            col : 'date'})
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['EMS', 'date'])

    ax.fill_between([np.min(df['date']), np.max(df['date']) + timedelta(days=1)],
                    [0.5, 0.5], [11.5, 11.5], linewidth=0, color=palette[0])
    for ems, edf in df.groupby('EMS') :
        max_in_col = np.max(edf[col])
        print(ems, max_in_col)
        for r, row in edf.iterrows() :
            ax.fill_between([row['date'], row['date'] + timedelta(days=1)],
                            [ems-0.5, ems-0.5], [ems+0.5, ems+0.5],
                            color=palette[int(row[col]/max_in_col*100)],
                            linewidth=0)
    ax.set_title(col)
    ax.set_ylabel('EMS region')
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())


def heatmap() :

    adf = load_cleaned_line_list()

    fig = plt.figure(figsize=(10,5))
    fig.subplots_adjust(left=0.05, right=0.97)
    cols = ['specimen_collection', 'deceased_date']

    for c, col in enumerate(cols) :
        ax = fig.add_subplot(1,len(cols),c+1)
        make_heatmap(ax, adf, col)

    plt.savefig(os.path.join(plot_path, 'EMS_cases_deaths_heatmap_%sLL.png' % LL_date))
    plt.show()


def aggregate_to_date_spec_collection() :

    adf = load_cleaned_line_list()
    col = 'specimen_collection'
    df = adf.dropna(subset=[col])
    df = df.groupby([col, 'EMS'])['id'].agg(len).reset_index()
    df = df.rename(columns={'id' : col,
                            col : 'date'})
    df = df.sort_values(by=['EMS', 'date'])
    df.to_csv(spec_coll_fname, index=False)


def plot_EMS_by_line(colname) :

    df = pd.read_csv(os.path.join(box_data_path, 'Cleaned Data', '%s_jg_aggregated_covidregion.csv' % LL_date))
    df = df[df['covid_region'].isin(range(1,12))]
    df['date'] = pd.to_datetime(df['date'])
    col = 'moving_ave'

    fig = plt.figure(figsize=(11,6))
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.05, top=0.95, hspace=0.3, wspace=0.25)
    palette = sns.color_palette('Set1')
    formatter = mdates.DateFormatter("%m-%d")
    for e, (ems, edf) in enumerate(df.groupby('covid_region')) :
        ax = fig.add_subplot(3,4,e+1)
        edf['moving_ave'] = edf[colname].rolling(window=7, center=False).mean()
        max_in_col = np.max(edf[col])
        ax.plot(edf['date'], edf[col], color=palette[0], label=ems)
        ax.fill_between(edf['date'].values, [0]*len(edf[col]), edf[col],
                        color=palette[0], linewidth=0, alpha=0.3)
        ax.set_title('region %d' % ems)
        ax.set_ylim(0, max_in_col*1.05)
        ax.set_xlim(date(2020,3,10), np.max(df['date']))
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        if e%4 == 0 :
            ax.set_ylabel(colname)
    fig.suptitle(colname)
    plt.savefig(os.path.join(plot_path, 'covid_region_%s_%sLL.png' % (colname, LL_date)))


def format_ax(ax, name) :
    ax.set_title(name)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')


class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, vcenter=None, clip=False):
        self.vcenter = vcenter
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.vcenter, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))


def plot_ratio_ems() :

    def get_ratio(adf, ems, w):
        edf = adf[adf['EMS'] == ems]
        col = 'specimen_collection'
        d = edf[col].values
        if w == 0:
            recent = np.mean(d[-7:])
        else:
            recent = np.mean(d[-7 * (w + 1):-7 * w])
        back = np.mean(d[-7 * (w + 2):-7 * (w + 1)])
        return recent / back

    df = pd.read_csv(spec_coll_fname)
    df['date'] = pd.to_datetime(df['date'])
    max_date = date(2020, 7, 8)
    df = df[df['date'] <= max_date]
    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    ems_shp['REGION'] = ems_shp['REGION'].astype(int)

    fig = plt.figure(figsize=(12, 10))
    fig.subplots_adjust(top=0.95)
    vmin, vmax = 0.4, 3
    norm = MidpointNormalize(vmin=vmin, vcenter=1, vmax=vmax)
    for week in range(6) :
        ax = fig.add_subplot(2,3,6-week)
        format_ax(ax, '%d weeks ago vs %d weeks ago' % (week, week+1))
        ems_shp['ratio'] = ems_shp['REGION'].apply(lambda x : get_ratio(df, x, week))
        ems_shp.plot(column='ratio', ax=ax, cmap='RdYlBu_r', edgecolor='0.8',
                     linewidth=0.8, legend=False, norm=norm)
        sm = plt.cm.ScalarMappable(cmap='RdYlBu_r', norm=norm)
        sm._A = []
        cbar = fig.colorbar(sm, ax=ax)
    fig.suptitle('week over week ratio of cases by specimen collection date\nLL data ending ' + str(max_date))
    plt.savefig(os.path.join(plot_path, 'EMS_weekly_case_ratio_%sLL.png' % LL_date))


def load_county_map_with_public_data() :

    from public_idph_data import load_county_cases
    df = load_county_cases()
    county_shp = gpd.read_file(os.path.join(shp_path, 'IL_BNDY_County', 'IL_BNDY_County_Py.shp'))

    cols = ['Positive_Cases', 'Deaths', 'Tested']
    sdf = df[df['County'].isin(['Cook', 'Chicago'])]
    sdf = sdf.groupby('update_date')[cols].agg(np.sum).reset_index()
    sdf['County'] = 'Cook'
    df = df[~df['County'].isin(['Cook', 'Chicago'])]
    df = pd.concat([df, sdf], sort=True)

    df['County'] = df['County'].apply(lambda x : x.upper())

    df.loc[df['County'] == 'DE WITT', 'County'] = 'DEWITT'
    # ds_shp = pd.merge(left=county_shp, right=df, left_on='COUNTY_NAM', right_on='County')
    df = df.sort_values(by=['County', 'update_date'])

    return county_shp, df


def plot_ratio_county() :

    ds_shp, df = load_county_map_with_public_data()
    max_date = np.max(df['update_date'])
    fig = plt.figure(figsize=(12, 10))
    fig.subplots_adjust(top=0.95)
    vmin, vmax = 0, 3
    norm = MidpointNormalize(vmin=vmin, vcenter=1, vmax=vmax)

    def get_ratio(adf, county, w):
        cdf = adf[adf['County'] == county.upper()]
        # if len(cdf) == 0 :
        #     return 100
        cdf['daily_pos'] = np.insert(np.diff(cdf['Positive_Cases']), 0, 0)
        d = cdf['daily_pos'].values
        if w == 0:
            recent = np.mean(d[-7:])
        else:
            recent = np.mean(d[-7 * (w + 1):-7 * w])
        back = np.mean(d[-7 * (w + 2):-7 * (w + 1)])
        if back == 0 and recent == 0 :
            return -1
        if back == 0 :
            return vmax
        return min([recent / back, vmax])

    for week in range(6) :
        ax = fig.add_subplot(2,3,6-week)
        format_ax(ax, '%d weeks ago vs %d weeks ago' % (week, week+1))
        ds_shp['ratio'] = ds_shp['COUNTY_NAM'].apply(lambda x : get_ratio(df, x, week))
        ds_shp.plot(ax=ax, color='#969696', edgecolor='0.8',
                    linewidth=0.8, legend=False)
        pdf = ds_shp[ds_shp['ratio'] == -1]
        pdf.plot(ax=ax, color='#313695', edgecolor='0.8',
                 linewidth=0.8, legend=False)
        pdf = ds_shp[ds_shp['ratio'] >= 0]
        pdf.plot(column='ratio', ax=ax, cmap='RdYlBu_r', edgecolor='0.8',
                     linewidth=0.8, legend=False, norm=norm)
        sm = plt.cm.ScalarMappable(cmap='RdYlBu_r', norm=norm)
        sm._A = []
        cbar = fig.colorbar(sm, ax=ax)
    fig.suptitle('week over week ratio of cases\npublic data ending ' + str(max_date))
    plt.savefig(os.path.join(plot_path, 'county_weekly_case_ratio.png'))


def plot_LL_all_IL() :

    df = pd.read_csv(os.path.join(box_data_path, 'Cleaned Data', '%s_jg_aggregated_covidregion.csv' % LL_date))
    df = df.groupby('date')[['cases', 'deaths', 'admissions']].agg(np.sum).reset_index()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    df = df[df['date'] >= date(2020, 3, 15)]

    palette = load_color_palette('wes')
    formatter = mdates.DateFormatter("%m-%d")
    sns.set_style('whitegrid', {'axes.linewidth' : 0.5})
    fig = plt.figure(figsize=(8,6))
    fig.subplots_adjust(left=0.1, right=0.97, bottom=0.05, top=0.97)

    def plot_data(adf, ax, col, color) :
        ax.bar(adf['date'].values, adf[col],
               align='center', color=color, linewidth=0, alpha=0.5)
        adf['moving_ave'] = adf[col].rolling(window=7, center=True).mean()
        ax.plot(adf['date'], adf['moving_ave'], '-', color=color)
        ax.set_ylabel('positives')
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_ylabel(col)

    ax = fig.add_subplot(3,1,1)
    plot_data(df, ax, 'cases', palette[0])
    ax = fig.add_subplot(3,1,2)
    plot_data(df, ax, 'admissions', palette[4])
    ax = fig.add_subplot(3,1,3)
    plot_data(df, ax, 'deaths', palette[3])

    fig.savefig(os.path.join(plot_path, 'IL_cases_deaths_LL%s.png' % LL_date))
    fig.savefig(os.path.join(plot_path, 'IL_cases_deaths_LL%s.pdf' % LL_date), format='PDF')


def combo_LL_emr() :

    ldf = pd.read_csv(os.path.join(box_data_path, 'Cleaned Data', '%s_jg_aggregated_ems.csv' % LL_date))
    edf = pd.read_csv(os.path.join(box_data_path, 'Corona virus reports', 'emresource_by_region.csv'))
    edf['date'] = pd.to_datetime(edf['date_of_extract'])
    edf = edf.rename(columns={'region' : 'EMS'})
    edf = edf[['date', 'covid_non_icu', 'confirmed_covid_icu', 'EMS']]
    ldf['date'] = pd.to_datetime(ldf['date'])
    df = pd.merge(left=ldf, right=edf, on=['date', 'EMS'], how='outer')
    df = df.sort_values(by=['EMS', 'date'])
    df[df['EMS'] == 11].to_csv(os.path.join(box_data_path, 'Cleaned Data', 'LL_EMR_%s_EMS11.csv' % LL_date), index=False)


if __name__ == '__main__' :

    # aggregate_to_date_spec_collection()
    # combo_LL_emr()
    # heatmap()
    plot_EMS_by_line('cases')
    plot_EMS_by_line('admissions')
    plot_EMS_by_line('deaths')
    # plot_ratio_ems()
    # plot_ratio_county()
    plot_LL_all_IL()
    # plt.show()

