import os
import pandas as pd
import sys

sys.path.append('../')
from load_paths import load_box_paths
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
sim_output_path = os.path.join(wdir, "simulation_output")


def trim_trajectories_Dat(exp_dir, VarsToKeep, keepTimes=None):
    """Generate a subset of the trajectoriesDat dataframe
    The new csv file is saved under trajectoriesDat_trim.csv, no dataframe is returned
    """

    column_list = VarsToKeep
    for ems_region in ['All', 'EMS-1', 'EMS-2', 'EMS-3', 'EMS-4', 'EMS-5', 'EMS-6', 'EMS-7', 'EMS-8', 'EMS-9', 'EMS-10', 'EMS-11']:
        column_list.append('susceptible_' + str(ems_region))
        column_list.append('infected_' + str(ems_region))
        column_list.append('recovered_' + str(ems_region))
        column_list.append('infected_cumul_' + str(ems_region))
        column_list.append('asymp_cumul_' + str(ems_region))
        column_list.append('asymp_det_cumul_' + str(ems_region))
        column_list.append('symp_mild_cumul_' + str(ems_region))
        column_list.append('symp_severe_cumul_' + str(ems_region))
        column_list.append('symp_mild_det_cumul_' + str(ems_region))
        column_list.append('symp_severe_det_cumul_' + str(ems_region))
        column_list.append('hosp_det_cumul_' + str(ems_region))
        column_list.append('hosp_cumul_' + str(ems_region))
        column_list.append('detected_cumul_' + str(ems_region))
        column_list.append('crit_cumul_' + str(ems_region))
        column_list.append('crit_det_cumul_' + str(ems_region))
        column_list.append('death_det_cumul_' + str(ems_region))
        column_list.append('deaths_' + str(ems_region))
        column_list.append('crit_det_' + str(ems_region))
        column_list.append('critical_det_' + str(ems_region))
        column_list.append('critical_' + str(ems_region))
        column_list.append('hospitalized_det_' + str(ems_region))
        column_list.append('hospitalized_' + str(ems_region))

    df = pd.read_csv(os.path.join(exp_dir, 'trajectoriesDat.csv'), usecols=column_list)

    if keepTimes is not None:
        df = df[df['time'] >= int(keepTimes)]

    df.to_csv(os.path.join(exp_dir, 'trajectoriesDat_trim.csv'), index=False)


if __name__ == '__main__':

    VarsToKeep = ['startdate', 'time', 'scen_num','sample_num', 'run_num',  'reopening_multiplier_4', 'reduced_inf_of_det_cases_ct1',
                            'change_testDelay_Sym_1', 'change_testDelay_As_1', 'd_Sym_ct1', 'd_AsP_ct1']

    stem = sys.argv[1]
    #stem ="20200722_IL_EMS_scen3"
    exp_names = [x for x in os.listdir(os.path.join(sim_output_path)) if stem in x]

    for exp_name in exp_names:
        exp_dir = os.path.join(sim_output_path, exp_name)
        trim_trajectories_Dat(exp_dir=exp_dir, VarsToKeep=VarsToKeep, keepTimes=120)
