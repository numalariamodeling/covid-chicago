import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
from processing_helpers import *


mpl.rcParams['pdf.fonttype'] = 42
today = datetime.today()

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()


ref_df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'emresource_by_region.csv'))

sxmin='2020-03-24'
xmin = datetime.strptime(sxmin, '%Y-%m-%d')
xmax = datetime.today()
datetoday=xmax.strftime('%y%m%d')

ref_df['suspected_and_confirmed_covid_icu'] = ref_df['suspected_covid_icu'] + ref_df['confirmed_covid_icu']
ref_df['date'] = pd.to_datetime(ref_df['date_of_extract'])
first_day=datetime.strptime('2020-03-24','%Y-%m-%d')

eachname=['confirmed_covid_deaths_prev_24h','confirmed_covid_icu','confirmed_covid_on_vents','suspected_and_confirmed_covid_icu']

if __name__ == '__main__' :
    fig = plt.figure(figsize=(10,6))
    for b,region_num in enumerate([1,2]):
        ax = fig.add_subplot(1,2,b+1)
        plt.xlim([xmin,xmax])
    
        for (c,name) in enumerate(eachname):
            df=ref_df[ref_df['region']==region_num]
            ax.plot(df['date'],df[name],label=name)
        plt.legend()
        plt.legend(loc='upper left')
        plt.title('EMS'+str(region_num))
        plt.gcf().autofmt_xdate()
    plt.suptitle('Northwest',fontsize=20)
    #plt.show()
    fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_northwest_'+datetoday+'.pdf'), format='PDF')

    fig = plt.figure(figsize=(10,6))
    for b,region_num in enumerate([4,5]):
        ax = fig.add_subplot(1,2,b+1)
        plt.xlim([xmin,xmax])
    
        for (c,name) in enumerate(eachname):
            df=ref_df[ref_df['region']==region_num]
            ax.plot(df['date'],df[name],label=name)
        plt.legend()
        plt.title('EMS'+str(region_num))
        plt.gcf().autofmt_xdate()
    
    plt.suptitle('Southern',fontsize=20)
    fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_southern_'+datetoday+'.pdf'), format='PDF')

    fig = plt.figure(figsize=(10,6))
    for b,region_num in enumerate([3,6]):
        ax = fig.add_subplot(1,2,b+1)
        plt.xlim([xmin,xmax])
    
        for (c,name) in enumerate(eachname):
            df=ref_df[ref_df['region']==region_num]
            ax.plot(df['date'],df[name],label=name)
        plt.legend()
        plt.title('EMS'+str(region_num))
        plt.gcf().autofmt_xdate()
    
    plt.suptitle('Central',fontsize=20)
    fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_central_'+datetoday+'.pdf'), format='PDF')

    fig = plt.figure(figsize=(14,6))
    for b,region_num in enumerate([7,8,9,10,11]):
        ax = fig.add_subplot(1,5,b+1)
        for (c,name) in enumerate(eachname):
            df=ref_df[ref_df['region']==region_num]
            ax.plot(df['date'],df[name],label=name)
    
        plt.title('EMS'+str(region_num))
        plt.xlim([xmin,xmax])
        plt.gcf().autofmt_xdate()
    plt.legend(loc='lower right')
    
    plt.suptitle('Northeast',fontsize=20)
    fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_northeast_'+datetoday+'.pdf'), format='PDF')
