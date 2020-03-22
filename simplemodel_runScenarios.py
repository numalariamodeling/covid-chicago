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
    #sim_output_path = git_dir  # for testing

# Selected range values from SEIR Parameter Estimates.xlsx
# Need to update to run for sample distributions, rather than discrete values
# Generate csv file with scenarios
# Load scenarios.csv

# print dataframe.
initial_infect = [1,5,10]
Ki = [0.05, 0.19, 0.312]
incubation_pd = [6.63, 4.2, 12.4]
recovery_rate = [6,13, 16 ]

def runExp_fullFactorial() :

    lst = []
    scen_num = 0

    # Requires exactly that order!
    for i in itertools.product(initial_infect, Ki, incubation_pd, recovery_rate) :
        scen_num += 1
        #print(scen_num)

        lst.append([scen_num ,i, "initial_infect, Ki, incubation_pd, recovery_rate"])

        fin = open("simplemodel_covid.emodl", "rt")
        data = fin.read()
        data = data.replace('(species I 10)', '(species I ' + str(i[0]) +')')
        data = data.replace('(param Ki 0.319)', '(param Ki '  + str(i[1]) +')')
        data = data.replace('(param incubation_pd 6.63)', '(param incubation_pd ' + str(i[2]) +')')
        data = data.replace('(param recovery_rate 16)', '(param recovery_rate '  + str(i[3]) +')')
        fin.close()

        fin = open("simplemodel_covid_i.emodl", "wt")
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
                   '"' + ' -m ' + '"' + os.path.join( git_dir, "simplemodel_covid_i.emodl", ) + '"')
        file.close()

        subprocess.call([r'runModel_i.bat'])

        df = pd.DataFrame(lst, columns=['scen_num', 'params', 'order'])
        df.to_csv("scenarios.csv")

def reprocess(input_fname, output_fname=None) :

    #input_fname ="trajectories_scen1.csv"
    fname = os.path.join(git_dir, input_fname)
    df = pd.read_csv(fname, skiprows=1)
    df = df.set_index('sampletimes').transpose()
    df = df.reset_index(drop=False)
    df = df.rename(columns={'index' : 'time'})
    df['time'] = df['time'].astype(float)

    channels = [x for x in df.columns.values if '{' in x]
    df = df.rename(columns={
        x : x.split('{')[0] for x in channels
    })

    if output_fname :
        df.to_csv(output_fname)
    return df

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

#if __name__ == '__main__' :

runExp_fullFactorial()
combineTrajectories(81)

