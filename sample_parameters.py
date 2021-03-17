import numpy as np
import pandas as pd
import json
import os
import matplotlib as mpl
import matplotlib.dates as mdates
from load_paths import load_box_paths
from simulation_helpers import *
from runScenarios import *
import itertools

mpl.rcParams['pdf.fonttype'] = 42


def parse_args():
    description = "Defining sample parameters for simulations, default set to locale emodl. "
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-mc",
        "--masterconfig",
        type=str,
        help="Master yaml file that includes all model parameters.",
        default='extendedcobey_200428.yaml'
    )

    parser.add_argument(
        "-rl",
        "--running_location",
        type=str,
        help="Location where the simulation is being run.",
        choices=["Local", "NUCLUSTER"],
        default="Local"
    )
    parser.add_argument(
        "-r",
        "--region",
        type=str,
        help="Region on which to run simulation. E.g. 'IL'",
        default='IL'
    )
    parser.add_argument(
        "-c",
        "--experiment_config",
        type=str,
        help=("Config file (in YAML) containing the parameters to override the default config. "
              "This file should have the same structure as the default config. "
              "example: ./experiment_configs/sample_experiment.yaml "),
        default='spatial_EMS_experiment.yaml'
    )

    parser.add_argument(
        "-e",
        "--emodl_template",
        type=str,
        help="Template emodl file to use",
        default="extendedmodel_EMS.emodl"
    )

    parser.add_argument(
        "-load",
        "--csv_name_load",
        type=str,
        help="Name of sampled_parameters.csv to read in, if none parameters are read from config files",
        default=None
    )

    parser.add_argument(
        "-save",
        "--csv_name_save",
        type=str,
        help="Name of sampled_parameters.csv to save",
        default='sampled_parameters.csv'
    )

    parser.add_argument(
        "-param",
        "--param_dic",
        type=json.loads,
        help="Dictionary for single parameter change, for more changes, edit the py file, example:  {\"capacity_multiplier\":\"0.5\"}",
        default={}
    )

    parser.add_argument(
        "-combo",
        "--csv_name_combo",
        type=str,
        help="Name of csv file with parameters to add to main sampled parameters",
        default=None
    )

    parser.add_argument(
        "-n",
        "--nsamples",
        type=str,
        help="If specified overwrites the number of samples defined in the masterconfig, or used to subset excisting parameter csv file",
        default=None
    )

    return parser.parse_args()


def get_full_factorial_df(df, column_name, values):
    dfs = []
    for value in values:
        df_copy = df.copy()
        df_copy[column_name] = value
        dfs.append(df_copy)
    result = pd.concat(dfs, ignore_index=True)
    return result


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
    df = get_full_factorial_df(df, "Ki", Kivalues)

    # Time-varying parameters for each start date.
    dfs = []
    for start_date in start_dates:
        df_copy = df.copy()
        df_copy['startdate'] = start_date
        df_copy = add_parameters(df_copy, "time_parameters", config, region, age_bins)
        df_copy = add_computed_parameters(df_copy)
        dfs.append(df_copy)

    result = pd.concat(dfs, ignore_index=True)
    result["sample_num"] = range(1, len(result) + 1)

    return result


def get_experiment_config(experiment_config_file):
    config = yaml.load(open(os.path.join('./experiment_configs', master_config)), Loader=yamlordereddictloader.Loader)
    yaml_file = open(os.path.join('./experiment_configs', experiment_config_file))
    expt_config = yaml.safe_load(yaml_file)
    for param_type, updated_params in expt_config.items():
        if not config[param_type]:
            config[param_type] = {}
        if updated_params:
            config[param_type].update(updated_params)
    return config


def get_parameters(from_configs=True, sub_samples=None, sample_csv_name='sampled_parameters.csv'):
    if from_configs:
        experiment_config = get_experiment_config(exp_config)
        experiment_setup_parameters = get_experiment_setup_parameters(experiment_config)
        np.random.seed(experiment_setup_parameters['random_seed'])

        fixed_parameters = get_region_specific_fixed_parameters(experiment_config, region)
        simulation_population = fixed_parameters['populations']
        start_dates = get_start_dates(fixed_parameters['startdate'])
        Kivalues = get_fitted_parameters(experiment_config, region)['Kis']
        age_bins = experiment_setup_parameters.get('age_bins')

        if sub_samples == None:
            sub_samples = experiment_setup_parameters['number_of_samples']
        else:
            sub_samples = int(sub_samples)

        dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population, start_dates=start_dates,
                                           config=experiment_config, age_bins=age_bins, Kivalues=Kivalues,
                                           region=region)

    if not from_configs:
        dfparam = pd.read_csv(os.path.join('./experiment_configs', 'input_csv', sample_csv_name))

        if sub_samples != None:
            dfparam[dfparam['sample_num'] <= sub_samples]

    return dfparam


def change_param(df, param_dic):
    """ Modify a parameter dataframe by replacing excisting parameters or adding new parameters.
    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing all the sampled parameters
    param_dic: str
        Dictionary with parameter name and new value.
        Ideally one one parameter is changed, but multiple parameter can be changed as well.
        Example: param_dic = {'capacity_multiplier': 0.8, 'contact_tracing_stop1': 838}
    """

    dic_old = {}
    for key in param_dic.keys():
        new_val = float(param_dic[key])

        if key in df.columns:
            dic_i = {key: [float(df[key].unique()), param_dic[key]]}
            dic_old = dict(dic_old, **dic_i)

            if df[key][0] == new_val:
                raise ValueError("The parameter value to replace is identical. "
                                 f"Value in df param {df[key][0]} value defined in param_dic {new_val}")
            if len(df[key].unique()) > 1:
                raise ValueError("The parameter to replace holds more than 1 unique value. "
                                 f"Parameter values to replace {len(df[key].unique())}")
            else:
                df[key] = new_val

        else:
            df[key] = new_val
            # print(f"Parameter  {key} was added to the parameter dataframe")

    return dic_old, df


def check_and_save_parameters(df, emodl_template, sample_csv_name):
    """ Given an emodl template file, replaces the placeholder names
    (which are bookended by '@') with the sampled parameter value.
    Parameters
    ----------
    df: pd.DataFrame
        DataFrame containing all the sampled parameters
    emodl_template: str
        File name of the emodl template file
    """
    fin = open(os.path.join(emodl_dir, emodl_template), "rt")
    data = fin.read()
    for col in df.columns:
        data = data.replace(f'@{col}@', str(df.iloc[0][col]))
    data = data.replace('@Ki@', '%.09f' % df['Ki'][0])
    remaining_placeholders = re.findall(r'@\w+@', data)
    if remaining_placeholders:
        raise ValueError("Not all placeholders have been defined in the sample parameters. "
                         f"Remaining placeholders: {remaining_placeholders}")
    fin.close()
    remaining_placeholders = re.findall(r'@\w+@', data)
    if remaining_placeholders:
        raise ValueError("Not all placeholders have been defined in the sample parameters. "
                         f"Remaining placeholders: {remaining_placeholders}")
    else:
        dfparam.to_csv(os.path.join('./experiment_configs', 'input_csv', sample_csv_name), index=False)
        print("All placeholders have been defined in the sample parameters. \n "
              f"File saved in {os.path.join('./experiment_configs', 'input_csv', sample_csv_name)}")


def make_identifier(df):
    """https://stackoverflow.com/a/44294454"""
    str_id = df.apply(lambda x: '_'.join(map(str, x)), axis=1)
    return pd.factorize(str_id)[0]


def gen_combos(csv_base, csv_add):
    """
    Function takes list of csv bases, generates a master
    csv file with all combinations of parameters contained therein.
    Ensure that all parameters have unique names in input files
    and that multiple input files are supplied.
    Function adapted from Reese Richardson 'condensed workflow' for running simulations.
    """

    ## Drop columns from csv_add in csv_base, as being replaced
    csv_base.drop(list(csv_add.columns), axis=1, inplace=True, errors='ignore')

    ## Rename unique scenario identifier
    csv_base = csv_base.rename(columns={"sample_num": "sample_num1"})
    ## Add unique scenario identifier
    csv_add['sample_num2'] = csv_add.reset_index().index

    dfs_list = [''] * (2)
    dfs_list[0] = csv_base.copy()
    dfs_list[1] = csv_add.copy()

    cool_list = np.array(list(itertools.product(dfs_list[0].to_numpy(), dfs_list[1].to_numpy())))
    cool_list = np.array(list(np.concatenate(x) for x in cool_list))

    # Creating a list of columns for use in the final DataFrame...
    master_columns = []
    for df in dfs_list:
        master_columns.extend(np.array(df.columns))

    # Isolating index columns...
    index_columns = []
    for col in master_columns:
        if 'index' in col:
            index_columns.append(col)

    # Writing all data to master DataFrame...
    master_df = pd.DataFrame(data=cool_list, columns=master_columns)

    # Restructuring master DataFrame to bring index columns to front...
    master_df = master_df[
        [c for c in master_df if c in index_columns] + [c for c in master_df if c not in index_columns]]

    ### Generate new unique scen_num
    master_df['sample_num'] = make_identifier(master_df[['sample_num1', 'sample_num2']])
    master_df['scen_num'] = master_df['sample_num']
    return master_df


if __name__ == '__main__':

    args = parse_args()
    master_config = args.masterconfig
    exp_config = args.experiment_config
    region = args.region
    emodl_name = args.emodl_template
    sub_samples = args.nsamples

    _, _, wdir, exe_dir, git_dir = load_box_paths(Location='Local')  # args.running_location
    Location = os.getenv("LOCATION") or args.running_location

    emodl_dir = os.path.join(git_dir, 'emodl')
    cfg_dir = os.path.join(git_dir, 'cfg')
    yaml_dir = os.path.join(git_dir, 'experiment_configs')

    if args.csv_name_load == None:

        dfparam = get_parameters(from_configs=True, sub_samples=sub_samples)

    else:

        dfparam = get_parameters(from_configs=False, sample_csv_name=args.csv_name_load)

    if bool(args.param_dic) and args.csv_name_combo == None:
        dic, dfparam = change_param(df=dfparam, param_dic=args.param_dic)

    if args.csv_name_combo != None:
        dfparam2 = pd.read_csv(os.path.join('./experiment_configs', 'input_csv', args.csv_name_combo))
        dfparam1 = dfparam
        del dfparam
        dfparam = gen_combos(csv_base=dfparam1, csv_add=dfparam2)

    check_and_save_parameters(df=dfparam, emodl_template=emodl_name, sample_csv_name=args.csv_name_save)