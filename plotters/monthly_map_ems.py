import os
import geopandas as gpd
import pandas as pd
import numpy as np
import sys
sys.path.append('../')
from load_paths import load_box_paths
from datetime import date
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
import seaborn as sns
import matplotlib.colors as colors

mpl.rcParams['pdf.fonttype'] = 42


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

scen_dir = os.path.join(projectpath, 'NU_civis_outputs', '20200429')
csv_dir = os.path.join(scen_dir, 'csv')
plot_dir = os.path.join(scen_dir, 'plots')
datapath = os.path.join(datapath, 'covid_IDPH')
shp_path = os.path.join(datapath, 'shapefiles')


if __name__ == '__main__' :

    channel = 'Number of Covid-19 infections'
    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    ems_pop = pd.read_csv(os.path.join(datapath, 'EMS Population', 'EMS_population_from_RTI.csv'))

    ems_shp['REGION'] = ems_shp['REGION'].astype(int)

    dates = [date(2020,m,1) for m in range(4, 10)]

    ems_fnames = [x for x in os.listdir(csv_dir) if 'ems' in x]
    for fname in ems_fnames :
        il_fname = fname.replace('ems', 'illinois')
        adf = pd.read_csv(os.path.join(csv_dir, fname))
        adf['Date'] = pd.to_datetime(adf['Date'])
        adf = adf[adf['Date'].isin(dates)]

        adf = pd.merge(left=adf, right=ems_pop, left_on='ems', right_on='EMS', how='left')
        adf['prevalence'] = adf['Number of Covid-19 infections']/adf['population']

        fig = plt.figure(figsize=(10,12))
        fig.subplots_adjust(top=0.95)

        vmin, vmax = 0, np.max(adf['prevalence'])
        norm = colors.Normalize(vmin=vmin,
                                vmax=vmax)

        for di, (d, ddf) in enumerate(adf.groupby('Date')) :
            ax = fig.add_subplot(3,2,di+1)

            ds_shp = pd.merge(left=ems_shp, right=ddf, left_on='REGION', right_on='ems')
            ds_shp.plot(column='prevalence', ax=ax, legend=False, cmap='Reds', norm=norm, edgecolor='0.8',
                        linewidth=0.8)

            sm = plt.cm.ScalarMappable(cmap='Reds', norm=plt.Normalize(vmin=vmin,
                                                                           vmax=vmax))
            sm._A = []
            cbar = fig.colorbar(sm, ax=ax)

            ax.set_title('{:%b %d %Y}'.format(d))
            ax.set_xticks([])
            ax.set_yticks([])
            ax.axis('off')

        plt.savefig(os.path.join(plot_dir, 'prevalence_map_%s' % il_fname.replace('csv', 'pdf')), format='PDF')
        plt.close(fig)

