from datetime import date, timedelta
import numpy as np

#modeltype="" # pick from: [extended_mod, extended_orig, simple, spatial, age]
testMode = True

master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
detection_channel_list = ['detected', 'detected_cumul',  'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul',  'crit_det_cumul']
custom_channel_list = ['detected_cumul', 'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul', 'crit_det_cumul', 'symp_cumul',  'asymp_cumul','hosp_cumul', 'crit_cumul']


first_day = date(2020, 3, 1)

### groupdic parameters
groupdic_filename='county_dic.csv'
grpname ='county'
ngroups=2


Kivalues = [4.45e-6, 6.0e-6] #np.random.uniform(3.23107e-06, 4.7126e-06 , 1)   # [9e-05, 7e-06, 8e-06, 9e-06, 9e-077]





# #**** only if group used****
# from emodl_generator_extended import read_group_dictionary
# group_dic= read_group_dictionary(filename='county_dic.csv',grpname ='county', Testmode=True, ngroups=2)
# #*****

# from locale_emodl_generator import generate_locale_emodl, generate_locale_cfg

# generate_locale_emodl(county_dic, param_dic,file_output, verbose=False)

