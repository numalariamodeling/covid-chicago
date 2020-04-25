import os
import subprocess
from load_paths import load_box_paths
datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

## directories
emodl_dir = os.path.join(git_dir,  'simple_model', 'emodl')
cfg_dir = os.path.join(git_dir,  'simple_model', 'cfg')
temp_dir = os.path.join(git_dir,  'simple_model', '_temp')
if not os.path.exists(temp_dir):
    os.makedirs(os.path.join(temp_dir ))

# Selected range values from SEIR Parameter Estimates.xlsx
# Need to update to run for sample distributions, rather than discrete values
initial_infect = [1,5,10]
Ki = [0.0009, 0.05, 0.32]
incubation_pd = [6.63, 4.2, 12.4]
recovery_rate = [6,13, 16 ]

def runExp_singleParamChange(param, paramname ) :

    # param = Ki
    # paramname = "Ki"
    for i in enumerate(param) :
        print(i)
        fin = open(os.path.join(emodl_dir , "simplemodel_covid.emodl"), "rt")
        data = fin.read()
        if(paramname ==  "initial_infect") : data = data.replace('(species I 10)', '(species I ' + str(i[1]) +')')
        if (paramname == "Ki") : data = data.replace('(param Ki 0.319)', '(param Ki '  + str(i[1]) +')')
        if (paramname == "incubation_pd") : data = data.replace('(param incubation_pd 6.63)', '(param incubation_pd ' + str(i[1]) +')')
        if (paramname == "recovery_rate") :data = data.replace('(param recovery_rate 16)', '(param recovery_rate '  + str(i[1]) +')')
        fin.close()
        fin = open(os.path.join(temp_dir, "simplemodel_covid_i.emodl"), "wt")
        fin.write(data)
        fin.close()
        # adjust simplemodel.cfg file as well
        fin = open(os.path.join(cfg_dir,  'simple_model',"simplemodel.cfg"), "rt")
        data_cfg = fin.read()
        data_cfg = data_cfg.replace('trajectories', 'trajectories_' + paramname + '_' + str(i[1]) )
        fin.close()
        fin = open(os.path.join(temp_dir,  "simplemodel_i.cfg"), "wt")
        fin.write(data_cfg)
        fin.close()
        file = open('runModel_i.bat', 'w')
        file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(temp_dir,   "simplemodel_i.cfg") +
                   '"' + ' -m ' + '"' + os.path.join( temp_dir,  "simplemodel_covid_i.emodl", ) + '"')
        file.close()
        subprocess.call([r'runModel_i.bat'])


runExp_singleParamChange(initial_infect,"initial_infect" )
runExp_singleParamChange(Ki ,"Ki " )
runExp_singleParamChange(incubation_pd,"incubation_pd" )
runExp_singleParamChange(recovery_rate,"recovery_rate" )