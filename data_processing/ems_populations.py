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


def count_total_pop(df, ems_poly, census_tract_shp) :
    census_tract_shp['in_ems'] = census_tract_shp['geometry'].apply(lambda x: x.intersects(ems_poly))
    tract_ids = census_tract_shp[census_tract_shp['in_ems']]['GEOID'].values

    sdf = df[df['tract_fips'].isin(tract_ids)]
    return np.sum(sdf['size']) + len(sdf)


if __name__ == '__main__' :

    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    census_tract_shp = gpd.read_file(os.path.join(shp_path, 'tl_2019_17_tract', 'tl_2019_17_tract.shp'))

    df = pd.read_csv(os.path.join(pop_path, 'IL2018_Households'))

    pop_df = pd.DataFrame( { 'EMS' : ems_shp['REGION'],
                             'population' : [count_total_pop(df, x, census_tract_shp) for x in ems_shp['geometry']]})

    pop_df.to_csv(os.path.join(datapath, 'EMS Population', 'EMS_population_from_RTI.csv'), index=False)
    print(np.sum(pop_df['population']))

