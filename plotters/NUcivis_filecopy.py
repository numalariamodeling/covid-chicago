import os
import sys
sys.path.append('../')
from load_paths import load_box_paths
import shutil
import pandas as pd

def createFolder(output_dir) :

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(os.path.join(output_dir, "plots")):
        os.makedirs(os.path.join(output_dir, "plots"))
    if not os.path.exists(os.path.join(output_dir, "csv")):
        os.makedirs(os.path.join(output_dir, "csv"))
    if not os.path.exists(os.path.join(output_dir, "trajectories")):
        os.makedirs(os.path.join(output_dir, "trajectories"))

def copyFiles(output_dir):
    fname1 = f'nu_{simdate}.csv'
    fname2 = f'nu_hospitaloverflow_{simdate}.csv'
    fname3 = f'trajectoriesDat_{exp_scenario}.csv'
    shutil.copyfile(os.path.join(exp_dir, fname1), os.path.join(output_dir,'csv', fname1))
    shutil.copyfile(os.path.join(exp_dir, fname2), os.path.join(output_dir,'csv', fname2))
    shutil.copyfile(os.path.join(exp_dir, 'trajectoriesDat.csv'), os.path.join(output_dir,'trajectories', fname3))

    filelist= [file for file in os.listdir(os.path.join(exp_dir, '_plots')) if file.endswith('.png')]
    for file in filelist :
        shutil.copyfile(os.path.join(os.path.join(exp_dir, '_plots'), file), os.path.join(output_dir,'plots', file))

def subset_df(fname, regions_to_keep, output_dir,save_dir=None):
    df = pd.read_csv(os.path.join(exp_dir, fname))
    df = df[df.geography_modeled.isin(regions_to_keep)]
    if save_dir==None :
        save_dir = os.path.join(output_dir,'csv')
    df.to_csv(os.path.join(save_dir, fname))


def writeChangelog(output_dir,A1=None,A2=None, A3=None, A4=None, A5=None, A6=None):
    Q1 = "1) How has the date range of data used changed since your last update?"
    Q2 = "2) How have data sources changed since your last update?"
    Q3 = "3) What important changes have you made in your methodology since the last update?"
    Q4 = "4) Which of these changes do you think are most important in driving differences between previous " \
         "forecasts and current forecasts?"
    Q5 = "5) Relevant time events in the simulations"
    Q6 = "Scenarios"

    if A1 == None :A1 = "- another week of EMResource and LL data"
    if A2 == None :A2 = "- same as last week, also using CLI admissions for validation"
    if A3 == None :A3 = "- updated fitting "
    if A4 == None :A4 = "..."
    if os.path.exists(os.path.join(exp_dir, f'traces_ranked_region_11.csv')):
        A4 = A4 + "\n Note: using the 50% if the simulation trajectories that best fit the data"
    if A5 == None :  A5 = "- Reduction in transmission rate due to 'shelter in place policies': " \
                          "2020-03-12, 2020-03-17, 2020-03-21, 2020-04-21" \
                          "\n- Change in transmission rate during reopening period : " \
                          "2020-06-21 ,2020-07-25, 2020-08-25 , 2020-09-17, 2020-10-10, 2020-11-07, 2020-12-20, 2021-01-19 "\
                          "\n- Decrease in cfr : 2020-06-01 , 2020-07-01"
    if A6 == None : A6 = "- No additional scenarios"

    file = open(os.path.join(output_dir, 'changelog.txt'), 'w')
    file.write(f'Northwestern University COVID-19 Modelling Team \n\n Date: {simdate} \n\n '
               f'{Q1} \n {A1} \n \n {Q2} \n {A2} \n \n {Q3} \n {A3} \n \n {Q4} \n {A4} \n \n {Q5} \n {A5}  \n \n {Q6} \n {A6}')
    file.close()

if __name__ == '__main__' :

    exp_name = sys.argv[1]
    datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
    expsplit = exp_name.split('_')
    simdate = expsplit[0]
    exp_scenario = expsplit[len(expsplit)-1]

    fname = f"nu_{simdate}.csv"
    exp_dir = os.path.join(wdir,"simulation_output", exp_name)
    NUcivis_dir = os.path.join(projectpath, 'NU_civis_outputs', simdate)

    """ Deliverables for CIVIS"""
    createFolder(output_dir=NUcivis_dir)
    copyFiles(output_dir=NUcivis_dir)
    writeChangelog(output_dir=NUcivis_dir)