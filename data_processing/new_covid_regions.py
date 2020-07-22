import geopandas as gpd
import pandas as pd
import numpy as np
import os
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns
from plotting.colors import load_color_palette

mpl.rcParams['pdf.fonttype'] = 42


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

plot_dir = os.path.join(projectpath, 'Plots + Graphs', '_trend_tracking')
datapath = os.path.join(datapath, 'covid_IDPH')
shp_path = os.path.join(datapath, 'shapefiles')


if __name__ == '__main__' :

    county_shp = gpd.read_file(os.path.join(shp_path, 'IL_BNDY_County', 'IL_BNDY_County_Py.shp'))
    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    ems_shp['REGION'] = ems_shp['REGION'].astype(int)
    ems_shp = ems_shp.set_index('REGION')
    chicago_poly = ems_shp.at[11, 'geometry']
    ems_shp = ems_shp.reset_index()
    ems_shp = ems_shp[ems_shp['REGION'] == 11]
    ems_shp = ems_shp.rename(columns={'REGION' : 'COUNTY_NAM',
                                      'OBJECTID' : 'CO_FIPS'})
    ems_shp['COUNTY_NAM'] = 'CHICAGO'

    for county, poly in zip(county_shp['COUNTY_NAM'], county_shp['geometry']) :
        if county == 'COOK' :
            intersection = poly.intersection(chicago_poly)
            suburb_cook_poly = poly.difference(intersection)
        if county == 'DUPAGE' :
            intersection = poly.intersection(chicago_poly)
            dupage_poly = poly.difference(intersection)

    county_shp = county_shp.set_index('COUNTY_NAM')
    county_shp.at['COOK', 'geometry'] = suburb_cook_poly
    county_shp.at['DUPAGE', 'geometry'] = dupage_poly
    county_shp = county_shp.reset_index()
    county_shp.loc[county_shp['COUNTY_NAM'] == 'DEWITT', 'COUNTY_NAM'] = 'DE WITT'
    county_shp = pd.concat([county_shp, ems_shp], sort=True)

    ref_df = pd.read_csv(os.path.join(datapath, 'Corona virus reports', 'county_restore_region_map.csv'))
    county_shp = pd.merge(left=county_shp, right=ref_df, left_on='COUNTY_NAM', right_on='county', how='left')
    county_shp['new_restore_region'] = county_shp['new_restore_region'].astype(int)

    county_shp.to_file(os.path.join(shp_path, 'covid_regions', 'counties.shp'))

    ems_shp = county_shp.dissolve(by='new_restore_region').reset_index()
    for col in ['county', 'COUNTY_NAM', 'CO_FIPS'] :
        del ems_shp[col]
    ems_shp = ems_shp.rename(columns={
        'new_restor' : 'covid_region',
        'restore_re' : 'restore_region'
    })
    ems_shp.to_file(os.path.join(shp_path, 'covid_regions', 'covid_regions.shp'))
