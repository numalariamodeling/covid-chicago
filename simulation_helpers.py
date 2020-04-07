import os
import subprocess
import shutil

def runExp(trajectories_dir, Location = 'Local' ):
    if Location =='Local' :
        p = os.path.join(trajectories_dir,  'runSimulations.bat')
        subprocess.call([p])
    if Location =='NUCLUSTER' :
        print('please submit sbatch runSimulations.sh in the terminal')


def reprocess(trajectories_dir, input_fname='trajectories.csv', output_fname=None):
    fname = os.path.join(trajectories_dir, input_fname)
    row_df = pd.read_csv(fname, skiprows=1)
    df = row_df.set_index('sampletimes').transpose()
    num_channels = len([x for x in df.columns.values if '{0}' in x])
    num_samples = int((len(row_df)) / num_channels)

    df = df.reset_index(drop=False)
    df = df.rename(columns={'index': 'time'})
    df['time'] = df['time'].astype(float)

    adf = pd.DataFrame()
    for sample_num in range(num_samples):
        channels = [x for x in df.columns.values if '{%d}' % sample_num in x]
        sdf = df[['time'] + channels]
        sdf = sdf.rename(columns={
            x: x.split('{')[0] for x in channels
        })
        sdf['sample_num'] = sample_num
        adf = pd.concat([adf, sdf])

    adf = adf.reset_index()
    del adf['index']
    if output_fname:
        adf.to_csv(os.path.join(temp_exp_dir,output_fname), index=False)
    return adf


def combineTrajectories(Nscenarios, deleteFiles=False):
    scendf = pd.read_csv(os.path.join(temp_exp_dir,"scenarios.csv"))

    df_list = []
    for scen_i in range(Nscenarios):
        input_name = "trajectories_scen" + str(scen_i) + ".csv"
        try:
            df_i = reprocess(input_name)
            df_i['scen_num'] = scen_i
            df_i = df_i.merge(scendf, on=['scen_num','sample_num'])
            df_list.append(df_i)
        except:
            continue

        if deleteFiles == True: os.remove(os.path.join(git_dir, input_name))

    dfc = pd.concat(df_list)
    dfc.to_csv( os.path.join(temp_exp_dir,"trajectoriesDat.csv"), index=False)

    return dfc


def cleanup(delete_temp_dir=True) :
    # Delete simulation model and emodl files
    # But keeps per default the trajectories, better solution, zip folders and copy
    if delete_temp_dir ==True :
        shutil.rmtree(temp_dir, ignore_errors=True)
        print('temp_dir folder deleted')
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


def generateSubmissionFile(scen_num, exp_name):
    file = open(os.path.join(trajectories_dir, 'runSimulations.bat'), 'w')
    file.write("ECHO start" + "\n" + "FOR /L %%i IN (1,1,{}) DO ( {} -c {} -m {})".format(
        str(scen_num),
        os.path.join(exe_dir, "compartments.exe"),
        os.path.join(temp_dir, "model_%%i" + ".cfg"),
        os.path.join(temp_dir, "simulation_%%i" + ".emodl")
    ) + "\n ECHO end")
    file.close()

    # Hardcoded Quest directories for now!
    # additional parameters , ncores, time, queue...
    exp_name_short = exp_name[-20:]
    header = '#!/bin/bash\n#SBATCH -A p30781\n#SBATCH -p short\n#SBATCH -t 04:00:00\n#SBATCH -N 1\n#SBATCH --ntasks-per-node=1'
    jobname = '\n#SBATCH	--job-name="' + exp_name_short + '"'
    array = '\n#SBATCH --array=1-' + str(scen_num)
    email = '\n# SBATCH --mail-user=manuela.runge@northwestern.edu'  ## create input mask or user txt where specified
    emailtype = '\n# SBATCH --mail-type=ALL'
    err = '\n#SBATCH --error=log/arrayJob_%A_%a.err'
    out = '\n#SBATCH --output=log/arrayJob_%A_%a.out'
    module = '\n\nmodule load singularity'
    singularity = '\n\nsingularity exec /software/singularity/images/singwine-v1.img wine /home/mrm9534/Box/NU-malaria-team/projects/binaries/compartments/compartments.exe  -c /home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/' + exp_name + '/simulations/model_${SLURM_ARRAY_TASK_ID}.cfg  -m /home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/' + exp_name + '/simulations/simulation_${SLURM_ARRAY_TASK_ID}.emodl'
    file = open(os.path.join(trajectories_dir, 'runSimulations.sh'), 'w')
    file.write(header + jobname + email + emailtype + array + err + out + module + singularity)
    file.close()

    submit_runSimulations = 'cd /home/mrm9534/Box/NU-malaria-team/projects/covid_chicago/cms_sim/simulation_output/' + exp_name + '/trajectories/\ndos2unix runSimulations.sh\nsbatch runSimulations.sh'
    file = open(os.path.join(temp_exp_dir, 'submit_runSimulations.sh'), 'w')
    file.write(submit_runSimulations)
    file.close()
