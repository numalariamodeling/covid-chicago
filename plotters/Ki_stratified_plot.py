import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
import seaborn as sns
from processing_helpers import *
from simulation_setup import *

## directories

master_channel_list = ['susceptible', 'exposed', 'infectious', 'symptomatic', 'detected',
                       'hospitalized', 'critical', 'death', 'recovered']
first_day = date(2020, 3, 1)

chicago_df= df= pd.read_csv(
        os.path.join(project_dir,'chicago/chicago_cases.csv'),
        index_col=0)
chicago_df= chicago_df.reset_index()#.head()
chicago_df['Date']=pd.to_datetime(chicago_df['Date'])

df2= pd.read_csv(
        os.path.join(project_dir,'fitting/trajectoriesDat.csv'),
        index_col=0)

###
adf= df2.copy()
allchannels= ['detected']

fig = plt.figure(figsize=(20,16))
palette = sns.color_palette('Set1', 10)

axes = [fig.add_subplot(3,3,x+1) for x in range(len(allchannels))]
fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)

mdf = adf.groupby(['time','Ki'])['detected'].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
mdf['dates']= pd.to_datetime([first_day + timedelta(days=int(x)) for x in mdf['time']])
#####

mdf=pd.merge(mdf,
             chicago_df[["Date",'confirmed_cases','cumulative_cases_calc']],
             left_on='dates',
             right_on='Date',how='left' )

for element in range(0, len(mdf['Ki'].unique())):
    plt.plot(mdf.loc[(mdf['Ki']==mdf['Ki'].unique()[element]),'dates'],
             mdf.loc[(mdf['Ki']==mdf['Ki'].unique()[element]),'mean'],
             label='detected_SEIR_Ki={}'.format(mdf['Ki'].unique()[element]),
             color=palette[element])



plt.plot(mdf['dates'], mdf['cumulative_cases_calc'], label='detected_reported', color=palette[element+1])

plt.title('confirmed_cases')#, y=0.8)
plt.legend()

ax = plt.gca()

formatter = mdates.DateFormatter("%m-%d")
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.set_xlim(first_day, )

#plt.set_title(channel, y=0.8)