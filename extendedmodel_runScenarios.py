import os
import subprocess
import pandas as pd
import itertools

## directories
user_path = os.path.expanduser('~')
exe_dir = os.path.join(user_path, 'Box/NU-malaria-team/projects/binaries/compartments/')

if "mrung" in user_path :
    git_dir = os.path.join(user_path, 'gitrepos/covid-chicago/')
    sim_output_path = os.path.join(user_path, 'Box/NU-malaria-team/projects/covid_chicago/cms_sim')

# Selected range values from SEIR Parameter Estimates.xlsx
initial_infect = [1,5,10]
Ki = [0.00000019,  0.0009, 0.05]
incubation_pd = [6.63, ]
recovery_rate = [6]

Testmode = False
if Testmode == True :
     initial_infect = [1,5]
     Ki = [0.0009]
     incubation_pd = [6.63]
     recovery_rate = [6]

def runExp_fullFactorial() :

    lst = []
    scen_num = 0

    # Requires exactly that order!
    for i in itertools.product(initial_infect, Ki, incubation_pd, recovery_rate) :
        scen_num += 1
       # print(i)

        lst.append([scen_num ,i, "initial_infect, Ki, incubation_pd, recovery_rate"])

        fin = open("extendedmodel_covid.emodl", "rt")
        data = fin.read()
        data = data.replace('(species I 10)', '(species I ' + str(i[0]) +')')
        data = data.replace('(param Ki 0.0005)', '(param Ki '  + str(i[1]) +')')
        data = data.replace('(param incubation_pd 6.63)', '(param incubation_pd ' + str(i[2]) +')')
        data = data.replace('(param recovery_rate 16)', '(param recovery_rate '  + str(i[3]) +')')
        fin.close()

        fin = open("extendedmodel_covid_i.emodl", "wt")
        fin.write(data)
        fin.close()

        # adjust simplemodel.cfg file as well
        fin = open("simplemodel.cfg", "rt")
        data_cfg = fin.read()
        data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num) )
        fin.close()
        fin = open("simplemodel_i.cfg", "wt")
        fin.write(data_cfg)
        fin.close()

        file = open('runModel_i.bat', 'w')
        file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(git_dir, "simplemodel_i.cfg") +
                   '"' + ' -m ' + '"' + os.path.join( git_dir, "extendedmodel_covid_i.emodl", ) + '"')
        file.close()

        subprocess.call([r'runModel_i.bat'])

    df = pd.DataFrame(lst, columns=['scen_num', 'params', 'order'])
    df.to_csv("scenarios.csv")
    return(scen_num)


def reprocess(input_fname='trajectories.csv', output_fname=None) :

    fname = os.path.join(git_dir, input_fname)
    row_df = pd.read_csv(fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    num_channels = len([x for x in df.columns.values if '{0}' in x])
    num_samples = int((len(row_df)-1)/num_channels)

    df = df.reset_index(drop=False)
    df = df.rename(columns={'index' : 'time'})
    df['time'] = df['time'].astype(float)

    adf = pd.DataFrame()
    for sample_num in range(num_samples) :
        channels = [x for x in df.columns.values if '{%d}' % sample_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x : x.split('{')[0] for x in channels
        })
        sdf['sample_num'] = sample_num
        adf = pd.concat([adf, sdf])

    adf = adf.reset_index()
    del adf['index']
    if output_fname :
        adf.to_csv(output_fname)
    return adf


def combineTrajectories(Nscenarios, deleteFiles=False) :

    scendf = pd.read_csv("scenarios.csv")
    #order = scendf[ 'order'][1]

    del scendf['order']
    del scendf['Unnamed: 0']

    scendf[['initial_infect', 'Ki', 'incubation_pd', 'recovery_rate']] = scendf.params.str.split(",", expand=True)
    scendf.recovery_rate = scendf.recovery_rate.str.extract('(\d+)')
    scendf.initial_infect = scendf.initial_infect.str.extract('(\d+)')

    df_list = []
    for scen_i in range(1,Nscenarios) :
        input_name = "trajectories_scen" + str(scen_i) + ".csv"
        df_i = reprocess(input_name )
        df_i['scen_num'] = scen_i

        df_i = df_i.merge(scendf, on ='scen_num')

        df_list.append(df_i)
        if deleteFiles ==True : os.remove( os.path.join(git_dir, input_name))

    dfc = pd.concat(df_list)
    dfc.to_csv("trajectoriesDat.csv")

    return dfc


def plot(adf, allchannels = master_channel_list) :

    fig = plt.figure(figsize=(8,6))
    palette = sns.color_palette('Set1', 10)

    axes = [fig.add_subplot(3,3,x+1) for x in range(len(allchannels))]
    fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
    for c, channel in enumerate(allchannels) :

        mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
        ax = axes[c]
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

    #plt.savefig(os.path.join(plot_path, 'sample_plot.png'))
    plt.show()


#if __name__ == '__main__' :

nscen = runExp_fullFactorial()
combineTrajectories(nscen)

df = pd.read_csv(os.path.join('trajectoriesDat.csv'))
df = df[df['Ki'] == 0.0009]
plot(df, allchannels=['susceptible', 'exposed', 'infectious', 'symptomatic', 'hospitalized', 'critical', 'deaths', 'recovered'])
