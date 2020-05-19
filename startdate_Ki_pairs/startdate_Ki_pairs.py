import os
import pandas as pd
import sys
sys.path.append('../')
from load_paths import load_box_paths
from simulation_helpers import writeTxt

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

input_dir  = os.path.join(projectpath, "parameter_estimates_by_EMS/best_parameter_sheets/")
output_dir = os.path.join(git_dir, "startdate_Ki_pairs/")
config_dir = os.path.join(git_dir, "experiment_configs/")


""" 
Latest fit (no testDelay model)
EMS : [Ki, Ki_red]
Note, in the fitting Ki_red corresponds to Ki_red3, as 1 and 2 were fixed
"""
EMS_fit = {1: [0.589, 0.220],
          2: [0.654, 0.152],
          3: [0.373, 0.210],
          4: [0.571, 0.163],
          5: [0.501, 0.195],
          6: [0.373, 0.210],
          7: [0.714, 0.122],
          8: [0.897, 0.100],
          9: [0.857, 0.120],
          10: [0.754, 0.118],
          11: [1.01, 0.100]}

""" 
Select number of Ki values drawn (full factorial for each starting date)
"""
n_Ki = "3"

""" 
constrain in variation around Ki_red3 (which  will stay fixed)
otherwise the range in startdate and Ki is too huge
"""
constrain = 0.03

startdate_ranges = ""
Ki_ranges =""
linebreak =""
for ems_nr in range(1,11) :
    if Ki_ranges != "" :
        linebreak = "\n"


    fname = 'best_parameter_ranges_ems'+ str(ems_nr)+'.csv'
    df = pd.read_csv(os.path.join(input_dir, fname))

    #### Constrain Ki_red (which will not be varied)
    ems_lo = EMS_fit[ems_nr][1]  - constrain
    ems_up = EMS_fit[ems_nr][1] + constrain

    ems1 = df[ (df['Ki_red'] > ems_lo) &  (df['Ki_red'] < ems_up) ]
    startdate_range_i = [min(ems1['Start_date']), max(ems1['Start_date'])]
    startdate_ranges = startdate_ranges + linebreak + "    'EMS_"+str(ems_nr)+"': " + str.replace(str(startdate_range_i), "'", "")

    Ki_range_i = [min(ems1['Ki']), max(ems1['Ki'])]

    Ki_str_I  = linebreak + "   'EMS_"+str(ems_nr)+"':\n     np: linspace \n     "
    Ki_str_II = "function_kwargs: {" + """'start': {Ki_lo}, 'stop': {Ki_up}""".format(Ki_lo=Ki_range_i[0], Ki_up = Ki_range_i[1]) +", 'num': "+n_Ki+"}"
    Ki_ranges = Ki_ranges  + Ki_str_I + Ki_str_II

## Write txt file
txt_str = startdate_ranges + "\n\n\n" + Ki_ranges
writeTxt(txtdir=output_dir, filename= "date_ki_pairs_"+str(constrain)+".txt" , textstring = txt_str)

### Create yaml file from template

fin = open(os.path.join(output_dir, "extendedcobey_200428_startdateKipair_template.yaml"), "rt")
yaml_template = fin.read()

yaml_template = yaml_template.replace('[STARTDATES]', startdate_ranges)
yaml_template = yaml_template.replace('[KIVALUES]', Ki_ranges)
fin.close()
fin = open(os.path.join(config_dir, "extendedcobey_200428_startdateKipair.yaml"), "wt")
fin.write(yaml_template)
fin.close()
