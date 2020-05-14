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
(species S_{grp} @speciesS_{grp}@)
(species As_{grp} 0)
(species E_{grp} 0)
(species As_det1_{grp} 0)
(species P_{grp} 0)
(species Sym_{grp} 0)
(species Sym_det2_{grp} 0)
(species Sys_{grp} 0)
(species Sys_det3_{grp} 0)
(species H1_{grp} 0)
(species H2_{grp} 0)
(species H3_{grp} 0)
(species H1_det3_{grp} 0)
(species H2_det3_{grp} 0)
(species H3_det3_{grp} 0)
(species C2_{grp} 0)
(species C3_{grp} 0)
(species C2_det3_{grp} 0)
(species C3_det3_{grp} 0)
(species D3_{grp} 0)
(species D3_det3_{grp} 0)
(species RAs_{grp} 0)
(species RAs_det1_{grp} 0)
(species RSym_{grp} 0)
(species RSym_det2_{grp} 0)
(species RH1_{grp} 0)
(species RH1_det3_{grp} 0)
(species RC2_{grp} 0)
(species RC2_det3_{grp} 0)
""".format(grp=grp)
    species_str = species_str.replace("  ", " ")

    expand_testDelay_str = """
(species Sym_preD_{grp} 0)
(species Sys_preD_{grp} 0)
""".format(grp=grp)

    expand_contactTracing_str = """
;(species Q_{grp} 0)
(species P_det_{grp} 0)
    """.format(grp=grp)

    expand_testDelay_contactTracing_str = """
;(species Q_{grp} 0)
(species P_det_{grp} 0)
(species Sym_preD_{grp} 0)
(species Sym_det2a_{grp} 0)
(species Sym_det2b_{grp} 0)
(species Sys_preD_{grp} 0)
(species Sys_det3a_{grp} 0)
(species Sys_det3b_{grp} 0)
""".format(grp=grp)

    if expandModel == "testDelay":
        species_str = species_str + expand_testDelay_str
    if expandModel == "contactTracing" :
        species_str = species_str + expand_contactTracing_str
    if expandModel == "testDelay_contactTracing":
        species_str = species_str + expand_testDelay_contactTracing_str

    return (species_str)

## For postprocessing that splits by '_', it is easier if EMS are names EMS-1 not EMS_1
## This might change depending on the postprocessing
def sub(x):
    xout = re.sub('_', '-', str(x), count=1)
    return (xout)


def write_observe(grp, expandModel=None):
    grp = str(grp)
    grpout = sub(grp)

    observe_str = """
(observe susceptible_{grpout} S_{grp})
(observe exposed_{grpout} E_{grp})
(observe asymptomatic_{grpout} asymptomatic_{grp})
                                      
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
""".format(grpout=grpout, grp=grp)

    
    expand_base_str = """
(observe presymptomatic_{grpout} P_{grp})
""".format(grpout=grpout, grp=grp)

    expand_contactTracing_str = """
;(observe quarantined Q_{grpout})
(observe presymptomatic_{grpout} presymptomatic_{grp})
""".format(grpout=grpout, grp=grp)

    expand_testDelay_contactTracing_str = """
;(observe quarantined Q_{grpout})
(observe presymptomatic_{grpout} presymptomatic_{grp})
""".format(grpout=grpout, grp=grp)

    if expandModel == None :
        observe_str = observe_str + expand_base_str
    if expandModel == "testDelay" :
        observe_str = observe_str + expand_base_str
    if expandModel == "contactTracing" :
        observe_str = observe_str + expand_contactTracing_str
    if expandModel == "testDelay_contactTracing" :
        observe_str = observe_str + expand_testDelay_contactTracing_str

    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


def write_functions(grp, expandModel=None):
    grp = str(grp)
    functions_str = """
(func asymptomatic_{grp}  (+ As_{grp} As_det1_{grp}))
(func hospitalized_{grp}  (+ H1_{grp} H2_{grp} H3_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp}))
(func critical_{grp} (+ C2_{grp} C3_{grp} C2_det3_{grp} C3_det3_{grp}))
(func deaths_{grp} (+ D3_{grp} D3_det3_{grp}))
(func recovered_{grp} (+ RAs_{grp} RSym_{grp} RH1_{grp} RC2_{grp} RAs_det1_{grp} RSym_det2_{grp} RH1_det3_{grp} RC2_det3_{grp}))

(func asymp_cumul_{grp} (+ asymptomatic_{grp} RAs_{grp} RAs_det1_{grp} ))
(func asymp_det_cumul_{grp} (+ As_det1_{grp} RAs_det1_{grp}))
(func symp_mild_cumul_{grp} (+ symptomatic_mild_{grp} RSym_{grp} RSym_det2_{grp}))
(func symp_mild_det_cumul_{grp} (+ RSym_det2_{grp} Sym_det2_{grp}))
(func symp_severe_cumul_{grp} (+ symptomatic_severe_{grp} hospitalized_{grp} critical_{grp} deaths_{grp} RH1_{grp} RC2_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(func symp_severe_det_cumul_{grp} (+ Sys_det3_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp} D3_det3_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(func hosp_cumul_{grp} (+ hospitalized_{grp} critical_{grp} deaths_{grp} RH1_{grp} RC2_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(func hosp_det_cumul_{grp} (+ H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp} D3_det3_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(func crit_cumul_{grp} (+ deaths_{grp} critical_{grp} RC2_{grp} RC2_det3_{grp}))
(func crit_det_cumul_{grp} (+ C2_det3_{grp} C3_det3_{grp} D3_det3_{grp} RC2_det3_{grp}))
(func crit_det_{grp} (+ C2_det3_{grp} C3_det3_{grp}))
(func detected_cumul_{grp} (+ (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} H1_det3_{grp} H2_det3_{grp} C2_det3_{grp} C3_det3_{grp}) RAs_det1_{grp} RSym_det2_{grp} RH1_det3_{grp} RC2_det3_{grp} D3_det3_{grp}))
(func death_det_cumul_{grp} D3_det3_{grp} )

(func detected_{grp} (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))
(func infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))
(func infected_cumul_{grp} (+ infected_{grp} recovered_{grp} deaths_{grp}))    
""".format(grp=grp)
    functions_str = functions_str.replace("  ", "")
    

    expand_base_str = """
(func symptomatic_mild_{grp}  (+ Sym_{grp} Sym_det2_{grp}))
(func symptomatic_severe_{grp}  (+ Sys_{grp} Sys_det3_{grp}))
(func infectious_undet_{grp} (+ As_{grp} P_{grp} Sym_{grp} Sys_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infectious_det_{grp} (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} ))
""".format(grp=grp)


    expand_testDelay_str = """
(func symptomatic_mild_{grp}  (+ Sym_{grp} Sym_preD_{grp} Sym_det2_{grp}))
(func symptomatic_severe_{grp}  (+ Sys_{grp} Sys_preD_{grp} Sys_det3_{grp}))
(func infectious_undet_{grp} (+ As_{grp} P_{grp} Sym_preD_{grp} Sym_{grp} Sys_preD_{grp} Sys_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infectious_det_{grp} (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} ))
""".format(grp=grp)


    expand_contactTracing_str = """
(func presymptomatic_{grp}  (+ P_{grp} P_det_{grp}))
(func symptomatic_mild_{grp}  (+ Sym_{grp} Sym_det2_{grp}))
(func symptomatic_severe_{grp}  (+ Sys_{grp} Sys_det3_{grp}))
(func infectious_undet_{grp} (+ As_{grp} P_{grp} Sym_{grp} Sys_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infectious_det_{grp} (+ As_det1_{grp} P_det_{grp} Sym_det2_{grp} Sys_det3_{grp} ))
""".format(grp=grp)

    expand_testDelay_contactTracing_str = """
(func presymptomatic_{grp}  (+ P_{grp} P_det_{grp}))
(func symptomatic_mild_{grp}  (+ Sym_{grp} Sym_preD_{grp} Sym_det2a_{grp} Sym_det2b_{grp}))
(func symptomatic_severe_{grp}  (+ Sys_{grp} Sys_preD_{grp} Sys_det3a_{grp} Sys_det3b_{grp}))
(func infectious_undet_{grp} (+ As_{grp} P_{grp} Sym_{grp} Sym_preD_{grp} Sys_{grp} Sys_preD_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infectious_det_{grp} (+ As_det1_{grp} P_det_{grp} Sym_det2a_{grp} Sym_det2b_{grp} Sys_det3a_{grp} Sys_det3b_{grp}))
""".format(grp=grp)

    if expandModel == None:
        functions_str = expand_base_str + functions_str
    if expandModel =="testDelay" :
        functions_str =  expand_testDelay_str + functions_str
    if expandModel == "contactTracing":
        functions_str = expand_contactTracing_str + functions_str
    if expandModel == "testDelay_contactTracing":
        functions_str = expand_testDelay_contactTracing_str + functions_str

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

(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))  
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@)))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@))) 
"""

    expand_base_str = """
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization ))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
"""


    expand_testDelay_str = """
(param time_D @time_to_detection@)
(param Ksys_D (/ 1 time_D))
(param Ksym_D (/ 1 time_D))
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization ))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
(param Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D)))
(param Kh2_D (/ fraction_critical (- time_to_hospitalization time_D) ))
(param Kh3_D (/ fraction_dead  (- time_to_hospitalization time_D)))
(param Kr_m_D (/ 1 (- recovery_time_mild time_D )))
"""

    expand_contactTracing_str = """
;(param d_SQ @d_SQ@)
(param d_P @d_P@)
(param d_As_ct1 @d_As_ct1@)
(param d_Sym_ct1 @d_Sym_ct1@)
"""


    if expandModel == None:
        params_str = params_str + expand_base_str
    if expandModel == "testDelay":
        params_str = params_str + expand_testDelay_str
    if expandModel == "contactTracing" :
        params_str = params_str + expand_base_str + expand_contactTracing_str
    if expandModel == "testDelay_contactTracing" :
        params_str = params_str + expand_testDelay_str + expand_contactTracing_str

    params_str = params_str.replace("  ", " ")

    return (params_str)

#### Used when Ki varies per group (i.e. in EMS model but not in age model)
def write_grp_params(grp):
    grp = str(grp)
    params_str = """
(param Ki_{grp} @Ki_{grp}@)
(time-event time_infection_import @time_infection_import_{grp}@ ((As_{grp} @initialAs_{grp}@) (S_{grp} (- S_{grp} @initialAs_{grp}@))))
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
    obs_All_str = obs_All_str + "\n(observe susceptible_All (+ " + repeat_string_by_grp('S_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe exposed_All (+ " + repeat_string_by_grp('E_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymptomatic_All (+ " + repeat_string_by_grp('asymptomatic_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe presymptomatic_All (+ " + repeat_string_by_grp('P_',    grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_mild_All (+ " + repeat_string_by_grp( 'symptomatic_mild_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symptomatic_severe_All (+ " + repeat_string_by_grp('symptomatic_severe_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe hospitalized_All (+ " + repeat_string_by_grp( 'hospitalized_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe critical_All (+ " + repeat_string_by_grp('critical_',  grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe deaths_All (+ " + repeat_string_by_grp('deaths_',   grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infected_All (+ " + repeat_string_by_grp('infected_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe recovered_All (+ " + repeat_string_by_grp('recovered_',   grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymp_cumul_All (+ " + repeat_string_by_grp( 'asymp_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe asymp_det_cumul_All (+ " + repeat_string_by_grp('asymp_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_mild_cumul_All (+ " + repeat_string_by_grp(  'symp_mild_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_mild_det_cumul_All (+ " + repeat_string_by_grp( 'symp_mild_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_severe_cumul_All (+ " + repeat_string_by_grp( 'symp_severe_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe symp_severe_det_cumul_All  (+ " + repeat_string_by_grp( 'symp_severe_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe hosp_cumul_All (+ " + repeat_string_by_grp('hosp_cumul_',  grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe hosp_det_cumul_All (+ " + repeat_string_by_grp( 'hosp_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe crit_cumul_All (+ " + repeat_string_by_grp('crit_cumul_',   grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe crit_det_cumul_All (+ " + repeat_string_by_grp(  'crit_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe crit_det_All (+ " + repeat_string_by_grp('crit_det_',    grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe detected_cumul_All (+ " + repeat_string_by_grp( 'detected_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe death_det_cumul_All (+ " + repeat_string_by_grp('death_det_cumul_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infected_cumul_All (+ " + repeat_string_by_grp('infected_cumul_', grpList) + "))"

    obs_All_str = obs_All_str + "\n(func infectious_det_All (+ " + repeat_string_by_grp( 'infectious_det_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(func infectious_undet_All (+ " + repeat_string_by_grp('infectious_undet_', grpList) + "))"
    obs_All_str = obs_All_str + "\n(observe infectious_det_All infectious_det_All)"
    obs_All_str = obs_All_str + "\n(observe infectious_undet_All infectious_undet_All)"

    return (obs_All_str)


# Reaction without contact matrix
# (reaction exposure_{grp}   (S_{grp}) (E_{grp}) (* Ki_{grp} S_{grp} (/  (+ infectious_undet_All (* infectious_det_All reduced_inf_of_det_cases)) N_All )))

def write_reactions(grp, expandModel=None):
    grp = str(grp)

    reaction_str_I = """
(reaction exposure_{grp}   (S_{grp}) (E_{grp}) (* Ki_{grp} S_{grp} (/  (+ infectious_undet_{grp} (* infectious_det_{grp} reduced_inf_of_det_cases)) N_{grp} )))
(reaction infection_asymp_undet_{grp}  (E_{grp})   (As_{grp})   (* Kl E_{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (E_{grp})   (As_det1_{grp})   (* Kl E_{grp} d_As))
""".format(grp=grp)

    reaction_str_III = """
(reaction recovery_As_{grp}   (As_{grp})   (RAs_{grp})   (* Kr_a As_{grp}))
(reaction recovery_Sym_{grp}   (Sym_{grp})   (RSym_{grp})   (* Kr_m  Sym_{grp}))
(reaction recovery_H1_{grp}   (H1_{grp})   (RH1_{grp})   (* Kr_h H1_{grp}))
(reaction recovery_C2_{grp}   (C2_{grp})   (RC2_{grp})   (* Kr_c C2_{grp}))
(reaction recovery_As_det_{grp} (As_det1_{grp})   (RAs_det1_{grp})   (* Kr_a As_det1_{grp}))
(reaction recovery_H1_det3_{grp}   (H1_det3_{grp})   (RH1_det3_{grp})   (* Kr_h H1_det3_{grp}))
(reaction recovery_C2_det3_{grp}   (C2_det3_{grp})   (RC2_det3_{grp})   (* Kr_c C2_det3_{grp}))
    """.format(grp=grp)

    expand_base_str = """
(reaction presymptomatic_{grp} (E_{grp})   (P_{grp})   (* Ks E_{grp}))
(reaction mild_symptomatic_undet_{grp} (P_{grp})  (Sym_{grp}) (* Ksym P_{grp} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{grp} (P_{grp})  (Sym_det2_{grp}) (* Ksym P_{grp} d_Sym))
(reaction severe_symptomatic_undet_{grp} (P_{grp})  (Sys_{grp})  (* Ksys P_{grp} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{grp} (P_{grp})  (Sys_det3_{grp})  (* Ksys P_{grp} d_Sys))

(reaction hospitalization_1_{grp}   (Sys_{grp})   (H1_{grp})   (* Kh1 Sys_{grp}))
(reaction hospitalization_2_{grp}   (Sys_{grp})   (H2_{grp})   (* Kh2 Sys_{grp}))
(reaction hospitalization_3_{grp}   (Sys_{grp})   (H3_{grp})   (* Kh3 Sys_{grp}))
(reaction critical_2_{grp}   (H2_{grp})   (C2_{grp})   (* Kc H2_{grp}))
(reaction critical_3_{grp}   (H3_{grp})   (C3_{grp})   (* Kc H3_{grp}))
(reaction death_{grp}   (C3_{grp})   (D3_{grp})   (* Km C3_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3_{grp})   (H1_det3_{grp})   (* Kh1 Sys_det3_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3_{grp})   (H2_det3_{grp})   (* Kh2 Sys_det3_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3_{grp})   (H3_det3_{grp})   (* Kh3 Sys_det3_{grp}))
(reaction critical_2_det2_{grp}   (H2_det3_{grp})   (C2_det3_{grp})   (* Kc H2_det3_{grp}))
(reaction critical_3_det2_{grp}   (H3_det3_{grp})   (C3_det3_{grp})   (* Kc H3_det3_{grp}))
(reaction death_det3_{grp}   (C3_det3_{grp})   (D3_det3_{grp})   (* Km C3_det3_{grp}))

(reaction recovery_Sym_det2_{grp}   (Sym_det2_{grp})   (RSym_det2_{grp})   (* Kr_m  Sym_det2_{grp}))
""".format(grp=grp)


    expand_testDelay_str = """
(reaction presymptomatic_{grp} (E_{grp})   (P_{grp})   (* Ks E_{grp}))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{grp} (P_{grp})  (Sym_preD_{grp}) (* Ksym P_{grp}))
(reaction severe_symptomatic_{grp} (P_{grp})  (Sys_preD_{grp})  (* Ksys P_{grp}))

; never detected 
(reaction mild_symptomatic_undet_{grp} (Sym_preD_{grp})  (Sym_{grp}) (* Ksym_D Sym_preD_{grp} (- 1 d_Sym)))
(reaction severe_symptomatic_undet_{grp} (Sys_preD_{grp})  (Sys_{grp})  (* Ksys_D Sys_preD_{grp} (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det_{grp} (Sym_preD_{grp})  (Sym_det2_{grp}) (* Ksym_D Sym_preD_{grp} d_Sym))
(reaction severe_symptomatic_det_{grp} (Sys_preD_{grp})  (Sys_det3_{grp})  (* Ksys_D Sys_preD_{grp} d_Sys))

(reaction hospitalization_1_{grp}   (Sys_{grp})   (H1_{grp})   (* Kh1_D Sys_{grp}))
(reaction hospitalization_2_{grp}   (Sys_{grp})   (H2_{grp})   (* Kh2_D Sys_{grp}))
(reaction hospitalization_3_{grp}   (Sys_{grp})   (H3_{grp})   (* Kh3_D Sys_{grp}))
(reaction critical_2_{grp}   (H2_{grp})   (C2_{grp})   (* Kc H2_{grp}))
(reaction critical_3_{grp}   (H3_{grp})   (C3_{grp})   (* Kc H3_{grp}))
(reaction death_{grp}   (C3_{grp})   (D3_{grp})   (* Km C3_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3_{grp})   (H1_det3_{grp})   (* Kh1_D Sys_det3_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3_{grp})   (H2_det3_{grp})   (* Kh2_D Sys_det3_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3_{grp})   (H3_det3_{grp})   (* Kh3_D Sys_det3_{grp}))
(reaction critical_2_det2_{grp}   (H2_det3_{grp})   (C2_det3_{grp})   (* Kc H2_det3_{grp}))
(reaction critical_3_det2_{grp}   (H3_det3_{grp})   (C3_det3_{grp})   (* Kc H3_det3_{grp}))
(reaction death_det3_{grp}   (C3_det3_{grp})   (D3_det3_{grp})   (* Km C3_det3_{grp}))

(reaction recovery_Sym_det2_{grp}   (Sym_det2_{grp})   (RSym_det2_{grp})   (* Kr_m_D  Sym_det2_{grp}))

""".format(grp=grp)


    expand_contactTracing_str = """
(reaction presymptomatic_{grp} (E_{grp})   (P_{grp})   (* Ks E_{grp} (- 1 d_P)))
(reaction presymptomatic_{grp} (E_{grp})   (P_det_{grp})   (* Ks E_{grp} d_P))

(reaction mild_symptomatic_undet_{grp} (P_{grp})  (Sym_{grp}) (* Ksym P_{grp} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{grp} (P_{grp})  (Sym_det2_{grp}) (* Ksym P_{grp} d_Sym))
(reaction severe_symptomatic_undet_{grp} (P_{grp})  (Sys_{grp})  (* Ksys P_{grp} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{grp} (P_{grp})  (Sys_det3_{grp})  (* Ksys P_{grp} d_Sys))

(reaction mild_symptomatic_det_{grp} (P_det_{grp})  (Sym_det2_{grp}) (* Ksym P_det_{grp}))
(reaction severe_symptomatic_det_{grp} (P_det_{grp})  (Sys_det3_{grp})  (* Ksys P_det_{grp} ))

(reaction hospitalization_1_{grp}   (Sys_{grp})   (H1_{grp})   (* Kh1 Sys_{grp}))
(reaction hospitalization_2_{grp}   (Sys_{grp})   (H2_{grp})   (* Kh2 Sys_{grp}))
(reaction hospitalization_3_{grp}   (Sys_{grp})   (H3_{grp})   (* Kh3 Sys_{grp}))
(reaction critical_2_{grp}   (H2_{grp})   (C2_{grp})   (* Kc H2_{grp}))
(reaction critical_3_{grp}   (H3_{grp})   (C3_{grp})   (* Kc H3_{grp}))
(reaction death_{grp}   (C3_{grp})   (D3_{grp})   (* Km C3_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3_{grp})   (H1_det3_{grp})   (* Kh1 Sys_det3_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3_{grp})   (H2_det3_{grp})   (* Kh2 Sys_det3_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3_{grp})   (H3_det3_{grp})   (* Kh3 Sys_det3_{grp}))
(reaction critical_2_det2_{grp}   (H2_det3_{grp})   (C2_det3_{grp})   (* Kc H2_det3_{grp}))
(reaction critical_3_det2_{grp}   (H3_det3_{grp})   (C3_det3_{grp})   (* Kc H3_det3_{grp}))
(reaction death_det3_{grp}   (C3_det3_{grp})   (D3_det3_{grp})   (* Km C3_det3_{grp}))

(reaction recovery_Sym_det2_{grp}   (Sym_det2_{grp})   (RSym_det2_{grp})   (* Kr_m  Sym_det2_{grp}))
""".format(grp=grp)

    expand_testDelay_contactTracing_str = """
(reaction presymptomatic_{grp} (E_{grp})   (P_{grp})   (* Ks E_{grp} (- 1 d_P)))
(reaction presymptomatic_{grp} (E_{grp})   (P_det_{grp})   (* Ks E_{grp} d_P))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{grp} (P_{grp})  (Sym_preD_{grp}) (* Ksym P_{grp}))
(reaction severe_symptomatic_{grp} (P_{grp})  (Sys_preD_{grp})  (* Ksys P_{grp}))
																   
; never detected 
(reaction mild_symptomatic_undet_{grp} (Sym_preD_{grp})  (Sym_{grp}) (* Ksym_D Sym_preD_{grp} (- 1 d_Sym)))
(reaction severe_symptomatic_undet_{grp} (Sys_preD_{grp})  (Sys_{grp})  (* Ksys_D Sys_preD_{grp} (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det_{grp} (Sym_preD_{grp})  (Sym_det2a_{grp}) (* Ksym_D Sym_preD_{grp} d_Sym))
(reaction severe_symptomatic_det_{grp} (Sys_preD_{grp})  (Sys_det3a_{grp})  (* Ksys_D Sys_preD_{grp} d_Sys))

; developing symptoms - already detected, same time to symptoms as in master emodl
(reaction mild_symptomatic_det_{grp} (P_det_{grp})  (Sym_det2b_{grp}) (* Ksym P_det_{grp}))
(reaction severe_symptomatic_det_{grp} (P_det_{grp})  (Sys_det3b_{grp})  (* Ksys P_det_{grp} ))

(reaction hospitalization_1_{grp}  (Sys_{grp})   (H1_{grp})   (* Kh1_D Sys_{grp}))
(reaction hospitalization_2_{grp}   (Sys_{grp})   (H2_{grp})   (* Kh2_D Sys_{grp}))
(reaction hospitalization_3_{grp}   (Sys_{grp})   (H3_{grp})   (* Kh3_D Sys_{grp}))
(reaction critical_2_{grp}  (H2_{grp})   (C2_{grp})   (* Kc H2_{grp}))
(reaction critical_3_{grp}   (H3_{grp})   (C3_{grp})   (* Kc H3_{grp}))
(reaction death_{grp}   (C3_{grp})   (D3_{grp})   (* Km C3_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3a_{grp})   (H1_det3_{grp})   (* Kh1_D Sys_det3a_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3a_{grp})   (H2_det3_{grp})   (* Kh2_D Sys_det3a_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3a_{grp})   (H3_det3_{grp})   (* Kh3_D Sys_det3a_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3b_{grp})   (H1_det3_{grp})   (* Kh1 Sys_det3b_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3b_{grp})   (H2_det3_{grp})   (* Kh2 Sys_det3b_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3b_{grp})   (H3_det3_{grp})   (* Kh3 Sys_det3b_{grp}))

(reaction critical_2_det2_{grp}   (H2_det3_{grp})   (C2_det3_{grp})   (* Kc H2_det3_{grp}))
(reaction critical_3_det2_{grp}   (H3_det3_{grp})   (C3_det3_{grp})   (* Kc H3_det3_{grp}))
(reaction death_det3_{grp}   (C3_det3_{grp})   (D3_det3_{grp})   (* Km C3_det3_{grp}))

(reaction recovery_Sym_det2a_{grp}   (Sym_det2a_{grp})   (RSym_det2_{grp})   (* Kr_m_D  Sym_det2a_{grp}))
(reaction recovery_Sym_det2b_{grp}   (Sym_det2b_{grp})   (RSym_det2_{grp})   (* Kr_m  Sym_det2b_{grp}))
 """.format(grp=grp)

    if expandModel ==None :
        reaction_str = reaction_str_I + expand_base_str + reaction_str_III
    if expandModel == "testDelay":
        reaction_str = reaction_str_I + expand_testDelay_str + reaction_str_III
    if expandModel == 'contactTracing':
        reaction_str = reaction_str_I + expand_contactTracing_str + reaction_str_III
    if expandModel == 'testDelay_contactTracing':
        reaction_str = reaction_str_I + expand_testDelay_contactTracing_str + reaction_str_III

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


    contactTracing_str = """
(time-event contact_tracing_start @contact_tracing_start_1@ ((d_As d_As_ct1) (d_P d_As_ct1) (d_Sym d_Sym_ct1)))
;(time-event contact_tracing_end @contact_tracing_stop1@ ((d_As @d_As@) (d_P @d_P@) (d_Sym @d_Sym@)))
    """
    for grp in grpList:
        temp_str = """
;(time-event contact_tracing_start @contact_tracing_start_1@ ((S_{grp} (* S_{grp} (- 1 d_SQ))) (Q (* S_{grp} d_SQ))))
;(time-event contact_tracing_end @contact_tracing_stop1@ ((S_{grp} (+ S_{grp} Q_{grp})) (Q_{grp} 0)))
        """.format(grp=grp)

        contactTracing_str =  temp_str + contactTracing_str

    if scenarioName == "interventionStop" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventiopnSTOP_str)
    if scenarioName == "gradual_reopening" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + gradual_reopening_str)
    if scenarioName == "continuedSIP" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str)
    if scenarioName == "contactTracing" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + gradual_reopening_str + contactTracing_str)
        #total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventiopnSTOP_str + contactTracing_str)
    if scenarioName == "testDelay_contactTracing" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + gradual_reopening_str + contactTracing_str)
        #total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventiopnSTOP_str + contactTracing_str)

    return (total_string)



###stringing all of my functions together to make the file:

def generate_emodl(grpList, file_output, expandModel, add_interventions):
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
        total_string = total_string + write_species(grp, expandModel )
        functions = write_functions(grp, expandModel)
        observe_string = observe_string + write_observe(grp, expandModel)
        reaction_string = reaction_string + write_reactions(grp, expandModel)
        functions_string = functions_string + functions
        param_string = param_string + write_grp_params(grp)


    param_string = write_params(expandModel) + param_string + write_N_population(grpList)
    functions_string = functions_string + write_All(grpList)
    intervention_string = ";[INTERVENTIONS]"

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string +  '\n\n' + reaction_string + '\n\n' + footer_str

    ### Custom adjustments for EMS 6 (earliest start date)
    total_string = total_string.replace('(species As_EMS_6 0)', '(species As_EMS_6 1)')

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
    generate_emodl(grpList=ems_grp, expandModel=None, add_interventions=None, file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_grp_neverSIP.emodl'))
    generate_emodl(grpList=ems_grp, expandModel=None, add_interventions='continuedSIP', file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_grp.emodl'))
    generate_emodl(grpList=ems_grp, expandModel=None, add_interventions='interventionStop',  file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_grp_interventionStop.emodl'))
    generate_emodl(grpList=ems_grp, expandModel=None, add_interventions='gradual_reopening', file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_grp_gradual_reopening.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="contactTracing", add_interventions='contactTracing',  file_output=os.path.join(emodl_dir, 'extendedmodel_EMS_grp_contactTracing.emodl'))

    generate_emodl(grpList=ems_grp, expandModel="testDelay",  add_interventions='continuedSIP', file_output=os.path.join(emodl_dir, 'extendedmodelTestDelay_EMS_grp.emodl'))

    generate_emodl(grpList=ems_grp, expandModel="testDelay", add_interventions=None, file_output=os.path.join(emodl_dir, 'extendedmodelTestDelay_EMS_grp_neverSIP.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay", add_interventions='continuedSIP', file_output=os.path.join(emodl_dir, 'extendedmodelTestDelay_EMS_grp.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay", add_interventions='interventionStop',  file_output=os.path.join(emodl_dir, 'extendedmodelTestDelay_EMS_grp_interventionStop.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay", add_interventions='gradual_reopening', file_output=os.path.join(emodl_dir, 'extendedmodelTestDelay_EMS_grp_gradual_reopening.emodl'))
    generate_emodl(grpList=ems_grp, expandModel="testDelay_contactTracing", add_interventions='contactTracing',  file_output=os.path.join(emodl_dir, 'extendedmodelTestDelay_EMS_grp_contactTracing.emodl'))
