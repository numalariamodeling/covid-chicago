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

LL_date = '210412'

idph_data_path = '/Volumes/fsmresfiles/PrevMed/Covid-19-Modeling/IDPH line list'
line_list_fname = os.path.join(idph_data_path,
                               'LL_%s.csv' % LL_date)
cleaned_line_list_fname = os.path.join(idph_data_path,
                                       'LL_%s_JGcleaned.csv' % LL_date)
cleaned_deduped_fname = os.path.join(idph_data_path,
                                     'LL_%s_JGcleaned_no_race.csv' % LL_date)
box_data_path = '/Users/jlg1657/Box/NU-malaria-team/data/covid_IDPH'
project_path = '/Users/jlg1657/Box/NU-malaria-team/projects/covid_chicago'
plot_path = os.path.join(project_path, 'Plots + Graphs')
shp_path = os.path.join(box_data_path, 'shapefiles')


def load_line_list() :

    # df = pd.read_excel(line_list_fname, sheet_name='NW0428')
    df = pd.read_csv(line_list_fname)
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
    # df.to_csv(os.path.join(box_data_path, 'Cleaned Data', 'daily_deaths_line_list_200522.csv'), index=False)
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
                                                                 60822, 61103, 62206, 61614, 60058, 62040, 60400,
                                                                 62002, 60824, 60159, 61341, 60809, 60146, 61821,
                                                                 61937, 61085, 60495, 62226, 60997, 60059, 60880,
                                                                 61282, 61239, 62242, 61011, 61435, 62082, 62992,
                                                                 60037, 61401, 60957, 60840, 61008, 61804, 62208,
                                                                 62230, 61111, 60290, 61068, 60530, 60353, 62265,
                                                                 62615, 62232, 62220, 60808, 60208, 61544, 60001,
                                                                 60567, 62837, 60985, 62939, 61231, 62634, 62869,
                                                                 60115, 60821, 60167, 60122, 60717, 61021, 60978,
                                                                 60413, 62098, 62864, 60884, 62035, 60833, 60926,
                                                                 60362, 60785, 61704, 61373, 61920, 61107, 61462,
                                                                 61820, 62817, 62301],
                                                        'ems' : [7, 7, 8, 8, 11, 2, 7,
                                                                 10, 1, 2, 3, 8, 5, 10,
                                                                 7, 3, 9, 2, 8, 2, 3,
                                                                 1, 4, 6, 2, 6, 5, 2,
                                                                 4, 3, 8, 8, 3, 10, 8,
                                                                 8, 1, 4, 2, 10, 4, 7,
                                                                 4, 7, 8, 2, 7, 8, 6,
                                                                 6, 1, 7, 4, 6, 9, 7,
                                                                 2, 2, 4, 1, 2, 3, 5,
                                                                 10, 2, 6, 8, 1, 6, 4,
                                                                 4, 1, 10, 1, 1, 8, 4,
                                                                 3, 4, 4, 7, 10, 2, 9,
                                                                 8, 5, 6, 5, 2, 3, 5,
                                                                 1, 10, 10, 8, 10, 1, 6,
                                                                 10, 3, 5, 10, 4, 10, 6,
                                                                 10, 10, 2, 2, 6, 1, 2,
                                                                 6, 5, 3]})], sort=True)
    ems_zip_df['zip'] = ems_zip_df['zip'].astype(int)
    ems_zip_df = ems_zip_df.sort_values(by='zip')

    return ems_county_df, ems_zip_df


def apply_ems() :

    ems_county_df, ems_zip_df = get_ems_counties_and_zips()
    df = load_line_list()
    df.loc[df['county_at_onset'] == 'St Clair', 'county_at_onset'] = 'St. Clair'
    df.loc[df['county_at_onset'] == 'Jodaviess', 'county_at_onset'] = 'Jo daviess'

    def set_ems_in_line_list(county, zipcode, ems_county_df, ems_zip_df) :
        if isinstance(county, str) and county.upper() in ems_county_df['county'].values :
            return ems_county_df[ems_county_df['county'] == county.upper()]['ems'].values[0]
        try :
            z = int(zipcode)
            if z in ems_zip_df['zip'].values :
                return ems_zip_df[ems_zip_df['zip'] == z]['ems'].values[0]
            elif z-1 in ems_zip_df['zip'].values :
                return ems_zip_df[ems_zip_df['zip'] == z-1]['ems'].values[0]
            # elif z < 60000 or z > 63000 :
            #     return 11
            elif z >= 60600 and z < 60700 :
                return 11
            else :
                print(zipcode)
                return np.nan
        except ValueError :
            return np.nan

    df['EMS'] = df.apply(lambda x : set_ems_in_line_list(x['county_at_onset'],
                                                         x['patient_home_zip'],
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


def assign_covid_region() :

    ref_df = pd.read_csv(os.path.join(box_data_path , 'Corona virus reports', 'county_restore_region_map.csv'))
    ref_df = ref_df.set_index('county')

    regions_shp = gpd.read_file(os.path.join(shp_path, 'covid_regions', 'covid_regions.shp'))
    zip_shp = gpd.read_file(os.path.join(shp_path, 'IL_zipcodes', 'IL_zipcodes.shp'))
    zip_shp = zip_shp.set_index('GEOID10')

    def assign_region(ems, county, my_zip) :

        def by_zip(my_zip) :
            try :
                zpoly = zip_shp.at[my_zip, 'geometry']
                ems_match = 0
                max_area = 0
                for ems, ems_poly in zip(regions_shp['new_restor'], regions_shp['geometry']):
                    a = zpoly.intersection(ems_poly).area
                    if a > max_area:
                        max_area = a
                        ems_match = ems
                    return ems_match
            except KeyError :
                return -1

        if ems in [1, 2, 3, 4, 5, 6, 11] or np.isnan(ems):
            return ems
        if county in ['Out Of State'] :
            return 0
        try :
            return ref_df.at[county.upper(), 'new_restore_region']
        except KeyError :
            match = by_zip(my_zip)
        except AttributeError :
            match = by_zip(my_zip)
        if match < 0 :
            return ems

    df = load_cleaned_line_list()
    df['covid_region'] = df.apply(lambda x : assign_region(x['EMS'],
                                                           x['county_at_onset'],
                                                           x['patient_home_zip']), axis=1)
    df.to_csv(cleaned_line_list_fname, index=False)


def generate_combo_LL_agg_csv() :

    spec_coll_fname = os.path.join(box_data_path, 'Cleaned Data', '%s_jg_specimen_collection_covidregion.csv' % LL_date)
    case_df = pd.read_csv(spec_coll_fname)
    case_df = case_df.rename(columns={'specimen_collection' : 'cases'})
    death_df = pd.read_csv(os.path.join(box_data_path, 'Cleaned Data', '%s_jg_deceased_date_covidregion.csv' % LL_date))
    death_df = death_df.rename(columns={'cases' : 'deaths'})
    adm_df = pd.read_csv(os.path.join(box_data_path, 'Cleaned Data', '%s_jg_admission_date_covidregion.csv' % LL_date))
    adm_df = adm_df.rename(columns={'cases' : 'admissions'})

    df = pd.merge(left=case_df, right=death_df, on=['date', 'covid_region'], how='outer')
    df = pd.merge(left=df, right=adm_df, on=['date', 'covid_region'], how='outer')
    df = df.fillna(0)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')
    df.to_csv(os.path.join(box_data_path, 'Cleaned Data', '%s_jg_aggregated_covidregion.csv' % LL_date), index=False)


if __name__ == '__main__' :

    # apply_ems()
    # exit()

    # assign_covid_region()
    # df = load_cleaned_line_list()
    # df = df[df['covid_region'] < 1]
    # print(df[['patient_home_zip', 'county_at_onset', 'EMS', 'covid_region']].to_string())

    df = load_line_list()
    del df['race']
    del df['ethnicity']
    df = df.drop_duplicates()
    df.to_csv(cleaned_deduped_fname, index=False)
    adf = pd.read_csv(cleaned_deduped_fname)

    for date_col in ['admission_date', 'deceased_date', 'specimen_collection'] :
        df = adf.groupby([date_col, 'covid_region'])['id'].agg(len).reset_index()
        df = df.rename(columns={'id' : 'cases',
                                date_col : 'date'})
        df = df.sort_values(by=['date', 'covid_region'])
        df['date'] = pd.to_datetime(df['date'])
        df.to_csv(os.path.join(box_data_path, 'Cleaned Data', '%s_jg_%s_covidregion.csv' % (LL_date, date_col)), index=False)
    generate_combo_LL_agg_csv()

    # df.loc[df['county_at_onset'] == 'St Clair', 'county_at_onset'] = 'St. Clair'
    # df.loc[df['county_at_onset'] == 'Jodaviess', 'county_at_onset'] = 'Jo daviess'
