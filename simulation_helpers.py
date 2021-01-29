import logging
import os
import subprocess
import shutil
import stat
import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

mpl.rcParams['pdf.fonttype'] = 42
from processing_helpers import CI_50, CI_25, CI_75,CI_2pt5, CI_97pt5

### GE added 04/10/20 to fix "wdir not defined error"
#import sys
#sys.path.append("C:\\Users\\garrett\\Documents\\GitHub\\covid-chicago") #added for the loadpaths for garrett
from load_paths import load_box_paths
datapath, projectpath, WDIR, EXE_DIR, GIT_DIR = load_box_paths()

log = logging.getLogger(__name__)


def DateToTimestep(date, startdate) :
    datediff = date - startdate
    timestep = datediff.days
    return timestep


def TimestepToDate(timesteps, startdate) :
    dates= startdate + pd.Timedelta(timesteps,'days')
    return dates


def get_cms_cmd(exe_dir=EXE_DIR, workdir=None, docker_image=None):
    """Generate the command to invoke the CMS executable

    Cross-platform -- generate the appropriate command on Windows, OS X, or Linux.
    On OS X or Linux, run either via a Docker container which contains CMS,
    or with wine.

    Parameters
    ----------
    exe_dir : str, optional
        The directory of your `compartments.exe` executable.
        Not needed if running via Docker.
    workdir : str, optional
        Only needed for non-Windows systems. The working directory, which
        must contain the config file, the emodl file, and the output location.
    docker_image : str, optional
        Only needed for non-Windows systems.
        If provided, generate a run command which invokes this Docker image.
        If not provided, generate a run command which invokes `wine` to run
        `compartments.exe`.

    Returns
    -------
    cmd : str
        A string which can be executed to run CMS
    """

    if sys.platform in ['win32', 'cygwin']:
        log.debug("Generating Windows run command")
        return os.path.join(exe_dir, 'compartments.exe')
    else:
        if docker_image:
            log.debug(f"Generating Docker run command for workdir {workdir}")
            if not workdir:
                raise TypeError("Must provide `workdir` input for running via Docker")
            cmd = f"docker run -v={workdir}:{workdir} {docker_image} -d {workdir}"
        else:
            cmd = f"wine {os.path.join(exe_dir, 'compartments.exe')} -d {workdir}"
        return cmd


def runExp(trajectories_dir, Location = 'Local', submission_script=None ):
    if Location =='Local' :
        log.info("Starting experiment.")
        p = os.path.join(trajectories_dir,  'runSimulations.bat')
        subprocess.call([p])
    if Location =='NUCLUSTER' :
        if submission_script is None:
            submission_script = 'submit_runSimulations.sh'
        p = os.path.join(trajectories_dir, submission_script)
        subprocess.call(['sh',p])


def reprocess(trajectories_dir, temp_exp_dir, input_fname='trajectories.csv', output_fname=None):
    fname = os.path.join(trajectories_dir, input_fname)
    row_df = pd.read_csv(fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    run_time = len([x for x in df.columns.values if '{0}' in x])
    num_runs = int((len(row_df)) / run_time)

    df = df.reset_index(drop=False)
    df = df.rename(columns={'index': 'time'})
    df['time'] = df['time'].astype(float)

    adf = pd.DataFrame()
    for run_num in range(num_runs):
        channels = [x for x in df.columns.values if '{%d}' % run_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x: x.split('{')[0] for x in channels
        })
        sdf['run_num'] = run_num
        adf = pd.concat([adf, sdf])

    adf = adf.reset_index()
    del adf['index']
    if output_fname:
        adf.to_csv(os.path.join(temp_exp_dir,output_fname), index=False)
    return adf


def combineTrajectories(Nscenarios,trajectories_dir, temp_exp_dir, deleteFiles=False,addSamples = True, git_dir=GIT_DIR):
    sampledf = pd.read_csv(os.path.join(temp_exp_dir,"sampled_parameters.csv"))
    if addSamples == False:
        sampledf = sampledf[["scen_num","sample_num","startdate"]]
    df_list = []
    for scen_i in range(Nscenarios+1):
        input_name = "trajectories_scen" + str(scen_i) + ".csv"
        try:
            df_i = reprocess(trajectories_dir=trajectories_dir, temp_exp_dir=temp_exp_dir, input_fname=input_name)
            df_i['scen_num'] = scen_i
            df_i = df_i.merge(sampledf, on=['scen_num'])
            df_list.append(df_i)
        except:
            continue

        if deleteFiles == True: os.remove(os.path.join(git_dir, input_name))

    dfc = pd.concat(df_list)
    dfc.to_csv( os.path.join(temp_exp_dir,"trajectoriesDat.csv"), index=False, date_format='%Y-%m-%d')

    nscenarios = sampledf['scen_num'].max()
    nscenarios_processed = len(dfc['scen_num'].unique())
    trackScen = "Number of scenarios processed n= " + str(nscenarios_processed) + " out of total N= " + str(nscenarios) + " (" + str(nscenarios_processed/ nscenarios)+ " %)"
    writeTxt(temp_exp_dir, "Simulation_report.txt" ,trackScen)

    return dfc


def cleanup(temp_dir, temp_exp_dir, sim_output_path,plot_path, delete_temp_dir=True) :
    # Delete simulation model and emodl files
    # But keeps per default the trajectories, better solution, zip folders and copy
    if delete_temp_dir:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print('temp_dir folder deleted')
    if not os.path.exists(sim_output_path):
        shutil.copytree(temp_exp_dir, sim_output_path)
        if not os.path.exists(plot_path):
            os.makedirs(plot_path)
        # Delete files after being copied to the project folder
        if os.path.exists(sim_output_path):
            shutil.rmtree(temp_exp_dir, ignore_errors=True)
        elif not os.path.exists(sim_output_path):
            print('Sim_output_path does not exists')


def writeTxt(txtdir, filename, textstring) :
    file = open(os.path.join(txtdir, filename), 'w')
    file.write(textstring)
    file.close()

def get_process_dict():
    process_dict = {'0_runCombineAndTrimTrajectories':'combine_and_trim.py',
                    '0_locale_age_postprocessing': 'locale_age_postprocessing.py',
                    '1_runTraceSelection': 'trace_selection.py',
                    '2_runDataComparison': 'data_comparison.py',
                    '3_runProcessTrajectories': 'process_for_civis_EMSgrp.py',
                    '4_runRtEstimation': 'estimate_Rt_forCivisOutputs.py',
                    '5_runOverflowProbabilities': 'overflow_probabilities.py',
                    '6_runPrevalenceIFR': 'plot_prevalence.py',
                    '7_runICUnonICU': 'plot_by_param_ICU_nonICU.py',
                    '8_runHospICUDeathsForecast': 'hosp_icu_deaths_forecast_plotter.py',
                    '9_runCopyDeliverables': 'NUcivis_filecopy.py',
                    '10_runIterationComparison': 'iteration_comparison.py',
                    '11_runCleanUpAndZip': 'cleanup_and_zip_simFiles.py'}
    return process_dict


def generateSubmissionFile(scen_num, exp_name, experiment_config, trajectories_dir, temp_dir, temp_exp_dir,sim_output_path,
                           exe_dir=EXE_DIR, docker_image="cms", git_dir=GIT_DIR, wdir=WDIR):


    process_dict = get_process_dict()

    fname = f'runSimulations.bat'
    log.debug(f"Generating submission file {fname}")
    if sys.platform not in ["win32", "cygwin"]:
        file = open(os.path.join(trajectories_dir, fname), 'w')
        # If this is OSX or Linux, mark the file as executable and
        # write a bash script
        os.chmod(fname, stat.S_IXUSR | stat.S_IWUSR | stat.S_IRUSR)
        cfg_fname = os.path.join(temp_dir, 'model_$i.cfg')
        emodl_fname = os.path.join(temp_dir, 'simulation_$i.emodl')
        file.write(f"""#!/bin/bash
echo start
for i in {{1..{scen_num}}} 
  do
    {get_cms_cmd(exe_dir, temp_exp_dir, docker_image)} -c "{cfg_fname}" -m "{emodl_fname}"
  done
echo end""")
    else:
        file = open(os.path.join(trajectories_dir, fname), 'w')
        file.write('ECHO start' + '\n' + 'FOR /L %%i IN (1,1,{}) DO ( "{}" -c "{}" -m "{}") >> "{}/log/log.txt"'.format(
            str(scen_num),
            get_cms_cmd(exe_dir, temp_exp_dir),
            os.path.join(temp_dir, "model_%%i" + ".cfg"),
            os.path.join(temp_dir, "simulation_%%i" + ".emodl"),
            os.path.join(temp_exp_dir)
        ) + "\n ECHO end")


        """ Postprocessing batch files """
        plotters_dir = os.path.join(git_dir, "plotters")

        file = open(os.path.join(temp_exp_dir, 'bat', f'{list(process_dict.keys())[0]}.bat'), 'w')
        file.write(f'cd {git_dir} \n python {list(process_dict.values())[0]} --exp_name "{exp_name}" \n')

        file = open(os.path.join(temp_exp_dir, 'bat', f'{list(process_dict.keys())[1]}.bat'), 'w')
        file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[1]} --stem "{exp_name}" >> "{sim_output_path}/log/{list(process_dict.keys())[1]}.txt" \n')

        file = open(os.path.join(temp_exp_dir, 'bat', f'{list(process_dict.keys())[2]}.bat'), 'w')
        file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[2]} --stem "{exp_name}" --plot >> "{sim_output_path}/log/{list(process_dict.keys())[2]}.txt" \n')

        fname = list(process_dict.values())[3]
        if "spatial_EMS" in experiment_config:
            fname = 'data_comparison_spatial.py'
        file = open(os.path.join(temp_exp_dir, 'bat', f'{list(process_dict.keys())[3]}.bat'), 'w')
        file.write(f'cd {plotters_dir} \n python {fname} --stem "{exp_name}" >> "{sim_output_path}/log/{list(process_dict.keys())[3]}.txt"  \n')

        if "spatial_EMS" in experiment_config :

            file = open(os.path.join(temp_exp_dir,'bat', f'{list(process_dict.keys())[4]}.bat'), 'w')
            file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[4]} --stem "{exp_name}" >> "{sim_output_path}/log/{list(process_dict.keys())[4]}.txt" \n')

            file = open(os.path.join(temp_exp_dir,'bat', f'{list(process_dict.keys())[5]}.bat'), 'w')
            file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[5]} --stem "{exp_name}"  >> "{sim_output_path}/log/{list(process_dict.keys())[5]}.txt" \n')

            file = open(os.path.join(temp_exp_dir,'bat', f'{list(process_dict.keys())[6]}.bat'), 'w')
            file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[6]} --stem "{exp_name}"  >> "{sim_output_path}/log/{list(process_dict.keys())[6]}.txt" \n')

            file = open(os.path.join(temp_exp_dir,'bat', f'{list(process_dict.keys())[7]}.bat'), 'w')
            file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[7]} --stem "{exp_name}"  >> "{sim_output_path}/log/{list(process_dict.keys())[7]}.txt" \n')

            file = open(os.path.join(temp_exp_dir,'bat', f'{list(process_dict.keys())[8]}.bat'), 'w')
            file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[8]} --exp_names "{exp_name}"  >> "{sim_output_path}/log/{list(process_dict.keys())[8]}.txt" \n')

            file = open(os.path.join(temp_exp_dir,'bat', f'{list(process_dict.keys())[9]}.bat'), 'w')
            file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[9]} --stem "{exp_name}"  >> "{sim_output_path}/log/{list(process_dict.keys())[9]}.txt" \n')

            file = open(os.path.join(temp_exp_dir,'bat', f'{list(process_dict.keys())[10]}.bat'), 'w')
            file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[10]}  "{exp_name}"  >> "{sim_output_path}/log/{list(process_dict.keys())[10]}.txt" \n')

            file = open(os.path.join(temp_exp_dir,'bat', f'{list(process_dict.keys())[11]}.bat'), 'w')
            file.write(f'cd {plotters_dir} \n python {list(process_dict.values())[11]}  "{exp_name}"  >> "{sim_output_path}/log/{list(process_dict.keys())[11]}.txt" \n')

            file = open(os.path.join(temp_exp_dir,'bat', f'{list(process_dict.keys())[12]}.bat'), 'w')
            file.write(f'cd { os.path.join(git_dir, "nucluster")} \n python {list(process_dict.values())[12]}  --stem "{exp_name}" --del_trajectories --zip_dir  >> "{sim_output_path}/log/{list(process_dict.keys())[12]}.txt" \n')


def generateSubmissionFile_quest(scen_num, exp_name, experiment_config, trajectories_dir, git_dir, temp_exp_dir,exe_dir,sim_output_path) :
    # Generic shell submission script that should run for all having access to  projects/p30781
    # submit_runSimulations.sh

    process_dict = get_process_dict()

    exp_name_short = exp_name[-20:]
    header = '#!/bin/bash\n' \
             '#SBATCH -A p30781\n' \
             '#SBATCH -p short\n' \
             '#SBATCH -t 00:30:00\n' \
             '#SBATCH -N 1\n' \
             '#SBATCH --ntasks-per-node=1\n' \
             '#SBATCH --mem=18G'
    header_post = '#!/bin/bash\n'\
                  '#SBATCH -A p30781\n' \
                  '#SBATCH -p short\n' \
                  '#SBATCH -t 02:00:00\n' \
                  '#SBATCH -N 1\n' \
                  '#SBATCH --ntasks-per-node=1\n' \
                  '#SBATCH --mem=64G'
    jobname = f'\n#SBATCH --job-name="{exp_name_short}"'
    array = f'\n#SBATCH --array=1-{str(scen_num)}'
    err = '\n#SBATCH --error=log/arrayJob_%A_%a.err'
    out = '\n#SBATCH --output=log/arrayJob_%A_%a.out'
    module = '\n\nmodule load singularity'
    slurmID = '${SLURM_ARRAY_TASK_ID}'
    singularity = '\n\nsingularity exec -B /projects:/projects/ /software/singularity/images/singwine-v1.img wine ' \
                  f'{exe_dir}/compartments.exe ' \
                  f'-c {git_dir}/_temp/{exp_name}/simulations/model_{slurmID}.cfg ' \
                  f'-m {git_dir}/_temp/{exp_name}/simulations/simulation_{slurmID}.emodl'
    file = open(os.path.join(trajectories_dir, 'runSimulations.sh'), 'w')
    file.write(header + jobname + array + err + out + module + singularity)
    file.close()

    plotters_dir = os.path.join(git_dir, "plotters")
    pymodule = '\n\nmodule purge all\nmodule load python/anaconda3.6\nsource activate /projects/p30781/anaconda3/envs/team-test-py37\n'

    """
    Use this batch files for postprocessing multiple steps
    """
    fname = list(process_dict.values())[3]
    if "spatial_EMS" in experiment_config:
        fname = 'data_comparison_spatial.py'

    pycommand = f'\ncd {git_dir}\npython {list(process_dict.values())[0]}  --exp_name "{exp_name}" --Location "NUCLUSTER" '
    file = open(os.path.join(temp_exp_dir, f'run_postprocessing.sh'), 'w')
    file.write(header_post + jobname + err + out + pymodule + pycommand)
    file.write(f'\n\ncd {git_dir}/nucluster \npython {git_dir}/nucluster/cleanup.py --stem "{exp_name}" --delete_simsfiles "True"')
    file.write(f'\n\ncd {plotters_dir} \npython {plotters_dir}/{fname} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[3]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[4]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[5]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[6]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[7]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\n\ncd {git_dir}/nucluster \npython {git_dir}/nucluster/{list(process_dict.values())[12]} --stem "{exp_name}" --zip_dir --Location "NUCLUSTER"')
    file.close()


    pycommand = f'\ncd {git_dir}\npython {list(process_dict.values())[0]}  --exp_name "{exp_name}" --Location "NUCLUSTER" '
    file = open(os.path.join(temp_exp_dir, f'run_postprocessing_with_trace_selection.sh'), 'w')
    file.write(header_post + jobname + err + out + pymodule + pycommand)
    file.write(f'\n\ncd {git_dir}/nucluster \npython {git_dir}/nucluster/cleanup.py --stem "{exp_name}" --delete_simsfiles "True"')
    file.write(f'\n\ncd {plotters_dir} \npython {plotters_dir}/{fname} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[2]} --stem "{exp_name}" --Location "NUCLUSTER" --plot')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[3]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[4]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[5]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[6]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[7]} --stem "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[8]} --exp_names "{exp_name}" --Location "NUCLUSTER"')
    file.write(f'\npython {plotters_dir}/{list(process_dict.values())[9]} --stem "{exp_name}" --Location "NUCLUSTER"')
    #file.write(f'\npython {plotters_dir}/{list(process_dict.values())[10]} "{exp_name}"')
    #file.write(f'\npython {plotters_dir}/{list(process_dict.values())[11]} "{exp_name}"')
    file.write(f'\n\ncd {git_dir}/nucluster \npython {git_dir}/nucluster/{list(process_dict.values())[12]} --stem "{exp_name}" --zip_dir --Location "NUCLUSTER"')
    file.close()

    """
    Single shell files for single job submission 
    (to do set up dependencies)
    """
    pycommand = f'\ncd {git_dir}\npython {list(process_dict.values())[0]}  --exp_name "{exp_name}" --Location "NUCLUSTER" '
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[0]}.sh'), 'w')
    file.write(header_post + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {git_dir}/nucluster \npython {git_dir}/nucluster/cleanup.py --stem "{exp_name}"' \
                ' --delete_simsfiles "True"'
    file = open(os.path.join(temp_exp_dir,'sh', '0_cleanupSimulations.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir} \npython {plotters_dir}/{list(process_dict.values())[1]} --stem "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[1]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir} \npython {plotters_dir}/{list(process_dict.values())[2]} --stem "{exp_name}" --Location "NUCLUSTER" --plot'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[2]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir} \npython {plotters_dir}/{fname} --stem "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir,'sh', f'{list(process_dict.keys())[3]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir} \npython {plotters_dir}/{list(process_dict.values())[4]} --stem "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[4]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir}\npython {plotters_dir}/{list(process_dict.values())[5]} --stem "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir,  'sh',f'{list(process_dict.keys())[5]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir}\npython {plotters_dir}/{list(process_dict.values())[6]} --stem "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[6]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir}\npython {plotters_dir}/{list(process_dict.values())[7]} --stem "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[7]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir}\npython {plotters_dir}/{list(process_dict.values())[8]} --stem "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[8]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir}\npython {plotters_dir}/{list(process_dict.values())[9]} --stem "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[9]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir}\npython {plotters_dir}/{list(process_dict.values())[10]} "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[10]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {plotters_dir}\npython {plotters_dir}/{list(process_dict.values())[11]} "{exp_name}" --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[11]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    pycommand = f'cd {git_dir}/nucluster \npython {git_dir}/nucluster/{list(process_dict.values())[12]} --stem "{exp_name}" --zip_dir  --Location "NUCLUSTER"'
    file = open(os.path.join(temp_exp_dir, 'sh', f'{list(process_dict.keys())[12]}.sh'), 'w')
    file.write(header + jobname + err + out + pymodule + pycommand)
    file.close()

    """
    Submit run simultation 
    Start postprocessing using singleton dependency
    """
    submit_runSimulations = f'cd {temp_exp_dir}/trajectories/\ndos2unix runSimulations.sh\nsbatch runSimulations.sh\n'
    submit_combineSimulations = f'cd {temp_exp_dir}/\nsbatch --dependency=singleton run_postprocessing.sh'
    submit_combineSimulations_trace = f'cd {temp_exp_dir}/\nsbatch --dependency=singleton run_postprocessing_with_trace_selection.sh'
    file = open(os.path.join(temp_exp_dir, 'submit_runSimulations.sh'), 'w')
    file.write(submit_runSimulations)
    file.write(submit_combineSimulations)
    file.close()

    file = open(os.path.join(temp_exp_dir, 'submit_runSimulations_with_trace_selection.sh'), 'w')
    file.write(submit_runSimulations)
    file.write(submit_combineSimulations_trace)
    file.close()


    """
    Draft for setting up job dependencies 
    """
    #file = open(os.path.join(temp_exp_dir,'submit_runPostprocessing_test2.sh'), 'w')
    #file.write(f'\n\n#cd {temp_exp_dir}'
    #           '\n\n#Submit after simulation are finished using job id\n#sbatch --dependency=afterok:<jobid> combineSimulations.sh'
    #           '\n\n#Submit after combineSimulations using job id\n#sbatch --dependency=afterany:<jobid> cleanupSimulations.sh'
    #           '\n\n#Submit after cleanupSimulations using job id\n#sbatch --dependency=afterany:<jobid> compareToData.sh'
    #           '\n\n#Submit after cleanupSimulations using job id\n#sbatch --dependency=afterany:<jobid> processForCivis.sh')
    #file.close()


def makeExperimentFolder(exp_name, emodl_dir, emodlname, cfg_dir, cfg_file, yaml_dir, DEFAULT_CONFIG, experiment_config, temp_exp_dir=None,
                         wdir=WDIR, git_dir=GIT_DIR): ## GE 04/10/20 added exp_name, emodl_dir,emodlname, cfg_dir here to fix exp_name not defined error
    sim_output_path = os.path.join(wdir, 'simulation_output', exp_name)
    plot_path = sim_output_path
    # Create temporary folder for the simulation files
    # currently allowing to run only 1 experiment at a time locally
    if temp_exp_dir == None :
        temp_exp_dir = os.path.join(git_dir, '_temp', exp_name)
    temp_dir = os.path.join(temp_exp_dir, 'simulations')
    trajectories_dir = os.path.join(temp_exp_dir, 'trajectories')
    if not os.path.exists(os.path.join(git_dir, '_temp')):
        os.makedirs(os.path.join(os.path.join(git_dir, '_temp')))
    if not os.path.exists(temp_exp_dir):
        os.makedirs(temp_exp_dir)
        os.makedirs(temp_dir)
        os.makedirs(trajectories_dir)
        os.makedirs(os.path.join(temp_exp_dir, 'log'))
        os.makedirs(os.path.join(trajectories_dir, 'log'))  # location of log file on quest
        os.makedirs(os.path.join(temp_exp_dir, '_plots'))
        os.makedirs(os.path.join(temp_exp_dir, '_plots','pdf'))
        os.makedirs(os.path.join(temp_exp_dir, 'bat'))
        os.makedirs(os.path.join(temp_exp_dir, 'sh'))
        os.makedirs(os.path.join(temp_exp_dir, 'sh', 'log'))

    ## Copy emodl and cfg file  to experiment folder
    shutil.copyfile(os.path.join(emodl_dir, emodlname), os.path.join(temp_exp_dir, emodlname))
    shutil.copyfile(os.path.join(cfg_dir, cfg_file), os.path.join(temp_exp_dir, cfg_file))
    shutil.copyfile(os.path.join(yaml_dir, experiment_config), os.path.join(temp_exp_dir, experiment_config))
    if DEFAULT_CONFIG != experiment_config :
        shutil.copyfile(os.path.join(yaml_dir, DEFAULT_CONFIG), os.path.join(temp_exp_dir, DEFAULT_CONFIG))

    return temp_dir, temp_exp_dir, trajectories_dir, sim_output_path, plot_path


def runSamplePlot(sim_output_path,plot_path,start_dates,channel_list_name = "master" ):
    # Once the simulations are done
    # number_of_samples*len(Kivalues) == nscen ### to check
    df = pd.read_csv(os.path.join(sim_output_path, 'trajectoriesDat.csv'))
    df.columns = df.columns.str.replace('_All', '')

    if channel_list_name =="master" :
        channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic_mild',
                        'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
    if channel_list_name == "detection":
        channel_list = ['detected', 'detected_cumul', 'asymp_det_cumul', 'hosp_det_cumul']
    if channel_list_name == "custom":
        channel_list = ['detected_cumul', 'symp_severe_cumul', 'asymp_det_cumul', 'hosp_det_cumul',
                        'symp_mild_cumul', 'asymp_cumul', 'hosp_cumul', 'crit_cumul']

    # FIXME: Timesteps shouldn't be all relative to start_dates[0],
    #    especially when we have multiple first days.
    sampleplot(df, allchannels=channel_list, start_date=start_dates[0],
               plot_fname=os.path.join(plot_path, f'{channel_list_name}_sample_plot.png'))



def sampleplot(adf, allchannels, start_date, plot_fname=None):
    fig = plt.figure(figsize=(18, 8))
    palette = sns.color_palette('Set1', 10)

    axes = [fig.add_subplot(3, 3, x + 1) for x in range(len(allchannels))]
    fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
    for c, channel in enumerate(allchannels):
        mdf = adf.groupby('time')[channel].agg([np.min, CI_50, CI_2pt5, CI_97pt5, CI_25, CI_75, np.max]).reset_index()
        ax = axes[c]
        dates = [start_date + pd.Timedelta(int(x),'days') for x in mdf['time']]
        ax.plot(dates, mdf['CI_50'], label=channel, color=palette[c])
        ax.fill_between(dates, mdf['CI_2pt5'], mdf['CI_97pt5'],
                        color=palette[c], linewidth=0, alpha=0.2)
        ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                        color=palette[c], linewidth=0, alpha=0.4)
        ax.fill_between(dates, mdf['amin'], mdf['amax'],
                        color=palette[c], linewidth=0, alpha=0.1)

        ax.set_title(channel, y=0.8)

        formatter = mdates.DateFormatter("%m-%d")
        ax.xaxis.set_major_formatter(formatter)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.set_xlim(start_date, )

    if plot_fname:
        log.info(f"Writing plot to {plot_fname}")
        plt.savefig(plot_fname)
    #plt.show()
