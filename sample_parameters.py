import numpy as np
import pandas as pd
import subprocess
import os
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta
from load_paths import load_box_paths
from simulation_helpers import *
from runScenarios import *

mpl.rcParams['pdf.fonttype'] = 42

today = date.today()

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

    return result


def get_experiment_config(experiment_config_file):
    config = yaml.load(open(os.path.join('./experiment_configs', master_config)), Loader=yamlordereddictloader.Loader)
    yaml_file = open(os.path.join('./experiment_configs',experiment_config_file))
    expt_config = yaml.safe_load(yaml_file)
    for param_type, updated_params in expt_config.items():
        if not config[param_type]:
            config[param_type] = {}
        if updated_params:
            config[param_type].update(updated_params)
    return config


def get_parameters_from_configs(sub_samples=None):
    experiment_config = get_experiment_config(exp_config)
    experiment_setup_parameters = get_experiment_setup_parameters(experiment_config)
    np.random.seed(experiment_setup_parameters['random_seed'])

    fixed_parameters = get_region_specific_fixed_parameters(experiment_config, region)
    simulation_population = fixed_parameters['populations']
    start_dates = get_start_dates(fixed_parameters['startdate'])
    Kivalues = get_fitted_parameters(experiment_config, region)['Kis']
    age_bins = experiment_setup_parameters.get('age_bins')

    if sub_samples == None :
        sub_samples = experiment_setup_parameters['number_of_samples']

    dfparam = generateParameterSamples(samples=sub_samples, pop=simulation_population, start_dates=start_dates,
                                       config=experiment_config, age_bins=age_bins, Kivalues=Kivalues, region=region)
    return dfparam


def check_and_save_parameters(df, emodl_template,sample_csv_name):
    """ Given an emodl template file, replaces the placeholder names
    (which are bookended by '@') with the sampled parameter value.
    This is saved as a (temporary) emodl file to be used in simulation runs.

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
    else :
        dfparam.to_csv(os.path.join('./experiment_configs', 'input_csv', sample_csv_name), index=False)
        print("All placeholders have been defined in the sample parameters. \n "
              f"File saved in {os.path.join('./experiment_configs', 'input_csv', sample_csv_name)}")




if __name__ == '__main__':
    
    args = parse_args()
    master_config =  args.masterconfig # "extendedcobey_200428.yaml"
    exp_config = args.experiment_config  # "spatial_EMS_experiment.yaml"  #args.experiment_config
    region = args.region #"IL"
    modelname  = args.emodl_template   #"extendedmodel_EMS.emodl"

    _, _, wdir, exe_dir, git_dir = load_box_paths(Location='Local') #args.running_location
    Location = os.getenv("LOCATION") or args.running_location

    emodl_dir = os.path.join(git_dir, 'emodl')
    cfg_dir = os.path.join(git_dir, 'cfg')
    yaml_dir = os.path.join(git_dir, 'experiment_configs')

    dfparam = get_parameters_from_configs()


    check_and_save_parameters(df=dfparam, emodl_template=modelname, sample_csv_name ="sample_parameters.csv")





