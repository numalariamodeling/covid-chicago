from datetime import date, timedelta
import numpy as np

modeltype="spatial_model" # pick from: [extended_mod, extended_orig, simple, spatial_model, age_extended, age_simple]
testMode = True

master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
detection_channel_list = ['detected', 'detected_cumul',  'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul',  'crit_det_cumul']
custom_channel_list = ['detected_cumul', 'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul', 'crit_det_cumul', 'symp_cumul',  'asymp_cumul','hosp_cumul', 'crit_cumul']


first_day = date(2020, 3, 1)

### groupdic parameters
groupdic_filename='county_dic.csv'
grpname ='county'
ngroups=5


#Kivalues = 6.0e-6#[4.45e-6, 6.0e-6] #np.random.uniform(3.23107e-06, 4.7126e-06 , 1)   # [9e-05, 7e-06, 8e-06, 9e-06, 9e-077]



# ###hardcoding params
# ki=4.45e-6
# incubation_pd=6.63
# recovery_rate=16
# waning=180


### uniform distribution from params:


sub_samples= 1

def param_sample():
    speciesS = 360980
    initialAs = np.random.uniform(1, 5)
    incubation_pd = np.random.uniform(4.2, 6.63)
    time_to_hospitalization = np.random.normal(5.9, 2)
    time_to_critical = np.random.normal(5.9, 2)
    time_to_death = np.random.uniform(1, 3)
    recovery_rate = np.random.uniform(6, 16)
    fraction_hospitalized = np.random.uniform(0.1, 5)
    fraction_symptomatic = np.random.uniform(0.5, 0.8)
    fraction_critical = np.random.uniform(0.1, 5)
    reduced_inf_of_det_cases = np.random.uniform(0,1)
    cfr = np.random.uniform(0.008, 0.022)
    d_Sy = np.random.uniform(0.2, 0.3)
    d_H = 1
    d_As = 0
    Ki = np.random.uniform(1e-6, 9e-5)
    return(speciesS,initialAs,incubation_pd,
          time_to_hospitalization,time_to_critical,time_to_death,
          recovery_rate, fraction_hospitalized,fraction_symptomatic,
          fraction_critical, reduced_inf_of_det_cases, cfr,
          d_Sy, d_H, d_As,
          Ki)




# #**** only if group used****
# from emodl_generator_extended import read_group_dictionary
# group_dic= read_group_dictionary(filename='county_dic.csv',grpname ='county', Testmode=True, ngroups=2)
# #*****

# from locale_emodl_generator import generate_locale_emodl, generate_locale_cfg

# generate_locale_emodl(county_dic, param_dic,file_output, verbose=False)

