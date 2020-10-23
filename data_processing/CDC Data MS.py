import os
import pandas as pd
import numpy as np
import sys
import seaborn as sns
import matplotlib.pyplot as plt
sys.path.append('../')
from load_paths import load_box_paths
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
from processing_helpers import *

""" 
df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'il_cdc_thru_0811.csv'),low_memory=False)
print(df)
"""
"""Read in only relevant columns """
column_list =['icu_length',	'hosp_length', 'age_group','res_county','res_state','hosp_yn', 'icu_yn', 'death_yn']
df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'il_cdc_thru_0811.csv'), usecols=column_list)
print(df)

"""Remove Missings and Unknowns """
df = df.dropna(subset=["hosp_length"])
df = df.dropna(subset=["age_group"])
df = df.dropna(subset=["death_yn"])
df = df[df['age_group'] != 'Unknown' ]
df = df[df['icu_yn'] != 'Unknown' ]
df = df[df['icu_yn'] != 'Missing' ]
print(df)
pd.crosstab(index=df['age_group'], columns='count')

### Look at median per age group
df = df[df['hosp_length'] !=0 ]
df_median = df.groupby(['age_group', 'death_yn'])['hosp_length'].agg([np.median]).reset_index()
print(df_median)
### Look at mean per age group
df = df[df['hosp_length'] !=0 ]
df_summary = df.groupby(['age_group', 'icu_yn'])['hosp_length'].agg([np.mean, CI_2pt5, CI_25, CI_50, CI_75, CI_97pt5]).reset_index()
df_summary = df_summary.sort_values(by=['icu_yn','age_group'])
print(df_summary)

"""Remove Missings and Unknowns """
df = df.dropna(subset=["hosp_length"])
df = df.dropna(subset=["age_group"])
df = df.dropna(subset=["death_yn"])
df = df[df['age_group'] != 'Unknown' ]
df = df[df['death_yn'] != 'Unknown' ]
df = df[df['death_yn'] != 'Missing' ]
print(df)
### Look at median per age group
df = df[df['hosp_length'] !=0 ]
df_median = df.groupby(['age_group', 'death_yn'])['hosp_length'].agg([np.median]).reset_index()
print(df_median)
### Look at mean per age group
df = df[df['hosp_length'] !=0 ]
df_summary = df.groupby(['age_group', 'death_yn'])['hosp_length'].agg([np.mean, CI_2pt5, CI_25, CI_50, CI_75, CI_97pt5]).reset_index()
df_summary = df_summary.sort_values(by=['death_yn','age_group'])
print(df_summary)


### Simple histogram, not age structured
plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':100})
x = df['hosp_length']
plt.hist(x, bins=50)
plt.gca().set(title='hosp_length', ylabel='Frequency');
plt.show()
### Function for age structured plot
def plot_hist() :
    ## Get age groups
    agegroups = list(df['age_group'].unique())
    fig = plt.figure(figsize=(10, 6))
    palette = sns.color_palette('husl', 8)
    k = 0
    for c, age in enumerate(agegroups):
        ax = fig.add_subplot(3, 3, c + 1)
        mdf = df[df['age_group'] == age]
        ax.hist(mdf['hosp_length'], bins=50)
        ax.set_title(agegroups[c], y=0.8, fontsize=12)
        #ax.set(xlabel='hosp_length', ylabel='Frequency')
    return plt
## Generate plot and save
age_plot = plot_hist()
age_plot.savefig(os.path.join(git_dir,   'hosp_length_age_hist.png'))

agegroups = list(df['age_group'].unique())
fig = plt.figure(figsize=(10, 6))
for c, age in enumerate(agegroups):
    ax = fig.add_subplot(3, 3, c + 1)
    mdf = df[df['age_group'] == age]
    ax.hist(mdf['hosp_length'], bins=50)
    ax.set_title(agegroups[c], y=0.8, fontsize=12)
    #ax.set(xlabel='hosp_length', ylabel='Frequency')


import os
import pandas as pd
import numpy as np
import sys
import seaborn as sns
import matplotlib.pyplot as plt
sys.path.append('../')
from load_paths import load_box_paths
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

column_list =['icu_length',    'hosp_length', 'age_group','res_county','res_state','hosp_yn', 'icu_yn']
df = pd.read_csv(os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'il_cdc_thru_0811.csv'), usecols=column_list)

def plot_hist() :
    ## Get age groups
    agegroups = list(df['age_group'].unique())
    fig = plt.figure(figsize=(10, 6))
    palette = sns.color_palette('husl', 8)
    k = 0
    for c, age in enumerate(agegroups):
        ax = fig.add_subplot(3, 3, c + 1)
        mdf = df[df['age_group'] == age]
        ax.hist(mdf['hosp_length'], bins=50)
        ax.set_title(agegroups[c], y=0.8, fontsize=12)
        #ax.set(xlabel='hosp_length', ylabel='Frequency')
    return plt

df = df.dropna(subset=["hosp_length"])
df = df.dropna(subset=["age_group"])
df = df[df['age_group'] != 'Unknown' ]

age_plot = plot_hist()





