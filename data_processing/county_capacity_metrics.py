import os
#import geopandas as gpd
import pandas as pd
import datetime as dt
import numpy as np
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date, timedelta
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

plot_dir = os.path.join(projectpath, 'Plots + Graphs', '_trend_tracking')
datapath = os.path.join(datapath, 'covid_IDPH')
shp_path = os.path.join(datapath, 'shapefiles')

#set last date to consider when calculating average occupancy (inclusive).
since_date = pd.to_datetime('2020-11-18')
today = dt.datetime.today()

def load_ref_df():
    ref_df = pd.read_csv(os.path.join(datapath, 'Corona virus reports', 'emresource_by_hospital.csv'), low_memory=False)
    return ref_df

def load_zip_to_county_dict():
    zip_county_df = pd.read_csv(os.path.join(datapath, 'Corona virus reports', 'zip_to_county_to_covid_region_map_not_complete.csv'), low_memory=False)
    zip_to_county = zip_county_df.set_index('zip').to_dict().get('county')
    return zip_to_county, zip_county_df

def get_capacity():
    emr = load_ref_df()
    zip_to_county, zip_county_df = load_zip_to_county_dict()
    #print(emr)
    emr['date_of_extract'] = pd.to_datetime(emr['date_of_extract'])
    emr['county'] = emr['zip'].apply(lambda x: zip_to_county.get(x))

    county_sum = emr[emr['date_of_extract'] >= since_date].groupby(['hospital', 'county'], axis=0).mean().groupby('county', axis=0).sum()
    county_list = np.unique(zip_county_df['county'].values)
    county_sum['icu_frac_covid_occupied'] = county_sum['confirmed_covid_icu']/county_sum['capacity_adult_icu']
    county_sum['med_surg_frac_covid_occupied'] = county_sum['covid_non_icu']/county_sum['capacity_med_surg']
    county_df = pd.merge(pd.DataFrame({'county':county_list}), county_sum, how='left', left_on='county', right_on='county')
    county_df = county_df[['county', 'covid_non_icu', 'confirmed_covid_icu', 'capacity_med_surg', 'capacity_adult_icu', 'icu_frac_covid_occupied', 'med_surg_frac_covid_occupied']]
    county_df['sum_metric'] = county_df['icu_frac_covid_occupied'] + county_df['med_surg_frac_covid_occupied']
    county_df = county_df.replace([np.inf, -np.inf], np.nan)
    county_df.to_csv(os.path.join(datapath, 'Corona virus reports', 'county_covid_capacity_metrics_'+ today.strftime("%y%m%d") + '.csv'), index=False)

if __name__ == '__main__' :
    get_capacity()