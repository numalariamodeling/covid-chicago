import os
import sys
import re


sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')


def write_species(expandModel=None):
    species_str = """
(species S @speciesS@)
(species As @initialAs@)
(species E 0)
(species As_det1 0)
(species P 0)
(species P_det 0)
(species Sym 0)
(species Sym_det2 0)
(species Sys 0)
(species Sys_det3 0)
(species H1 0)
(species H2 0)
(species H3 0)
(species H1_det3 0)
(species H2_det3 0)
(species H3_det3 0)
(species C2 0)
(species C3 0)
(species C2_det3 0)
(species C3_det3 0)
(species D3 0)
(species D3_det3 0)
(species RAs 0)
(species RAs_det1 0)
(species RSym 0)
(species RSym_det2 0)
(species RH1 0)
(species RH1_det3 0)
(species RC2 0)
(species RC2_det3 0)
"""
    species_str = species_str.replace("  ", " ")

    expand_testDelay_SymSys_str = """
(species Sym_preD 0)
(species Sys_preD 0)
"""

    expand_testDelay_AsSymSys_str = """
(species As_preD 0)
(species Sym_preD 0)
(species Sym_det2a 0)
(species Sym_det2b 0)
(species Sys_preD 0)
(species Sys_det3a 0)
(species Sys_det3b 0)
"""

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
    
def write_observe(expandModel=None):


    observe_str = """
(observe susceptible S)
(observe exposed E)
(observe asymptomatic asymptomatic)
(observe presymptomatic presymptomatic)
(observe symptomatic_mild symptomatic_mild)
(observe symptomatic_severe symptomatic_severe)
(observe hospitalized hospitalized)
(observe critical critical)
(observe deaths deaths)
(observe recovered recovered)

(observe asymptomatic_det asymptomatic_det)
(observe presymptomatic_det presymptomatic_det )
(observe symptomatic_mild_det symptomatic_mild_det)
(observe symptomatic_severe_det symptomatic_severe_det)
(observe hospitalized_det hospitalized_det)
(observe critical_det critical_det)
(observe deaths_det D3_det3)
(observe recovered_det recovered_det)

(observe asymp_cumul asymp_cumul )
(observe asymp_det_cumul asymp_det_cumul)
(observe symp_mild_cumul symp_mild_cumul)

(observe symp_severe_cumul symp_severe_cumul)
 
(observe hosp_cumul hosp_cumul)
(observe hosp_det_cumul hosp_det_cumul )
(observe crit_cumul crit_cumul)
(observe crit_det_cumul crit_det_cumul)
(observe crit_det crit_det)
(observe death_det_cumul death_det_cumul )

(observe infected infected)
(observe infected_cumul infected_cumul)

(observe infectious_undet infectious_undet)
(observe infectious_det infectious_det)
(observe infectious_det_symp infectious_det_symp)
(observe infectious_det_AsP infectious_det_AsP)

(observe symp_mild_det_cumul symp_mild_det_cumul)
(observe symp_severe_det_cumul symp_severe_det_cumul)
(observe detected detected)
(observe detected_cumul detected_cumul )

(observe prevalence prevalence)    
(observe seroprevalence seroprevalence )
(observe prevalence_det prevalence_det)    
(observe seroprevalence_det seroprevalence_det )

"""
    
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


def write_functions(expandModel=None):
    
    functions_str = """
(func presymptomatic  (+ P P_det))
(func presymptomatic_det  (- presymptomatic P))
(func asymptomatic_det  (- asymptomatic As))
(func symptomatic_mild_det  (- symptomatic_mild Sym))
(func symptomatic_severe_det  (- symptomatic_severe Sys))

(func hospitalized  (+ H1 H2 H3 H1_det3 H2_det3 H3_det3))
(func hospitalized_det  (+ H1_det3 H2_det3 H3_det3))
(func critical (+ C2 C3 C2_det3 C3_det3))
(func critical_det (+ C2_det3 C3_det3))
(func deaths (+ D3 D3_det3))
(func recovered (+ RAs RSym RH1 RC2 RAs_det1 RSym_det2 RH1_det3 RC2_det3))
(func recovered_det (+ RAs_det1 RSym_det2 RH1_det3 RC2_det3))
(func asymp_cumul (+ asymptomatic RAs RAs_det1 ))
(func asymp_det_cumul (+ As_det1 RAs_det1))
(func symp_mild_cumul (+ symptomatic_mild RSym RSym_det2))
(func symp_mild_det_cumul (+ RSym_det2 Sym_det2))
(func symp_severe_cumul (+ symptomatic_severe hospitalized critical deaths RH1 RC2 RH1_det3 RC2_det3))
(func symp_severe_det_cumul (+ Sys_det3 H1_det3 H2_det3 H3_det3 C2_det3 C3_det3 D3_det3 RH1_det3 RC2_det3))
(func hosp_cumul (+ hospitalized critical deaths RH1 RC2 RH1_det3 RC2_det3))
(func hosp_det_cumul (+ H1_det3 H2_det3 H3_det3 C2_det3 C3_det3 D3_det3 RH1_det3 RC2_det3))
(func crit_cumul (+ deaths critical RC2 RC2_det3))
(func crit_det_cumul (+ C2_det3 C3_det3 D3_det3 RC2_det3))
(func crit_det (+ C2_det3 C3_det3))
(func detected_cumul (+ (+ As_det1 Sym_det2 Sys_det3 H1_det3 H2_det3 C2_det3 C3_det3) RAs_det1 RSym_det2 RH1_det3 RC2_det3 D3_det3))
(func death_det_cumul D3_det3 )

(func detected (+ As_det1 Sym_det2 Sys_det3 H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))
(func infected (+ infectious_det infectious_undet H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))
(func infected_det (+ infectious_det H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))
(func infected_cumul (+ infected recovered deaths))    

(func prevalence (/ infected N))    
(func seroprevalence (/ (+ infected recovered) N))    

(func prevalence_det (/ infected_det N))    
(func seroprevalence_det (/ (+ infected_det recovered_det) N))    
  
"""
    functions_str = functions_str.replace("  ", "")
    

    expand_base_str = """
(func asymptomatic  (+ As As_det1))
(func symptomatic_mild  (+ Sym Sym_det2))
(func symptomatic_severe  (+ Sys Sys_det3))
(func infectious_undet (+ As P Sym Sys H1 H2 H3 C2 C3))
(func infectious_det (+ As_det1 P_det Sym_det2 Sys_det3 ))
(func infectious_det_symp (+ Sym_det2 Sys_det3 ))
(func infectious_det_AsP (+ As_det1 P_det))
"""


    expand_testDelay_SymSys_str = """
(func asymptomatic  (+ As As_det1))
(func symptomatic_mild  (+ Sym Sym_preD Sym_det2))
(func symptomatic_severe  (+ Sys Sys_preD Sys_det3))
(func infectious_undet (+ As P Sym_preD Sym Sys_preD Sys H1 H2 H3 C2 C3))
(func infectious_det (+ As_det1 P_det Sym_det2 Sys_det3 ))

(func infectious_det_symp (+ Sym_det2 Sys_det3 ))
(func infectious_det_AsP (+ As_det1 P_det))
"""


    expand_testDelay_AsSymSys_str = """
(func asymptomatic  (+ As_preD As As_det1))
(func symptomatic_mild  (+ Sym Sym_preD Sym_det2a Sym_det2b))
(func symptomatic_severe  (+ Sys Sys_preD Sys_det3a Sys_det3b))
(func infectious_undet (+ As_preD As P Sym Sym_preD Sys Sys_preD H1 H2 H3 C2 C3))
(func infectious_det (+ As_det1 P_det Sym_det2a Sym_det2b Sys_det3a Sys_det3b))

(func infectious_det_symp (+ Sym_det2a Sym_det2b Sys_det3a Sys_det3b ))
(func infectious_det_AsP (+ As_det1 P_det))
"""

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
(param fraction_critical @fraction_critical@ )

(param cfr @cfr@)
(param fraction_dead (/ cfr fraction_severe))
(param fraction_hospitalized (- 1 (+ fraction_critical fraction_dead)))

(param reduced_inf_of_det_cases @reduced_inf_of_det_cases@)
(param reduced_inf_of_det_cases_ct 0)	

(param d_As @d_As@)
(param d_P @d_P@)
(param d_Sym @d_Sym@)
(param d_Sys @d_Sys@)

(param Ki @Ki@)
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

### Monitor time varying parameters
def write_observed_param():
    observed_param_str = """  
(observe Ki_t Ki)
(observe d_As_t d_As)
(observe d_P_t d_P)
(observe d_Sym_t d_Sym)
(observe frac_crit_t fraction_critical)
(observe fraction_hospitalized_t fraction_hospitalized)
(observe fraction_dead_t fraction_dead)
(observe cfr_t cfr)
(observe d_Sys_t d_Sys)
"""
   
    return observed_param_str

def write_N_population():
    string1 = """\n(param N (+ @speciesS@ @initialAs@) )"""
    return (string1)


def write_reactions(expandModel=None):
    

    reaction_str_I = """
(reaction exposure   (S) (E) (* Ki S (/  (+ infectious_undet (* infectious_det reduced_inf_of_det_cases)) N )))
"""

    reaction_str_III = """
(reaction recovery_H1   (H1)   (RH1)   (* Kr_h H1))
(reaction recovery_C2   (C2)   (RC2)   (* Kr_c C2))
(reaction recovery_H1_det3   (H1_det3)   (RH1_det3)   (* Kr_h H1_det3))
(reaction recovery_C2_det3   (C2_det3)   (RC2_det3)   (* Kr_c C2_det3))
    """

    expand_base_str = """
(reaction infection_asymp_undet  (E)   (As)   (* Kl E (- 1 d_As)))
(reaction infection_asymp_det  (E)   (As_det1)   (* Kl E d_As))
(reaction presymptomatic (E)   (P)   (* Ks E (- 1 d_P)))
(reaction presymptomatic (E)   (P_det)   (* Ks E d_P))

(reaction mild_symptomatic_undet (P)  (Sym) (* Ksym P (- 1 d_Sym)))
(reaction mild_symptomatic_det (P)  (Sym_det2) (* Ksym P d_Sym))
(reaction severe_symptomatic_undet (P)  (Sys)  (* Ksys P (- 1 d_Sys)))
(reaction severe_symptomatic_det (P)  (Sys_det3)  (* Ksys P d_Sys))

(reaction mild_symptomatic_det (P_det)  (Sym_det2) (* Ksym P_det))
(reaction severe_symptomatic_det (P_det)  (Sys_det3)  (* Ksys P_det ))

(reaction hospitalization_1   (Sys)   (H1)   (* Kh1 Sys))
(reaction hospitalization_2   (Sys)   (H2)   (* Kh2 Sys))
(reaction hospitalization_3   (Sys)   (H3)   (* Kh3 Sys))
(reaction critical_2   (H2)   (C2)   (* Kc H2))
(reaction critical_3   (H3)   (C3)   (* Kc H3))
(reaction death   (C3)   (D3)   (* Km C3))

(reaction hospitalization_1_det   (Sys_det3)   (H1_det3)   (* Kh1 Sys_det3))
(reaction hospitalization_2_det   (Sys_det3)   (H2_det3)   (* Kh2 Sys_det3))
(reaction hospitalization_3_det   (Sys_det3)   (H3_det3)   (* Kh3 Sys_det3))
(reaction critical_2_det2   (H2_det3)   (C2_det3)   (* Kc H2_det3))
(reaction critical_3_det2   (H3_det3)   (C3_det3)   (* Kc H3_det3))
(reaction death_det3   (C3_det3)   (D3_det3)   (* Km C3_det3))

(reaction recovery_As   (As)   (RAs)   (* Kr_a As))
(reaction recovery_As_det (As_det1)   (RAs_det1)   (* Kr_a As_det1))

(reaction recovery_Sym   (Sym)   (RSym)   (* Kr_m  Sym))
(reaction recovery_Sym_det2   (Sym_det2)   (RSym_det2)   (* Kr_m  Sym_det2))
"""


    expand_testDelay_SymSys_str = """
(reaction infection_asymp_undet  (E)   (As)   (* Kl E (- 1 d_As)))
(reaction infection_asymp_det  (E)   (As_det1)   (* Kl E d_As))
(reaction presymptomatic (E)   (P)   (* Ks E))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic (P)  (Sym_preD) (* Ksym P))
(reaction severe_symptomatic (P)  (Sys_preD)  (* Ksys P))

; never detected 
(reaction mild_symptomatic_undet (Sym_preD)  (Sym) (* Ksym_D Sym_preD (- 1 d_Sym)))
(reaction severe_symptomatic_undet (Sys_preD)  (Sys)  (* Ksys_D Sys_preD (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det (Sym_preD)  (Sym_det2) (* Ksym_D Sym_preD d_Sym))
(reaction severe_symptomatic_det (Sys_preD)  (Sys_det3)  (* Ksys_D Sys_preD d_Sys))

(reaction hospitalization_1   (Sys)   (H1)   (* Kh1_D Sys))
(reaction hospitalization_2   (Sys)   (H2)   (* Kh2_D Sys))
(reaction hospitalization_3   (Sys)   (H3)   (* Kh3_D Sys))
(reaction critical_2   (H2)   (C2)   (* Kc H2))
(reaction critical_3   (H3)   (C3)   (* Kc H3))
(reaction death   (C3)   (D3)   (* Km C3))

(reaction hospitalization_1_det   (Sys_det3)   (H1_det3)   (* Kh1_D Sys_det3))
(reaction hospitalization_2_det   (Sys_det3)   (H2_det3)   (* Kh2_D Sys_det3))
(reaction hospitalization_3_det   (Sys_det3)   (H3_det3)   (* Kh3_D Sys_det3))
(reaction critical_2_det2   (H2_det3)   (C2_det3)   (* Kc H2_det3))
(reaction critical_3_det2   (H3_det3)   (C3_det3)   (* Kc H3_det3))
(reaction death_det3   (C3_det3)   (D3_det3)   (* Km C3_det3))

(reaction recovery_As   (As)   (RAs)   (* Kr_a As))
(reaction recovery_As_det (As_det1)   (RAs_det1)   (* Kr_a As_det1))
(reaction recovery_Sym   (Sym)   (RSym)   (* Kr_m_D  Sym))
(reaction recovery_Sym_det2   (Sym_det2)   (RSym_det2)   (* Kr_m_D  Sym_det2))

"""


    expand_testDelay_AsSymSys_str = """
(reaction infection_asymp_det  (E)   (As_preD)   (* Kl E))
(reaction infection_asymp_undet  (As_preD)   (As)   (* Kl_D As_preD (- 1 d_As)))
(reaction infection_asymp_det  (As_preD)   (As_det1)   (* Kl_D As_preD d_As))

(reaction presymptomatic (E)   (P)   (* Ks E (- 1 d_P)))
(reaction presymptomatic (E)   (P_det)   (* Ks E d_P))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic (P)  (Sym_preD) (* Ksym P))
(reaction severe_symptomatic (P)  (Sys_preD)  (* Ksys P))
																   
; never detected 
(reaction mild_symptomatic_undet (Sym_preD)  (Sym) (* Ksym_D Sym_preD (- 1 d_Sym)))
(reaction severe_symptomatic_undet (Sys_preD)  (Sys)  (* Ksys_D Sys_preD (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det (Sym_preD)  (Sym_det2a) (* Ksym_D Sym_preD d_Sym))
(reaction severe_symptomatic_det (Sys_preD)  (Sys_det3a)  (* Ksys_D Sys_preD d_Sys))

; developing symptoms - already detected, same time to symptoms as in master emodl
(reaction mild_symptomatic_det (P_det)  (Sym_det2b) (* Ksym P_det))
(reaction severe_symptomatic_det (P_det)  (Sys_det3b)  (* Ksys P_det ))

(reaction hospitalization_1  (Sys)   (H1)   (* Kh1_D Sys))
(reaction hospitalization_2   (Sys)   (H2)   (* Kh2_D Sys))
(reaction hospitalization_3   (Sys)   (H3)   (* Kh3_D Sys))
(reaction critical_2  (H2)   (C2)   (* Kc H2))
(reaction critical_3   (H3)   (C3)   (* Kc H3))
(reaction death   (C3)   (D3)   (* Km C3))

(reaction hospitalization_1_det   (Sys_det3a)   (H1_det3)   (* Kh1_D Sys_det3a))
(reaction hospitalization_2_det   (Sys_det3a)   (H2_det3)   (* Kh2_D Sys_det3a))
(reaction hospitalization_3_det   (Sys_det3a)   (H3_det3)   (* Kh3_D Sys_det3a))

(reaction hospitalization_1_det   (Sys_det3b)   (H1_det3)   (* Kh1 Sys_det3b))
(reaction hospitalization_2_det   (Sys_det3b)   (H2_det3)   (* Kh2 Sys_det3b))
(reaction hospitalization_3_det   (Sys_det3b)   (H3_det3)   (* Kh3 Sys_det3b))

(reaction critical_2_det2   (H2_det3)   (C2_det3)   (* Kc H2_det3))
(reaction critical_3_det2   (H3_det3)   (C3_det3)   (* Kc H3_det3))
(reaction death_det3   (C3_det3)   (D3_det3)   (* Km C3_det3))

(reaction recovery_As   (As)   (RAs)   (* Kr_a_D As))
(reaction recovery_As_det (As_det1)   (RAs_det1)   (* Kr_a_D As_det1))

(reaction recovery_Sym   (Sym)   (RSym)   (* Kr_m_D  Sym))
(reaction recovery_Sym_det2a   (Sym_det2a)   (RSym_det2)   (* Kr_m_D  Sym_det2a))
(reaction recovery_Sym_det2b   (Sym_det2b)   (RSym_det2)   (* Kr_m  Sym_det2b))
 """

    if expandModel ==None :
        reaction_str = reaction_str_I + expand_base_str + reaction_str_III
    if expandModel == "testDelay_SymSys" or  expandModel == "uniformtestDelay" :
        reaction_str = reaction_str_I + expand_testDelay_SymSys_str + reaction_str_III
    if expandModel == 'testDelay_AsSymSys':
        reaction_str = reaction_str_I + expand_testDelay_AsSymSys_str + reaction_str_III

    reaction_str = reaction_str.replace("  ", " ")

    return (reaction_str)



def define_change_detection_and_isolation(reduced_inf_of_det_cases=True,
                                          d_As=True,
                                          d_P=True,
                                          d_Sym_ct=True):

    """ Write the emodl chunk for changing detection rates and reduced infectiousness
    to approximate contact tracing or improved health system interventions.
    Helper function called by write_interventions

    Parameters
    ----------
    reduced_inf_of_det_cases : boolean
        Boolean to add a change in infectiousness of As and P detected cases if set to True
    d_As : boolean
        Boolean to add a change in detection of asymptomatic cases if set to True
    d_P : boolean
        Boolean to add a change in detection of presymptomatic cases if set to True
    d_Sym_ct : boolean
        Boolean to add a change in detection of symptomatic cases if set to True
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
        d_Sym_ct_str = """(d_Sym @d_Sym_ct1@)"""

    change_param_str = reduced_inf_of_det_cases_str + d_As_str + d_P_str + d_Sym_ct_str
    time_event_str = """(time-event contact_tracing_start @contact_tracing_start_1@ ( {change_param} ))""".format(change_param=change_param_str)

    contactTracing_str = d_Sym_ct_param_str + "\n" + time_event_str

    return (contactTracing_str)


def write_interventions( total_string, scenarioName, change_testDelay=None, trigger_channel=None) :

    param_change_str = """
(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@)))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@)))
(time-event detection4 @detection_time_4@ ((d_Sys @d_Sys_incr4@)))
(time-event detection5 @detection_time_5@ ((d_Sys @d_Sys_incr5@)))
(time-event detection6 @detection_time_6@ ((d_Sys @d_Sys_incr6@)))

(time-event frac_crit_adjust1 @crit_time_1@ ((fraction_critical @fraction_critical_incr1@) (fraction_hospitalized (- 1 (+ @fraction_critical_incr1@ @fraction_dead@))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) ))  
(time-event frac_crit_adjust2 @crit_time_2@ ((fraction_critical @fraction_critical_incr2@) (fraction_hospitalized (- 1 (+ @fraction_critical_incr2@ @fraction_dead@))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) ))
(time-event frac_crit_adjust3 @crit_time_3@ ((fraction_critical @fraction_critical_incr3@) (fraction_hospitalized (- 1 (+ @fraction_critical_incr3@ @fraction_dead@))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) )) 

(time-event cfr_adjust1 @cfr_time_1@ ((cfr @cfr_change1@) (fraction_dead (/ cfr fraction_severe)) (fraction_hospitalized (- 1 (+ fraction_critical fraction_dead))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) )) 
"""

    socialDistance_change_str = """
(param Ki_red1 (* Ki @social_multiplier_1@))
(param Ki_red2 (* Ki @social_multiplier_2@))
(param Ki_red3 (* Ki @social_multiplier_3@))
(param Ki_red4 (* Ki @social_multiplier_4@))

(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki Ki_red1)))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki Ki_red2)))
(time-event socialDistance_start @socialDistance_time3@ ((Ki Ki_red3)))
(time-event socialDistance_change @socialDistance_time4@ ((Ki Ki_red4)))
            """
    rollback_str ="""
(time-event socialDistance_change_rollback @socialDistance_rollback_time@ ((Ki Ki_red4)))
                """

    rollbacktriggered_str =  """
(state-event rollbacktrigger (and (> time @triggertime@) (> {channel} (* @trigger@ @capacity_multiplier@)) ) ((Ki Ki_red4)))
                    """.format(channel=trigger_channel)

    d_Sym_change_str = """
(time-event d_Sym_change1 @d_Sym_change_time_1@ ((d_Sym @d_Sym_change1@)))
(time-event d_Sym_change2 @d_Sym_change_time_2@ ((d_Sym @d_Sym_change2@)))
(time-event d_Sym_change3 @d_Sym_change_time_3@ ((d_Sym @d_Sym_change3@)))
(time-event d_Sym_change4 @d_Sym_change_time_4@ ((d_Sym @d_Sym_change4@)))
(time-event d_Sym_change5 @d_Sym_change_time_5@ ((d_Sym @d_Sym_change5@)))
    """


    interventionSTOP_str =  """
(param Ki_back (* Ki @backtonormal_multiplier@))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki Ki_back)))
        """

# % change from lowest transmission level - immediate
# starting point is lowest level of transmission  Ki_red4
    interventionSTOP_adj_str = """
(param Ki_back (+ Ki_red4 (* @backtonormal_multiplier@ (- Ki Ki_red4))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki Ki_back)))
        """

# % change from current transmission level - immediate
# starting point is current level of transmission  Ki_red5
    interventionSTOP_adj2_str = """
(param Ki_back (+ Ki_red5 (* @backtonormal_multiplier@ (- Ki Ki_red5))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki Ki_back)))
        """

    gradual_reopening_str =  """
(param Ki_back1 (+ Ki_red4 (* @reopening_multiplier_1@ (- Ki Ki_red4))))
(param Ki_back2 (+ Ki_red4 (* @reopening_multiplier_2@ (- Ki Ki_red4))))
(param Ki_back3 (+ Ki_red4 (* @reopening_multiplier_3@ (- Ki Ki_red4))))
(param Ki_back4 (+ Ki_red4 (* @reopening_multiplier_4@ (- Ki Ki_red4))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki Ki_back1)))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki Ki_back2)))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki Ki_back3)))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki Ki_back4)))
    """

# gradual reopening from 'current' transmission level
    gradual_reopening2_str =  """
(param Ki_back1 (+ Ki_red5 (* @reopening_multiplier_4@ 0.25 (- Ki Ki_red5))))
(param Ki_back2 (+ Ki_red5 (* @reopening_multiplier_4@ 0.50 (- Ki Ki_red5))))
(param Ki_back3 (+ Ki_red5 (* @reopening_multiplier_4@ 0.75 (- Ki Ki_red5))))
(param Ki_back4 (+ Ki_red5 (* @reopening_multiplier_4@ 1.00 (- Ki Ki_red5))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki Ki_back1)))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki Ki_back2)))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki Ki_back3)))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki Ki_back4)))
        """


    improveHS_str = define_change_detection_and_isolation( reduced_inf_of_det_cases = False,
                                    d_As = False,
                                    d_P = False ,
                                    d_Sym_ct = True)


    contactTracing_str = define_change_detection_and_isolation( reduced_inf_of_det_cases = True,
                                    d_As = True,
                                    d_P = True ,
                                    d_Sym_ct = False)


    contactTracing_improveHS_str = define_change_detection_and_isolation( reduced_inf_of_det_cases = True,
                                    d_As = True,
                                    d_P = True,
                                    d_Sym_ct = True)



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
        total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + rollbacktriggered_str)

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
        if change_testDelay == "AsP" :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_P_str)
        if change_testDelay == "AsSymSys"  :
            total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' +  change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)



    return (total_string)


###stringing all of my functions together to make the file:

def generate_emodl( file_output, expandModel, add_interventions,  trigger_channel=None, change_testDelay =None):
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

    total_string = total_string + write_species(expandModel)
    functions = write_functions(expandModel)
    observe_string = observe_string + write_observe(expandModel)
    reaction_string = reaction_string + write_reactions(expandModel)
    functions_string = functions_string + functions

    param_string =  write_params(expandModel) + param_string + write_observed_param() +  write_N_population()
    functions_string = functions_string 
    intervention_string = ";[INTERVENTIONS]\n;[ADDITIONAL_TIMEEVENTS]"

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string +  '\n\n' + reaction_string + '\n\n' + footer_str

    ### Custom adjustments for EMS 6 (earliest start date)
    total_string = total_string.replace('(species As::EMS_6 0)', '(species As::EMS_6 1)')
    ### Add interventions (optional)
    if add_interventions != None :
        total_string = write_interventions( total_string, add_interventions, change_testDelay, trigger_channel)

    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


if __name__ == '__main__':

    generateBaselineReopeningEmodls = True
    if generateBaselineReopeningEmodls:
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='continuedSIP' ,  file_output=os.path.join(emodl_dir, 'extendedmodel.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='rollback' ,  file_output=os.path.join(emodl_dir, 'extendedmodel_rollback.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='reopen_rollback' ,  file_output=os.path.join(emodl_dir, 'extendedmodel_reopen_rollback.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='interventionSTOP_adj' ,  file_output=os.path.join(emodl_dir, 'extendedmodel_interventionSTOPadj.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions=None ,  file_output=os.path.join(emodl_dir, 'extendedmodel_neverSIP.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='interventionStop',   file_output=os.path.join(emodl_dir, 'extendedmodel_interventionStop.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='gradual_reopening2' , file_output=os.path.join(emodl_dir, 'extendedmodel_gradual_reopening.emodl'))

        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='rollbacktriggered', trigger_channel = "critical", file_output=os.path.join(emodl_dir, 'extendedmodel_critical_triggeredrollback.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='rollbacktriggered', trigger_channel = "critical_det", file_output=os.path.join(emodl_dir, 'extendedmodel_criticaldet_triggeredrollback.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='rollbacktriggered', trigger_channel = "hospitalized", file_output=os.path.join(emodl_dir, 'extendedmodel_hosp_triggeredrollback.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='rollbacktriggered', trigger_channel = "hospitalized_det", file_output=os.path.join(emodl_dir, 'extendedmodel_hospdet_triggeredrollback.emodl'))

    generateImprovedDetectionEmodls = True
    if generateImprovedDetectionEmodls:
        generate_emodl(expandModel="testDelay_AsSymSys",  add_interventions='continuedSIP', change_testDelay = "Sym", file_output=os.path.join(emodl_dir, 'extendedmodel_changeTD.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='improveHS',  file_output=os.path.join(emodl_dir, 'extendedmodel_dSym.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='improveHS', change_testDelay = "Sym",  file_output=os.path.join(emodl_dir, 'extendedmodel_dSym_TD.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='contactTracing',  file_output=os.path.join(emodl_dir, 'extendedmodel_dAsP.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='contactTracing', change_testDelay = "AsSym",  file_output=os.path.join(emodl_dir, 'extendedmodel_dAsP_TD.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='contactTracing_improveHS',  file_output=os.path.join(emodl_dir, 'extendedmodel_dAsPSym.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='contactTracing_improveHS',  change_testDelay = "AsSym",  file_output=os.path.join(emodl_dir, 'extendedmodel_dAsPSym_TD.emodl'))

    generateImprovedDetectionEmodls_withReopening = True
    if generateImprovedDetectionEmodls_withReopening:
        generate_emodl(expandModel="testDelay_AsSymSys",  add_interventions='gradual_reopening2', change_testDelay = "Sym", file_output=os.path.join(emodl_dir, 'extendedmodel_reopen_changeTD.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='reopen_improveHS',  file_output=os.path.join(emodl_dir, 'extendedmodel_reopen_dSym.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='reopen_improveHS',  change_testDelay = "Sym",  file_output=os.path.join(emodl_dir, 'extendedmodel_reopen_dSym_TD.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='reopen_contactTracing',  file_output=os.path.join(emodl_dir, 'extendedmodel_reopen_dAsP.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='reopen_contactTracing',  change_testDelay = "AsSym",  file_output=os.path.join(emodl_dir, 'extendedmodel_reopen_dAsP_TD.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='reopen_contactTracing_improveHS',  file_output=os.path.join(emodl_dir, 'extendedmodel_reopen_dAsPSym.emodl'))
        generate_emodl(expandModel="testDelay_AsSymSys", add_interventions='reopen_contactTracing_improveHS',  change_testDelay = "AsSym",  file_output=os.path.join(emodl_dir, 'extendedmodel_reopen_dAsPSym_TD.emodl'))
