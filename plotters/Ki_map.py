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
import codecs

mpl.rcParams['pdf.fonttype'] = 42

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

#plot_dir = os.path.join(scen_dir, 'plots')
datapath_1 = os.path.join(datapath, 'covid_chicago')
shp_path = os.path.join(datapath, 'covid_IDPH','shapefiles')

if __name__ == '__main__' :

    #channel=
    ems_shp = gpd.read_file(os.path.join(shp_path, 'EMS_Regions', 'EMS_Regions.shp'))
    ems_shp['REGION'] = ems_shp['REGION'].astype(int)
    with codecs.open(r'C:\Users\bluen\Box\covid_chicago\project_notes\EMS_parameters_050520.csv', "r", "Shift-JIS", "ignore") as file:
        df = pd.read_table(file, delimiter=",")

    fig = plt.figure(figsize=(10, 12))
    vmin, vmax = 0, np.max(df['Ki'])
    norm = colors.Normalize(vmin=vmin,
                            vmax=vmax)
    ax = fig.add_subplot(1,1,1)
    df_shp = pd.merge(left=ems_shp, right=df, left_on='REGION', right_on='EMS')
    df_shp.plot(column='Ki', ax=ax, legend=False, cmap='Blues', norm=norm, edgecolor='0.8',
                linewidth=0.8)

    sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin,
                                                               vmax=vmax))
    sm._A = []
    cbar = fig.colorbar(sm, ax=ax)

    ax.set_title('Ki', fontsize=20)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')

    plt.savefig(os.path.join(r'C:\Users\bluen\Desktop\figures', 'Ki_map.pdf'), format='PDF')
    plt.close(fig)