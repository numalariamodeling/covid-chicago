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

    expand_testDelay_AsPSymSys_str = """
(species As_preD::{grp} 0)
(species P_preD::{grp} 0)
(species Sym_preD::{grp} 0)
(species Sym_det2a::{grp} 0)
(species Sym_det2b::{grp} 0)
(species Sys_preD::{grp} 0)
(species Sys_det3a::{grp} 0)
(species Sys_det3b::{grp} 0)
""".format(grp=grp)

    if expandModel == "testDelay_SymSys" or  expandModel == "uniformtestDelay" :
        species_str = species_str + expand_testDelay_SymSys_str
    if expandModel == "testDelay_AsPSymSys":
        species_str = species_str + expand_testDelay_AsPSymSys_str

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

(observe symp_mild_det_cumul_{grpout} symp_mild_det_cumul_{grp})
(observe symp_severe_det_cumul_{grpout} symp_severe_det_cumul_{grp})
(observe detected_{grpout} detected_{grp})
(observe detected_cumul_{grpout} detected_cumul_{grp} )

(observe Ki_{grpout} Ki_{grp})
""".format(grpout=grpout, grp=grp)
    
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


def write_functions(grp, expandModel=None):
    grp = str(grp)
    functions_str = """
(func hospitalized_{grp}  (+ H1::{grp} H2::{grp} H3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp}))
(func critical_{grp} (+ C2::{grp} C3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func deaths_{grp} (+ D3::{grp} D3_det3::{grp}))
(func recovered_{grp} (+ RAs::{grp} RSym::{grp} RH1::{grp} RC2::{grp} RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
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
(func infected_cumul_{grp} (+ infected_{grp} recovered_{grp} deaths_{grp}))    
""".format(grp=grp)
    functions_str = functions_str.replace("  ", "")
    

    expand_base_str = """
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))
(func presymptomatic_{grp}  (+ P::{grp} P_det::{grp}))
(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_det2::{grp}))
(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_det3::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym::{grp} Sys::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} P_det::{grp} Sym_det2::{grp} Sys_det3::{grp} ))
""".format(grp=grp)


    expand_testDelay_SymSys_str = """
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))
(func presymptomatic_{grp}  (+ P::{grp} P_det::{grp}))
(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_preD::{grp} Sym_det2::{grp}))
(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_preD::{grp} Sys_det3::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym_preD::{grp} Sym::{grp} Sys_preD::{grp} Sys::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} P_det::{grp} Sym_det2::{grp} Sys_det3::{grp} ))
""".format(grp=grp)


    expand_testDelay_AsPSymSys_str = """
(func asymptomatic_{grp}  (+ As_preD::{grp} As::{grp} As_det1::{grp}))
(func presymptomatic_{grp}  (+ P_preD::{grp} P::{grp} P_det::{grp}))
(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_preD::{grp} Sym_det2a::{grp} Sym_det2b::{grp}))
(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_preD::{grp} Sys_det3a::{grp} Sys_det3b::{grp}))
(func infectious_undet_{grp} (+ As_preD::{grp} As::{grp} P_preD::{grp} P::{grp} Sym::{grp} Sym_preD::{grp} Sys::{grp} Sys_preD::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} P_det::{grp} Sym_det2a::{grp} Sym_det2b::{grp} Sys_det3a::{grp} Sys_det3b::{grp}))
""".format(grp=grp)

    if expandModel == None:
        functions_str = expand_base_str + functions_str
    if expandModel == "testDelay_SymSys" or  expandModel == "uniformtestDelay" :
        functions_str =  expand_testDelay_SymSys_str + functions_str
    if expandModel == "testDelay_AsPSymSys":
        functions_str = expand_testDelay_AsPSymSys_str + functions_str

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

;(param Ki @Ki@)
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

(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@) (d_Sym @d_Sym_incr1@) ))  
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@) (d_Sym @d_Sym_incr2@) ))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@) (d_Sym @d_Sym_incr3@) )) 
(time-event detection4 @detection_time_4@ ((d_Sys @d_Sys_incr4@) (d_Sym @d_Sym_incr4@) )) 
(time-event detection5 @detection_time_5@ ((d_Sys @d_Sys_incr5@) (d_Sym @d_Sym_incr5@) )) 

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


    expand_testDelay_AsPSymSys_str = """
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

(param time_D_P @time_to_detection_P@)
(param Ks_D (/ 1 time_D_P))
(param Ksym_DP (/ 1 (- time_to_symptoms time_D_P )))
(param Ksys_DP (/ 1 (- time_to_symptoms time_D_P )))
"""

    if expandModel == None:
        params_str = params_str + expand_base_str
    if expandModel == "testDelay_SymSys":
        params_str = params_str + expand_testDelay_SymSys_str
    if expandModel == "uniformtestDelay":
        params_str = params_str + expand_uniformtestDelay_str
    if expandModel == "contactTracing" :
        params_str = params_str + expand_base_str + expand_contactTracing_str
    if expandModel == "testDelay_AsPSymSys" :
        params_str = params_str + expand_testDelay_AsPSymSys_str

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


def write_travel_reaction_chunk(grpList,travelspeciesList=None) :
    x1 = range(1, len(grpList) + 1)
    x2 = range(1, len(grpList) + 1)
    reaction_str = ""
    if travelspeciesList ==None:
        travelspeciesList = ["S","E","As","P"]

    for x1_i in x1 :
        reaction_str = reaction_str + "\n"
        for travelspecies in travelspeciesList:
            reaction_str = reaction_str + "\n"
            for x2_i in x2 :
                #x1_i=1
                reaction_str = reaction_str + """\n(reaction {travelspecies}_travel_EMS_{x2_i}to{x1_i}  ({travelspecies}::EMS_{x2_i}) ({travelspecies}::EMS_{x1_i}) (* {travelspecies}::EMS_{x2_i} toEMS_{x1_i}_from_EMS_{x2_i} (/ N_EMS_{x2_i} (+ S::EMS_{x2_i} E::EMS_{x2_i} As::EMS_{x2_i} P::EMS_{x2_i} recovered_EMS_{x2_i}))))""".format(travelspecies=travelspecies, x1_i=x1_i, x2_i=x2_i)

    return (reaction_str)


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
    params_str = """
(param Ki_{grp} @Ki_{grp}@)
(time-event time_infection_import @time_infection_import_{grp}@ ((As::{grp} @initialAs_{grp}@) (S::{grp} (- S::{grp} @initialAs_{grp}@))))
""".format(grp=grp)
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
    obs_All_str = obs_All_str + "\n(observe presymptomatic_All (+ " + repeat_string_by_grp('P::', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_mild_All (+ " + repeat_string_by_grp(  'symptomatic_mild_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_severe_All (+ " + repeat_string_by_grp( 'symptomatic_severe_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe hospitalized_All (+ " + repeat_string_by_grp('hospitalized_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe critical_All (+ " + repeat_string_by_grp('critical_',    grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe deaths_All (+ " + repeat_string_by_grp('deaths_',   grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infected_All (+ " + repeat_string_by_grp('infected_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe recovered_All (+ " + repeat_string_by_grp('recovered_',    grpList) + "))"
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
    obs_All_str = obs_All_str + "\n(func infectious_det_All (+ " + repeat_string_by_grp('infectious_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(func infectious_undet_All (+ " + repeat_string_by_grp( 'infectious_undet_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infectious_det_All infectious_det_All)"
    obs_All_str = obs_All_str + "\n(observe infectious_undet_All infectious_undet_All)"


    return (obs_All_str)



def write_reactions(grp, expandModel=None):
    grp = str(grp)

    reaction_str_I = """
(reaction exposure_{grp}   (S::{grp}) (E::{grp}) (* Ki_{grp} S::{grp} (/  (+ infectious_undet_{grp} (* infectious_det_{grp} reduced_inf_of_det_cases)) N_{grp} )))
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

(reaction mild_symptomatic_undet_{grp} (P::{grp})  (Sym::{grp}) (* Ksym P::{grp} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{grp} (P::{grp})  (Sym_det2::{grp}) (* Ksym P::{grp} d_Sym))
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
(reaction mild_symptomatic_undet_{grp} (Sym_preD::{grp})  (Sym::{grp}) (* Ksym_D Sym_preD::{grp} (- 1 d_Sym)))
(reaction severe_symptomatic_undet_{grp} (Sys_preD::{grp})  (Sys::{grp})  (* Ksys_D Sys_preD::{grp} (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det_{grp} (Sym_preD::{grp})  (Sym_det2::{grp}) (* Ksym_D Sym_preD::{grp} d_Sym))
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


    expand_testDelay_AsPSymSys_str = """
(reaction infection_asymp_det_{grp}  (E::{grp})   (As_preD::{grp})   (* Kl E::{grp}))
(reaction infection_asymp_undet_{grp}  (As_preD::{grp})   (As::{grp})   (* Kl_D As_preD::{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (As_preD::{grp})   (As_det1::{grp})   (* Kl_D As_preD::{grp} d_As))

(reaction presymptomatic_{grp} (E::{grp})   (P_preD::{grp})   (* Ks E::{grp} ))
(reaction presymptomatic_{grp} (P_preD::{grp})   (P::{grp})   (* Ks_D P_preD::{grp} (- 1 d_P)))
(reaction presymptomatic_{grp} (P_preD::{grp})   (P_det::{grp})   (* Ks_D P_preD::{grp} d_P))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{grp} (P::{grp})  (Sym_preD::{grp}) (* Ksym P::{grp}))
(reaction severe_symptomatic_{grp} (P::{grp})  (Sys_preD::{grp})  (* Ksys P::{grp}))
																   
; never detected 
(reaction mild_symptomatic_undet_{grp} (Sym_preD::{grp})  (Sym::{grp}) (* Ksym_D Sym_preD::{grp} (- 1 d_Sym)))
(reaction severe_symptomatic_undet_{grp} (Sys_preD::{grp})  (Sys::{grp})  (* Ksys_D Sys_preD::{grp} (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det_{grp} (Sym_preD::{grp})  (Sym_det2a::{grp}) (* Ksym_D Sym_preD::{grp} d_Sym))
(reaction severe_symptomatic_det_{grp} (Sys_preD::{grp})  (Sys_det3a::{grp})  (* Ksys_D Sys_preD::{grp} d_Sys))

; developing symptoms - already detected, same time to symptoms as in master emodl
(reaction mild_symptomatic_det_{grp} (P_det::{grp})  (Sym_det2b::{grp}) (* Ksym_DP P_det::{grp}))
(reaction severe_symptomatic_det_{grp} (P_det::{grp})  (Sys_det3b::{grp})  (* Ksym_DP P_det::{grp} ))

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
    if expandModel == 'testDelay_AsPSymSys':
        reaction_str = reaction_str_I + expand_testDelay_AsPSymSys_str + reaction_str_III

    reaction_str = reaction_str.replace("  ", " ")

    return (reaction_str)


def write_interventions(grpList, total_string, scenarioName, expandModel, change_testDelay=None) :

    continuedSIP_str = ""
    for grp in grpList:
        temp_str = """
(param Ki_red1_{grp} (* Ki_{grp} @social_multiplier_1_{grp}@))
(param Ki_red2_{grp} (* Ki_{grp} @social_multiplier_2_{grp}@))
(param Ki_red3_{grp} (* Ki_{grp} @social_multiplier_3_{grp}@))
(param Ki_red4_{grp} (* Ki_{grp} @social_multiplier_4_{grp}@))

(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki_{grp} Ki_red1_{grp})))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki_{grp} Ki_red2_{grp})))
(time-event socialDistance_start @socialDistance_time3@ ((Ki_{grp} Ki_red3_{grp})))
(time-event socialDistance_change @socialDistance_time4@ ((Ki_{grp} Ki_red4_{grp})))
            """.format(grp=grp)
        continuedSIP_str = continuedSIP_str + temp_str

    interventiopnSTOP_str = ""
    for grp in grpList :
        temp_str = """
(param Ki_back_{grp} (* Ki_{grp} @backtonormal_multiplier@))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{grp} Ki_back_{grp})))
        """.format(grp=grp)
        interventiopnSTOP_str = interventiopnSTOP_str + temp_str

    interventionSTOP_adj_str = ""
    for grp in grpList :
        temp_str = """
(param Ki_back_{grp} (+ Ki_red3_{grp} (* @backtonormal_multiplier@ (- Ki_{grp} Ki_red3_{grp}))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{grp} Ki_back_{grp})))
        """.format(grp=grp)
        interventionSTOP_adj_str = interventionSTOP_adj_str + temp_str

    gradual_reopening_str = ""
    for grp in grpList:
        temp_str = """
(param Ki_back1_{grp} (+ Ki_red3_{grp} (* @reopening_multiplier_1@ (- Ki_{grp} Ki_red3_{grp}))))
(param Ki_back2_{grp} (+ Ki_red3_{grp} (* @reopening_multiplier_2@ (- Ki_{grp} Ki_red3_{grp}))))
(param Ki_back3_{grp} (+ Ki_red3_{grp} (* @reopening_multiplier_3@ (- Ki_{grp} Ki_red3_{grp}))))
(param Ki_back4_{grp} (+ Ki_red3_{grp} (* @reopening_multiplier_4@ (- Ki_{grp} Ki_red3_{grp}))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki_{grp} Ki_back1_{grp})))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki_{grp} Ki_back2_{grp})))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki_{grp} Ki_back3_{grp})))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki_{grp} Ki_back4_{grp})))
    """.format(grp=grp)
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

     ### (change_testDelay_P_str not used)
    change_testDelay_P_str = """
(time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} {} {} {} {} ))
    """.format("(time_D_P @change_testDelay_P_1@)",
               "(Kl_D (/ 1 time_D_As))",
               "(Ksym_DP (/ 1 (- time_to_symptoms time_D_P )))",
               "(Ksys_DP (/ 1 (- time_to_symptoms time_D_P )))")
   
    if scenarioName == "interventionStop" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventiopnSTOP_str)
    if scenarioName == "interventionSTOP_adj" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventionSTOP_adj_str)
    if scenarioName == "gradual_reopening" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + gradual_reopening_str)
    if scenarioName == "continuedSIP" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str)
    if scenarioName == "contactTracing" :
        #total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + gradual_reopening_str + contactTracing_str)
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventiopnSTOP_str + contactTracing_str)

    if change_testDelay != None :
        if change_testDelay == "uniform" :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_uniformtestDelay_str)
        if change_testDelay == "As"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str )
        if change_testDelay == "P"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_P_str )
        if change_testDelay == "Sym"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sym_str )
        if change_testDelay == "Sys"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sys_str )
        if change_testDelay == "AsSym"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_Sys_str )
        if change_testDelay == "SymSys" :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)
        if change_testDelay == "AsP" :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_P_str)
        if change_testDelay == "AsPSymSys"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_P_str + '\n' + change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)


    return (total_string)


###stringing all of my functions together to make the file:

def generate_emodl(grpList, file_output, expandModel, add_interventions, add_migration=True, change_testDelay =None):
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

    param_string =  write_params(expandModel) + param_string + write_N_population(grpList)
    if(add_migration) :
        param_string = param_string + write_migration_param(grpList)
    functions_string = functions_string + write_All(grpList)
    intervention_string = ";[INTERVENTIONS]\n;[ADDITIONAL_TIMEEVENTS]"

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string +  '\n\n' + reaction_string + '\n\n' + footer_str

    ### Custom adjustments for EMS 6 (earliest start date)
    total_string = total_string.replace('(species As::EMS_6 0)', '(species As::EMS_6 1)')
    ### Add interventions (optional)
    if add_interventions != None :
        total_string = write_interventions(grpList, total_string, add_interventions, expandModel, change_testDelay)

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


    ## By default include migration in spatial model, but also generate a test version without migration
    
    ### Vary test delay  (i.e. change_testDelay = "SymSys"   )
    generate_emodl(grpList=ems_grp, expandModel=None,  add_interventions='continuedSIP', add_migration=False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_noTD.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys",  add_interventions='continuedSIP', add_migration=False, change_testDelay = "SymSys", file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_changeTD.emodl'))
    #generate_emodl(grpList=ems_grp, expandModel="uniformtestDelay",  add_interventions='continuedSIP', add_migration=False, change_testDelay = "uniform", file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_changeuniformTD.emodl'))

    ### Emodls without migration between EMS areas
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='continuedSIP', add_migration=False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='interventionSTOP_adj', add_migration=False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_interventionSTOPadj.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions=None, add_migration=False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_neverSIP.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='interventionStop', add_migration=False,  file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_interventionStop.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='gradual_reopening', add_migration=False, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_gradual_reopening.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='contactTracing', add_migration=False,  file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_contactTracing.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='contactTracing', add_migration=False, change_testDelay = "AsPSymSys", file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_contactTracingChangeTD.emodl'))
  
    ### Emodls with migration between EMS areas  
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='continuedSIP', add_migration=True, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='interventionSTOP_adj', add_migration=True, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_interventionSTOPadj.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions=None, add_migration=True, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_neverSIP.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='interventionStop', add_migration=True,  file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_interventionStop.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='gradual_reopening', add_migration=True, file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_gradual_reopening.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='contactTracing', add_migration=True,  file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_contactTracing.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_AsPSymSys", add_interventions='contactTracing', add_migration=True, change_testDelay = "AsPSymSys", file_output=os.path.join(emodl_dir, 'extendedmodel_migration_EMS_contactTracingChangeTD.emodl'))