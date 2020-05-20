import os
import sys
import re


sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')


def write_species(grp):
    grp = str(grp)
    species_str = """
(species S::{grp} @speciesS_{grp}@)
(species As::{grp} 0)
(species E::{grp} 0)
(species As_det1::{grp} 0)
(species P::{grp} 0)
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
    return (species_str)

## For postprocessing that splits by '_', it is easier if EMS are names EMS-1 not EMS_1
## This might change depending on the postprocessing
def sub(x):
    xout = re.sub('_','-', str(x), count=1)
    return(xout)
    
def write_observe(grp):
    grp = str(grp)
    grpout = sub(grp)

    observe_str = """
(observe susceptible_{grpout} S::{grp})
(observe exposed_{grpout} E::{grp})
(observe asymptomatic_{grpout} asymptomatic_{grp})
(observe presymptomatic_{grpout} P::{grp})
(observe symptomatic_mild_{grpout} symptomatic_mild_{grp})
(observe symptomatic_severe_{grpout} symptomatic_severe_{grp})
(observe hospitalized_{grpout} hospitalized_{grp})
(observe critical_{grpout} critical_{grp})
(observe deaths_{grpout} deaths_{grp})
(observe recovered_{grpout} recovered_{grp})

(observe asymp_cumul_{grpout} (+ asymptomatic_{grp} RAs::{grp} RAs_det1::{grp} ))
(observe asymp_det_cumul_{grpout} (+ As_det1::{grp} RAs_det1::{grp}))
(observe symp_mild_cumul_{grpout} (+ symptomatic_mild_{grp} RSym::{grp} RSym_det2::{grp}))
(observe symp_mild_det_cumul_{grpout} (+ RSym_det2::{grp} Sym_det2::{grp}))
(observe symp_severe_cumul_{grpout} (+ symptomatic_severe_{grp} hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(observe symp_severe_det_cumul_{grpout} (+ Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(observe hosp_cumul_{grpout} (+ hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(observe hosp_det_cumul_{grpout} (+ H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(observe crit_cumul_{grpout} (+ deaths_{grp} critical_{grp} RC2::{grp} RC2_det3::{grp}))
(observe crit_det_cumul_{grpout} (+ C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RC2_det3::{grp}))
(observe crit_det_{grpout} (+ C2_det3::{grp} C3_det3::{grp}))
(observe death_det_cumul_{grpout} D3_det3::{grp} )
(observe detected_cumul_{grpout} (+ (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} C2_det3::{grp} C3_det3::{grp}) RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp} D3_det3::{grp}))

(observe detected_{grpout} (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(observe infected_{grpout} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
""".format(grpout=grpout, grp=grp)
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


def write_functions(grp):
    grp = str(grp)
    functions_str = """
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))
(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_det2::{grp}))
(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_det3::{grp}))
(func hospitalized_{grp}  (+ H1::{grp} H2::{grp} H3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp}))
(func critical_{grp} (+ C2::{grp} C3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func deaths_{grp} (+ D3::{grp} D3_det3::{grp}))
(func recovered_{grp} (+ RAs::{grp} RSym::{grp} RH1::{grp} RC2::{grp} RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym::{grp} Sys::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} ))

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


""".format(grp=grp)
    functions_str = functions_str.replace("  ", "")
    return (functions_str)


###
def write_params():
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
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization ))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
(param Kc (/ 1 time_to_critical))
(param Km (/ 1 time_to_death))

(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))  
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@)))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@))) 
"""

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
    obs_All_str = obs_All_str + "\n(func infectious_det_All (+ " + repeat_string_by_grp('infectious_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(func infectious_undet_All (+ " + repeat_string_by_grp( 'infectious_undet_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infectious_det_All infectious_det_All)"
    obs_All_str = obs_All_str + "\n(observe infectious_undet_All infectious_undet_All)"


    return (obs_All_str)



def write_reactions(grp):
    grp = str(grp)

    reaction_str = """
(reaction exposure_{grp}   (S::{grp}) (E::{grp}) (* Ki_{grp} S::{grp} (/  (+ infectious_undet_{grp} (* infectious_det_{grp} reduced_inf_of_det_cases)) N_{grp} )))
(reaction infection_asymp_undet_{grp}  (E::{grp})   (As::{grp})   (* Kl E::{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (E::{grp})   (As_det1::{grp})   (* Kl E::{grp} d_As))
(reaction presymptomatic_{grp} (E::{grp})   (P::{grp})   (* Ks E::{grp}))
(reaction mild_symptomatic_undet_{grp} (P::{grp})  (Sym::{grp}) (* Ksym P::{grp} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{grp} (P::{grp})  (Sym_det2::{grp}) (* Ksym P::{grp} d_Sym))
(reaction severe_symptomatic_undet_{grp} (P::{grp})  (Sys::{grp})  (* Ksys P::{grp} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{grp} (P::{grp})  (Sys_det3::{grp})  (* Ksys P::{grp} d_Sys))

(reaction hospitalization_1_{grp}   (Sys::{grp})   (H1::{grp})   (* Kh1 Sys::{grp}))
(reaction hospitalization_2_{grp}   (Sys::{grp})   (H2::{grp})   (* Kh2 Sys::{grp}))
(reaction hospitalization_3_{grp}   (Sys::{grp})   (H3::{grp})   (* Kh3 Sys::{grp}))
(reaction critical_2_{grp}   (H2::{grp})   (C2::{grp})   (* Kc H2::{grp}))
(reaction critical_3_{grp}   (H3::{grp})   (C3::{grp})   (* Kc H3::{grp}))
(reaction death_{grp}   (C3::{grp})   (D3::{grp})   (* Km C3::{grp}))

(reaction recovery_As_{grp}   (As::{grp})   (RAs::{grp})   (* Kr_a As::{grp}))
(reaction recovery_Sym_{grp}   (Sym::{grp})   (RSym::{grp})   (* Kr_m  Sym::{grp}))
(reaction recovery_H1_{grp}   (H1::{grp})   (RH1::{grp})   (* Kr_h H1::{grp}))
(reaction recovery_C2_{grp}   (C2::{grp})   (RC2::{grp})   (* Kr_c C2::{grp}))

(reaction recovery_As_det_{grp} (As_det1::{grp})   (RAs_det1::{grp})   (* Kr_a As_det1::{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3::{grp})   (H1_det3::{grp})   (* Kh1 Sys_det3::{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3::{grp})   (H2_det3::{grp})   (* Kh2 Sys_det3::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3::{grp})   (H3_det3::{grp})   (* Kh3 Sys_det3::{grp}))
(reaction critical_2_det2_{grp}   (H2_det3::{grp})   (C2_det3::{grp})   (* Kc H2_det3::{grp}))
(reaction critical_3_det2_{grp}   (H3_det3::{grp})   (C3_det3::{grp})   (* Kc H3_det3::{grp}))
(reaction death_det3_{grp}   (C3_det3::{grp})   (D3_det3::{grp})   (* Km C3_det3::{grp}))

(reaction recovery_Sym_det2_{grp}   (Sym_det2::{grp})   (RSym_det2::{grp})   (* Kr_m  Sym_det2::{grp}))
(reaction recovery_H1_det3_{grp}   (H1_det3::{grp})   (RH1_det3::{grp})   (* Kr_h H1_det3::{grp}))
(reaction recovery_C2_det3_{grp}   (C2_det3::{grp})   (RC2_det3::{grp})   (* Kr_c C2_det3::{grp}))
""".format(grp=grp)

    reaction_str = reaction_str.replace("  ", " ")
    return (reaction_str)

def write_interventions(grpList, total_string, scenarioName) :

    continuedSIP_str = ""
    for grp in grpList:
        temp_str = """
(param Ki_red1_{grp} (* Ki_{grp} @social_multiplier_1_{grp}@))
(param Ki_red2_{grp} (* Ki_{grp} @social_multiplier_2_{grp}@))
(param Ki_red3_{grp} (* Ki_{grp} @social_multiplier_3_{grp}@))

(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki_{grp} Ki_red1_{grp})))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki_{grp} Ki_red2_{grp})))
(time-event socialDistance_start @socialDistance_time3@ ((Ki_{grp} Ki_red3_{grp})))
            """.format(grp=grp)
        continuedSIP_str = continuedSIP_str + temp_str

    interventiopnSTOP_str = ""
    for grp in grpList :
        temp_str = """
(param Ki_back_{grp} (* Ki_{grp} @backtonormal_multiplier@))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{grp} Ki_back_{grp})))
        """.format(grp=grp)
        interventiopnSTOP_str = interventiopnSTOP_str + temp_str

    gradual_reopening_str = ""
    for grp in grpList:
        temp_str = """
(param Ki_back1_{grp} (* Ki_{grp} @reopening_multiplier_1@))
(param Ki_back2_{grp} (* Ki_{grp} @reopening_multiplier_2@))
(param Ki_back3_{grp} (* Ki_{grp} @reopening_multiplier_3@))
(param Ki_back4_{grp} (* Ki_{grp} @reopening_multiplier_4@))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki_{grp} Ki_back1_{grp})))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki_{grp} Ki_back2_{grp})))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki_{grp} Ki_back3_{grp})))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki_{grp} Ki_back4_{grp})))
    """.format(grp=grp)
        gradual_reopening_str = gradual_reopening_str + temp_str

    ### contact tracing not working yet, as P_det is missing in emodl structure
    ### placeholder only
    contactTracing_str = """
(time-event contact_tracing_start @contact_tracing_start_1@ ((d_As d_As_ct1) (d_P d_As_ct1) (d_Sym d_Sym_ct1)))
;(time-event contact_tracing_end @contact_tracing_stop1@ ((d_As @d_As@) (d_P @d_P@) (d_Sym @d_Sym@)))
    """
    for grp in grpList:
        temp_str = """
;(time-event contact_tracing_start @contact_tracing_start_1@ ((S_{grp} (* S_{grp} (- 1 d_SQ))) (Q (* S_{grp} d_SQ))))
;(time-event contact_tracing_end @contact_tracing_stop1@ ((S_{grp} (+ S_{grp} Q_{grp})) (Q_{grp} 0)))
        """.format(grp=grp)
        contactTracing_str = contactTracing_str +  temp_str

    if scenarioName == "interventionStop" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventiopnSTOP_str)
    if scenarioName == "gradual_reopening" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + gradual_reopening_str)
    if scenarioName == "contactTracing" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + contactTracing_str)
    if scenarioName == "continuedSIP" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str)

    return (total_string)


###stringing all of my functions together to make the file:

def generate_locale_emodl_extended(grpList, file_output, add_interventions, add_migration=True):
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
        total_string = total_string +  write_species(grp)
        functions = write_functions(grp)
        observe_string = observe_string + write_observe(grp)
        if (add_migration):
            reaction_string = reaction_string + write_travel_reaction(grp)
        reaction_string = reaction_string + write_reactions(grp)
        functions_string = functions_string + functions
        param_string = param_string + write_Ki_timevents(grp)
        
    param_string =  write_params() + param_string + write_N_population(grpList)
    if(add_migration) :
        param_string = param_string + write_migration_param(grpList)
    functions_string = functions_string + write_All(grpList)
    intervention_string = ";[INTERVENTIONS]"

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string +  '\n\n' + reaction_string + '\n\n' + footer_str

    ### Add interventions (optional)
    if add_interventions != None :
        total_string = write_interventions(grpList, total_string, add_interventions)

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
    #generate_locale_emodl_extended(grpList=ems_grp, add_interventions=None, file_output=os.path.join(emodl_dir, 'extendedmodel_locale_EMS_neversip.emodl'))
    generate_locale_emodl_extended(grpList=ems_grp, add_interventions='continuedSIP', file_output=os.path.join(emodl_dir, 'extendedmodel_locale_EMS.emodl'))
    #generate_locale_emodl_extended(grpList=ems_grp, add_interventions='interventionStop', file_output=os.path.join(emodl_dir, 'extendedmodel_locale_EMS_interventionStop.emodl'))
    #generate_locale_emodl_extended(grpList=ems_grp, add_interventions='gradual_reopening', file_output=os.path.join(emodl_dir, 'extendedmodel_locale_EMS_reopening.emodl'))

