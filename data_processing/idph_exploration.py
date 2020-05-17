import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
import geopandas as gpd
from shapely.geometry import mapping, Point, Polygon

mpl.rcParams['pdf.fonttype'] = 42


idph_data_path = '/Volumes/fsmresfiles/PrevMed/Covid-19-Modeling'
line_list_fname = os.path.join(idph_data_path,
                               'COVID_19Confirmed_Modeling___northwestern_0428.xlsx')
cleaned_line_list_fname = os.path.join(idph_data_path,
                                       'LL_200515.csv')
box_data_path = '/Users/jlg1657/Box/NU-malaria-team/data/covid_IDPH'
project_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago'
plot_path = os.path.join(project_path, 'Plots + Graphs')
shp_path = os.path.join(box_data_path, 'shapefiles')


def load_line_list() :

    df = pd.read_excel(line_list_fname, sheet_name='NW0428')
    return df

def load_cleaned_line_list() :

    df = pd.read_csv(cleaned_line_list_fname)
    return df

def print_num_missing_rows() :

    df = load_line_list()
    rows = len(df)
    print(rows)
    for col in df.columns.values :
        print(col, rows-len(df.dropna(subset=[col])))


def compare_death_plots() :

    df = load_cleaned_line_list()
    df = df.dropna(subset=['deceased_date'])
    df = df.groupby('deceased_date')['id'].agg(len).reset_index()
    df = df.rename(columns={'id' : 'daily_deaths_line_list',
                            'deceased_date' : 'Deceased Date'})
    # df.to_csv(os.path.join(box_data_path, 'Cleaned Data', 'daily_deaths_line_list_200515.csv'), index=False)
    # exit()

    df['Deceased Date'] = pd.to_datetime(df['Deceased Date'])

    ddf = pd.read_csv(os.path.join(box_data_path, 'Cleaned Data', 'daily_deaths_comparison_for_jaline_2.csv'))
    ddf['date'] = pd.to_datetime(ddf['date'])

    ddf = pd.merge(left=ddf, right=df, left_on='date', right_on='Deceased Date', how='outer')
    ddf['date'].fillna(ddf['Deceased Date'], inplace=True)
    ddf = ddf.sort_values(by='date')
    fig = plt.figure()
    ax = fig.gca()
    for col in [x for x in ddf.columns.values if 'death' in x] :
        sdf = ddf.dropna(subset=[col])
        ax.plot(sdf['date'], sdf[col], label=col)
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.legend()
    plt.savefig(os.path.join(plot_path, 'death_comparison.png'))
    plt.show()


def impute_onset_date() :

    adf = load_cleaned_line_list()
    adf = adf.dropna(subset=['Onset Date', 'Specimen Collection Date'], how='all')
    adf['Onset Date'] = pd.to_datetime(adf['Onset Date'])
    adf['Specimen Collection Date'] = pd.to_datetime(adf['Specimen Collection Date'])
    df = adf.dropna(subset=['Onset Date', 'Specimen Collection Date'])
    df['days between'] = df.apply(lambda x : (x['Specimen Collection Date'] - x['Onset Date']).days, axis=1)
    observed_days_between = df['days between'].values

    adf['imputed_days_between'] = np.random.choice(observed_days_between, len(adf), replace=True)
    sdf = adf[adf['Onset Date'].isna()]
    sdf['Onset Date imputed'] = sdf['Specimen Collection Date']
    sdf['Onset Date imputed'] = sdf.apply(lambda x : x['Specimen Collection Date'] - timedelta(days=x['imputed_days_between']), axis=1)
    sdf = sdf[['ID', 'Onset Date imputed']]
    adf = pd.merge(left=adf, right=sdf, on='ID', how='left')
    adf['Onset Date imputed'].fillna(adf['Onset Date'], inplace=True)

    adf.to_csv(cleaned_line_list_fname, index=False)


def plot_positives_by_date_type() :

    df = load_cleaned_line_list()
    fig = plt.figure()
    ax = fig.gca()
    cols = ['Onset Date', 'Specimen Collection Date', 'Onset Date imputed', 'Admission Date']
    for col in cols :
        sdf = df.groupby(col)['ID'].agg(len).reset_index()
        sdf = sdf.rename(columns={'ID' : 'by %s' % col})
        sdf[col] = pd.to_datetime(sdf[col])
        sdf = sdf.sort_values(by=col)
        sdf = sdf[(sdf[col] >= date(2020, 2, 23)) & (sdf[col] <= date(2020,4,12))]

        ax.plot(sdf[col], sdf['by %s' % col], label='by %s' % col)
    ax.set_ylabel('number positive tests')
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    ax.legend()
    plt.savefig(os.path.join(plot_path, 'num_positive_by_date_type.png'))
    plt.show()


def get_ems_counties_and_zips() :

    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    county_shp = gpd.read_file(os.path.join(shp_path, 'IL_BNDY_County', 'IL_BNDY_County_Py.shp'))
    zip_shp = gpd.read_file(os.path.join(shp_path, 'IL_zipcodes', 'IL_zipcodes.shp'))

    def list_in_ems(small_area_shp, small_area_col, ems_poly):
        small_area_shp['in_ems'] = small_area_shp['geometry'].apply(lambda x: x.intersects(ems_poly))
        return small_area_shp[small_area_shp['in_ems']][small_area_col].values

    rural_ems = range(1,7)
    ems_county_df = pd.DataFrame()
    ems_zip_df = pd.DataFrame()
    for ems, ems_poly in zip(ems_shp['REGION'], ems_shp['geometry']) :
        if int(ems) in rural_ems :
            sdf = pd.DataFrame( { 'county' : list_in_ems(county_shp, 'COUNTY_NAM', ems_poly) })
            sdf['ems'] = int(ems)
            ems_county_df = pd.concat([ems_county_df, sdf])
        else :
            sdf = pd.DataFrame( { 'zip' : list_in_ems(zip_shp, 'GEOID10', ems_poly) })
            sdf['ems'] = int(ems)
            ems_zip_df = pd.concat([ems_zip_df, sdf])
    zdf = ems_zip_df.groupby('zip').agg(len).reset_index()
    zdf = zdf.rename(columns={'ems' : 'num appearances'})
    zdf = zdf[zdf['num appearances'] > 1]
    repeated_zips = zdf['zip'].values

    ems_zip_df = ems_zip_df[~ems_zip_df['zip'].isin(repeated_zips)]

    def get_biggest_ems_match(zipcode, ems_shp, zdf) :
        zpoly = zdf.at[zipcode, 'geometry']
        ems_match = 0
        max_area = 0
        for ems, ems_poly in zip(ems_shp['REGION'], ems_shp['geometry']):
            a = zpoly.intersection(ems_poly).area
            if a > max_area:
                max_area = a
                ems_match = ems

        return ems_match

    counties = ems_county_df['county'].unique()
    ems_county_df = pd.DataFrame( { 'county' : counties,
                                    'ems' : [get_biggest_ems_match(x, ems_shp, county_shp.set_index('COUNTY_NAM')) for x in counties]})

    zdf = pd.DataFrame( { 'zip' : repeated_zips,
                          'ems' : [get_biggest_ems_match(x, ems_shp, zip_shp.set_index('GEOID10')) for x in repeated_zips]})
    ems_zip_df = pd.concat([ems_zip_df, zdf]).reset_index()
    ems_county_df = ems_county_df.sort_values(by='county')
    ems_zip_df = pd.concat([ems_zip_df, pd.DataFrame( { 'zip' : [60434, 60418, 60303, 60161, 60690, 61615, 60499,
                                                                 60024, 61101, 61701, 62559, 60168, 62881, 60079,
                                                                 60732, 62711, 60116, 61604, 60598, 61764, 62353,
                                                                 61032, 62233, 62526, 61603, 61832, 62901, 61525,
                                                                 62259, 62650, 60197, 60864, 62702, 60206, 60801,
                                                                 60822],
                                                        'ems' : [7, 7, 8, 8, 11, 2, 7,
                                                                 10, 1, 2, 3, 8, 5, 10,
                                                                 7, 3, 9, 2, 8, 2, 3,
                                                                 1, 4, 6, 2, 6, 5, 2,
                                                                 4, 3, 8, 8, 3, 10, 8,
                                                                 8]})], sort=True)
    ems_zip_df['zip'] = ems_zip_df['zip'].astype(int)
    ems_zip_df = ems_zip_df.sort_values(by='zip')

    return ems_county_df, ems_zip_df


def apply_ems() :

    ems_county_df, ems_zip_df = get_ems_counties_and_zips()
    df = load_line_list()
    df.loc[df['County at Onset'] == 'St Clair', 'County at Onset'] = 'St. Clair'
    df.loc[df['County at Onset'] == 'Jodaviess', 'County at Onset'] = 'Jo daviess'

    def set_ems_in_line_list(county, zipcode, ems_county_df, ems_zip_df) :
        if isinstance(county, str) and county.upper() in ems_county_df['county'].values :
            return ems_county_df[ems_county_df['county'] == county.upper()]['ems'].values[0]
        try :
            z = int(zipcode)
            if z in ems_zip_df['zip'].values :
                return ems_zip_df[ems_zip_df['zip'] == z]['ems'].values[0]
            elif z-1 in ems_zip_df['zip'].values :
                return ems_zip_df[ems_zip_df['zip'] == z-1]['ems'].values[0]
            elif z < 60000 or z > 63000 :
                return 11
            elif z >= 60600 and z < 60700 :
                return 11
            else :
                print(zipcode)
                return np.nan
        except ValueError :
            return np.nan

    df['EMS'] = df.apply(lambda x : set_ems_in_line_list(x['County at Onset'],
                                                         x['Patient Home Zip'],
                                                         ems_county_df,
                                                         ems_zip_df), axis=1)
    df.to_csv(cleaned_line_list_fname, index=False)


def plot_days_between_onset_and_specimen() :

    df = load_cleaned_line_list()
    df = df.dropna(subset=['Onset Date', 'Specimen Collection Date'])
    df['Onset Date'] = pd.to_datetime(df['Onset Date'])
    df['Specimen Collection Date'] = pd.to_datetime(df['Specimen Collection Date'])
    df['days between'] = df.apply(lambda x : (x['Specimen Collection Date'] - x['Onset Date']).days, axis=1)
    df = df[['Onset Date', 'Specimen Collection Date', 'days between']]
    df = df.sort_values(by='days between')

    fig = plt.figure()
    ax = fig.gca()
    hist, edges = np.histogram(df['days between'].values, bins=40)
    ax.bar(edges[:-1], hist)
    ax.set_xlabel('specimen collection date - onset date')
    ax.set_ylabel('count')
    plt.savefig(os.path.join(plot_path, 'difference between specimen and onset.png'))
    plt.show()


if __name__ == '__main__' :

    df = compare_death_plots()
    exit()

    df = load_cleaned_line_list()
    date_col = 'deceased_date'
    df = df.groupby([date_col, 'ems_region'])['ID'].agg(len).reset_index()
    df = df.rename(columns={'id' : 'cases',
                            date_col : 'date',
                            'ems_region' : 'EMS'})
    df = df.sort_values(by=['date', 'EMS'])
    df.to_csv(os.path.join(box_data_path, 'Cleaned Data', '200515_jg_%s_ems.csv' % date_col), index=False)

    # df.loc[df['County at Onset'] == 'St Clair', 'County at Onset'] = 'St. Clair'
    # df.loc[df['County at Onset'] == 'Jodaviess', 'County at Onset'] = 'Jo daviess'
