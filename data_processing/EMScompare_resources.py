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
            df['moving_ave'] = df[name].rolling(window = 7, center=True).mean()
            ax.plot(df['date'],df['moving_ave'],label=name)
            ax.scatter(df['date'],df[name],s=10,alpha=0.5)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.legend()
        plt.legend(loc='upper left')
        plt.title('EMS'+str(region_num))
        plt.gcf().autofmt_xdate()
    plt.suptitle('North_Central',fontsize=20)
    fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_northcentral.pdf'), format='PDF')
    fig = plt.figure(figsize=(10,6))
    for b,region_num in enumerate([4,5]):
        ax = fig.add_subplot(1,2,b+1)
        plt.xlim([xmin,xmax])
    
        for (c,name) in enumerate(eachname):
            df=ref_df[ref_df['region']==region_num]
            df['moving_ave'] = df[name].rolling(window = 7, center=True).mean()
            ax.plot(df['date'],df['moving_ave'],label=name)
            ax.scatter(df['date'],df[name],s=10,alpha=0.5)
        plt.legend()
        plt.title('EMS'+str(region_num))
        plt.gcf().autofmt_xdate()
    
    plt.suptitle('Southern',fontsize=20)
    fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_southern.pdf'), format='PDF')

    fig = plt.figure(figsize=(10,6))
    for b,region_num in enumerate([3,6]):
        ax = fig.add_subplot(1,2,b+1)
        plt.xlim([xmin,xmax])
    
        for (c,name) in enumerate(eachname):
            df=ref_df[ref_df['region']==region_num]
            df['moving_ave'] = df[name].rolling(window = 7,center=True).mean()
            ax.plot(df['date'],df['moving_ave'],label=name)
            ax.scatter(df['date'],df[name],s=10,alpha=0.5)
        plt.legend()
        plt.title('EMS'+str(region_num))
        plt.gcf().autofmt_xdate()
    
    plt.suptitle('Central',fontsize=20)
    fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_central.pdf'), format='PDF')

    fig = plt.figure(figsize=(14,10))
    for b,region_num in enumerate([7,8,9,10,11]):
        ax = fig.add_subplot(2,3,b+1)
        plt.xlim([xmin,xmax])
        for (c,name) in enumerate(eachname):
            df=ref_df[ref_df['region']==region_num]
            df['moving_ave'] = df[name].rolling(window = 7,center=True).mean()
            ax.plot(df['date'],df['moving_ave'],label=name)
            ax.scatter(df['date'],df[name],s=10,alpha=0.5)
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))   
        plt.title('EMS'+str(region_num))
        plt.gcf().autofmt_xdate()
    plt.legend(loc='upper right')
    
    plt.suptitle('Northeast',fontsize=20)
    fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_northeast.pdf'), format='PDF')
    
    df=ref_df[ref_df['region']==1]
    dfall_1=pd.DataFrame()
    dfall=pd.DataFrame()
    dfall['date_of_extract']=df['date_of_extract']
    dfall_1['date_of_extract']=df['date_of_extract']

    
    for name in eachname:
        dfall['1']=df[name]
        for i in range(2,12):
            df=ref_df[ref_df['region']==i]
            df=df.reset_index()
            dfall['%s'%i]=df[name]
        dfall['all']=dfall.sum(axis=1)
        dfall_1[name]=dfall['all']

    fig = plt.figure(figsize=(6,4))
    ax = fig.add_subplot(1,1,1)
    plt.xlim([xmin,xmax])
    for (c,name) in enumerate(eachname):
        df=ref_df[ref_df['region']==region_num]
        df['moving_ave'] = df[name].rolling(window = 7,center=True).mean()
        ax.plot(df['date'],df['moving_ave'],label=name)
        ax.scatter(df['date'],df[name],s=10,alpha=0.5)
        plt.legend()
        plt.legend(loc='upper left')
        plt.title('All')
    #fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_all.pdf'), format='PDF')


    fig = plt.figure(figsize=(12,8))
    ax = fig.add_subplot(2,2,1)
    plt.xlim([xmin,xmax])
    for (c,name) in enumerate(eachname):
        df=ref_df[ref_df['region']==1]
        dfall_1=pd.DataFrame()
        dfall=pd.DataFrame()
        dfall['date']=df['date']
        dfall_1['date']=df['date']
        dfall['1']=df[name]
        for i in [2]:
            df=ref_df[ref_df['region']==i]
            df=df.reset_index()
            dfall['%s'%i]=df[name]
        dfall['all']=dfall.sum(axis=1)
        dfall_1[name]=dfall['all']
        dfall_1['moving_ave'] = dfall_1[name].rolling(window = 7,center=True).mean()
        ax.plot(dfall_1['date'],dfall_1['moving_ave'],label=name)
        ax.scatter(dfall_1['date'],dfall_1[name],s=10,alpha=0.5)
    plt.legend(loc='upper left')
    plt.title('North Central')
    plt.gcf().autofmt_xdate()


    ax = fig.add_subplot(2,2,2)

    plt.xlim([xmin,xmax])
    for (c,name) in enumerate(eachname):
        df=ref_df[ref_df['region']==4]
        df=df.reset_index()
        dfall_1=pd.DataFrame()
        dfall=pd.DataFrame()
        dfall['date']=df['date']
        dfall_1['date']=df['date']
        dfall['4']=df[name]
        for i in [5]:
            df=ref_df[ref_df['region']==i]
            df=df.reset_index()
            dfall['%s'%i]=df[name]
        dfall['all']=dfall.sum(axis=1)
        dfall_1[name]=dfall['all']
        dfall_1['moving_ave'] = dfall_1[name].rolling(window = 7,center=True).mean()
        ax.plot(dfall_1['date'],dfall_1['moving_ave'],label=name)
        ax.scatter(dfall_1['date'],dfall_1[name],s=10,alpha=0.5)
    plt.legend(loc='upper left')
    plt.title('Southern')
    plt.gcf().autofmt_xdate()

    ax = fig.add_subplot(2,2,3)

    for (c,name) in enumerate(eachname):
        df=ref_df[ref_df['region']==3]
        df=df.reset_index()
        dfall_1=pd.DataFrame()
        dfall=pd.DataFrame()
        dfall['date']=df['date']
        dfall_1['date']=df['date']
        plt.xlim([xmin,xmax])
        dfall['4']=df[name]
        for i in [6]:
            df=ref_df[ref_df['region']==i]
            df=df.reset_index()
            dfall['%s'%i]=df[name]
        dfall['all']=dfall.sum(axis=1)
        dfall_1[name]=dfall['all']
        dfall_1['moving_ave'] = dfall_1[name].rolling(window = 7,center=True).mean()
        ax.plot(dfall_1['date'],dfall_1['moving_ave'],label=name)
        ax.scatter(dfall_1['date'],dfall_1[name],s=10,alpha=0.5)
    plt.legend(loc='upper left')
    plt.title('Central')
    plt.gcf().autofmt_xdate()

    ax = fig.add_subplot(2,2,4)

    for (c,name) in enumerate(eachname):
        df=ref_df[ref_df['region']==7]
        df=df.reset_index()
        dfall_1=pd.DataFrame()
        dfall=pd.DataFrame()
        dfall['date']=df['date']
        dfall_1['date']=df['date']
        plt.xlim([xmin,xmax]) 
        dfall['1']=df[name]
        for i in [8,9,10,11]:
            df=ref_df[ref_df['region']==i]
            df=df.reset_index()
            dfall['%s'%i]=df[name]
        dfall['all']=dfall.sum(axis=1)
        dfall_1[name]=dfall['all']
        dfall_1['moving_ave'] = dfall_1[name].rolling(window = 7,center=True).mean()
        ax.plot(dfall_1['date'],dfall_1['moving_ave'],label=name)
        ax.scatter(dfall_1['date'],dfall_1[name],s=10,alpha=0.5)
    plt.legend(loc='upper left')
    plt.title('North East')
    plt.gcf().autofmt_xdate()
    fig.savefig(os.path.join(datapath, 'covid_chicago','Plots + Graphs', 'Emresource Plots','EMSresources_region.pdf'), format='PDF')