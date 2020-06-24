import os
import sys
import re


sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')


def write_N_population(ageList, regionList, pop_dic):
    stringAll = ""
    for age, region in [(x, y) for x in ageList for y in regionList]:
        string1 = """\n(param N_{age}_{region} {age_reg_pop} )""".format(age=age, region=region, age_reg_pop=pop_dic[region][0][age])
        stringAll = stringAll + string1

    string2 = ""
    for age_i in ageList:
        temp_str = "\n(param N_" + age_i + " (+ " + repeat_string_by_grp(fixedstring='N_' + age_i + '_', grpList1=regionList, grpList2=None) + "))"
        string2 = string2 + temp_str

    ### Change order to N_age_region, fixedstring or loop needs to be separated
    #string3 = ""
    #for region_i in regionList:
    #  temp_str = "\n(param N_" + region_i + " (+ " + repeat_string_by_grp(fixedstring='N_' + region_i + '_', grpList1=ageList, grpList2=None) + "))"
    #  string3 = string3 + temp_str

    string4 = "\n(param N_All (+ " + repeat_string_by_grp('N_', ageList, regionList) + "))"

    stringAll = stringAll + "\n" + string2 + "\n"  +  string4 # + string3 + "\n"

    return (stringAll)


def write_Ki_timevents(age, region, import_dic2):

    params_str = """
(time-event time_infection_import @time_infection_import_{region}@ ((As_{age}::{region} {age_reg_import}) (S_{age}::{region} (- S_{age}::{region} {age_reg_import}))))
""".format(age=age, region=region, age_reg_import=import_dic2[region][0][age])
    params_str = params_str.replace("  ", " ")

    return (params_str)

def set_population(age, region, pop_dic, import_dic):
    initial_population_str = """
(species S_{age}::{region} {age_reg_pop})
(species As_{age}::{region} {age_reg_infect})
""".format(age=age,
            region=region,
            age_reg_pop=pop_dic[region][0][age],
            age_reg_infect=import_dic[region][0][age])
    return initial_population_str

def write_species(age, region, expandModel=None):

    species_str = """
(species E_{age}::{region} 0)
(species As_det1_{age}::{region} 0)
(species P_{age}::{region} 0)
(species P_det_{age}::{region} 0)
(species Sym_{age}::{region} 0)
(species Sym_det2_{age}::{region} 0)
(species Sys_{age}::{region} 0)
(species Sys_det3_{age}::{region} 0)
(species H1_{age}::{region} 0)
(species H2_{age}::{region} 0)
(species H3_{age}::{region} 0)
(species H1_det3_{age}::{region} 0)
(species H2_det3_{age}::{region} 0)
(species H3_det3_{age}::{region} 0)
(species C2_{age}::{region} 0)
(species C3_{age}::{region} 0)
(species C2_det3_{age}::{region} 0)
(species C3_det3_{age}::{region} 0)
(species D3_{age}::{region} 0)
(species D3_det3_{age}::{region} 0)
(species RAs_{age}::{region} 0)
(species RAs_det1_{age}::{region} 0)
(species RSym_{age}::{region} 0)
(species RSym_det2_{age}::{region} 0)
(species RH1_{age}::{region} 0)
(species RH1_det3_{age}::{region} 0)
(species RC2_{age}::{region} 0)
(species RC2_det3_{age}::{region} 0)
""".format(age=age, region=region)
    species_str = species_str.replace("  ", " ")

    expand_testDelay_SymSys_str = """
(species Sym_preD_{age}::{region} 0)
(species Sys_preD_{age}::{region} 0)
""".format(age=age, region=region)


    expand_testDelay_AsSymSys_str = """
(species As_preD_{age}::{region} 0)
(species Sym_preD_{age}::{region} 0)
(species Sym_det2a_{age}::{region} 0)
(species Sym_det2b_{age}::{region} 0)
(species Sys_preD_{age}::{region} 0)
(species Sys_det3a_{age}::{region} 0)
(species Sys_det3b_{age}::{region} 0)
""".format(age=age, region=region)

    if expandModel == "testDelay_SymSys" or  expandModel == "uniformtestDelay" :
        species_str = species_str + expand_testDelay_SymSys_str
    if expandModel == "testDelay_AsSymSys":
        species_str = species_str + expand_testDelay_AsSymSys_str

    return (species_str)

## For postprocessing that splits by '_', it is easier if EMS are names EMS-1 not EMS_1
## This might change depending on the postprocessing
def sub(x):
    xout = re.sub('_','-', str(x), count=1)
    return(xout)
    
def write_observe(age, region, expandModel=None):
    region = str(region)
    grpout = sub(region)

    observe_str = """
(observe susceptible_{age}_{grpout} S_{age}::{region})
(observe exposed_{age}_{grpout} E_{age}::{region})
(observe asymptomatic_{age}_{grpout} asymptomatic_{age}_{region})
(observe presymptomatic_{age}_{grpout} presymptomatic_{age}_{region})
(observe symptomatic_mild_{age}_{grpout} symptomatic_mild_{age}_{region})
(observe symptomatic_severe_{age}_{grpout} symptomatic_severe_{age}_{region})
(observe hospitalized_{age}_{grpout} hospitalized_{age}_{region})
(observe critical_{age}_{grpout} critical_{age}_{region})
(observe deaths_{age}_{grpout} deaths_{age}_{region})
(observe recovered_{age}_{grpout} recovered_{age}_{region})

(observe asymp_cumul_{age}_{grpout} asymp_cumul_{age}_{region} )
(observe asymp_det_cumul_{age}_{grpout} asymp_det_cumul_{age}_{region})
(observe symp_mild_cumul_{age}_{grpout} symp_mild_cumul_{age}_{region})

(observe symp_severe_cumul_{age}_{grpout} symp_severe_cumul_{age}_{region})
 
(observe hosp_cumul_{age}_{grpout} hosp_cumul_{age}_{region})
(observe hosp_det_cumul_{age}_{grpout} hosp_det_cumul_{age}_{region} )
(observe crit_cumul_{age}_{grpout} crit_cumul_{age}_{region})
(observe crit_det_cumul_{age}_{grpout} crit_det_cumul_{age}_{region})
(observe crit_det_{age}_{grpout} crit_det_{age}_{region})
(observe death_det_cumul_{age}_{grpout} death_det_cumul_{age}_{region} )

(observe infected_{age}_{grpout} infected_{age}_{region})
(observe infected_cumul_{age}_{grpout} infected_cumul_{age}_{region})

(observe symp_mild_det_cumul_{age}_{grpout} symp_mild_det_cumul_{age}_{region})
(observe symp_severe_det_cumul_{age}_{grpout} symp_severe_det_cumul_{age}_{region})
(observe detected_{age}_{grpout} detected_{age}_{region})
(observe detected_cumul_{age}_{grpout} detected_cumul_{age}_{region} )

""".format(grpout=grpout, age=age, region=region)
    
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)

### Monitor time varying parameters
def write_observed_param(ageList, regionList):
    observed_param_str = """  
(observe d_As_t d_As)
(observe d_P_t d_P)
(observe d_Sym_t d_Sym)
(observe d_Sys_t d_Sys)
"""

    #for age, region in [(x, y) for x in ageList for y in regionList]:
    for region in regionList:
        region = str(region)
        temp_str = """
(param Ki_{region} @Ki_{region}@)
(observe Ki_{region}_t Ki_{region})
""".format(region=region)
        observed_param_str = observed_param_str + temp_str
        
    return observed_param_str
    

def write_functions(age, region, expandModel=None):

    functions_str = """
(func hospitalized_{age}_{region}  (+ H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region}))
(func critical_{age}_{region} (+ C2_{age}::{region} C3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
(func deaths_{age}_{region} (+ D3_{age}::{region} D3_det3_{age}::{region}))
(func recovered_{age}_{region} (+ RAs_{age}::{region} RSym_{age}::{region} RH1_{age}::{region} RC2_{age}::{region} RAs_det1_{age}::{region} RSym_det2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(func asymp_cumul_{age}_{region} (+ asymptomatic_{age}_{region} RAs_{age}::{region} RAs_det1_{age}::{region} ))
(func asymp_det_cumul_{age}_{region} (+ As_det1_{age}::{region} RAs_det1_{age}::{region}))
(func symp_mild_cumul_{age}_{region} (+ symptomatic_mild_{age}_{region} RSym_{age}::{region} RSym_det2_{age}::{region}))
(func symp_mild_det_cumul_{age}_{region} (+ RSym_det2_{age}::{region} Sym_det2_{age}::{region}))
(func symp_severe_cumul_{age}_{region} (+ symptomatic_severe_{age}_{region} hospitalized_{age}_{region} critical_{age}_{region} deaths_{age}_{region} RH1_{age}::{region} RC2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(func symp_severe_det_cumul_{age}_{region} (+ Sys_det3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region} D3_det3_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(func hosp_cumul_{age}_{region} (+ hospitalized_{age}_{region} critical_{age}_{region} deaths_{age}_{region} RH1_{age}::{region} RC2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(func hosp_det_cumul_{age}_{region} (+ H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region} D3_det3_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(func crit_cumul_{age}_{region} (+ deaths_{age}_{region} critical_{age}_{region} RC2_{age}::{region} RC2_det3_{age}::{region}))
(func crit_det_cumul_{age}_{region} (+ C2_det3_{age}::{region} C3_det3_{age}::{region} D3_det3_{age}::{region} RC2_det3_{age}::{region}))
(func crit_det_{age}_{region} (+ C2_det3_{age}::{region} C3_det3_{age}::{region}))
(func detected_cumul_{age}_{region} (+ (+ As_det1_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}) RAs_det1_{age}::{region} RSym_det2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region} D3_det3_{age}::{region}))
(func death_det_cumul_{age}_{region} D3_det3_{age}::{region} )

(func detected_{age}_{region} (+ As_det1_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
(func infected_{age}_{region} (+ infectious_det_{age}_{region} infectious_undet_{age}_{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
(func infected_cumul_{age}_{region} (+ infected_{age}_{region} recovered_{age}_{region} deaths_{age}_{region}))    
""".format(age=age, region=region)
    functions_str = functions_str.replace("  ", "")
    

    expand_base_str = """
(func asymptomatic_{age}_{region}  (+ As_{age}::{region} As_det1_{age}::{region}))
(func presymptomatic_{age}_{region}  (+ P_{age}::{region} P_det_{age}::{region}))
(func symptomatic_mild_{age}_{region}  (+ Sym_{age}::{region} Sym_det2_{age}::{region}))
(func symptomatic_severe_{age}_{region}  (+ Sys_{age}::{region} Sys_det3_{age}::{region}))
(func infectious_undet_{age}_{region} (+ As_{age}::{region} P_{age}::{region} Sym_{age}::{region} Sys_{age}::{region} H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} C2_{age}::{region} C3_{age}::{region}))
(func infectious_det_{age}_{region} (+ As_det1_{age}::{region} P_det_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} ))
""".format(age=age, region=region)


    expand_testDelay_SymSys_str = """
(func asymptomatic_{age}_{region}  (+ As_{age}::{region} As_det1_{age}::{region}))
(func presymptomatic_{age}_{region}  (+ P_{age}::{region} P_det_{age}::{region}))
(func symptomatic_mild_{age}_{region}  (+ Sym_{age}::{region} Sym_preD_{age}::{region} Sym_det2_{age}::{region}))
(func symptomatic_severe_{age}_{region}  (+ Sys_{age}::{region} Sys_preD_{age}::{region} Sys_det3_{age}::{region}))
(func infectious_undet_{age}_{region} (+ As_{age}::{region} P_{age}::{region} Sym_preD_{age}::{region} Sym_{age}::{region} Sys_preD_{age}::{region} Sys_{age}::{region} H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} C2_{age}::{region} C3_{age}::{region}))
(func infectious_det_{age}_{region} (+ As_det1_{age}::{region} P_det_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} ))
""".format(age=age, region=region)


    expand_testDelay_AsSymSys_str = """
(func asymptomatic_{age}_{region}  (+ As_preD_{age}::{region} As_{age}::{region} As_det1_{age}::{region}))
(func presymptomatic_{age}_{region}  (+ P_{age}::{region} P_det_{age}::{region}))
(func symptomatic_mild_{age}_{region}  (+ Sym_{age}::{region} Sym_preD_{age}::{region} Sym_det2a_{age}::{region} Sym_det2b_{age}::{region}))
(func symptomatic_severe_{age}_{region}  (+ Sys_{age}::{region} Sys_preD_{age}::{region} Sys_det3a_{age}::{region} Sys_det3b_{age}::{region}))
(func infectious_undet_{age}_{region} (+ As_preD_{age}::{region} As_{age}::{region} P_{age}::{region} Sym_{age}::{region} Sym_preD_{age}::{region} Sys_{age}::{region} Sys_preD_{age}::{region} H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} C2_{age}::{region} C3_{age}::{region}))
(func infectious_det_{age}_{region} (+ As_det1_{age}::{region} P_det_{age}::{region} Sym_det2a_{age}::{region} Sym_det2b_{age}::{region} Sys_det3a_{age}::{region} Sys_det3b_{age}::{region}))
""".format(age=age, region=region)


    if expandModel == None:
        functions_str = expand_base_str + functions_str
    if expandModel == "testDelay_SymSys" or  expandModel == "uniformtestDelay" :
        functions_str =  expand_testDelay_SymSys_str + functions_str
    if expandModel == "testDelay_AsSymSys":
        functions_str = expand_testDelay_AsSymSys_str + functions_str

    return (functions_str)

###
def write_params(expandModel=None):
    params_str = """
(param time_to_infectious @time_to_infectious@)
(param time_to_symptoms @time_to_symptoms@)
(param time_to_hospitalization @time_to_hospitalization@)
(param time_to_critical @time_to_critical@)
(param time_to_death @time_to_death@)
(param recovery_time_asymp @recovery_time_asymp@)
(param recovery_time_mild @recovery_time_mild@)
(param recovery_time_hosp @recovery_time_hosp@)
(param recovery_time_crit @recovery_time_crit@)
(param fraction_symptomatic @fraction_symptomatic@)
(param fraction_severe @fraction_severe@)
(param fraction_hospitalized @fraction_hospitalized@)
(param fraction_critical @fraction_critical@ )
(param fraction_dead @fraction_dead@)
(param reduced_inf_of_det_cases @reduced_inf_of_det_cases@)

(param d_As @d_As@)
(param d_P @d_P@)
(param d_Sym @d_Sym@)
(param d_Sys @d_Sys@)

(param Kr_a (/ 1 recovery_time_asymp))
(param Kr_m (/ 1 recovery_time_mild))
(param Kr_h (/ 1 recovery_time_hosp))
(param Kr_c (/ 1 recovery_time_crit))
(param Kl (/ (- 1 fraction_symptomatic ) time_to_infectious))
(param Ks (/ fraction_symptomatic  time_to_infectious))
(param Ksys (* fraction_severe (/ 1 time_to_symptoms)))
(param Ksym (* (- 1 fraction_severe) (/ 1 time_to_symptoms)))
(param Kc (/ 1 time_to_critical))
(param Km (/ 1 time_to_death))

(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@) (d_Sym @d_Sym_incr1@)))  
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@) (d_Sym @d_Sym_incr2@)))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@) (d_Sym @d_Sym_incr3@))) 
(time-event detection4 @detection_time_4@ ((d_Sys @d_Sys_incr4@) (d_Sym @d_Sym_incr4@))) 
(time-event detection5 @detection_time_5@ ((d_Sys @d_Sys_incr5@) (d_Sym @d_Sym_incr5@))) 
(time-event detection6 @detection_time_6@ ((d_Sys @d_Sys_incr6@) (d_Sym @d_Sym_incr6@))) 

"""

    expand_base_str = """
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
"""

    expand_uniformtestDelay_str = """
(param time_D @time_to_detection@)
(param Ksym_D (/ 1 time_D))
(param Ksys_D (/ 1 time_D))
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
(param Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D)))
(param Kh2_D (/ fraction_critical (- time_to_hospitalization time_D)))
(param Kh3_D (/ fraction_dead  (- time_to_hospitalization time_D)))
(param Kr_m_D (/ 1 (- recovery_time_mild time_D)))
"""

    expand_testDelay_SymSys_str = """
(param time_D_Sym @time_to_detection_Sym@)
(param time_D_Sys @time_to_detection_Sys@)
(param Ksym_D (/ 1 time_D_Sym))
(param Ksys_D (/ 1 time_D_Sys))
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
(param Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys)))
(param Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys)))
(param Kh3_D (/ fraction_dead  (- time_to_hospitalization time_D_Sys)))
(param Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym)))
"""

    expand_testDelay_AsSymSys_str = """
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization))
(param Kh3 (/ fraction_dead  time_to_hospitalization))

(param time_D_Sys @time_to_detection_Sys@)
(param Ksys_D (/ 1 time_D_Sys))
(param Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys)))
(param Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys)))
(param Kh3_D (/ fraction_dead  (- time_to_hospitalization time_D_Sys)))

(param time_D_Sym @time_to_detection_Sym@)
(param Ksym_D (/ 1 time_D_Sym))
(param Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym)))

(param time_D_As @time_to_detection_As@)
(param Kl_D (/ 1 time_D_As))
(param Kr_a_D (/ 1 (- recovery_time_asymp time_D_As)))
"""

    if expandModel == None:
        params_str = params_str + expand_base_str
    if expandModel == "testDelay_SymSys":
        params_str = params_str + expand_testDelay_SymSys_str
    if expandModel == "uniformtestDelay":
        params_str = params_str + expand_uniformtestDelay_str
    if expandModel == "contactTracing" :
        params_str = params_str + expand_base_str + expand_contactTracing_str
    if expandModel == "testDelay_AsSymSys" :
        params_str = params_str + expand_testDelay_AsSymSys_str

    params_str = params_str.replace("  ", " ")

    return (params_str)

def write_ki_mix(nageGroups, scale=True):
    grp_x = range(1, nageGroups + 1)
    grp_y = reversed(grp_x)

    ki_dic = {}
    for i, xy in enumerate(itertools.product(grp_x, grp_y)):
        ki_dic[i] = ["C" + str(xy[0]) + '_' + str(xy[1])]

    ki_mix_param1 = ""
    ki_mix_param3 = ""
    for i in range(len(ki_dic.keys())):
        string_i = "\n(param " + sub(ki_dic[i][0]) + " @" + ki_dic[i][0] + "@ )"
        ki_mix_param1 = ki_mix_param1 + string_i
        
        string_i = "\n(param " + ki_dic[i][0]  + " (/ " + sub(ki_dic[i][0]) + " norm_factor))"
        ki_mix_param3 = ki_mix_param3 + string_i

    ## To do - remove hardcoding and if statement
    if nageGroups ==4 :
        ki_mix_param2 = "\n(param sum1 (+ C11 C12 C13 C14))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum2  (+ C21 C22 C23 C24))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum3 (+ C31 C32 C33 C34))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum4 (+ C41 C42 C43 C44))"
        norm_factor = "\n(param norm_factor (+ (* sum1 p1) (* sum2  p2) (* sum3 p3) (* sum4  p4)))"

    if nageGroups ==8:
        ki_mix_param2 = "\n(param sum1 (+ C11 C12 C13 C14 C15 C16 C17 C18))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum2 (+ C21 C22 C23 C24 C25 C26 C27 C28))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum3 (+ C31 C32 C33 C34 C35 C36 C37 C38))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum4 (+ C41 C42 C43 C44 C45 C46 C47 C48))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum5 (+ C51 C52 C53 C54 C55 C56 C57 C58))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum6 (+ C61 C62 C63 C64 C65 C66 C67 C68))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum7 (+ C71 C72 C73 C74 C75 C76 C77 C78))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum8 (+ C81 C82 C83 C84 C85 C86 C87 C88))"
        norm_factor = "\n(param norm_factor (+ (* sum1 p1) (* sum2  p2) (* sum3 p3) (* sum4  p4) (* sum5  p5) (* sum6  p6) (* sum7  p7) (* sum8  p8)))"

    ki_mix_param = ki_mix_param1 + "\n" + ki_mix_param2 + "\n" + norm_factor + "\n" + ki_mix_param3
    
    return ki_mix_param
   

def repeat_string_by_grp(fixedstring, grpList1, grpList2):
    stringAll = ""
    middlesymbol = "_"
    
    if fixedstring == "S_" or fixedstring == "E_" or fixedstring == "P_":
        middlesymbol = "::"

    if grpList2 !=  None :
        for age, region in [(x, y) for x in grpList1 for y in grpList2]:
            temp_string = " " + fixedstring + age + middlesymbol + region
            stringAll = stringAll + temp_string

    if grpList2 == None :
        for grp  in grpList1:
            temp_string = " " + fixedstring + grp
            stringAll = stringAll + temp_string

    return stringAll


def write_All(ageList, regionList):
    obs_All_str = ""
    obs_All_str = obs_All_str + "\n(observe susceptible_All (+ " + repeat_string_by_grp('S_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe exposed_All (+ " + repeat_string_by_grp('E_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymptomatic_All (+ " + repeat_string_by_grp('asymptomatic_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe presymptomatic_All (+ " + repeat_string_by_grp('P_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_mild_All (+ " + repeat_string_by_grp('symptomatic_mild_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_severe_All (+ " + repeat_string_by_grp( 'symptomatic_severe_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe hospitalized_All (+ " + repeat_string_by_grp('hospitalized_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe critical_All (+ " + repeat_string_by_grp('critical_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe deaths_All (+ " + repeat_string_by_grp('deaths_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe infected_All (+ " + repeat_string_by_grp('infected_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe recovered_All (+ " + repeat_string_by_grp('recovered_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymp_cumul_All (+ " + repeat_string_by_grp( 'asymp_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymp_det_cumul_All (+ " + repeat_string_by_grp( 'asymp_det_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_mild_cumul_All (+ " + repeat_string_by_grp( 'symp_mild_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_mild_det_cumul_All (+ " + repeat_string_by_grp( 'symp_mild_det_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_severe_cumul_All (+ " + repeat_string_by_grp( 'symp_severe_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_severe_det_cumul_All  (+ " + repeat_string_by_grp(  'symp_severe_det_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe hosp_cumul_All (+ " + repeat_string_by_grp('hosp_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe hosp_det_cumul_All (+ " + repeat_string_by_grp( 'hosp_det_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe crit_cumul_All (+ " + repeat_string_by_grp('crit_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe crit_det_cumul_All (+ " + repeat_string_by_grp(  'crit_det_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe crit_det_All (+ " + repeat_string_by_grp('crit_det_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe detected_cumul_All (+ " + repeat_string_by_grp( 'detected_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe death_det_cumul_All (+ " + repeat_string_by_grp('death_det_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe infected_cumul_All (+ " + repeat_string_by_grp('infected_cumul_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(func infectious_det_All (+ " + repeat_string_by_grp('infectious_det_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(func infectious_undet_All (+ " + repeat_string_by_grp( 'infectious_undet_', ageList, regionList) + "))"
    obs_All_str = obs_All_str + "\n(observe infectious_det_All infectious_det_All)"
    obs_All_str = obs_All_str + "\n(observe infectious_undet_All infectious_undet_All)"

    return (obs_All_str)
 
    
def write_reactions(age, region, expandModel=None):

    reaction_str_I = """
(reaction exposure_{age}_{region}   (S_{age}::{region}) (E_{age}::{region}) (* Ki_{region} S_{age}::{region} (/  (+ infectious_undet_{age}_{region} (* infectious_det_{age}_{region} reduced_inf_of_det_cases)) N_{age}_{region} )))
""".format(age=age, region=region)

    reaction_str_III = """
(reaction recovery_H1_{age}_{region}   (H1_{age}::{region})   (RH1_{age}::{region})   (* Kr_h H1_{age}::{region}))
(reaction recovery_C2_{age}_{region}   (C2_{age}::{region})   (RC2_{age}::{region})   (* Kr_c C2_{age}::{region}))
(reaction recovery_H1_det3_{age}_{region}   (H1_det3_{age}::{region})   (RH1_det3_{age}::{region})   (* Kr_h H1_det3_{age}::{region}))
(reaction recovery_C2_det3_{age}_{region}   (C2_det3_{age}::{region})   (RC2_det3_{age}::{region})   (* Kr_c C2_det3_{age}::{region}))
    """.format(age=age, region=region)

    expand_base_str = """
(reaction infection_asymp_undet_{age}_{region}  (E_{age}::{region})   (As_{age}::{region})   (* Kl E_{age}::{region} (- 1 d_As)))
(reaction infection_asymp_det_{age}_{region}  (E_{age}::{region})   (As_det1_{age}::{region})   (* Kl E_{age}::{region} d_As))
(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_{age}::{region})   (* Ks E_{age}::{region} (- 1 d_P)))
(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_det_{age}::{region})   (* Ks E_{age}::{region} d_P))

(reaction mild_symptomatic_undet_{age}_{region} (P_{age}::{region})  (Sym_{age}::{region}) (* Ksym P_{age}::{region} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{age}_{region} (P_{age}::{region})  (Sym_det2_{age}::{region}) (* Ksym P_{age}::{region} d_Sym))
(reaction severe_symptomatic_undet_{age}_{region} (P_{age}::{region})  (Sys_{age}::{region})  (* Ksys P_{age}::{region} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{age}_{region} (P_{age}::{region})  (Sys_det3_{age}::{region})  (* Ksys P_{age}::{region} d_Sys))

(reaction mild_symptomatic_det_{age}_{region} (P_det_{age}::{region})  (Sym_det2_{age}::{region}) (* Ksym P_det_{age}::{region}))
(reaction severe_symptomatic_det_{age}_{region} (P_det_{age}::{region})  (Sys_det3_{age}::{region})  (* Ksys P_det_{age}::{region} ))

(reaction hospitalization_1_{age}_{region}   (Sys_{age}::{region})   (H1_{age}::{region})   (* Kh1 Sys_{age}::{region}))
(reaction hospitalization_2_{age}_{region}   (Sys_{age}::{region})   (H2_{age}::{region})   (* Kh2 Sys_{age}::{region}))
(reaction hospitalization_3_{age}_{region}   (Sys_{age}::{region})   (H3_{age}::{region})   (* Kh3 Sys_{age}::{region}))
(reaction critical_2_{age}_{region}   (H2_{age}::{region})   (C2_{age}::{region})   (* Kc H2_{age}::{region}))
(reaction critical_3_{age}_{region}   (H3_{age}::{region})   (C3_{age}::{region})   (* Kc H3_{age}::{region}))
(reaction death_{age}_{region}   (C3_{age}::{region})   (D3_{age}::{region})   (* Km C3_{age}::{region}))

(reaction hospitalization_1_det_{age}_{region}   (Sys_det3_{age}::{region})   (H1_det3_{age}::{region})   (* Kh1 Sys_det3_{age}::{region}))
(reaction hospitalization_2_det_{age}_{region}   (Sys_det3_{age}::{region})   (H2_det3_{age}::{region})   (* Kh2 Sys_det3_{age}::{region}))
(reaction hospitalization_3_det_{age}_{region}   (Sys_det3_{age}::{region})   (H3_det3_{age}::{region})   (* Kh3 Sys_det3_{age}::{region}))
(reaction critical_2_det2_{age}_{region}   (H2_det3_{age}::{region})   (C2_det3_{age}::{region})   (* Kc H2_det3_{age}::{region}))
(reaction critical_3_det2_{age}_{region}   (H3_det3_{age}::{region})   (C3_det3_{age}::{region})   (* Kc H3_det3_{age}::{region}))
(reaction death_det3_{age}_{region}   (C3_det3_{age}::{region})   (D3_det3_{age}::{region})   (* Km C3_det3_{age}::{region}))

(reaction recovery_As_{age}_{region}   (As_{age}::{region})   (RAs_{age}::{region})   (* Kr_a As_{age}::{region}))
(reaction recovery_As_det_{age}_{region} (As_det1_{age}::{region})   (RAs_det1_{age}::{region})   (* Kr_a As_det1_{age}::{region}))

(reaction recovery_Sym_{age}_{region}   (Sym_{age}::{region})   (RSym_{age}::{region})   (* Kr_m  Sym_{age}::{region}))
(reaction recovery_Sym_det2_{age}_{region}   (Sym_det2_{age}::{region})   (RSym_det2_{age}::{region})   (* Kr_m  Sym_det2_{age}::{region}))
""".format(age=age, region=region)


    expand_testDelay_SymSys_str = """
(reaction infection_asymp_undet_{age}_{region}  (E_{age}::{region})   (As_{age}::{region})   (* Kl E_{age}::{region} (- 1 d_As)))
(reaction infection_asymp_det_{age}_{region}  (E_{age}::{region})   (As_det1_{age}::{region})   (* Kl E_{age}::{region} d_As))
(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_{age}::{region})   (* Ks E_{age}::{region}))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{age}_{region} (P_{age}::{region})  (Sym_preD_{age}::{region}) (* Ksym P_{age}::{region}))
(reaction severe_symptomatic_{age}_{region} (P_{age}::{region})  (Sys_preD_{age}::{region})  (* Ksys P_{age}::{region}))

; never detected 
(reaction mild_symptomatic_undet_{age}_{region} (Sym_preD_{age}::{region})  (Sym_{age}::{region}) (* Ksym_D Sym_preD_{age}::{region} (- 1 d_Sym)))
(reaction severe_symptomatic_undet_{age}_{region} (Sys_preD_{age}::{region})  (Sys_{age}::{region})  (* Ksys_D Sys_preD_{age}::{region} (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det_{age}_{region} (Sym_preD_{age}::{region})  (Sym_det2_{age}::{region}) (* Ksym_D Sym_preD_{age}::{region} d_Sym))
(reaction severe_symptomatic_det_{age}_{region} (Sys_preD_{age}::{region})  (Sys_det3_{age}::{region})  (* Ksys_D Sys_preD_{age}::{region} d_Sys))

(reaction hospitalization_1_{age}_{region}   (Sys_{age}::{region})   (H1_{age}::{region})   (* Kh1_D Sys_{age}::{region}))
(reaction hospitalization_2_{age}_{region}   (Sys_{age}::{region})   (H2_{age}::{region})   (* Kh2_D Sys_{age}::{region}))
(reaction hospitalization_3_{age}_{region}   (Sys_{age}::{region})   (H3_{age}::{region})   (* Kh3_D Sys_{age}::{region}))
(reaction critical_2_{age}_{region}   (H2_{age}::{region})   (C2_{age}::{region})   (* Kc H2_{age}::{region}))
(reaction critical_3_{age}_{region}   (H3_{age}::{region})   (C3_{age}::{region})   (* Kc H3_{age}::{region}))
(reaction death_{age}_{region}   (C3_{age}::{region})   (D3_{age}::{region})   (* Km C3_{age}::{region}))

(reaction hospitalization_1_det_{age}_{region}   (Sys_det3_{age}::{region})   (H1_det3_{age}::{region})   (* Kh1_D Sys_det3_{age}::{region}))
(reaction hospitalization_2_det_{age}_{region}   (Sys_det3_{age}::{region})   (H2_det3_{age}::{region})   (* Kh2_D Sys_det3_{age}::{region}))
(reaction hospitalization_3_det_{age}_{region}   (Sys_det3_{age}::{region})   (H3_det3_{age}::{region})   (* Kh3_D Sys_det3_{age}::{region}))
(reaction critical_2_det2_{age}_{region}   (H2_det3_{age}::{region})   (C2_det3_{age}::{region})   (* Kc H2_det3_{age}::{region}))
(reaction critical_3_det2_{age}_{region}   (H3_det3_{age}::{region})   (C3_det3_{age}::{region})   (* Kc H3_det3_{age}::{region}))
(reaction death_det3_{age}_{region}   (C3_det3_{age}::{region})   (D3_det3_{age}::{region})   (* Km C3_det3_{age}::{region}))

(reaction recovery_As_{age}_{region}   (As_{age}::{region})   (RAs_{age}::{region})   (* Kr_a As_{age}::{region}))
(reaction recovery_As_det_{age}_{region} (As_det1_{age}::{region})   (RAs_det1_{age}::{region})   (* Kr_a As_det1_{age}::{region}))
(reaction recovery_Sym_{age}_{region}   (Sym_{age}::{region})   (RSym_{age}::{region})   (* Kr_m_D  Sym_{age}::{region}))
(reaction recovery_Sym_det2_{age}_{region}   (Sym_det2_{age}::{region})   (RSym_det2_{age}::{region})   (* Kr_m_D  Sym_det2_{age}::{region}))

""".format(age=age, region=region)


    expand_testDelay_AsSymSys_str = """
(reaction infection_asymp_det_{age}_{region}  (E_{age}::{region})   (As_preD_{age}::{region})   (* Kl E_{age}::{region}))
(reaction infection_asymp_undet_{age}_{region}  (As_preD_{age}::{region})   (As_{age}::{region})   (* Kl_D As_preD_{age}::{region} (- 1 d_As)))
(reaction infection_asymp_det_{age}_{region}  (As_preD_{age}::{region})   (As_det1_{age}::{region})   (* Kl_D As_preD_{age}::{region} d_As))

(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_{age}::{region})   (* Ks  E_{age}::{region} (- 1 d_P)))
(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_det_{age}::{region})   (* Ks  E_{age}::{region} d_P))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{age}_{region} (P_{age}::{region})  (Sym_preD_{age}::{region}) (* Ksym P_{age}::{region}))
(reaction severe_symptomatic_{age}_{region} (P_{age}::{region})  (Sys_preD_{age}::{region})  (* Ksys P_{age}::{region}))
																   
; never detected 
(reaction mild_symptomatic_undet_{age}_{region} (Sym_preD_{age}::{region})  (Sym_{age}::{region}) (* Ksym_D Sym_preD_{age}::{region} (- 1 d_Sym)))
(reaction severe_symptomatic_undet_{age}_{region} (Sys_preD_{age}::{region})  (Sys_{age}::{region})  (* Ksys_D Sys_preD_{age}::{region} (- 1 d_Sys)))

; new detections  - time to detection is subtracted from hospital time
(reaction mild_symptomatic_det_{age}_{region} (Sym_preD_{age}::{region})  (Sym_det2a_{age}::{region}) (* Ksym_D Sym_preD_{age}::{region} d_Sym))
(reaction severe_symptomatic_det_{age}_{region} (Sys_preD_{age}::{region})  (Sys_det3a_{age}::{region})  (* Ksys_D Sys_preD_{age}::{region} d_Sys))

; developing symptoms - already detected, same time to symptoms as in master emodl
(reaction mild_symptomatic_det_{age}_{region} (P_det_{age}::{region})  (Sym_det2b_{age}::{region}) (* Ksym  P_det_{age}::{region}))
(reaction severe_symptomatic_det_{age}_{region} (P_det_{age}::{region})  (Sys_det3b_{age}::{region})  (* Ksys  P_det_{age}::{region} ))

(reaction hospitalization_1_{age}_{region}  (Sys_{age}::{region})   (H1_{age}::{region})   (* Kh1_D Sys_{age}::{region}))
(reaction hospitalization_2_{age}_{region}   (Sys_{age}::{region})   (H2_{age}::{region})   (* Kh2_D Sys_{age}::{region}))
(reaction hospitalization_3_{age}_{region}   (Sys_{age}::{region})   (H3_{age}::{region})   (* Kh3_D Sys_{age}::{region}))
(reaction critical_2_{age}_{region}  (H2_{age}::{region})   (C2_{age}::{region})   (* Kc H2_{age}::{region}))
(reaction critical_3_{age}_{region}   (H3_{age}::{region})   (C3_{age}::{region})   (* Kc H3_{age}::{region}))
(reaction death_{age}_{region}   (C3_{age}::{region})   (D3_{age}::{region})   (* Km C3_{age}::{region}))

(reaction hospitalization_1_det_{age}_{region}   (Sys_det3a_{age}::{region})   (H1_det3_{age}::{region})   (* Kh1_D Sys_det3a_{age}::{region}))
(reaction hospitalization_2_det_{age}_{region}   (Sys_det3a_{age}::{region})   (H2_det3_{age}::{region})   (* Kh2_D Sys_det3a_{age}::{region}))
(reaction hospitalization_3_det_{age}_{region}   (Sys_det3a_{age}::{region})   (H3_det3_{age}::{region})   (* Kh3_D Sys_det3a_{age}::{region}))

(reaction hospitalization_1_det_{age}_{region}   (Sys_det3b_{age}::{region})   (H1_det3_{age}::{region})   (* Kh1 Sys_det3b_{age}::{region}))
(reaction hospitalization_2_det_{age}_{region}   (Sys_det3b_{age}::{region})   (H2_det3_{age}::{region})   (* Kh2 Sys_det3b_{age}::{region}))
(reaction hospitalization_3_det_{age}_{region}   (Sys_det3b_{age}::{region})   (H3_det3_{age}::{region})   (* Kh3 Sys_det3b_{age}::{region}))

(reaction critical_2_det2_{age}_{region}   (H2_det3_{age}::{region})   (C2_det3_{age}::{region})   (* Kc H2_det3_{age}::{region}))
(reaction critical_3_det2_{age}_{region}   (H3_det3_{age}::{region})   (C3_det3_{age}::{region})   (* Kc H3_det3_{age}::{region}))
(reaction death_det3_{age}_{region}   (C3_det3_{age}::{region})   (D3_det3_{age}::{region})   (* Km C3_det3_{age}::{region}))

(reaction recovery_As_{age}_{region}   (As_{age}::{region})   (RAs_{age}::{region})   (* Kr_a_D As_{age}::{region}))
(reaction recovery_As_det_{age}_{region} (As_det1_{age}::{region})   (RAs_det1_{age}::{region})   (* Kr_a_D As_det1_{age}::{region}))

(reaction recovery_Sym_{age}_{region}   (Sym_{age}::{region})   (RSym_{age}::{region})   (* Kr_m_D  Sym_{age}::{region}))
(reaction recovery_Sym_det2a_{age}_{region}   (Sym_det2a_{age}::{region})   (RSym_det2_{age}::{region})   (* Kr_m_D  Sym_det2a_{age}::{region}))
(reaction recovery_Sym_det2b_{age}_{region}   (Sym_det2b_{age}::{region})   (RSym_det2_{age}::{region})   (* Kr_m  Sym_det2b_{age}::{region}))
 """.format(age=age, region=region)

    if expandModel ==None :
        reaction_str = reaction_str_I + expand_base_str + reaction_str_III
    if expandModel == "testDelay_SymSys" or  expandModel == "uniformtestDelay" :
        reaction_str = reaction_str_I + expand_testDelay_SymSys_str + reaction_str_III
    if expandModel == 'testDelay_AsSymSys':
        reaction_str = reaction_str_I + expand_testDelay_AsSymSys_str + reaction_str_III
        
    reaction_str = reaction_str.replace("  ", " ")

    return (reaction_str)


def write_interventions(regionList, total_string, scenarioName, expandModel, change_testDelay=None) :

    continuedSIP_str = ""
    for region in regionList:
        temp_str = """
(param Ki_red1_{region} (* Ki_{region} @social_multiplier_1_{region}@))
(param Ki_red2_{region} (* Ki_{region} @social_multiplier_2_{region}@))
(param Ki_red3_{region} (* Ki_{region} @social_multiplier_3_{region}@))
(param Ki_red4_{region} (* Ki_{region} @social_multiplier_4_{region}@))

(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki_{region} Ki_red1_{region})))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki_{region} Ki_red2_{region})))
(time-event socialDistance_start @socialDistance_time3@ ((Ki_{region} Ki_red3_{region})))
(time-event socialDistance_change @socialDistance_time4@ ((Ki_{region} Ki_red4_{region})))
            """.format(region=region)
        continuedSIP_str = continuedSIP_str + temp_str

    interventiopnSTOP_str = ""
    for region in regionList :
        temp_str = """
(param Ki_back_{region} (* Ki_{region} @backtonormal_multiplier@))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{region} Ki_back_{region})))
        """.format(region=region)
        interventiopnSTOP_str = interventiopnSTOP_str + temp_str

    interventionSTOP_adj_str = ""
    for region in regionList :
        temp_str = """
(param Ki_back_{region} (+ Ki_red4_{region} (* @backtonormal_multiplier@ (- Ki_{region} Ki_red4_{region}))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{region} Ki_back_{region})))
        """.format(region=region)
        interventionSTOP_adj_str = interventionSTOP_adj_str + temp_str

    gradual_reopening_str = ""
    for region in regionList:
        temp_str = """
(param Ki_back1_{region} (+ Ki_red4_{region} (* @reopening_multiplier_1@ (- Ki_{region} Ki_red4_{region}))))
(param Ki_back2_{region} (+ Ki_red4_{region} (* @reopening_multiplier_2@ (- Ki_{region} Ki_red4_{region}))))
(param Ki_back3_{region} (+ Ki_red4_{region} (* @reopening_multiplier_3@ (- Ki_{region} Ki_red4_{region}))))
(param Ki_back4_{region} (+ Ki_red4_{region} (* @reopening_multiplier_4@ (- Ki_{region} Ki_red4_{region}))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki_{region} Ki_back1_{region})))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki_{region} Ki_back2_{region})))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki_{region} Ki_back3_{region})))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki_{region} Ki_back4_{region})))
    """.format(region=region)
        gradual_reopening_str = gradual_reopening_str + temp_str

    contactTracing_str = """
(time-event contact_tracing_start @contact_tracing_start_1@ ((reduced_inf_of_det_cases @reduced_inf_of_det_cases_ct1@ ) (d_As @d_AsP_ct1@) (d_P @d_AsP_ct1@) (d_Sym @d_Sym_ct1@)))
;(time-event contact_tracing_end @contact_tracing_stop1@ ((reduced_inf_of_det_cases @reduced_inf_of_det_cases@ ) (d_As @d_As@) (d_P @d_P@) (d_Sym @d_Sym@)))
    """

    change_uniformtestDelay_str = """
(time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} {} {} {} {} ))
    """.format("(time_D @change_testDelay_1@)",
               "(Ksys_D (/ 1 time_D))",
               "(Ksym_D (/ 1 time_D))",
               "(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D)))",
               "(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D) ))",
               "(Kh3_D (/ fraction_dead (- time_to_hospitalization time_D)))",
               "(Kr_m_D (/ 1 (- recovery_time_mild time_D )))")

    change_testDelay_Sym_str = """
(time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} ))
    """.format("(time_D_Sym @change_testDelay_Sym_1@)",
               "(Ksym_D (/ 1 time_D_Sym))",
               "(Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym )))")

    change_testDelay_Sys_str = """
(time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} {} {} ))
    """.format("(time_D_Sys @change_testDelay_Sys_1@)",
               "(Ksys_D (/ 1 time_D_Sys))",
               "(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys)))",
               "(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) ))",
               "(Kh3_D (/ fraction_dead (- time_to_hospitalization time_D_Sys)))")
               
    change_testDelay_As_str = """
(time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} ))
    """.format("(time_D_As @change_testDelay_As_1@)",
               "(Kl_D (/ 1 time_D_As))",
               "(Kr_a_D (/ 1 (- recovery_time_asymp time_D_As )))")  

   
    if scenarioName == "interventionStop" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventiopnSTOP_str)
    if scenarioName == "interventionSTOP_adj" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventionSTOP_adj_str)
    if scenarioName == "gradual_reopening" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + gradual_reopening_str)
    if scenarioName == "continuedSIP" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str)
    if scenarioName == "contactTracing" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventionSTOP_adj_str + contactTracing_str)

    if change_testDelay != None :
        if change_testDelay == "uniform" :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_uniformtestDelay_str)
        if change_testDelay == "As"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str )
        if change_testDelay == "Sym"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sym_str )
        if change_testDelay == "Sys"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sys_str )
        if change_testDelay == "AsSym"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_Sys_str )
        if change_testDelay == "SymSys" :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)
        if change_testDelay == "AsSymSys"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)


    return (total_string)


###stringing all of my functions together to make the file:

def generate_emodl(age_list, region_list,pop_dic, import_dic, import_dic2,file_output, expandModel, add_interventions, add_migration=True, change_testDelay =None):
    if (os.path.exists(file_output)):
        os.remove(file_output)

    model_name = "seir.emodl"  ### can make this more flexible
    header_str = "; simplemodel \n\n" + "(import (rnrs) (emodl cmslib)) \n\n" + '(start-model "{}") \n\n'.format(
        model_name)
    footer_str = "(end-model)"

    # building up the .emodl string
    total_string = ""
    species_string = ""
    observe_string = ""
    param_string = ""
    reaction_string = ""
    functions_string = ""
    total_string = total_string + header_str

    for region in region_list:
        total_string = total_string + "\n(locale site-{})\n".format(region)
        total_string = total_string + "(set-locale site-{})\n".format(region)
        
        for age in age_list:
            #species_init = write_species_init_2grp(age=age, region_dic=region_dic, region=key)
            species_init = set_population(age, region,pop_dic, import_dic)
            species = write_species(age, region)
            total_string = total_string + species_init + species

    for age, region in [(x, y) for x in age_list for y in region_list]:
         observe_string = observe_string + write_observe(age, region)
         reaction_string = reaction_string + write_reactions(age, region)
         functions_string = functions_string + write_functions(age, region)
         param_string = param_string + write_Ki_timevents(age, region, import_dic2) # + write_age_param(age)
            
    param_string = write_params(expandModel) + param_string + write_observed_param(age_list, region_list) + write_N_population(age_list, region_list, pop_dic)

    functions_string = functions_string + write_All(age_list, region_list)
    intervention_string = ";[INTERVENTIONS]\n;[ADDITIONAL_TIMEEVENTS]"

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string +  '\n\n' + reaction_string + '\n\n' + footer_str

    ### Custom adjustments for EMS 6 (earliest start date)
    #total_string = total_string.replace('(species As::EMS_6 0)', '(species As::EMS_6 1)')
    ### Add interventions (optional)
    if add_interventions != None :
        total_string = write_interventions(region_list, total_string, add_interventions, expandModel, change_testDelay)

    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


if __name__ == '__main__':
    age_grp8 = ["age0to9", "age10to19", "age20to29", "age30to39", "age40to49", "age50to59", "age60to69", "age70to100"]
    #region_list = ['EMS_1', 'EMS_2', 'EMS_3', 'EMS_4', 'EMS_5', 'EMS_6', 'EMS_7', 'EMS_8', 'EMS_9', 'EMS_10','EMS_11']
    region_list = ['EMS_1', 'EMS_2']
    age_region_pop = {
    'EMS_1' : [{"age0to9": 78641	, "age10to19": 91701	, "age20to29": 94681	, "age30to39" : 89371	, "age40to49": 92396	,"age50to59": 110878	, "age60to69" :92988	, "age70to100" :89076	}],
    'EMS_2' : [{"age0to9": 114210	, "age10to19": 132626	, "age20to29": 150792 	, "age30to39" : 141161	, "age40to49": 140827	,"age50to59": 170321	, "age60to69" :143642	, "age70to100" :135817	}],
    'EMS_3' : [{"age0to9": 57069	, "age10to19": 71489	, "age20to29": 76506	, "age30to39" : 71437	, "age40to49": 79844	,"age50to59": 101522	, "age60to69" :82573	, "age70to100" :81032	}],
    'EMS_4' : [{"age0to9": 72063	, "age10to19": 84167	, "age20to29": 89843	, "age30to39" : 88706	, "age40to49": 89248	,"age50to59": 110692	, "age60to69" :87058	, "age70to100" :79757	}],
    'EMS_5' : [{"age0to9": 41533	, "age10to19": 48068	, "age20to29": 55005	, "age30to39" : 48713	, "age40to49": 49212	,"age50to59": 64576	    , "age60to69" :54930	, "age70to100" :57281	}],
    'EMS_6' : [{"age0to9": 78524	, "age10to19": 92005	, "age20to29": 119387	, "age30to39" : 96035	, "age40to49": 94670	,"age50to59": 117353	, "age60to69" :99559	, "age70to100" :94750	}],
    'EMS_7' : [{"age0to9": 208260	, "age10to19": 251603	, "age20to29": 217013	, "age30to39" : 238956	, "age40to49": 251248	,"age50to59": 280849	, "age60to69" :206843	, "age70to100" :171112	}],
    'EMS_8' : [{"age0to9": 187495	, "age10to19": 218993	, "age20to29": 204630	, "age30to39" : 235119	, "age40to49": 233866	,"age50to59": 258661	, "age60to69" :190207	, "age70to100" :154577	}],
    'EMS_9' : [{"age0to9": 223250	, "age10to19": 259507	, "age20to29": 232036	, "age30to39" : 274367	, "age40to49": 284363	,"age50to59": 307266	, "age60to69" :221915	, "age70to100" :177803	}],
    'EMS_10': [{"age0to9": 113783	, "age10to19": 138714	, "age20to29": 118833	, "age30to39" : 134124	, "age40to49": 147069	,"age50to59": 166857	, "age60to69" :127055	, "age70to100" :111866	}],
    'EMS_11': [{"age0to9": 326312	, "age10to19": 330144	, "age20to29": 432323	, "age30to39" : 457425	, "age40to49": 349783	,"age50to59": 347788	, "age60to69" :270747	, "age70to100" :230158	}]
   }

    ## Earliest start date
    age_region_initialInfect = {
    'EMS_1' : [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_2' : [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_3' : [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_4' : [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_5' : [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_6' : [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_7' : [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_8' : [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_9' : [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_10': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_11': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}]
   }

    ## Later start dates for other EMS regions
    age_region_importedInfect = {
    'EMS_1' : [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_2' : [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_3' : [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_4' : [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_5' : [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_6' : [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_7' : [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_8' : [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_9' : [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_10': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}],
    'EMS_11': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0, "age60to69": 0, "age70to100": 0}]
   }



    ### Vary test delay  (i.e. change_testDelay = "SymSys"   )
    generate_emodl(age_list=age_grp8,
                   region_list=region_list,
                   pop_dic=age_region_pop,
                   import_dic=age_region_initialInfect,
                   import_dic2=age_region_importedInfect,
                   expandModel=None,
                   add_interventions='continuedSIP',
                   add_migration=False,
                   file_output=os.path.join(emodl_dir, 'extendedmodel_agelocale_test.emodl'))