import os
import sys
import re


sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')


def write_species(grp, expandModel=None):
    grp = str(grp)
    species_str = """
(species S::{grp} @speciesS_{grp}@)
(species As::{grp} 0)
(species E::{grp} 0)
(species As_det1::{grp} 0)
(species P::{grp} 0)
(species P_det::{grp} 0)
(species Sym::{grp} 0)
(species Sym_det2::{grp} 0)
(species Sys::{grp} 0)
(species Sys_det3::{grp} 0)
(species H1::{grp} 0)
(species H2::{grp} 0)
(species H3::{grp} 0)
(species H1_det3::{grp} 0)
(species H2_det3::{grp} 0)
(species H3_det3::{grp} 0)
(species C2::{grp} 0)
(species C3::{grp} 0)
(species C2_det3::{grp} 0)
(species C3_det3::{grp} 0)
(species D3::{grp} 0)
(species D3_det3::{grp} 0)
(species RAs::{grp} 0)
(species RAs_det1::{grp} 0)
(species RSym::{grp} 0)
(species RSym_det2::{grp} 0)
(species RH1::{grp} 0)
(species RH1_det3::{grp} 0)
(species RC2::{grp} 0)
(species RC2_det3::{grp} 0)
""".format(grp=grp)
    species_str = species_str.replace("  ", " ")

    expand_testDelay_SymSys_str = """
(species Sym_preD::{grp} 0)
(species Sys_preD::{grp} 0)
""".format(grp=grp)


    expand_testDelay_AsSymSys_str = """
(species As_preD::{grp} 0)
(species Sym_preD::{grp} 0)
(species Sym_det2a::{grp} 0)
(species Sym_det2b::{grp} 0)
(species Sys_preD::{grp} 0)
(species Sys_det3a::{grp} 0)
(species Sys_det3b::{grp} 0)
""".format(grp=grp)



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
    
def write_observe(grp, expandModel=None):
    grp = str(grp)
    grpout = sub(grp)

    observe_str = """
(observe susceptible_{grpout} S::{grp})
(observe exposed_{grpout} E::{grp})
(observe asymptomatic_{grpout} asymptomatic_{grp})
(observe presymptomatic_{grpout} presymptomatic_{grp})
(observe symptomatic_mild_{grpout} symptomatic_mild_{grp})
(observe symptomatic_severe_{grpout} symptomatic_severe_{grp})
(observe hospitalized_{grpout} hospitalized_{grp})
(observe critical_{grpout} critical_{grp})
(observe deaths_{grpout} deaths_{grp})
(observe recovered_{grpout} recovered_{grp})

(observe asymptomatic_det_{grpout} asymptomatic_det_{grp})
(observe presymptomatic_det{grpout} presymptomatic_det_{grp} )
(observe symptomatic_mild_det_{grpout} symptomatic_mild_det_{grp})
(observe symptomatic_severe_det_{grpout} symptomatic_severe_det_{grp})
(observe hospitalized_det_{grpout} hospitalized_det_{grp})
(observe critical_det_{grpout} critical_det_{grp})
(observe deaths_det_{grpout} D3_det3::{grp})
(observe recovered_det_{grpout} recovered_det_{grp})

(observe asymp_cumul_{grpout} asymp_cumul_{grp} )
(observe asymp_det_cumul_{grpout} asymp_det_cumul_{grp})
(observe symp_mild_cumul_{grpout} symp_mild_cumul_{grp})

(observe symp_severe_cumul_{grpout} symp_severe_cumul_{grp})
 
(observe hosp_cumul_{grpout} hosp_cumul_{grp})
(observe hosp_det_cumul_{grpout} hosp_det_cumul_{grp} )
(observe crit_cumul_{grpout} crit_cumul_{grp})
(observe crit_det_cumul_{grpout} crit_det_cumul_{grp})
(observe crit_det_{grpout} crit_det_{grp})
(observe death_det_cumul_{grpout} death_det_cumul_{grp} )

(observe infected_{grpout} infected_{grp})
(observe infected_cumul_{grpout} infected_cumul_{grp})

(observe infectious_undet_{grpout} infectious_undet_{grp})
(observe infectious_det_{grpout} infectious_det_{grp})
(observe infectious_det_symp_{grpout} infectious_det_symp_{grp})
(observe infectious_det_AsP_{grpout} infectious_det_AsP_{grp})

(observe symp_mild_det_cumul_{grpout} symp_mild_det_cumul_{grp})
(observe symp_severe_det_cumul_{grpout} symp_severe_det_cumul_{grp})
(observe detected_{grpout} detected_{grp})
(observe detected_cumul_{grpout} detected_cumul_{grp} )

(observe prevalence_{grpout} prevalence_{grp})    
(observe seroprevalence_{grpout} seroprevalence_{grp} )
(observe prevalence_det_{grpout} prevalence_det_{grp})    
(observe seroprevalence_det_{grpout} seroprevalence_det_{grp} )

""".format(grpout=grpout, grp=grp)
    
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


def write_functions(grp, expandModel=None):
    grp = str(grp)
    functions_str = """
(func presymptomatic_{grp}  (+ P::{grp} P_det::{grp}))
(func presymptomatic_det_{grp}  (- presymptomatic_{grp} P::{grp}))
(func asymptomatic_det_{grp}  (- asymptomatic_{grp} As::{grp}))
(func symptomatic_mild_det_{grp}  (- symptomatic_mild_{grp} Sym::{grp}))
(func symptomatic_severe_det_{grp}  (- symptomatic_severe_{grp} Sys::{grp}))

(func hospitalized_{grp}  (+ H1::{grp} H2::{grp} H3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp}))
(func hospitalized_det_{grp}  (+ H1_det3::{grp} H2_det3::{grp} H3_det3::{grp}))
(func critical_{grp} (+ C2::{grp} C3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func critical_det_{grp} (+ C2_det3::{grp} C3_det3::{grp}))
(func deaths_{grp} (+ D3::{grp} D3_det3::{grp}))
(func recovered_{grp} (+ RAs::{grp} RSym::{grp} RH1::{grp} RC2::{grp} RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func recovered_det_{grp} (+ RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func asymp_cumul_{grp} (+ asymptomatic_{grp} RAs::{grp} RAs_det1::{grp} ))
(func asymp_det_cumul_{grp} (+ As_det1::{grp} RAs_det1::{grp}))
(func symp_mild_cumul_{grp} (+ symptomatic_mild_{grp} RSym::{grp} RSym_det2::{grp}))
(func symp_mild_det_cumul_{grp} (+ RSym_det2::{grp} Sym_det2::{grp}))
(func symp_severe_cumul_{grp} (+ symptomatic_severe_{grp} hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func symp_severe_det_cumul_{grp} (+ Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func hosp_cumul_{grp} (+ hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func hosp_det_cumul_{grp} (+ H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func crit_cumul_{grp} (+ deaths_{grp} critical_{grp} RC2::{grp} RC2_det3::{grp}))
(func crit_det_cumul_{grp} (+ C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RC2_det3::{grp}))
(func crit_det_{grp} (+ C2_det3::{grp} C3_det3::{grp}))
(func detected_cumul_{grp} (+ (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} C2_det3::{grp} C3_det3::{grp}) RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp} D3_det3::{grp}))
(func death_det_cumul_{grp} D3_det3::{grp} )

(func detected_{grp} (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func infected_det_{grp} (+ infectious_det_{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func infected_cumul_{grp} (+ infected_{grp} recovered_{grp} deaths_{grp}))    

(func prevalence_{grp} (/ infected_{grp} N_{grp}))    
(func seroprevalence_{grp} (/ (+ infected_{grp} recovered_{grp}) N_{grp}))    

(func prevalence_det_{grp} (/ infected_det_{grp} N_{grp}))    
(func seroprevalence_det_{grp} (/ (+ infected_det_{grp} recovered_det_{grp}) N_{grp}))    

""".format(grp=grp)
    functions_str = functions_str.replace("  ", "")
    

    expand_base_str = """
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))
(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_det2::{grp}))
(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_det3::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym::{grp} Sys::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} P_det::{grp} Sym_det2::{grp} Sys_det3::{grp} ))

(func infectious_det_symp_{grp} (+ Sym_det2::{grp} Sys_det3::{grp} ))
(func infectious_det_AsP_{grp} (+ As_det1::{grp} P_det::{grp}))
""".format(grp=grp)


    expand_testDelay_SymSys_str = """
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))
(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_preD::{grp} Sym_det2::{grp}))
(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_preD::{grp} Sys_det3::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym_preD::{grp} Sym::{grp} Sys_preD::{grp} Sys::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} P_det::{grp} Sym_det2::{grp} Sys_det3::{grp} ))

(func infectious_det_symp_{grp} (+ Sym_det2::{grp} Sys_det3::{grp} ))
(func infectious_det_AsP_{grp} (+ As_det1::{grp} P_det::{grp}))
""".format(grp=grp)


    expand_testDelay_AsSymSys_str = """
(func asymptomatic_{grp}  (+ As_preD::{grp} As::{grp} As_det1::{grp}))
(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_preD::{grp} Sym_det2a::{grp} Sym_det2b::{grp}))
(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_preD::{grp} Sys_det3a::{grp} Sys_det3b::{grp}))
(func infectious_undet_{grp} (+ As_preD::{grp} As::{grp} P::{grp} Sym::{grp} Sym_preD::{grp} Sys::{grp} Sys_preD::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} P_det::{grp} Sym_det2a::{grp} Sym_det2b::{grp} Sys_det3a::{grp} Sys_det3b::{grp}))

(func infectious_det_symp_{grp} (+ Sym_det2a::{grp} Sym_det2b::{grp} Sys_det3a::{grp} Sys_det3b::{grp} ))
(func infectious_det_AsP_{grp} (+ As_det1::{grp} P_det::{grp}))
""".format(grp=grp)


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
(param reduced_inf_of_det_cases_ct 0)

(param d_As @d_As@)
(param d_P @d_P@)
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
"""

    expand_base_str = """
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization ))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
"""

    expand_uniformtestDelay_str = """
(param time_D @time_to_detection@)
(param Ksym_D (/ 1 time_D))
(param Ksys_D (/ 1 time_D))
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization ))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
(param Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D)))
(param Kh2_D (/ fraction_critical (- time_to_hospitalization time_D) ))
(param Kh3_D (/ fraction_dead  (- time_to_hospitalization time_D)))
(param Kr_m_D (/ 1 (- recovery_time_mild time_D )))
"""


    expand_testDelay_SymSys_str = """
(param time_D_Sym @time_to_detection_Sym@)
(param time_D_Sys @time_to_detection_Sys@)
(param Ksym_D (/ 1 time_D_Sym))
(param Ksys_D (/ 1 time_D_Sys))
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization ))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
(param Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys)))
(param Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) ))
(param Kh3_D (/ fraction_dead  (- time_to_hospitalization time_D_Sys)))
(param Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym )))
"""

    expand_testDelay_AsSymSys_str = """
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization ))
(param Kh3 (/ fraction_dead  time_to_hospitalization))

(param time_D_Sys @time_to_detection_Sys@)
(param Ksys_D (/ 1 time_D_Sys))
(param Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys)))
(param Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) ))
(param Kh3_D (/ fraction_dead  (- time_to_hospitalization time_D_Sys)))

(param time_D_Sym @time_to_detection_Sym@)
(param Ksym_D (/ 1 time_D_Sym))
(param Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym )))

(param time_D_As @time_to_detection_As@)
(param Kl_D (/ 1 time_D_As))
(param Kr_a_D (/ 1 (- recovery_time_asymp time_D_As )))
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


def write_migration_param(grpList) :
    x1 = range(1, len(grpList) + 1)
    x2 = range(1, len(grpList) + 1)
    param_str = ""
    for x1_i in x1 :
        param_str = param_str + "\n"
        for x2_i in x2 :
            #x1_i=1
            param_str = param_str + """\n(param toEMS_{x1_i}_from_EMS_{x2_i} @toEMS_{x1_i}_from_EMS_{x2_i}@)""".format(x1_i=x1_i, x2_i=x2_i)
    return (param_str)


def write_travel_reaction(grp, travelspeciesList=None):
    x1_i = int(grp.split("_")[1])
    x2 = list(range(1,12))
    x2 = [i for i in x2 if i != x1_i ]
    reaction_str = ""
    if travelspeciesList == None:
        travelspeciesList = ["S", "E", "As", "P"]

    for travelspecies in travelspeciesList:
        reaction_str = reaction_str + "\n"
        for x2_i in x2:
            # x1_i=1
            reaction_str = reaction_str + """\n(reaction {travelspecies}_travel_EMS_{x2_i}to{x1_i}  ({travelspecies}::EMS_{x2_i}) ({travelspecies}::EMS_{x1_i}) (* {travelspecies}::EMS_{x2_i} toEMS_{x1_i}_from_EMS_{x2_i} (/ N_EMS_{x2_i} (+ S::EMS_{x2_i} E::EMS_{x2_i} As::EMS_{x2_i} P::EMS_{x2_i} recovered_EMS_{x2_i}))))""".format(
                travelspecies=travelspecies, x1_i=x1_i, x2_i=x2_i)

    return (reaction_str)


def write_Ki_timevents(grp):
    grp = str(grp)
    grpout = sub(grp)
    params_str = """
(param Ki_{grp} @Ki_{grp}@)
(observe Ki_t_{grpout} Ki_{grp})
(time-event time_infection_import @time_infection_import_{grp}@ ((As::{grp} @initialAs_{grp}@) (S::{grp} (- S::{grp} @initialAs_{grp}@))))
""".format(grpout=grpout,grp=grp)
    params_str = params_str.replace("  ", " ")

    return (params_str)



def write_N_population(grpList):
    stringAll = ""
    for key in grpList:
        string1 = """\n(param N_{grp} (+ @speciesS_{grp}@ @initialAs_{grp}@) )""".format(grp=key)
        stringAll = stringAll + string1

    string2 = "\n(param N_All (+ " + repeat_string_by_grp('N_', grpList) + "))"
    stringAll = stringAll + string2

    return (stringAll)


def repeat_string_by_grp(fixedstring, grpList):
    stringAll = ""
    for grp in grpList:
        temp_string = " " + fixedstring + grp
        stringAll = stringAll + temp_string

    return stringAll


def write_All(grpList):
    obs_All_str = ""
    obs_All_str = obs_All_str + "\n(observe susceptible_All (+ " + repeat_string_by_grp('S::', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe exposed_All (+ " + repeat_string_by_grp('E::',  grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymptomatic_All (+ " + repeat_string_by_grp( 'asymptomatic_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymptomatic_det_All (+ " + repeat_string_by_grp( 'asymptomatic_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe presymptomatic_All (+ " + repeat_string_by_grp('P::', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe presymptomatic_det_All (+ " + repeat_string_by_grp( 'presymptomatic_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_mild_All (+ " + repeat_string_by_grp(  'symptomatic_mild_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_mild_det_All (+ " + repeat_string_by_grp(  'symptomatic_mild_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_severe_All (+ " + repeat_string_by_grp( 'symptomatic_severe_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_severe_det_All (+ " + repeat_string_by_grp( 'symptomatic_severe_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe hospitalized_All (+ " + repeat_string_by_grp('hospitalized_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe hospitalized_det_All (+ " + repeat_string_by_grp('hospitalized_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe critical_All (+ " + repeat_string_by_grp('critical_',    grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe critical_det_All (+ " + repeat_string_by_grp('critical_det_',    grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe deaths_All (+ " + repeat_string_by_grp('deaths_',   grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe deaths_det_All (+ " + repeat_string_by_grp('D3_det3::',  grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infected_All (+ " + repeat_string_by_grp('infected_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infected_det_All (+ " + repeat_string_by_grp('infected_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe recovered_All (+ " + repeat_string_by_grp('recovered_',    grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe recovered_det_All (+ " + repeat_string_by_grp('recovered_det_',    grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymp_cumul_All (+ " + repeat_string_by_grp( 'asymp_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymp_det_cumul_All (+ " + repeat_string_by_grp( 'asymp_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_mild_cumul_All (+ " + repeat_string_by_grp( 'symp_mild_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_mild_det_cumul_All (+ " + repeat_string_by_grp( 'symp_mild_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_severe_cumul_All (+ " + repeat_string_by_grp( 'symp_severe_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_severe_det_cumul_All  (+ " + repeat_string_by_grp(  'symp_severe_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe hosp_cumul_All (+ " + repeat_string_by_grp('hosp_cumul_',  grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe hosp_det_cumul_All (+ " + repeat_string_by_grp( 'hosp_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe crit_cumul_All (+ " + repeat_string_by_grp('crit_cumul_',   grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe crit_det_cumul_All (+ " + repeat_string_by_grp(  'crit_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe crit_det_All (+ " + repeat_string_by_grp('crit_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe detected_cumul_All (+ " + repeat_string_by_grp( 'detected_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe death_det_cumul_All (+ " + repeat_string_by_grp('death_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infected_cumul_All (+ " + repeat_string_by_grp('infected_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infectious_det_All (+ " + repeat_string_by_grp('infectious_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infectious_undet_All (+ " + repeat_string_by_grp( 'infectious_undet_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infectious_det_symp_All (+ " + repeat_string_by_grp('infectious_det_symp_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infectious_det_AsP_All (+ " + repeat_string_by_grp( 'infectious_det_AsP_', grpList) + "))"

    obs_All_str = obs_All_str + "\n(observe prevalence_All (+ " + repeat_string_by_grp( 'prevalence_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe seroprevalence_All (+ " + repeat_string_by_grp( 'seroprevalence_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe prevalence_det_All (+ " + repeat_string_by_grp( 'prevalence_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe seroprevalence_det_All (+ " + repeat_string_by_grp( 'seroprevalence_det_', grpList) + "))"

    return (obs_All_str)


def write_Custom_Groups(grpDic):

    def write_Custom_Group_Sub(obs_customGrp, grpList) :
        obs_customGrp_str = ""
        obs_customGrp_str = obs_customGrp_str + """\n(observe susceptible_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('S::', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe exposed_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('E::',  grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe asymptomatic_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'asymptomatic_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe asymptomatic_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'asymptomatic_det_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe presymptomatic_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('P::', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe presymptomatic_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'presymptomatic_det_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe symptomatic_mild_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp(  'symptomatic_mild_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe symptomatic_mild_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp(  'symptomatic_mild_det_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe symptomatic_severe_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'symptomatic_severe_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe symptomatic_severe_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'symptomatic_severe_det_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe hospitalized_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('hospitalized_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe hospitalized_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('hospitalized_det_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe critical_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('critical_',    grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe critical_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('critical_det_',    grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe deaths_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('deaths_',   grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe deaths_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('D3_det3::',  grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe infected_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('infected_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe infected_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('infected_det_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe recovered_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('recovered_',    grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe recovered_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('recovered_det_',    grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe asymp_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'asymp_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe asymp_det_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'asymp_det_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe symp_mild_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'symp_mild_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe symp_mild_det_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'symp_mild_det_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe symp_severe_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'symp_severe_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe symp_severe_det_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp(  'symp_severe_det_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe hosp_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('hosp_cumul_',  grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe hosp_det_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'hosp_det_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe crit_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('crit_cumul_',   grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe crit_det_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp(  'crit_det_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe crit_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('crit_det_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe detected_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'detected_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe death_det_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('death_det_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe infected_cumul_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('infected_cumul_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe infectious_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('infectious_det_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe infectious_undet_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'infectious_undet_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe infectious_det_symp_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp('infectious_det_symp_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe infectious_det_AsP_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'infectious_det_AsP_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe prevalence_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'prevalence_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe seroprevalence_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'seroprevalence_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe prevalence_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'prevalence_det_', grpList) + "))"
        obs_customGrp_str = obs_customGrp_str + """\n(observe seroprevalence_det_{obs_customGrp} (+ """.format(obs_customGrp=obs_customGrp) + repeat_string_by_grp( 'seroprevalence_det_', grpList) + "))"

        return obs_customGrp_str

    obs_All_str = ""
    for key in grpDic.keys() :

        temp_str = write_Custom_Group_Sub(obs_customGrp=key, grpList=grpDic[key] )
        obs_All_str = obs_All_str + temp_str

    return (obs_All_str)


def write_reactions(grp, expandModel=None):
    grp = str(grp)

    reaction_str_I = """
(reaction exposure_{grp}   (S::{grp}) (E::{grp}) (* Ki_{grp} S::{grp} (/  (+ infectious_undet_{grp} (* infectious_det_symp_{grp} reduced_inf_of_det_cases) (* infectious_det_AsP_{grp} reduced_inf_of_det_cases_ct)) N_{grp} )))
""".format(grp=grp)

    reaction_str_III = """
(reaction recovery_H1_{grp}   (H1::{grp})   (RH1::{grp})   (* Kr_h H1::{grp}))
(reaction recovery_C2_{grp}   (C2::{grp})   (RC2::{grp})   (* Kr_c C2::{grp}))
(reaction recovery_H1_det3_{grp}   (H1_det3::{grp})   (RH1_det3::{grp})   (* Kr_h H1_det3::{grp}))
(reaction recovery_C2_det3_{grp}   (C2_det3::{grp})   (RC2_det3::{grp})   (* Kr_c C2_det3::{grp}))
    """.format(grp=grp)

    expand_base_str = """
(reaction infection_asymp_undet_{grp}  (E::{grp})   (As::{grp})   (* Kl E::{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (E::{grp})   (As_det1::{grp})   (* Kl E::{grp} d_As))
(reaction presymptomatic_{grp} (E::{grp})   (P::{grp})   (* Ks E::{grp} (- 1 d_P)))
(reaction presymptomatic_{grp} (E::{grp})   (P_det::{grp})   (* Ks E::{grp} d_P))

(reaction mild_symptomatic_undet_{grp} (P::{grp})  (Sym::{grp}) (* Ksym P::{grp} (- 1 d_Sym_{grp})))
(reaction mild_symptomatic_det_{grp} (P::{grp})  (Sym_det2::{grp}) (* Ksym P::{grp} d_Sym_{grp}))
(reaction severe_symptomatic_undet_{grp} (P::{grp})  (Sys::{grp})  (* Ksys P::{grp} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{grp} (P::{grp})  (Sys_det3::{grp})  (* Ksys P::{grp} d_Sys))

(reaction mild_symptomatic_det_{grp} (P_det::{grp})  (Sym_det2::{grp}) (* Ksym P_det::{grp}))
(reaction severe_symptomatic_det_{grp} (P_det::{grp})  (Sys_det3::{grp})  (* Ksys P_det::{grp} ))

(reaction hospitalization_1_{grp}   (Sys::{grp})   (H1::{grp})   (* Kh1 Sys::{grp}))
(reaction hospitalization_2_{grp}   (Sys::{grp})   (H2::{grp})   (* Kh2 Sys::{grp}))
(reaction hospitalization_3_{grp}   (Sys::{grp})   (H3::{grp})   (* Kh3 Sys::{grp}))
(reaction critical_2_{grp}   (H2::{grp})   (C2::{grp})   (* Kc H2::{grp}))
(reaction critical_3_{grp}   (H3::{grp})   (C3::{grp})   (* Kc H3::{grp}))
(reaction death_{grp}   (C3::{grp})   (D3::{grp})   (* Km C3::{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3::{grp})   (H1_det3::{grp})   (* Kh1 Sys_det3::{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3::{grp})   (H2_det3::{grp})   (* Kh2 Sys_det3::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3::{grp})   (H3_det3::{grp})   (* Kh3 Sys_det3::{grp}))
(reaction critical_2_det2_{grp}   (H2_det3::{grp})   (C2_det3::{grp})   (* Kc H2_det3::{grp}))
(reaction critical_3_det2_{grp}   (H3_det3::{grp})   (C3_det3::{grp})   (* Kc H3_det3::{grp}))
(reaction death_det3_{grp}   (C3_det3::{grp})   (D3_det3::{grp})   (* Km C3_det3::{grp}))

(reaction recovery_As_{grp}   (As::{grp})   (RAs::{grp})   (* Kr_a As::{grp}))
(reaction recovery_As_det_{grp} (As_det1::{grp})   (RAs_det1::{grp})   (* Kr_a As_det1::{grp}))

(reaction recovery_Sym_{grp}   (Sym::{grp})   (RSym::{grp})   (* Kr_m  Sym::{grp}))
(reaction recovery_Sym_det2_{grp}   (Sym_det2::{grp})   (RSym_det2::{grp})   (* Kr_m  Sym_det2::{grp}))
""".format(grp=grp)


    expand_testDelay_SymSys_str = """
(reaction infection_asymp_undet_{grp}  (E::{grp})   (As::{grp})   (* Kl E::{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (E::{grp})   (As_det1::{grp})   (* Kl E::{grp} d_As))
(reaction presymptomatic_{grp} (E::{grp})   (P::{grp})   (* Ks E::{grp}))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{grp} (P::{grp})  (Sym_preD::{grp}) (* Ksym P::{grp}))
(reaction severe_symptomatic_{grp} (P::{grp})  (Sys_preD::{grp})  (* Ksys P::{grp}))

; never detected 
(reaction mild_symptomatic_undet_{grp} (Sym_preD::{grp})  (Sym::{grp}) (* Ksym_D Sym_preD::{grp} (- 1 d_Sym_{grp})))
(reaction severe_symptomatic_undet_{grp} (Sys_preD::{grp})  (Sys::{grp})  (* Ksys_D Sys_preD::{grp} (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det_{grp} (Sym_preD::{grp})  (Sym_det2::{grp}) (* Ksym_D Sym_preD::{grp} d_Sym_{grp}))
(reaction severe_symptomatic_det_{grp} (Sys_preD::{grp})  (Sys_det3::{grp})  (* Ksys_D Sys_preD::{grp} d_Sys))

(reaction hospitalization_1_{grp}   (Sys::{grp})   (H1::{grp})   (* Kh1_D Sys::{grp}))
(reaction hospitalization_2_{grp}   (Sys::{grp})   (H2::{grp})   (* Kh2_D Sys::{grp}))
(reaction hospitalization_3_{grp}   (Sys::{grp})   (H3::{grp})   (* Kh3_D Sys::{grp}))
(reaction critical_2_{grp}   (H2::{grp})   (C2::{grp})   (* Kc H2::{grp}))
(reaction critical_3_{grp}   (H3::{grp})   (C3::{grp})   (* Kc H3::{grp}))
(reaction death_{grp}   (C3::{grp})   (D3::{grp})   (* Km C3::{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3::{grp})   (H1_det3::{grp})   (* Kh1_D Sys_det3::{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3::{grp})   (H2_det3::{grp})   (* Kh2_D Sys_det3::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3::{grp})   (H3_det3::{grp})   (* Kh3_D Sys_det3::{grp}))
(reaction critical_2_det2_{grp}   (H2_det3::{grp})   (C2_det3::{grp})   (* Kc H2_det3::{grp}))
(reaction critical_3_det2_{grp}   (H3_det3::{grp})   (C3_det3::{grp})   (* Kc H3_det3::{grp}))
(reaction death_det3_{grp}   (C3_det3::{grp})   (D3_det3::{grp})   (* Km C3_det3::{grp}))

(reaction recovery_As_{grp}   (As::{grp})   (RAs::{grp})   (* Kr_a As::{grp}))
(reaction recovery_As_det_{grp} (As_det1::{grp})   (RAs_det1::{grp})   (* Kr_a As_det1::{grp}))
(reaction recovery_Sym_{grp}   (Sym::{grp})   (RSym::{grp})   (* Kr_m_D  Sym::{grp}))
(reaction recovery_Sym_det2_{grp}   (Sym_det2::{grp})   (RSym_det2::{grp})   (* Kr_m_D  Sym_det2::{grp}))

""".format(grp=grp)


    expand_testDelay_AsSymSys_str = """
(reaction infection_asymp_det_{grp}  (E::{grp})   (As_preD::{grp})   (* Kl E::{grp}))
(reaction infection_asymp_undet_{grp}  (As_preD::{grp})   (As::{grp})   (* Kl_D As_preD::{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (As_preD::{grp})   (As_det1::{grp})   (* Kl_D As_preD::{grp} d_As))

(reaction presymptomatic_{grp} (E::{grp})   (P::{grp})   (* Ks  E::{grp} (- 1 d_P)))
(reaction presymptomatic_{grp} (E::{grp})   (P_det::{grp})   (* Ks  E::{grp} d_P))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{grp} (P::{grp})  (Sym_preD::{grp}) (* Ksym P::{grp}))
(reaction severe_symptomatic_{grp} (P::{grp})  (Sys_preD::{grp})  (* Ksys P::{grp}))
																   
; never detected 
(reaction mild_symptomatic_undet_{grp} (Sym_preD::{grp})  (Sym::{grp}) (* Ksym_D Sym_preD::{grp} (- 1 d_Sym_{grp})))
(reaction severe_symptomatic_undet_{grp} (Sys_preD::{grp})  (Sys::{grp})  (* Ksys_D Sys_preD::{grp} (- 1 d_Sys)))

; new detections  - time to detection is subtracted from hospital time
(reaction mild_symptomatic_det_{grp} (Sym_preD::{grp})  (Sym_det2a::{grp}) (* Ksym_D Sym_preD::{grp} d_Sym_{grp}))
(reaction severe_symptomatic_det_{grp} (Sys_preD::{grp})  (Sys_det3a::{grp})  (* Ksys_D Sys_preD::{grp} d_Sys))

; developing symptoms - already detected, same time to symptoms as in master emodl
(reaction mild_symptomatic_det_{grp} (P_det::{grp})  (Sym_det2b::{grp}) (* Ksym  P_det::{grp}))
(reaction severe_symptomatic_det_{grp} (P_det::{grp})  (Sys_det3b::{grp})  (* Ksys  P_det::{grp} ))

(reaction hospitalization_1_{grp}  (Sys::{grp})   (H1::{grp})   (* Kh1_D Sys::{grp}))
(reaction hospitalization_2_{grp}   (Sys::{grp})   (H2::{grp})   (* Kh2_D Sys::{grp}))
(reaction hospitalization_3_{grp}   (Sys::{grp})   (H3::{grp})   (* Kh3_D Sys::{grp}))
(reaction critical_2_{grp}  (H2::{grp})   (C2::{grp})   (* Kc H2::{grp}))
(reaction critical_3_{grp}   (H3::{grp})   (C3::{grp})   (* Kc H3::{grp}))
(reaction death_{grp}   (C3::{grp})   (D3::{grp})   (* Km C3::{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3a::{grp})   (H1_det3::{grp})   (* Kh1_D Sys_det3a::{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3a::{grp})   (H2_det3::{grp})   (* Kh2_D Sys_det3a::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3a::{grp})   (H3_det3::{grp})   (* Kh3_D Sys_det3a::{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3b::{grp})   (H1_det3::{grp})   (* Kh1 Sys_det3b::{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3b::{grp})   (H2_det3::{grp})   (* Kh2 Sys_det3b::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3b::{grp})   (H3_det3::{grp})   (* Kh3 Sys_det3b::{grp}))

(reaction critical_2_det2_{grp}   (H2_det3::{grp})   (C2_det3::{grp})   (* Kc H2_det3::{grp}))
(reaction critical_3_det2_{grp}   (H3_det3::{grp})   (C3_det3::{grp})   (* Kc H3_det3::{grp}))
(reaction death_det3_{grp}   (C3_det3::{grp})   (D3_det3::{grp})   (* Km C3_det3::{grp}))

(reaction recovery_As_{grp}   (As::{grp})   (RAs::{grp})   (* Kr_a_D As::{grp}))
(reaction recovery_As_det_{grp} (As_det1::{grp})   (RAs_det1::{grp})   (* Kr_a_D As_det1::{grp}))

(reaction recovery_Sym_{grp}   (Sym::{grp})   (RSym::{grp})   (* Kr_m_D  Sym::{grp}))
(reaction recovery_Sym_det2a_{grp}   (Sym_det2a::{grp})   (RSym_det2::{grp})   (* Kr_m_D  Sym_det2a::{grp}))
(reaction recovery_Sym_det2b_{grp}   (Sym_det2b::{grp})   (RSym_det2::{grp})   (* Kr_m  Sym_det2b::{grp}))
 """.format(grp=grp)

    if expandModel ==None :
        reaction_str = reaction_str_I + expand_base_str + reaction_str_III
    if expandModel == "testDelay_SymSys" or  expandModel == "uniformtestDelay" :
        reaction_str = reaction_str_I + expand_testDelay_SymSys_str + reaction_str_III
    if expandModel == 'testDelay_AsSymSys':
        reaction_str = reaction_str_I + expand_testDelay_AsSymSys_str + reaction_str_III
        
    reaction_str = reaction_str.replace("  ", " ")

    return (reaction_str)


def define_change_detection_and_isolation(grpList=None,
                                          reduced_inf_of_det_cases=True,
                                          d_As=True,
                                          d_P=True,
                                          d_Sym_ct=True,
                                          d_Sym_grp=False,
                                          d_Sym_grp_option=None):

    """ Write the emodl chunk for changing detection rates and reduced infectiousness
    to approximate contact tracing or improved health system interventions.
    Helper function called by write_interventions

    Parameters
    ----------
    grpList: list
        List that contains the groupnames for which parameters are repeated
    reduced_inf_of_det_cases : boolean
        Boolean to add a change in infectiousness of As and P detected cases if set to True
    d_As : boolean
        Boolean to add a change in detection of asymptomatic cases if set to True
    d_P : boolean
        Boolean to add a change in detection of presymptomatic cases if set to True
    d_Sym_ct : boolean
        Boolean to add a change in detection of symptomatic cases if set to True
    d_Sym_grp : boolean
        Boolean to denote whether dSym is group specific or generic
    d_Sym_grp_option : character
        Chracter used to flag which increase option to select, possible characters are:
        increase_to_grp_target (select for each group a specific target to reach),
        increase_to_common_target (use same target for all groups),
        common_increase (rather than replacing the old detection level, increase by a specified percentage),
        grp_specific_increase (define a group specific increase, i.e. group 1 by 10%, group 2 by 50%).
        Default is increase_to_common_target
    """

    observe_str = """
(observe d_As_t d_As)
(observe d_P_t d_P)
"""

    reduced_inf_of_det_cases_str = ""
    d_As_str = ""
    d_P_str = ""
    d_Sym_ct_param_str = ""
    d_Sym_ct_str = ""

    if reduced_inf_of_det_cases:
        reduced_inf_of_det_cases_str = """(reduced_inf_of_det_cases_ct @reduced_inf_of_det_cases_ct1@ )"""
    if d_As:
        d_As_str = """(d_As @d_AsP_ct1@)"""
    if d_P:
        d_P_str = """(d_P @d_AsP_ct1@)"""

    if d_Sym_ct:

        ### Simple, not group specific
        if d_Sym_ct and not d_Sym_grp:
            d_Sym_ct_str = """(d_Sym @d_Sym_ct1@)"""

        ### Group specific
        if d_Sym_grp:

            for grp in grpList:

                if d_Sym_grp_option == 'increase_to_grp_target':
                    d_Sym_ct_param_str = d_Sym_ct_param_str + """(param d_Sym_ct1_{grp} @d_Sym_ct1_{grp}@)""".format(
                        grp=grp)

                if d_Sym_grp_option == 'increase_to_common_target':
                    d_Sym_ct_param_str = d_Sym_ct_param_str + "\n" + """(param d_Sym_ct1_{grp} @d_Sym_ct1@)""".format(
                        grp=grp)

                if d_Sym_grp_option == 'common_increase':
                    d_Sym_ct_param_str = d_Sym_ct_param_str + "\n" + """(param d_Sym_ct1_{grp} (+ @d_Sym_change5_{grp}@ (* @d_Sym_change5_{grp}@ @d_Sym_ct1@ )))""".format(
                        grp=grp)

                if d_Sym_grp_option == 'grp_specific_increase':
                    d_Sym_ct_param_str = d_Sym_ct_param_str + "\n" + """(param d_Sym_ct1_{grp} (+ @d_Sym_change5_{grp}@ (* @d_Sym_change5_{grp}@ @d_Sym_ct1_{grp}@ )))""".format(
                        grp=grp)

                d_Sym_ct_str = d_Sym_ct_str + """(d_Sym_{grp} d_Sym_ct1_{grp})""".format(grp=grp)

    observe_str = observe_str + "\n" + d_Sym_ct_param_str
    change_param_str = reduced_inf_of_det_cases_str + d_As_str + d_P_str + d_Sym_ct_str
    time_event_str = """(time-event contact_tracing_start @contact_tracing_start_1@ ( {change_param} ))""".format(change_param=change_param_str)

    contactTracing_str = observe_str + "\n" + time_event_str

    return (contactTracing_str)

def write_interventions(grpList, total_string, scenarioName, change_testDelay=None, trigger_channel=None) :

    param_change_str = """
;(observe d_Sys_t d_Sys)
(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@)))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@)))
(time-event detection4 @detection_time_4@ ((d_Sys @d_Sys_incr4@)))
(time-event detection5 @detection_time_5@ ((d_Sys @d_Sys_incr5@)))
(time-event detection6 @detection_time_6@ ((d_Sys @d_Sys_incr6@)))
(time-event detection5 @detection_time_7@ ((d_Sys @d_Sys_incr7@)))


;(observe frac_crit_t fraction_critical)
(time-event frac_crit_adjust1 @crit_time_1@ ((fraction_critical @fraction_critical_incr1@) (fraction_hospitalized (- 1 (+ @fraction_critical_incr1@ @fraction_dead@))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) ))  
(time-event frac_crit_adjust2 @crit_time_2@ ((fraction_critical @fraction_critical_incr2@) (fraction_hospitalized (- 1 (+ @fraction_critical_incr2@ @fraction_dead@))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) ))
(time-event frac_crit_adjust3 @crit_time_3@ ((fraction_critical @fraction_critical_incr3@) (fraction_hospitalized (- 1 (+ @fraction_critical_incr3@ @fraction_dead@))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) )) 
"""

    socialDistance_change_str = ""
    for grp in grpList:
        temp_str = """
(param Ki_red1_{grp} (* Ki_{grp} @social_multiplier_1_{grp}@))
(param Ki_red2_{grp} (* Ki_{grp} @social_multiplier_2_{grp}@))
(param Ki_red3_{grp} (* Ki_{grp} @social_multiplier_3_{grp}@))
(param Ki_red4_{grp} (* Ki_{grp} @social_multiplier_4_{grp}@))
(param Ki_red5_{grp} (* Ki_{grp} @social_multiplier_5_{grp}@))
(param Ki_red6_{grp} (* Ki_{grp} @social_multiplier_6_{grp}@))

(param backtonormal_multiplier_1_{grp}  (/ (- Ki_red5_{grp}  Ki_red4_{grp} ) (- Ki_{grp} Ki_red4_{grp} ) ) )  
(observe backtonormal_multiplier_1_{grp} backtonormal_multiplier_1_{grp})

(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki_{grp} Ki_red1_{grp})))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki_{grp} Ki_red2_{grp})))
(time-event socialDistance_start @socialDistance_time3@ ((Ki_{grp} Ki_red3_{grp})))
(time-event socialDistance_change @socialDistance_time4@ ((Ki_{grp} Ki_red4_{grp})))
(time-event socialDistance_change_2 @socialDistance_time5@ ((Ki_{grp} Ki_red5_{grp})))
(time-event socialDistance_change_3 @socialDistance_time6@ ((Ki_{grp} Ki_red6_{grp})))
            """.format(grp=grp)
        socialDistance_change_str = socialDistance_change_str + temp_str

    rollback_str = ""
    for grp in grpList:
        temp_str = """
(time-event socialDistance_change_rollback @socialDistance_rollback_time@ ((Ki_{grp} Ki_red4_{grp})))
                """.format(grp=grp)
        rollback_str = rollback_str + temp_str


    rollbacktriggered_str = ""
    for grp in grpList:
        temp_str = """
(state-event rollbacktrigger_{grp} (and (> time @today@) (> {channel}_{grp} (* @trigger_{grp}@ @capacity_multiplier@)) ) ((Ki_{grp} Ki_red4_{grp})))
                    """.format(channel=trigger_channel,grp=grp)
        rollbacktriggered_str = rollbacktriggered_str + temp_str

    rollbacktriggered_delay_str = ""
    for grp in grpList:
        temp_str = """
(param time_of_trigger_{grp} 10000)
(state-event rollbacktrigger_{grp} (and (> time @today@) (> critical_det_{grp} (* @trigger_{grp}@ @capacity_multiplier@)) ) ((time_of_trigger_{grp} time)))
(func time_since_trigger_{grp} (- time time_of_trigger_{grp}))
(state-event apply_rollback_{grp} (> (- time_since_trigger_{grp} @trigger_delay_days@) 0) ((Ki_{grp} Ki_red4_{grp})))   
(observe triggertime_{grp} time_since_trigger_{grp})
                   """.format(channel=trigger_channel,grp=grp)
        rollbacktriggered_delay_str = rollbacktriggered_delay_str + temp_str
        
    d_Sym_change_str = ""
    for grp in grpList:
        grpout = sub(grp)
        temp_str = """
(param d_Sym_{grp} @d_Sym_{grp}@)
(observe d_Sym_t_{grpout} d_Sym_{grp})

(time-event d_Sym_change1 @d_Sym_change_time_1@ ((d_Sym_{grp} @d_Sym_change1_{grp}@)))
(time-event d_Sym_change2 @d_Sym_change_time_2@ ((d_Sym_{grp} @d_Sym_change2_{grp}@)))
(time-event d_Sym_change3 @d_Sym_change_time_3@ ((d_Sym_{grp} @d_Sym_change3_{grp}@)))
(time-event d_Sym_change4 @d_Sym_change_time_4@ ((d_Sym_{grp} @d_Sym_change4_{grp}@)))
(time-event d_Sym_change5 @d_Sym_change_time_5@ ((d_Sym_{grp} @d_Sym_change5_{grp}@)))
            """.format(grpout=grpout,grp=grp)
        d_Sym_change_str = d_Sym_change_str + temp_str
        
    interventionSTOP_str = ""
    for grp in grpList :
        temp_str = """
(param Ki_back_{grp} (* Ki_{grp} @backtonormal_multiplier@))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{grp} Ki_back_{grp})))
        """.format(grp=grp)
        interventionSTOP_str = interventionSTOP_str + temp_str

# % change from lowest transmission level - immediate
# starting point is lowest level of transmission  Ki_red4
    interventionSTOP_adj_str = ""
    for grp in grpList :
        temp_str = """
(param Ki_back_{grp} (+ Ki_red4_{grp} (* @backtonormal_multiplier@ (- Ki_{grp} Ki_red4_{grp}))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{grp} Ki_back_{grp})))
        """.format(grp=grp)
        interventionSTOP_adj_str = interventionSTOP_adj_str + temp_str

# % change from current transmission level - immediate
# starting point is current level of transmission  Ki_red5
    interventionSTOP_adj2_str = ""
    for grp in grpList :
        temp_str = """
(param Ki_back_{grp} (+ Ki_red6_{grp} (* @backtonormal_multiplier@ (- Ki_{grp} Ki_red6_{grp}))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{grp} Ki_back_{grp})))
        """.format(grp=grp)
        interventionSTOP_adj2_str = interventionSTOP_adj2_str + temp_str


# gradual reopening from 'lowest' transmission level,  Ki_red5 == Ki_back1
    gradual_reopening_str = ""
    for grp in grpList:
        temp_str = """
(param backtonormal_multiplier_1_adj_{grp}  (- @backtonormal_multiplier@ backtonormal_multiplier_1_{grp} ))
(observe backtonormal_multiplier_1_adj_{grp}  backtonormal_multiplier_1_adj_{grp})

(param Ki_back2_{grp} (+ Ki_red5_{grp} (* backtonormal_multiplier_1_adj_{grp} 0.3333 (- Ki_{grp} Ki_red4_{grp}))))
(param Ki_back3_{grp} (+ Ki_red5_{grp} (* backtonormal_multiplier_1_adj_{grp} 0.6666 (- Ki_{grp} Ki_red4_{grp}))))
(param Ki_back4_{grp} (+ Ki_red5_{grp} (* backtonormal_multiplier_1_adj_{grp} 1.00 (- Ki_{grp} Ki_red4_{grp}))))
(time-event gradual_reopening2 @gradual_reopening_time1@ ((Ki_{grp} Ki_back2_{grp})))
(time-event gradual_reopening3 @gradual_reopening_time2@ ((Ki_{grp} Ki_back3_{grp})))
(time-event gradual_reopening4 @gradual_reopening_time3@ ((Ki_{grp} Ki_back4_{grp})))
        """.format(grp=grp)
        gradual_reopening_str = gradual_reopening_str + temp_str
            
# gradual reopening from 'current' transmission level 
    gradual_reopening2_str = ""
    for grp in grpList:
        temp_str = """
(param Ki_back1_{grp} (+ Ki_red6_{grp} (* @reopening_multiplier_4@ 0.25 (- Ki_{grp} Ki_red6_{grp}))))
(param Ki_back2_{grp} (+ Ki_red6_{grp} (* @reopening_multiplier_4@ 0.50 (- Ki_{grp} Ki_red6_{grp}))))
(param Ki_back3_{grp} (+ Ki_red6_{grp} (* @reopening_multiplier_4@ 0.75 (- Ki_{grp} Ki_red6_{grp}))))
(param Ki_back4_{grp} (+ Ki_red6_{grp} (* @reopening_multiplier_4@ 1.00 (- Ki_{grp} Ki_red6_{grp}))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki_{grp} Ki_back1_{grp})))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki_{grp} Ki_back2_{grp})))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki_{grp} Ki_back3_{grp})))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki_{grp} Ki_back4_{grp})))
        """.format(grp=grp)
        gradual_reopening2_str = gradual_reopening2_str + temp_str

# gradual reopening from 'current' transmission level with region-specific reopening
    gradual_reopening3_str = ""
    for grp in grpList:
        temp_str = """
(param Ki_back1_{grp} (+ Ki_red6_{grp} (* @reopening_multiplier_4_{grp}@ 0.25 (- Ki_{grp} Ki_red6_{grp}))))
(param Ki_back2_{grp} (+ Ki_red6_{grp} (* @reopening_multiplier_4_{grp}@ 0.50 (- Ki_{grp} Ki_red6_{grp}))))
(param Ki_back3_{grp} (+ Ki_red6_{grp} (* @reopening_multiplier_4_{grp}@ 0.75 (- Ki_{grp} Ki_red6_{grp}))))
(param Ki_back4_{grp} (+ Ki_red6_{grp} (* @reopening_multiplier_4_{grp}@ 1.00 (- Ki_{grp} Ki_red6_{grp}))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki_{grp} Ki_back1_{grp})))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki_{grp} Ki_back2_{grp})))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki_{grp} Ki_back3_{grp})))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki_{grp} Ki_back4_{grp})))
        """.format(grp=grp)
        gradual_reopening3_str = gradual_reopening3_str + temp_str


    improveHS_str = define_change_detection_and_isolation(grpList=grpList,
                                    reduced_inf_of_det_cases = False,
                                    d_As = False,
                                    d_P = False ,
                                    d_Sym_ct = True,
                                    d_Sym_grp = True,
                                    d_Sym_grp_option = 'increase_to_common_target')


    contactTracing_str = define_change_detection_and_isolation(grpList=grpList,
                                    reduced_inf_of_det_cases = True,
                                    d_As = True,
                                    d_P = True ,
                                    d_Sym_ct = False,
                                    d_Sym_grp = False,
                                    d_Sym_grp_option = None)


    contactTracing_improveHS_str = define_change_detection_and_isolation(grpList=grpList,
                                    reduced_inf_of_det_cases = True,
                                    d_As = True,
                                    d_P = True,
                                    d_Sym_ct = True,
                                    d_Sym_grp = True,
                                    d_Sym_grp_option = 'increase_to_common_target')


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

    fittedTimeEvents_str = param_change_str + socialDistance_change_str + d_Sym_change_str
   
    if scenarioName == "interventionStop" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_str)
    if scenarioName == "interventionSTOP_adj" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj_str)
    if scenarioName == "interventionSTOP_adj2":
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj2_str)
    if scenarioName == "gradual_reopening" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening_str)
    if scenarioName == "gradual_reopening2" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str)
    if scenarioName == "gradual_reopening3" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening3_str)
    if scenarioName == "continuedSIP" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str)
    if scenarioName == "rollback" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + rollback_str)
    if scenarioName == "reopen_rollback":
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj2_str + rollback_str)
    if scenarioName == "reopen_contactTracing" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + contactTracing_str)
    if scenarioName == "reopen_contactTracing_improveHS" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + contactTracing_improveHS_str)
    if scenarioName == "reopen_improveHS" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + improveHS_str)
    if scenarioName == "contactTracing" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + contactTracing_str)
    if scenarioName == "contactTracing_improveHS" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + contactTracing_improveHS_str)
    if scenarioName == "improveHS" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + improveHS_str)
    if scenarioName == "rollbacktriggered" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + rollbacktriggered_str)
    if scenarioName == "rollbacktriggered_delay" :
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening3_str + rollbacktriggered_delay_str)

   # if scenarioName == "gradual_contactTracing" :
   #    total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + contactTracing_gradual_str)


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
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_Sym_str )
        if change_testDelay == "SymSys" :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)
        if change_testDelay == "AsSymSys" :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)


    return (total_string)


###stringing all of my functions together to make the file:

def generate_emodl(grpList, file_output, expandModel, add_interventions, add_migration=True, change_testDelay =None, trigger_channel=None, observe_customGroups = False, grpDic = None):
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

    for grp in grpList:
        total_string = total_string + "\n(locale site-{})\n".format(grp)
        total_string = total_string + "(set-locale site-{})\n".format(grp)
        total_string = total_string + write_species(grp, expandModel)
        functions = write_functions(grp, expandModel)
        observe_string = observe_string + write_observe(grp, expandModel)
        if (add_migration):
            reaction_string = reaction_string + write_travel_reaction(grp)
        reaction_string = reaction_string + write_reactions(grp, expandModel)
        functions_string = functions_string + functions
        param_string = param_string + write_Ki_timevents(grp)

    param_string =  write_params(expandModel) + param_string +  write_N_population(grpList)
    if(add_migration) :
        param_string = param_string + write_migration_param(grpList)
    functions_string = functions_string + write_All(grpList)
    
    if(observe_customGroups) :
        if grpDic == None :
            grpDic = {'northcentral' : ['EMS_1', 'EMS_2'],
               'northeast' : ['EMS_7', 'EMS_8', 'EMS_9', 'EMS_10', 'EMS_11'],
               'central' : ['EMS_3', 'EMS_6'],
               'southern': ['EMS_4', 'EMS_5']}
               
        functions_string = functions_string + write_Custom_Groups(grpDic)
    
    intervention_string = ";[INTERVENTIONS]\n;[ADDITIONAL_TIMEEVENTS]"

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string +  '\n\n' + reaction_string + '\n\n' + footer_str

    ### Custom adjustments for EMS 6 (earliest start date)
    total_string = total_string.replace('(species As::EMS_6 0)', '(species As::EMS_6 1)')
    ### Add interventions (optional)
    if add_interventions != None :
        total_string = write_interventions(grpList, total_string, add_interventions, change_testDelay, trigger_channel)

    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


if __name__ == '__main__':
    ems_grp = ['EMS_1', 'EMS_2', 'EMS_3', 'EMS_4', 'EMS_5', 'EMS_6', 'EMS_7', 'EMS_8', 'EMS_9', 'EMS_10', 'EMS_11']

    ### Emodls without migration between EMS areas
    generateBaselineReopeningEmodls = True
    if generateBaselineReopeningEmodls:
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='continuedSIP', add_migration=False, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='rollback', add_migration=False, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_rollback.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='reopen_rollback', add_migration=False, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_reopen_rollback.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='interventionSTOP_adj', add_migration=False, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_interventionSTOPadj.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions=None, add_migration=False, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_neverSIP.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='interventionStop', add_migration=False,  observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_interventionStop.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='gradual_reopening2', add_migration=False, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_gradual_reopening.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='gradual_reopening3', add_migration=False, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_gradual_reopening_region_specific.emodl'))

        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='rollbacktriggered', add_migration=False, observe_customGroups = False, trigger_channel = "critical_det", file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_criticaldet_triggeredrollback.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='rollbacktriggered', add_migration=False, observe_customGroups = False, trigger_channel = "hospitalized_det", file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_hospdet_triggeredrollback.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='rollbacktriggered_delay', add_migration=False, observe_customGroups = False, trigger_channel = "critical_det", file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_criticaldet_triggeredrollbackdelay.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='rollbacktriggered_delay', add_migration=False, observe_customGroups = False, trigger_channel = "hospitalized_det", file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_hospdet_triggeredrollbackdelay.emodl'))


    generateImprovedDetectionEmodls = True
    if generateImprovedDetectionEmodls:
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys",  add_interventions='continuedSIP', add_migration=False, observe_customGroups = False, change_testDelay = "Sym", file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_changeTD.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='improveHS', add_migration=False,  observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_dSym.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='improveHS', add_migration=False, change_testDelay = "Sym", observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_dSym_TD.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='contactTracing', add_migration=False,  observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_dAsP.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='contactTracing', add_migration=False, change_testDelay = "AsSym", observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_dAsP_TD.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='contactTracing_improveHS', add_migration=False,  observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_dAsPSym.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='contactTracing_improveHS', add_migration=False, change_testDelay = "AsSym", observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_dAsPSym_TD.emodl'))

    generateImprovedDetectionEmodls_withReopening = True
    if generateImprovedDetectionEmodls_withReopening:
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys",  add_interventions='gradual_reopening2', add_migration=False, observe_customGroups = False, change_testDelay = "Sym", file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_reopen_changeTD.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='reopen_improveHS', add_migration=False,  observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_reopen_dSym.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='reopen_improveHS', add_migration=False, change_testDelay = "Sym", observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_reopen_dSym_TD.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='reopen_contactTracing', add_migration=False,  observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_reopen_dAsP.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='reopen_contactTracing', add_migration=False, change_testDelay = "AsSym", observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_reopen_dAsP_TD.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='reopen_contactTracing_improveHS', add_migration=False,  observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_reopen_dAsPSym.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='reopen_contactTracing_improveHS', add_migration=False, change_testDelay = "AsSym", observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_reopen_dAsPSym_TD.emodl'))


    ### Emodls with migration between EMS areas
    generateMigrationEmodls =False
    if generateMigrationEmodls:
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='continuedSIP', add_migration=True, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='interventionSTOP_adj', add_migration=True, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_interventionSTOPadj.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions=None, add_migration=True, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_neverSIP.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='interventionStop', add_migration=True,  observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_interventionStop.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='gradual_reopening', add_migration=True, observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_gradual_reopening.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='contactTracing', add_migration=True,  observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_contactTracing.emodl'))
        generate_emodl(grpList=ems_grp, expandModel="testDelay_AsSymSys", add_interventions='contactTracing', add_migration=True, change_testDelay = "AsSym", observe_customGroups = False, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_contactTracingChangeTD.emodl'))