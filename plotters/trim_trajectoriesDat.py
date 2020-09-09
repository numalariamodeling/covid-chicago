import os
import pandas as pd
import sys

sys.path.append('../')
from load_paths import load_box_paths
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
sim_output_path = os.path.join(wdir, "simulation_output")


def trim_trajectories_Dat(exp_dir, VarsToKeep, keepTimes='today',lagtime_days=15, grpnames=None, channels=None, grpspecific_params=None):
    """Generate a subset of the trajectoriesDat dataframe
    The new csv file is saved under trajectoriesDat_trim.csv, no dataframe is returned
    """

    if VarsToKeep == None :
        VarsToKeep = ['startdate', 'time', 'scen_num', 'sample_num', 'run_num']

    if grpnames == None:
        grpnames = ['All', 'EMS-1', 'EMS-2', 'EMS-3', 'EMS-4', 'EMS-5', 'EMS-6', 'EMS-7', 'EMS-8', 'EMS-9', 'EMS-10', 'EMS-11']
        grpnames_ki = ['EMS-1', 'EMS-2', 'EMS-3', 'EMS-4', 'EMS-5', 'EMS-6', 'EMS-7', 'EMS-8', 'EMS-9', 'EMS-10','EMS-11']

    if channels == None:
        channels = ['susceptible', 'infected', 'recovered', 'infected_cumul', 'detected_cumul',
                    'asymp_cumul', 'asymp_det_cumul',
                    'symp_mild_cumul', 'symptomatic_mild', 'symp_mild_det_cumul',
                    'symp_severe_cumul','symptomatic_severe', 'symp_severe_det_cumul',
                    'hosp_det_cumul', 'hosp_cumul', 'hospitalized_det', 'hospitalized',
                    'crit_cumul','crit_det_cumul', 'crit_det', 'critical_det', 'critical',
                    'death_det_cumul',  'deaths' ]

    if grpspecific_params == None:
        grpspecific_params = ['Ki_t']  # ['Ki_t', 'triggertime','reopening_multiplier_4']

    column_list = VarsToKeep
    for channel in channels:
        for grp in grpnames:
            column_list.append(channel + "_" + str(grp))

    for grpspecific_param in grpspecific_params:
        for grp in grpnames_ki:
            column_list.append(grpspecific_param + "_" + str(grp))

    df = pd.read_csv(os.path.join(exp_dir, 'trajectoriesDat.csv'), usecols=column_list)

    if keepTimes is not None:
        if keepTimes !='today':
            df = df[df['time'] >= int(keepTimes)]

        if keepTimes =='today':
            today = datetime.today()
            datetoday = date(today.year, today.month, today.day)
            datetoday = pd.to_datetime(datetoday)
            df['startdate'] = pd.to_datetime(df['startdate'])
            df['todayintime'] = datetoday - df['startdate']
            df['todayintime'] = pd.to_numeric(df['todayintime'].dt.days, downcast='integer')
            ## keep 15 days before today
            df = df[df['time'] >= df['todayintime'] - lagtime_days]

    df.to_csv(os.path.join(exp_dir, 'trajectoriesDat_trim.csv'), index=False)


if __name__ == '__main__':

    VarsToKeep = ['startdate', 'time', 'scen_num','sample_num', 'run_num']

   # moreVarsToKeep = ['capacity_multiplier', 'reopening_multiplier_4','reduced_inf_of_det_cases_ct1', 'change_testDelay_Sym_1', 'change_testDelay_As_1', 'd_Sym_ct1', 'd_AsP_ct1']
   # VarsToKeep = VarsToKeep + moreVarsToKeep

    #stem = sys.argv[1]
    stem ="20200907_IL_baseline_cfr_test"
    exp_names = [x for x in os.listdir(os.path.join(sim_output_path)) if stem in x]

    from datetime import date,  datetime

    for exp_name in exp_names:
        exp_dir = os.path.join(sim_output_path, exp_name)
        trim_trajectories_Dat(exp_dir=exp_dir, VarsToKeep=VarsToKeep, keepTimes='today', lagtime_days=15)
