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
shp_path = os.path.join(datapath, 'shapefiles')
pop_path = os.path.join(datapath, 'rasters', 'IL_2018_synpop')


def count_total_pop_for_ems(df, ems_poly, census_tract_shp) :
    census_tract_shp['in_ems'] = census_tract_shp['geometry'].apply(lambda x: x.intersects(ems_poly))
    tract_ids = census_tract_shp[census_tract_shp['in_ems']]['GEOID'].values

    sdf = df[df['tract_fips'].isin(tract_ids)]
    return np.sum(sdf['size']) + len(sdf)


def pop_by_ems(ems_shp, census_tract_shp) :

    df = pd.read_csv(os.path.join(pop_path, 'IL2018_Households'))

    pop_df = pd.DataFrame( { 'EMS' : ems_shp['REGION'],
                             'population' : [count_total_pop_for_ems(df, x, census_tract_shp) for x in ems_shp['geometry']]})

    pop_df.to_csv(os.path.join(datapath, 'EMS Population', 'EMS_population_from_RTI.csv'), index=False)
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


if __name__ == '__main__' :

    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    census_tract_shp = gpd.read_file(os.path.join(shp_path, 'tl_2019_17_tract', 'tl_2019_17_tract.shp'))

    # pop_by_ems(ems_shp, census_tract_shp)

    agebins = [0, 20, 40, 60, 200]
    # agebins = [0, 10, 20, 30, 40, 50, 60, 70, 200]

    output_fname = os.path.join(datapath, 'EMS Population', 'EMS_population_from_RTI_by_age_4grp.csv')
    pop_age_structure_by_ems(ems_shp, census_tract_shp, agebins, output_fname)

