import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
from scipy.interpolate import interp1d

## directories
user_path = os.path.expanduser('~')

if "mrung" in user_path :
    project_dir= os.path.join(user_path,'Box/NU-malaria-team/projects/covid_chicago/cms_sim/')
    exe_dir = os.path.join(user_path, 'Box/NU-malaria-team/projects/binaries/compartments/')
    git_dir = os.path.join(user_path, 'gitrepos/covid-chicago/')
elif 'geickelb1' in user_path:
    project_dir= os.path.join(user_path,'Box/covid_chicago/cms_sim/')
    exe_dir = os.path.join(user_path,'Desktop/compartments/')
    git_dir = os.path.join(user_path, 'Documents/Github/covid-chicago/')

master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'detected', 'hospitalized', 'critical', 'death', 'recovered']

def CI_5(x) :

    return np.percentile(x, 5)


def CI_95(x) :

    return np.percentile(x, 95)


def CI_25(x) :

    return np.percentile(x, 25)


def CI_75(x) :

    return np.percentile(x, 75)


chicago_df= df= pd.read_csv(
        os.path.join(project_dir,'chicago/chicago_cases.csv'),
        index_col=0)
chicago_df= chicago_df.reset_index()#.head()
chicago_df['Date']=pd.to_datetime(chicago_df['Date'])

df2= pd.read_csv(
        os.path.join('trajectoriesDat_locale.csv'),
        index_col=0)

###
adf= df.copy()
allchannels= ['detected']

fig = plt.figure()
palette = sns.color_palette('Set1', 10)

axes = fig.gca() #[fig.add_subplot(3,3,x+1) for x in range(len(allchannels))]
#fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)

first_day = date(2020, 2, 21)

mdf = adf.groupby(['time','Ki'])['detected'].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
mdf['dates']= pd.to_datetime([first_day + timedelta(days=int(x)) for x in mdf['time']])
#####

mdf=pd.merge(mdf,
             chicago_df[["Date",'confirmed_cases','cumulative_cases_calc']],
             left_on='dates',
             right_on='Date',how='left' )

#mdf= mdf[mdf['Ki'] == mdf.Ki.unique()[2]]

def plot():
    fig = plt.figure()
    palette = sns.color_palette('Set1', 10)

    ax = plt.gca()
    mdf = adf.groupby('time')['Ki'].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
    dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
    ax.plot(dates, mdf['mean'], label=channel, color=palette[c])
    ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                     color=palette[c], linewidth=0, alpha=0.2)
    ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                        color=palette[c], linewidth=0, alpha=0.4)

    ax.set_title(channel, y=0.8)
    formatter = mdates.DateFormatter("%m-%d")
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.set_xlim(first_day, )

    # plt.savefig(os.path.join(plot_path, 'sample_plot.png'))
    plt.show()


for element in range(0, len(mdf['Ki'].unique())):
    plt.plot(mdf.loc[(mdf['Ki']==mdf['Ki'].unique()[element]),'dates'],
             mdf.loc[(mdf['Ki']==mdf['Ki'].unique()[element]),'mean'],
             label='detected_SEIR_Ki={}'.format(mdf['Ki'].unique()[element]),
             color=palette[element])

plt.plot(mdf['dates'], mdf['cumulative_cases_calc'], label='detected_reported')

plt.title('confirmed_cases')#, y=0.8)
plt.legend()

ax = plt.gca()
formatter = mdates.DateFormatter("%m-%d")
ax.xaxis.set_major_formatter(formatter)
#ax.xaxis.set_major_locator(mdates.WeekLocator())
ax.set_xlim(first_day, )

#plt.set_title(channel, y=0.8)


adf= df.copy()

fig = plt.figure(figsize=(8,6))
palette = sns.color_palette('Set1', 10)

axes = [fig.add_subplot(3,3,x+1) for x in range(len(allchannels))]
fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)

mdf = adf.groupby('time')['detected'].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()

##########

mdf['dates']= pd.to_datetime([first_day + timedelta(days=int(x)) for x in mdf['time']])
mdf=pd.merge(mdf,chicago_df[["Date",'confirmed_cases','cumulative_cases_calc']], left_on='dates', right_on='Date',how='left'  )

plt.plot(mdf['dates'], mdf['mean'], label='detected_SEIR', color=palette[0])
plt.fill_between(mdf['dates'], mdf['CI_5'], mdf['CI_95'],
                color=palette[0], linewidth=0, alpha=0.2)
plt.fill_between(mdf['dates'], mdf['CI_25'], mdf['CI_75'],
                color=palette[0], linewidth=0, alpha=0.4)
plt.plot(mdf['dates'], mdf['cumulative_cases_calc'], label='detected_reported', color=palette[1])

plt.title('confirmed_cases')#, y=0.8)
plt.legend()

ax = plt.gca()

formatter = mdates.DateFormatter("%m-%d")
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.set_xlim(first_day, )
