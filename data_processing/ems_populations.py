import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping, Point, Polygon
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
datapath = os.path.join(datapath, 'covid_IDPH')
census_path = os.path.join(datapath, 'census')
shp_path = os.path.join(datapath, 'shapefiles')
pop_path = os.path.join(datapath, 'rasters', 'IL_2018_synpop')


def count_total_pop_for_ems(df, ems_poly, census_tract_shp) :
    census_tract_shp['in_ems'] = census_tract_shp['geometry'].apply(lambda x: x.intersects(ems_poly))
    tract_ids = census_tract_shp[census_tract_shp['in_ems']]['GEOID'].values

    sdf = df[df['tract_fips'].isin(tract_ids)]
    return np.sum(sdf['size']) + len(sdf)


def pop_by_ems(ems_shp, census_tract_shp) :

    df = pd.read_csv(os.path.join(pop_path, 'IL2018_Households'))

    pop_df = pd.DataFrame( { 'covid_region' : ems_shp['new_restor'],
                             'population' : [count_total_pop_for_ems(df, x, census_tract_shp) for x in ems_shp['geometry']]})

    pop_df.to_csv(os.path.join(datapath, 'EMS Population', 'covid_region_population_from_RTI.csv'), index=False)
    print(np.sum(pop_df['population']))


def pop_age_structure_by_ems(ems_shp, census_tract_shp, agebins, output_fname) :

    right_edges = [x-1 for x in agebins[1:]]
    right_edges[-1] = 100

    colnames = ['%dto%d' % (x,y) for x,y in zip(agebins[:-1], right_edges)]

    hh_df = pd.read_csv(os.path.join(pop_path, 'IL2018_Households'))
    person_df = pd.read_csv(os.path.join(pop_path, 'IL2018_Persons'))

    adf = pd.DataFrame()
    for ems, ems_poly in zip(ems_shp['REGION'], ems_shp['geometry']) :
        census_tract_shp['in_ems'] = census_tract_shp['geometry'].apply(lambda x: x.intersects(ems_poly))
        tract_ids = census_tract_shp[census_tract_shp['in_ems']]['GEOID'].values

        hh_ids = hh_df[hh_df['tract_fips'].isin(tract_ids)]['hh_id'].values
        ages = person_df[person_df['hh_id'].isin(hh_ids)]['agep'].values

        hist, bins = np.histogram(ages, bins=agebins)
        sdf = pd.DataFrame( { binname : [val] for binname, val in zip(colnames, hist)})
        sdf['ems'] = ems
        adf = pd.concat([adf, sdf])

    adf.to_csv(output_fname, index=False)


def ems_pop_structure() :

    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    census_tract_shp = gpd.read_file(os.path.join(shp_path, 'tl_2019_17_tract', 'tl_2019_17_tract.shp'))

    # pop_by_ems(ems_shp, census_tract_shp)

    # agebins = [0, 20, 40, 60, 200]
    agebins = [0, 20, 30, 40, 50, 60, 70, 80, 200]

    output_fname = os.path.join(datapath, 'EMS Population', 'EMS_population_from_RTI_by_age_8grpLL.csv')
    pop_age_structure_by_ems(ems_shp, census_tract_shp, agebins, output_fname)


def ems_proportional_pop_by_county() :

    ems_pop_structure()
    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    county_shp = gpd.read_file(os.path.join(shp_path, 'IL_BNDY_County', 'IL_BNDY_County_Py.shp'))
    census_tract_shp = gpd.read_file(os.path.join(shp_path, 'tl_2019_17_tract', 'tl_2019_17_tract.shp'))
    df = pd.read_csv(os.path.join(pop_path, 'IL2018_Households'))

    def list_in_ems(small_area_shp, small_area_col, ems_poly):
        small_area_shp['in_ems'] = small_area_shp['geometry'].apply(lambda x: x.intersects(ems_poly))
        return small_area_shp[small_area_shp['in_ems']][small_area_col].values

    ems_county_df = pd.DataFrame()
    for ems, ems_poly in zip(ems_shp['REGION'], ems_shp['geometry']) :
        counties = list_in_ems(county_shp, 'COUNTY_NAM', ems_poly)
        county_shp_df = county_shp[county_shp['COUNTY_NAM'].isin(counties)]
        pops = []
        for county, county_poly in zip(county_shp_df['COUNTY_NAM'], county_shp_df['geometry']) :
            poly = county_poly.intersection(ems_poly)
            pops.append(count_total_pop_for_ems(df, poly, census_tract_shp))
        cdf = pd.DataFrame({ 'county' : counties,
                             'pop in ems' : pops})
        cdf['EMS'] = int(ems)
        ems_county_df = pd.concat([ems_county_df, cdf])
    ems_county_df.to_csv(os.path.join(datapath, 'EMS Population', 'EMS_population_by_county.csv'), index=False)
    ems_df = pd.read_csv(os.path.join(datapath, 'EMS Population', 'EMS_population_from_RTI.csv'))
    ems_df = ems_df.rename(columns={'population' : 'EMS population'})
    ems_county_df = pd.merge(left=ems_county_df, right=ems_df, on='EMS', how='left')
    ems_county_df['share_of_ems_pop'] = ems_county_df['pop in ems']/ems_county_df['EMS population']
    ems_county_df.to_csv(os.path.join(datapath, 'EMS Population', 'EMS_population_by_county.csv'), index=False)


def ems_race_and_ethnicity_structure() :

    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    cbg_shp = gpd.read_file(os.path.join(shp_path, 'tl_2016_17_bg', 'tl_2016_17_bg.shp'))

    race_df = pd.read_csv(os.path.join(census_path, 'data', 'cbg_b02.csv'))
    keep_race_cols = [x for x in race_df.columns.values if '1e' in x]
    eth_df = pd.read_csv(os.path.join(census_path, 'data', 'cbg_b03.csv'))
    keep_eth_cols = [x for x in eth_df.columns.values if '2e' in x]

    ems_race_df = pd.DataFrame()
    ems_eth_df = pd.DataFrame()
    for ems, ems_poly in zip(ems_shp['REGION'], ems_shp['geometry']) :
        cbg_shp['in_ems'] = cbg_shp['geometry'].apply(lambda x: x.intersects(ems_poly))
        tract_ids = cbg_shp[cbg_shp['in_ems']]['GEOID'].values

        rdf = race_df[race_df['census_block_group'].isin(tract_ids)]
        rdf['ems'] = ems
        sdf = rdf.groupby('ems').agg(np.sum).reset_index()
        sdf = sdf[['ems'] + keep_race_cols]
        ems_race_df = pd.concat([ems_race_df, sdf])

        rdf = eth_df[eth_df['census_block_group'].isin(tract_ids)]
        rdf['ems'] = ems
        sdf = rdf.groupby('ems').agg(np.sum).reset_index()
        sdf = sdf[['ems'] + keep_eth_cols]
        ems_eth_df = pd.concat([ems_eth_df, sdf])

    colname_df = pd.read_csv(os.path.join(census_path, 'metadata', 'cbg_field_descriptions.csv'))
    colname_df = colname_df.set_index('table_id')
    ems_race_df = ems_race_df.rename(columns={
        col : colname_df.at[col, 'field_full_name'] for col in keep_race_cols
    })
    ems_eth_df = ems_eth_df.rename(columns={
        col : colname_df.at[col, 'field_full_name'] for col in keep_eth_cols
    })

    race_output_fname = os.path.join(datapath, 'EMS Population', 'EMS_population_by_race_cbg.csv')
    eth_output_fname = os.path.join(datapath, 'EMS Population', 'EMS_population_by_eth_cbg.csv')

    ems_race_df.to_csv(race_output_fname, index=False)
    ems_eth_df.to_csv(eth_output_fname, index=False)


if __name__ == '__main__' :

    # ems_race_and_ethnicity_structure()
    # ems_pop_structure()
    regions_shp = gpd.read_file(os.path.join(shp_path, 'covid_regions', 'covid_regions.shp'))
    census_tract_shp = gpd.read_file(os.path.join(shp_path, 'tl_2019_17_tract', 'tl_2019_17_tract.shp'))
    pop_by_ems(regions_shp, census_tract_shp)
