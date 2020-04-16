import argparse
import re
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

log = logging.getLogger(__name__)

mpl.rcParams['pdf.fonttype'] = 42
Location = 'Local'  # 'NUCLUSTER'

today = date.today()

DEFAULT_CONFIG = './extendedcobey.yaml'


def add_config_parameter_column(df, parameter, parameter_function):
    if isinstance(parameter_function, int):
        df[parameter] = parameter_function
    elif 'matrix' in parameter_function:
        m = parameter_function['matrix']
        for i, row in enumerate(m):
            for j, item in enumerate(row):
                df[f'{parameter}{i+1}_{j+1}'] = item
    elif 'np.random' in parameter_function:
        function_kwargs = parameter_function['function_kwargs']
        df[parameter] = [getattr(np.random, parameter_function['np.random'])(**function_kwargs)
                         for i in range(len(df))]
    elif 'custom_function' in parameter_function:
        function_name = parameter_function['custom_function']
        function_kwargs = parameter_function['function_kwargs']
        if function_name == 'DateToTimestep':
            function_kwargs['startdate'] = first_day
            df[parameter] = [globals()[function_name](**function_kwargs) for i in range(len(df))]
            # Note that the custom_function needs to be imported
        elif function_name == 'subtract':
            df[parameter] = df[function_kwargs['x1']] - df[function_kwargs['x2']]
    else:
        raise ValueError(f"Unknown type of parameter {parameter}")
    return df


def add_fixed_parameters_region_specific(df, config, region):
    for parameter_group, parameter_group_values in config['fixed_parameters_region_specific'].items():
        if parameter_group in ('populations', 'startdate'):
            continue
        for parameter, parameter_function in parameter_group_values[region].items():
            df = add_config_parameter_column(df, parameter, parameter_function)
    return df


def add_computed_parameters(df):
    df['fraction_dead'] = df.apply(lambda x: x['cfr'] / x['fraction_severe'], axis=1)
    df['fraction_hospitalized'] = df.apply(lambda x: 1 - x['fraction_critical'] - x['fraction_dead'], axis=1)
    return df


def generateParameterSamples(samples, pop, first_day, config):
    """ Given a yaml configuration file (e.g. ./extendedcobey.yaml),
    generate a dataframe of the parameters for a simulation run using the specified
    functions/sampling mechansims.
    Supported functions are in the FUNCTIONS variable.
    """
    df = pd.DataFrame()
    df['sample_num'] = range(samples)
    df['speciesS'] = pop
    df['initialAs'] = config['experiment_setup_parameters']['initialAs']

    for parameter, parameter_function in config['sampled_parameters'].items():
        df = add_config_parameter_column(df, parameter, parameter_function)
    df = add_fixed_parameters_region_specific(df, config, region)
    for parameter, parameter_function in config['fixed_parameters_global'].items():
        df = add_config_parameter_column(df, parameter, parameter_function)
    df = add_computed_parameters(df)

    df.to_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"), index=False)
    print(df.columns)
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
    sample_nr: int
        Sample number of the df to use in generating the emodl file
    emodl_template: str
        File name of the emodl template file
    scen_num: int
        Scenario number of the simulation run
    """
    fin = open(os.path.join(temp_exp_dir, emodl_template), "rt")
    data = fin.read()
    for col in df.columns:
        data = data.replace(f'@{col}@', str(df[col][sample_nr]))
    data = data.replace('@Ki@', '%.09f' % Ki_i)
    remaining_placeholders = re.findall(r'@\w+@', data)
    if remaining_placeholders:
        raise ValueError("Not all placeholders have been replaced in the template emodl file. "
                         f"Remaining placeholders: {remaining_placeholders}")
    fin.close()
    fin = open(os.path.join(temp_dir, f"simulation_{scen_num}.emodl"), "wt")
    fin.write(data)
    fin.close()


def generateScenarios(simulation_population, Kivalues, duration, monitoring_samples,
                      nruns, sub_samples, modelname, first_day, Location, experiment_config):
    lst = []
    scen_num = 0
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population, first_day=first_day,
                                       config=experiment_config)

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
                data_cfg = data_cfg.replace('trajectories',
                                            f'./_temp/{exp_name}/trajectories/trajectories_scen{scen_num}')
            else:
                raise RuntimeError("Unable to decide where to put the trajectories file.")
            fin.close()
            fin = open(os.path.join(temp_dir, "model_"+str(scen_num)+".cfg"), "wt")
            fin.write(data_cfg)
            fin.close()

    df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki', 'first_day', 'simulation_population'])
    df.to_csv(os.path.join(temp_exp_dir, "scenarios.csv"), index=False)
    return scen_num


def get_experiment_config(experiment_config_file):
    config = yaml.load(open(DEFAULT_CONFIG), Loader=yaml.FullLoader)
    yaml_file = open(experiment_config_file)
    expt_config = yaml.load(yaml_file, Loader=yaml.FullLoader)
    for param_type, updated_params in expt_config.items():
        if not config[param_type]:
            config[param_type] = {}
        if updated_params:
            config[param_type].update(updated_params)
    return config


def get_experiment_setup_parameters(experiment_config):
    return experiment_config['experiment_setup_parameters']


def get_region_specific_fixed_parameters(experiment_config, region):
    fixed = experiment_config['fixed_parameters_region_specific']
    return {param: fixed[param][region] for param in fixed}


def get_fitted_parameters(experiment_config, region):
    fitted = experiment_config['fitted_parameters']
    fitted_parameters = {}
    for param, region_values in fitted.items():
        region_parameter = region_values[region]
        if 'np' in region_parameter:
            fitted_parameters[param] = getattr(np, region_parameter['np'])(**region_parameter['function_kwargs'])
    return fitted_parameters


def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "--region",
        type=str,
        help="Region on which to run simulation. E.g. 'IL'",
        required=True
    )
    parser.add_argument(
        "--experiment_config",
        type=str,
        help=("Config file (in YAML) containing the parameters to override the default config. "
              "This file should have the same structure as the default config. "
              "example: ./sample_experiment.yaml "),
        required=True
    )
    parser.add_argument(
        "--emodl_template",
        type=str,
        help="Template emodl file to use",
        default="extendedmodel_cobey.emodl"
    )

    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level="DEBUG")
    logging.getLogger("matplotlib").setLevel("INFO")  # Matplotlib has noisy debugs

    args = parse_args()

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
    experiment_config = get_experiment_config(args.experiment_config)
    experiment_setup_parameters = get_experiment_setup_parameters(experiment_config)
    np.random.seed(experiment_setup_parameters['random_seed'])

    region = args.region
    fixed_parameters = get_region_specific_fixed_parameters(experiment_config, region)
    simulation_population = fixed_parameters['populations']
    first_day = fixed_parameters['startdate']
    Kivalues = get_fitted_parameters(experiment_config, region)['Kis']

    exp_name = f"{today.strftime('%Y%m%d')}_{region}_updatedStartDate_rn{int(np.random.uniform(10, 99))}"

    # Generate folders and copy required files
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder(
        exp_name, emodl_dir, args.emodl_template, cfg_dir, wdir=wdir,
        git_dir=git_dir)  # GE 04/10/20 added exp_name,emodl_dir,emodlname,cfg_dir here to fix exp_name not defined error
    log.debug(f"temp_dir = {temp_dir}\n"
              f"temp_exp_dir = {temp_exp_dir}\n"
              f"trajectories_dir = {trajectories_dir}\n"
              f"sim_output_path = {sim_output_path}\n"
              f"plot_path = {plot_path}")

    nscen = generateScenarios(
        simulation_population, Kivalues,
        nruns=experiment_setup_parameters['number_of_runs'],
        sub_samples=experiment_setup_parameters['number_of_samples'],
        duration=experiment_setup_parameters['duration'],
        monitoring_samples=experiment_setup_parameters['monitoring_samples'],
        modelname=args.emodl_template, first_day=first_day, Location=Location,
        experiment_config=experiment_config)

    generateSubmissionFile(
        nscen, exp_name, trajectories_dir, temp_dir, temp_exp_dir,
        exe_dir=exe_dir, docker_image=docker_image)

    if Location == 'Local':
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
