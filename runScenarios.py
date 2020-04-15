import logging
import numpy as np
import pandas as pd
import os
import matplotlib as mpl
from datetime import date
import sys
import yaml

from dotenv import load_dotenv

from load_paths import load_box_paths
from simulation_helpers import (DateToTimestep, makeExperimentFolder, generateSubmissionFile,
                                combineTrajectories, runExp, cleanup, sampleplot)
from simulation_setup import load_setting_parameter

log = logging.getLogger(__name__)
logging.basicConfig(level="DEBUG")
logging.getLogger("matplotlib").setLevel("INFO")  # Matplotlib has noisy debugs


mpl.rcParams['pdf.fonttype'] = 42
Location = 'Local'  # 'NUCLUSTER'

today = date.today()

FUNCTIONS = {'uniform': np.random.uniform}

NUMBER_OF_SAMPLES = 2
NUMBER_OF_RUNS = 1
DURATION = 365
MONITORING_SAMPLES = 365  # needs to be smaller than duration


def generateParameterSamples(samples, pop, first_day, config_name='./extendedcobey.yaml'):
    """ Given a yaml configuration file (e.g. ./extendedcobey.yaml),
    generate a dataframe of the parameters for a simulation run using the specified
    functions/sampling mechansims.
    Supported functions are in the FUNCTIONS variable.
    """
    yaml_file = open(config_name)
    config = yaml.load(yaml_file, Loader=yaml.FullLoader)

    df = pd.DataFrame()
    df['sample_num'] = range(samples)
    df['speciesS'] = pop
    df['initialAs'] = 10

    for parameter, parameter_function in config['parameters'].items():
        function_string = parameter_function['replacement_function']
        function_kwargs = parameter_function['replacement_args']
        df[parameter] = [FUNCTIONS[function_string](**function_kwargs) for i in range(samples)]

    df['fraction_dead'] = df.apply(lambda x: x['cfr'] / x['fraction_severe'], axis=1)
    df['fraction_hospitalized'] = df.apply(lambda x: 1 - x['fraction_critical'] - x['fraction_dead'], axis=1)
    df['socialDistance_time1'] = DateToTimestep(date(2020, 3, 12), startdate=first_day)
    df['socialDistance_time2'] = DateToTimestep(date(2020, 3, 17), startdate=first_day)
    df['socialDistance_time3'] = DateToTimestep(date(2020, 3, 21), startdate=first_day)

    df.to_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"), index=False)
    return(df)


def replaceParameters(df, Ki_i, sample_nr, emodl_template, scen_num):
    """ Given an emodl template file, replaces the placeholder names
    (which are bookended by '@') with the sampled parameter value.
    This is saved as a (temporary) emodl file to be used in simulation runs.
    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing all the sampled parameters
    Ki_i: float
        ???
    sample_nr: int
        Sample number of the df to use in generating the emodl file
    emodl_template: str
        File name of the emodl template fileOA
    scen_num: int
        Scenario number of the simulation run
    """
    print(Ki_i, sample_nr, emodl_template,  scen_num)
    fin = open(os.path.join(temp_exp_dir, emodl_template), "rt")
    data = fin.read()
    for col in df.columns:
        data = data.replace(f'@{col}@', str(df[col][sample_nr]))
    data = data.replace('@Ki@', '%.09f' % Ki_i)
    fin.close()
    fin = open(os.path.join(temp_dir, f"simulation_{scen_num}.emodl"), "wt")
    fin.write(data)
    fin.close()


def generateScenarios(simulation_population, Kivalues, duration, monitoring_samples,
                      nruns, sub_samples, modelname, first_day, Location):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population, first_day=first_day)

    for sample in range(sub_samples):
        for i in Kivalues:
            scen_num += 1

            lst.append([sample, scen_num, i, first_day, simulation_population])
            replaceParameters(df=dfparam, Ki_i=i, sample_nr=sample, emodl_template=modelname, scen_num=scen_num)

            # adjust model.cfg
            fin = open(os.path.join(temp_exp_dir, "model.cfg"), "rt")
            data_cfg = fin.read()
            data_cfg = data_cfg.replace('@duration@', str(duration))
            data_cfg = data_cfg.replace('@monitoring_samples@', str(monitoring_samples))
            data_cfg = data_cfg.replace('@nruns@', str(nruns))
            if not Location == 'Local':
                data_cfg = data_cfg.replace('trajectories', f'trajectories_scen{scen_num}')
            elif sys.platform not in ["win32", "cygwin"]:
                # When running on Linux or OSX (and not in Quest), assume the
                # trajectories directory is in the working directory.
                traj_fname = os.path.join('trajectories', f'trajectories_scen{scen_num}')
                data_cfg = data_cfg.replace('trajectories', traj_fname)
            elif Location == 'Local':
                data_cfg = data_cfg.replace('trajectories', f'./_temp/{exp_name}/trajectories/trajectories_scen{scen_num}')
            else:
                raise RuntimeError("Unable to decide where to put the trajectories file.")
            fin.close()
            fin = open(os.path.join(temp_dir, "model_"+str(scen_num)+".cfg"), "wt")
            fin.write(data_cfg)
            fin.close()

    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki', 'first_day', 'simulation_population'])
    df.to_csv(os.path.join(temp_exp_dir, "scenarios.csv"), index=False)
    return scen_num


if __name__ == '__main__' :
    # Load parameters
    load_dotenv()

    _, _, wdir, exe_dir, git_dir = load_box_paths()
    Location = os.getenv("LOCATION") or Location

    # Only needed on non-Windows, non-Quest platforms
    docker_image = os.getenv("DOCKER_IMAGE")

    emodl_dir = os.path.join(git_dir, 'emodl')
    cfg_dir = os.path.join(git_dir, 'cfg')

    log.debug(f"Running in Location = {Location}")
    if sys.platform not in ['win32', 'cygwin']:
        log.debug(f"Running in a non-Windows environment; "
                  f'docker_image="{docker_image}"')
    log.debug(f"Working directory: wdir={wdir}")
    log.debug(f"git_dir={git_dir}")

    master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild',
                           'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
    detection_channel_list = ['detected', 'detected_cumul', 'asymp_det_cumul', 'hosp_det_cumul']
    custom_channel_list = ['detected_cumul', 'symp_severe_cumul', 'asymp_det_cumul', 'hosp_det_cumul',
                           'symp_mild_cumul', 'asymp_cumul', 'hosp_cumul', 'crit_cumul']

    # =============================================================
    #   Experiment design, fitting parameter and population
    # =============================================================

    # Define setting
    region = 'NMH_catchment'  # NMH_catchment  # IL  #EMS_3  # Chicago
    exp_name = today.strftime("%Y%m%d") + '_%s_updatedStartDate' % region + '_rn' + str(int(np.random.uniform(10, 99)))

    # Selected SEIR model
    emodl_template = 'extendedmodel_cobey.emodl'

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder(
        exp_name, emodl_dir, emodl_template, cfg_dir, wdir=wdir,
        git_dir=git_dir)  # GE 04/10/20 added exp_name,emodl_dir,emodlname, cfg_dir here to fix exp_name not defined error
    log.debug(f"temp_dir = {temp_dir}\n"
              f"temp_exp_dir = {temp_exp_dir}\n"
              f"trajectories_dir = {trajectories_dir}\n"
              f"sim_output_path = {sim_output_path}\n"
              f"plot_path = {plot_path}")

    populations, Kis, startdate = load_setting_parameter()

    simulation_population = populations[region]

    # Parameter values
    Kivalues = Kis[region]
    first_day = startdate[region]

    nscen = generateScenarios(
        simulation_population, Kivalues,
        nruns=NUMBER_OF_RUNS, sub_samples=NUMBER_OF_SAMPLES,
        duration=DURATION, monitoring_samples=MONITORING_SAMPLES,
        modelname=emodl_template, first_day=first_day, Location=Location)
'''
    generateSubmissionFile(
        nscen, exp_name, trajectories_dir, temp_dir, temp_exp_dir,
        exe_dir=exe_dir, docker_image=docker_image)

    if Location == 'Local' :
        runExp(trajectories_dir=trajectories_dir, Location='Local')

        # Once the simulations are done
        # number_of_samples*len(Kivalues) == nscen ### to check
        combineTrajectories(Nscenarios=nscen, trajectories_dir=trajectories_dir,
                            temp_exp_dir=temp_exp_dir, deleteFiles=False)
        cleanup(temp_exp_dir=temp_exp_dir, sim_output_path=sim_output_path,
                plot_path=plot_path, delete_temp_dir=False)
        df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))

        sampleplot(df, allchannels=master_channel_list, first_day=first_day,
                   plot_fname=os.path.join(plot_path, 'main_channels.png'))
        sampleplot(df, allchannels=detection_channel_list, first_day=first_day,
                   plot_fname=os.path.join('detection_channels.png'))
        sampleplot(df, allchannels=custom_channel_list, first_day=first_day,
                   plot_fname=os.path.join('cumulative_channels.png'))
'''
