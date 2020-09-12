import os
import sys
sys.path.append('../')
from load_paths import load_box_paths
import shutil

def createFolder() :

    if not os.path.exists(NUcivis_dir):
        os.makedirs(NUcivis_dir)
        os.makedirs(os.path.join(NUcivis_dir, "plots"))
        os.makedirs(os.path.join(NUcivis_dir, "csv"))
        os.makedirs(os.path.join(NUcivis_dir, "trajectories"))

def copyFiles():
    fname1 = f'nu_{simdate}.csv'
    fname2 = f'nu_hospitaloverflow_{simdate}.csv'
    fname3 = f'trajectoriesDat_{exp_scenario}.csv'
    shutil.copyfile(os.path.join(exp_dir, fname1), os.path.join(NUcivis_dir,'csv', fname1))
    shutil.copyfile(os.path.join(exp_dir, fname2), os.path.join(NUcivis_dir,'csv', fname2))
    shutil.copyfile(os.path.join(exp_dir, 'trajectoriesDat.csv'), os.path.join(NUcivis_dir,'trajectories', fname3))

    filelist= [file for file in os.listdir(exp_dir) if file.endswith('.png')]
    for file in filelist :
        shutil.copyfile(os.path.join(exp_dir, file), os.path.join(NUcivis_dir,'plots', file))
    del filelist

    filelist= [file for file in os.listdir(os.path.join(exp_dir, '_plots')) if file.endswith('.png')]
    for file in filelist :
        shutil.copyfile(os.path.join(os.path.join(exp_dir, '_plots'), file), os.path.join(NUcivis_dir,'plots', file))

def writeChangelog(A1=None,A2=None, A3=None, A4=None, A5=None, A6=None):
    Q1 = "1) How has the date range of data used changed since your last update?"
    Q2 = "2) How have data sources changed since your last update?"
    Q3 = "3) What important changes have you made in your methodology since the last update?"
    Q4 = "4) Which of these changes do you think are most important in driving differences between previous forecasts and current forecasts?"
    Q5 = "5) Relevant time events in the simulations"
    Q6 = "Scenarios"

    if A1 == None :A1 = "- another week of EMresource and LL data"
    if A2 == None :A2 = "- same as last week"
    if A3 == None :A3 = "- updated fitting "
    if A4 == None :A4 = "..."
    if A5 == None :  A5 = "- Reduction in transmission rate due to 'shelter in place policies': 2020-03-12, 2020-03-17, 2020-03-21, 2020-04-21 " \
         "\n- Increase in transmission rate due to relaxation of 'shelter in place policies' : 2020-06-21 ,2020-07-25 " \
         "\n- Decrease in cfr : 2020-06-01 , 2020-07-01"
    if A6 == None : A6 = "- No additional scenarios "


    file = open(os.path.join(NUcivis_dir, 'changelog.txt'), 'w')
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

    createFolder()
    copyFiles()
    writeChangelog()