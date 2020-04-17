import os
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('../')
from load_paths import load_box_paths
import matplotlib as mpl
import matplotlib.dates as mdates
from datetime import date, timedelta, datetime
import seaborn as sns
import yaml
from processing_helpers import *
from simulation_setup import *
from data_comparison import load_sim_data


mpl.rcParams['pdf.fonttype'] = 42
today = datetime.today()
DEFAULT_CONFIG = './extendedcobey.yaml'

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

def get_experiment_config(experiment_config_file):
    #config = yaml.load(open(DEFAULT_CONFIG), Loader=yaml.FullLoader)
    config = yaml.load(open(os.path.join(git_dir, DEFAULT_CONFIG)), Loader=yaml.FullLoader)
    #yaml_file = open(experiment_config_file)
    yaml_file = open(os.path.join(git_dir, experiment_config_file))
    expt_config = yaml.load(yaml_file, Loader=yaml.FullLoader)
    for param_type, updated_params in expt_config.items():
        if updated_params:
            config[param_type].update(updated_params)
    return config


def get_fixed_parameters(experiment_config, region):
    fixed = experiment_config['fixed_parameters']
    return {param: fixed[param][region] for param in fixed}

if __name__ == '__main__' :

    exp_name = '20200416_EMS_4_mr_run4'

    region = 'EMS_4'  # region = args.region

    experiment_config = "./extendedcobey.yaml"
    experiment_config = get_experiment_config(experiment_config)
    fixed_parameters = get_fixed_parameters(experiment_config, region)

    first_day = fixed_parameters['startdate'] # date(2020, 2, 28)

    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    df = load_sim_data(exp_name)

    channels = ['infected', 'deaths', 'hospitalized', 'critical', 'ventilators']
    df['ventilators'] = df['critical']*0.8

    fig = plt.figure(figsize=(8,12))
    fig.subplots_adjust(right=0.97, wspace=0.2, left=0.07, hspace=0.15)
    palette = sns.color_palette('Set1', len(channels))

    adf = pd.DataFrame()
    for c, channel in enumerate(channels) :
        ax = fig.add_subplot(4,2,c+1)
        mdf = df.groupby('time')[channel].agg([CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75]).reset_index()
        mdf['date'] = mdf['time'].apply(lambda x : first_day + timedelta(days=int(x)))

        ax.plot(mdf['date'], mdf['CI_50'], color=palette[c])
        ax.fill_between(mdf['date'].values, mdf['CI_2pt5'], mdf['CI_97pt5'],
                        color=palette[c], linewidth=0, alpha=0.2)
        ax.fill_between(mdf['date'].values, mdf['CI_25'], mdf['CI_75'],
                        color=palette[c], linewidth=0, alpha=0.4)
        ax.set_title(channel, y=0.85)
        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())

        mdf = mdf.rename(columns={'CI_50' : '%s_median' % channel,
                                  'CI_2pt5' : '%s_95CI_lower' % channel,
                                  'CI_97pt5' : '%s_95CI_upper' % channel})
        mdf = mdf[mdf['time'] >= 22]
        del mdf['time']
        del mdf['CI_25']
        del mdf['CI_75']
        if adf.empty :
            adf = mdf
        else :
            adf = pd.merge(left=adf, right=mdf, on='date')
    adf.to_csv(os.path.join(sim_output_path, 'projection_for_civis.csv'), index=False)
    plt.savefig(os.path.join(sim_output_path, 'projection_for_civis.png'))
    plt.savefig(os.path.join(sim_output_path, 'projection_for_civis.pdf'), format='PDF')
    plt.show()

