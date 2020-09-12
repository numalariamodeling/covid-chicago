import argparse
import datetime
import logging
import os
import re
import sys
import subprocess
import matplotlib as mpl
import numpy as np
import pandas as pd
import yaml
import yamlordereddictloader

from load_paths import load_box_paths
from simulation_helpers import (DateToTimestep, cleanup, combineTrajectories,
                                generateSubmissionFile, generateSubmissionFile_quest, makeExperimentFolder,
                                runExp, runSamplePlot)

log = logging.getLogger(__name__)

mpl.rcParams['pdf.fonttype'] = 42

today = datetime.datetime.today()

def _get_full_factorial_df(df, column_name, values):
    dfs = []
    for value in values:
        df_copy = df.copy()
        df_copy[column_name] = value
        dfs.append(df_copy)
    result = pd.concat(dfs, ignore_index=True)
    return result


def _parse_config_parameter(df, parameter, parameter_function, column_name, full_factorial):
    if isinstance(parameter_function, (int, float)):
        df[column_name] = parameter_function
        return df
    elif 'np.random' in parameter_function:
        function_kwargs = parameter_function['function_kwargs']
        func = getattr(np.random, parameter_function['np.random'])
        if full_factorial:
            params = func(**{"size": 1, **function_kwargs})
            result = _get_full_factorial_df(df, column_name, params)
        else:
            params = [func(**function_kwargs, size=1)[0]
                      for _ in range(len(df))]
            result = df
            result[column_name] = params
        return result
    elif 'np' in parameter_function:
        function_kwargs = parameter_function['function_kwargs']
        func = getattr(np, parameter_function['np'])
        if full_factorial:
            params = func(**{"num": 1, **function_kwargs})
            result = _get_full_factorial_df(df, column_name, params)
        else:
            params = [func(**function_kwargs, num=1)[0]
                      for _ in range(len(df))]
            result = df
            result[column_name] = params
        return result
    elif 'custom_function' in parameter_function:
        function_name = parameter_function['custom_function']
        function_kwargs = parameter_function['function_kwargs']
        if function_name == 'DateToTimestep':
            start_dates_from_yaml = function_kwargs['dates']
            if not isinstance(start_dates_from_yaml, list):
                # `start_dates_from_yaml` is a single datetime object.
                start_dates_from_yaml = [start_dates_from_yaml]
            dfs = []
            for start_date_from_yaml in start_dates_from_yaml:
                df_copy = df.copy()
                df_copy[column_name] = [
                    DateToTimestep(start_date_from_yaml, df_copy["startdate"][i])
                    for i in range(len(df_copy))
                ]
                dfs.append(df_copy)
            df = pd.concat(dfs, ignore_index=True)
            return df
        elif function_name == 'subtract':
            df[column_name] = df[function_kwargs['x1']] - df[function_kwargs['x2']]
            return df
        else:
            raise ValueError(f"Unknown function for parameter {parameter}: {function_name}")
    else:
        raise ValueError(f"Unknown type of parameter {parameter}")


def _parse_age_specific_distribution(df, parameter, parameter_function, age_bins, full_factorial):
    """Age-specific parameter sampling from a numpy distribution

    Create a column in the DataFrame for each age bin, and sample from
    the specified distribution.

    Modifies the input DataFrame in place.
    """
    # Error-check and standardize "function_kwargs"
    kwargs = parameter_function.get('function_kwargs')
    if isinstance(kwargs, list):
        if len(kwargs) != len(age_bins):
            raise ValueError(f"function_kwargs for {parameter} have {len(kwargs)} "
                             f"entries, but there are {len(age_bins)} age bins.")
    elif not isinstance(kwargs, dict):
        raise TypeError(f"Parameter {parameter} must have a list or dict "
                        f"for function_kwargs.")
    else:
        # If a dictionary, use the same dictionary for each age bin.
        kwargs = len(age_bins) * [kwargs]

    # Error-check and standardize the distribution name
    distribution = parameter_function['np.random']
    if isinstance(distribution, list):
        if len(distribution) != len(age_bins):
            raise ValueError(f"List of distributions for {parameter} "
                             f"has {len(distribution)} entries, but there are "
                             f"{len(age_bins)} age bins.")
    elif not isinstance(distribution, str):
        raise TypeError(f"Parameter {parameter} must have a list or a string "
                        f"for the distribution name.")
    else:
        distribution = len(age_bins) * [distribution]

    # Do the sampling
    for _bin, _dist, _kwargs in zip(age_bins, distribution, kwargs):
        func = getattr(np.random, _dist)
        column_name = f"{parameter}_{_bin}"
        if full_factorial:
            params = func(**{"size": 1, **_kwargs})
            df = _get_full_factorial_df(df, column_name, params)
        else:
            params = [func(**_kwargs, size=1)[0] for _ in range(len(df))]
            df[column_name] = params
    return df


def add_config_parameter_column(df, parameter, parameter_function, age_bins=None, full_factorial=True):
    """ Applies the described function and adds the column to the dataframe

    The input DataFrame will be modified in place.

    Parameters
    ----------
    df: pd.DataFrame
        dataframe of the fixed and sampled parameters which is used to generate scenarios
    parameter: str
        Name of the parameter to compute and add to the parameters dataframe
        e.g.: incubation_pd
    parameter_function: dict
        A dictionary describing the function or constant to compute for the given parameter.
        Supported options are:
        - int: The column will contain a constant value
          e.g.: initialAs
        - matrix: Each matrix value is a numeric and the new columns added are of the form "<parameter><row>_<column>".
          e.g. the contact matrix
        - sampling: Any of the functions available in np.random can be used to randomly samply values for the parameter.
          Arguments are passed to the sampling function as kwargs (which are specified in the yaml).
        - DateToTimestep: This is a custom function that is supported to compute the amount of time
          from an intervention date. e.g. socialDistance_time
        - subtract: This subtracts one column in the dataframe (x2) from another (x1).
          e.g. SpeciesS (given N and initialAs)
    age_bins: list of str, optional
        If the parameter is to be expanded by age, the new dataframe with have individual parameters for each bin.
    full_factorial : bool, optional
        If True, the returned df has a full factorial with the given parameter values.

    Returns
    -------
    df: pd.DataFrame
        dataframe with the additional column(s) added
    """
    if isinstance(parameter_function, dict) and parameter_function.get('expand_by_age'):
        if not age_bins:
            raise ValueError("Ages bins must be specified if using an age expansion")
        if 'list' in parameter_function:
            n_list = len(parameter_function['list'])
            if n_list != len(age_bins):
                raise ValueError(f"{parameter} has a list with {n_list} elements, "
                                 f"but there are {len(age_bins)} age bins.")
            for bin, val in zip(age_bins, parameter_function['list']):
                df = _parse_config_parameter(df, parameter, val, f'{parameter}_{bin}', full_factorial)
        elif 'custom_function' in parameter_function:
            function_name = parameter_function['custom_function']
            if function_name == 'subtract':
                for bin in age_bins:
                    df = _parse_config_parameter(
                        df, parameter,
                        {'custom_function': 'subtract',
                         'function_kwargs': {'x1': f'{parameter_function["function_kwargs"]["x1"]}_{bin}',
                                             'x2': f'{parameter_function["function_kwargs"]["x2"]}_{bin}'}},
                        f'{parameter}_{bin}',
                        full_factorial,
                    )
            else:
                raise ValueError(f"Unknown custom function: {function_name}")
        elif 'np.random' in parameter_function:
            df = _parse_age_specific_distribution(df, parameter, parameter_function, age_bins, full_factorial)
        else:
            raise ValueError(f"Unknown type of parameter {parameter} for expand_by_age")
    else:
        if isinstance(parameter_function, dict) and 'matrix' in parameter_function:
            m = parameter_function['matrix']
            for i, row in enumerate(m):
                for j, item in enumerate(row):
                    df = _parse_config_parameter(df, parameter, item, f'{parameter}{i+1}_{j+1}', full_factorial)
        else:
            df = _parse_config_parameter(df, parameter, parameter_function, parameter, full_factorial)
    return df


def add_fixed_parameters_region_specific(df, config, region, age_bins):
    """ For each of the region-specific parameters, iteratively add them to the parameters dataframe
    """
    for parameter, parameter_function in config['fixed_parameters_region_specific'].items():
        if parameter in ('populations', 'startdate'):
            continue
        param_func_with_age = {'expand_by_age': parameter_function.get('expand_by_age'),
                               'list': parameter_function[region]}
        df = add_config_parameter_column(df, parameter, param_func_with_age, age_bins)

    return df


def add_computed_parameters(df):
    """ Parameters that are computed from other parameters are computed and added to the parameters
    dataframe.
    """
    df['fraction_dead'] = df['cfr'] / df['fraction_severe']
    df['fraction_hospitalized'] = 1 - df['fraction_critical'] - df['fraction_dead']

    ##If due to random sampling  time_to_detection > time_to_hospitalization, set to at least one day before hospitalization
    ##df['time_to_detection'][df.time_to_detection > df.time_to_hospitalization] = df['time_to_hospitalization'][df.time_to_detection > df.time_to_hospitalization] -1

    return df


def add_parameters(df, parameter_type, config, region, age_bins, full_factorial=True):
    """Append parameters to the DataFrame"""
    if parameter_type not in ("time_parameters", "intervention_parameters",
                              "sampled_parameters", "fixed_parameters_global"):
        raise ValueError(f"Unrecognized parameter type: {parameter_type}")
    for parameter, parameter_function in config[parameter_type].items():
        if region in parameter_function:
            # Check for a distribution specific to this region
            parameter_function = parameter_function[region]
        df = add_config_parameter_column(df, parameter, parameter_function, age_bins, full_factorial)
    return df


def generateParameterSamples(samples, pop, start_dates, config, age_bins, Kivalues, region):
    """ Given a yaml configuration file (e.g. ./extendedcobey.yaml),
    generate a dataframe of the parameters for a simulation run using the specified
    functions/sampling mechanisms.
    """
    # Time-independent parameters. No full factorial across parameters.
    df = pd.DataFrame()
    df['sample_num'] = range(samples)
    df['speciesS'] = pop
    df['initialAs'] = config['experiment_setup_parameters']['initialAs']
    df = add_fixed_parameters_region_specific(df, config, region, age_bins)
    df = add_parameters(df, "sampled_parameters", config, region, age_bins, full_factorial=False)

    # Time-independent parameters. Create full factorial.
    df = add_parameters(df, "intervention_parameters", config, region, age_bins)
    df = add_parameters(df, "fixed_parameters_global", config, region, age_bins)
    df = _get_full_factorial_df(df, "Ki", Kivalues)

    # Time-varying parameters for each start date.
    dfs = []
    for start_date in start_dates:
        df_copy = df.copy()
        df_copy['startdate'] = start_date
        df_copy = add_parameters(df_copy, "time_parameters", config, region, age_bins)
        df_copy = add_computed_parameters(df_copy)
        dfs.append(df_copy)

    result = pd.concat(dfs, ignore_index=True)
    result["scen_num"] = range(1, len(result) + 1)
    result.to_csv(os.path.join(temp_exp_dir, "sampled_parameters.csv"), index=False)
    return result


def replaceParameters(df, row_i, Ki_i, emodl_template, scen_num):
    """ Given an emodl template file, replaces the placeholder names
    (which are bookended by '@') with the sampled parameter value.
    This is saved as a (temporary) emodl file to be used in simulation runs.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing all the sampled parameters
    row_i : int
        Index of which row in df we are handling
    Ki_i: float
    emodl_template: str
        File name of the emodl template file
    scen_num: int
        Scenario number of the simulation run
    """
    fin = open(os.path.join(temp_exp_dir, emodl_template), "rt")
    data = fin.read()
    for col in df.columns:
        data = data.replace(f'@{col}@', str(df.iloc[row_i][col]))
    data = data.replace('@Ki@', '%.09f' % Ki_i)
    remaining_placeholders = re.findall(r'@\w+@', data)
    if remaining_placeholders:
        raise ValueError("Not all placeholders have been replaced in the template emodl file. "
                         f"Remaining placeholders: {remaining_placeholders}")
    fin.close()
    remaining_placeholders = re.findall(r'@\w+@', data)
    if remaining_placeholders:
        raise ValueError("Not all placeholders have been replaced in the template emodl file. "
                         f"Remaining placeholders: {remaining_placeholders}")
    fin = open(os.path.join(temp_dir, f"simulation_{scen_num}.emodl"), "wt")
    fin.write(data)
    fin.close()


def generateScenarios(simulation_population, Kivalues, duration, monitoring_samples,
                      nruns, sub_samples, modelname, cfg_file, start_dates, Location,
                      experiment_config, age_bins, region):
    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population, start_dates=start_dates,
                                       config=experiment_config, age_bins=age_bins, Kivalues=Kivalues, region=region)

    for row_i, row in dfparam.iterrows():
        Ki = row['Ki']
        scen_num = row['scen_num']

        replaceParameters(df=dfparam, row_i=row_i, Ki_i=Ki,  emodl_template=modelname, scen_num=scen_num)

        # adjust model.cfg
        fin = open(os.path.join(temp_exp_dir, cfg_file), "rt")
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

    return len(dfparam)


def get_experiment_config(experiment_config_file):
    config = yaml.load(open(os.path.join('./experiment_configs', args.masterconfig)), Loader=yamlordereddictloader.Loader)
    yaml_file = open(os.path.join('./experiment_configs',experiment_config_file))
    expt_config = yaml.safe_load(yaml_file)
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


def get_start_dates(start_date):
    if isinstance(start_date, list):
        # `start_date` is a list of exactly two datetime.date objects,
        # representing the range of the start dates we want.
        start_date, end_date = start_date
        n_days = (end_date - start_date).days + 1
        return [start_date + datetime.timedelta(days=delta)
                for delta in range(n_days)]
    else:
        # Assume `start_date` is a single datetime.date object.
        return [start_date]


def parse_args():
    description = "Simulation run for modeling Covid-19"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-mc",
        "--masterconfig",
        type=str,
        help="Master yaml file that includes all model parameters.",
        default='extendedcobey_200428.yaml',
    )

    parser.add_argument(
        "-rl",
        "--running_location",
        type=str,
        help="Location where the simulation is being run.",
        choices=["Local", "NUCLUSTER"],
        default=None,
    )
    parser.add_argument(
        "-r",
        "--region",
        type=str,
        help="Region on which to run simulation. E.g. 'IL'",
        required=True
    )
    parser.add_argument(
        "-c",
        "--experiment_config",
        type=str,
        help=("Config file (in YAML) containing the parameters to override the default config. "
              "This file should have the same structure as the default config. "
              "example: ./experiment_configs/sample_experiment.yaml "),
        required=True
    )
    parser.add_argument(
        "-e",
        "--emodl_template",
        type=str,
        help="Template emodl file to use",
        default="extendedmodel_cobey.emodl"
    )
    parser.add_argument(
        "-cfg",
        "--cfg_template",
        type=str,
        help="Template cfg file to use",
        default="model_B.cfg"
    )

    parser.add_argument(
        "-n",
        "--name_suffix",
        type=str,
        help="Adding custom suffix to the experiment name. Ignored if '--name' specified.",
        default= f"_test_rn{str(today.microsecond)[-2:]}"
    )

    parser.add_argument(
        "--exp-name",
        type=str,
        help="Experiment name; also the output directory name",
        default=None,
    )

    parser.add_argument(
        "--post_process",
        type=str,
        help="Whether or not to run post-processing functions current options are 'dataComparison'  'processForCivis' 'SamplePlot' ",
        default=None,
    )

    parser.add_argument(
        "--noSamplePlot",
        action='store_true',
        help="If specified, no sample plot with main trajectories will be generated",
    )


    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level="DEBUG")
    logging.getLogger("matplotlib").setLevel("INFO")  # Matplotlib has noisy debugs

    args = parse_args()

    _, _, wdir, exe_dir, git_dir = load_box_paths(Location=args.running_location)
    Location = os.getenv("LOCATION") or args.running_location
    if not Location:
        raise ValueError("Please provide a running location via environment "
                         "variable or CLI parameter.")

    # Only needed on non-Windows, non-Quest platforms
    docker_image = os.getenv("DOCKER_IMAGE")

    emodl_dir = os.path.join(git_dir, 'emodl')
    cfg_dir = os.path.join(git_dir, 'cfg')
    yaml_dir = os.path.join(git_dir, 'experiment_configs')

    log.debug(f"Running in Location = {Location}")
    if sys.platform not in ['win32', 'cygwin']:
        log.debug(f"Running in a non-Windows environment; "
                  f'docker_image="{docker_image}"')
    log.debug(f"Working directory: wdir={wdir}")
    log.debug(f"git_dir={git_dir}")

    # =============================================================
    #   Experiment design, fitting parameter and population
    # =============================================================
    experiment_config = get_experiment_config(args.experiment_config)
    experiment_setup_parameters = get_experiment_setup_parameters(experiment_config)
    np.random.seed(experiment_setup_parameters['random_seed'])

    region = args.region
    fixed_parameters = get_region_specific_fixed_parameters(experiment_config, region)
    simulation_population = fixed_parameters['populations']
    start_dates = get_start_dates(fixed_parameters['startdate'])
    Kivalues = get_fitted_parameters(experiment_config, region)['Kis']

    exp_name = args.exp_name or f"{today.strftime('%Y%m%d')}_{region}_{args.name_suffix}"

    # Generate folders and copy required files
    # GE 04/10/20 added exp_name,emodl_dir,emodlname,cfg_dir here to fix exp_name not defined error
    temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path = makeExperimentFolder(
        exp_name, emodl_dir, args.emodl_template, cfg_dir, args.cfg_template,  yaml_dir,  args.masterconfig, args.experiment_config, wdir=wdir,
        git_dir=git_dir)
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
        modelname=args.emodl_template, start_dates=start_dates, Location=Location,
        cfg_file=args.cfg_template,
        experiment_config=experiment_config,
        age_bins=experiment_setup_parameters.get('age_bins'),
        region=region,
    )

    if Location == 'NUCLUSTER':
        generateSubmissionFile_quest(nscen, exp_name, args.experiment_config, trajectories_dir,  temp_exp_dir)
        runExp(trajectories_dir=temp_exp_dir, Location='NUCLUSTER')

    if Location == 'Local':
        generateSubmissionFile(
            nscen, exp_name, args.experiment_config,trajectories_dir, temp_dir, temp_exp_dir,
            exe_dir=exe_dir, docker_image=docker_image)

        runExp(trajectories_dir=trajectories_dir, Location='Local')

        combineTrajectories(Nscenarios=nscen, trajectories_dir=trajectories_dir,
                            temp_exp_dir=temp_exp_dir, deleteFiles=False)
        cleanup(temp_dir=temp_dir, temp_exp_dir=temp_exp_dir, sim_output_path=sim_output_path,
                plot_path=plot_path, delete_temp_dir=True)
        log.info(f"Outputs are in {sim_output_path}")

        if not args.noSamplePlot:
            log.info("Sample plot")
            runSamplePlot(sim_output_path=sim_output_path, plot_path=plot_path,start_dates=start_dates,channel_list="master")

        if args.post_process == 'dataComparison':
            log.info("Compare to data")
            p0 = os.path.join(sim_output_path, 'runDataComparison.bat')
            subprocess.call([p0])

        if args.post_process == 'processForCivis':

            log.info("Compare to data")
            p0 = os.path.join(sim_output_path, 'runDataComparison.bat')
            subprocess.call([p0])

            log.info("Process for civis - csv file")
            p1 = os.path.join(sim_output_path, 'runProcessForCivis_1.bat')
            subprocess.call([p1])

            log.info("Process for civis - overflow probabilities")
            p2 = os.path.join(sim_output_path, 'runProcessForCivis_2.bat')
            subprocess.call([p2])

            log.info("Process for civis - Rt estimation")
            p3 = os.path.join(sim_output_path, 'runProcessForCivis_3.bat')
            subprocess.call([p3])

            log.info("Process for civis - file copy and changelog")
            p4 = os.path.join(sim_output_path, 'runProcessForCivis_4.bat')
            subprocess.call([p4])



