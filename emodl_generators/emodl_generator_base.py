import os
import sys
import re
import json

sys.path.append('../')
from load_paths import load_box_paths

try:
    print(Location)
except NameError:
    if os.name == "posix":
        Location = "NUCLUSTER"
    else:
        Location = "Local"

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)


class covidModel:

    def __init__(self, expandModel='testDelay_AsSymSys', observeLevel='primary', add_interventions='baseline',
                 change_testDelay=None, intervention_config='intervention_emodl_config.yaml', fit_params=None,emodl_name=None, git_dir=git_dir):
        self.model = 'base'
        self.expandModel = expandModel
        self.observeLevel = observeLevel
        self.add_interventions = add_interventions
        self.change_testDelay = change_testDelay
        self.intervention_config = intervention_config
        self.emodl_name = emodl_name
        self.emodl_dir = os.path.join(git_dir, 'emodl')

    def write_species(self):
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

        if self.expandModel == "testDelay_SymSys" or self.expandModel == "uniformtestDelay":
            species_str = species_str + expand_testDelay_SymSys_str
        if self.expandModel == "testDelay_AsSymSys":
            species_str = species_str + expand_testDelay_AsSymSys_str

        return species_str

    ## For postprocessing that splits by '_', it is easier if EMS are names EMS-1 not EMS_1
    ## This might change depending on the postprocessing
    def sub(x):
        xout = re.sub('_', '-', str(x), count=1)
        return xout

    def write_observe(self):

        observe_primary_channels_str = """
(observe susceptible S)
(observe infected infected)
(observe recovered recovered)
(observe infected_cumul infected_cumul)

(observe asymp_cumul asymp_cumul )
(observe asymp_det_cumul asymp_det_cumul)
(observe symptomatic_mild symptomatic_mild)
(observe symptomatic_severe symptomatic_severe)
(observe symp_mild_cumul symp_mild_cumul)
(observe symp_severe_cumul symp_severe_cumul)
(observe symp_mild_det_cumul symp_mild_det_cumul)
(observe symp_severe_det_cumul symp_severe_det_cumul)

(observe hosp_det_cumul hosp_det_cumul )
(observe hosp_cumul hosp_cumul)
(observe detected_cumul detected_cumul )

(observe crit_cumul crit_cumul)
(observe crit_det_cumul crit_det_cumul)
(observe death_det_cumul death_det_cumul )

(observe deaths_det D3_det3)
(observe deaths deaths)

(observe crit_det crit_det)
(observe critical critical)
(observe hosp_det hosp_det)
(observe hospitalized hospitalized)
    """

        observe_secondary_channels_str = """
(observe exposed E)
(observe asymptomatic asymptomatic)
(observe presymptomatic presymptomatic)
(observe detected detected)
(observe asymptomatic_det As_det1)
(observe presymptomatic_det P_det )
(observe symptomatic_mild_det symptomatic_mild_det)
(observe symptomatic_severe_det symptomatic_severe_det)
(observe recovered_det recovered_det)
    """

        observe_tertiary_channels_str = """
(observe infectious_undet infectious_undet)
(observe infectious_det infectious_det)
(observe infectious_det_symp infectious_det_symp)
(observe infectious_det_AsP infectious_det_AsP)
    """

        if self.observeLevel == 'primary':
            observe_str = observe_primary_channels_str
        if self.observeLevel == 'secondary':
            observe_str = observe_primary_channels_str + observe_secondary_channels_str
        if self.observeLevel == 'tertiary':
            observe_str = observe_primary_channels_str + observe_tertiary_channels_str
        if self.observeLevel == 'all':
            observe_str = observe_primary_channels_str + observe_secondary_channels_str + observe_tertiary_channels_str

        observe_str = observe_str.replace("  ", " ")
        return (observe_str)

    def write_functions(self):

        functions_str = """
(func presymptomatic  (+ P P_det))

(func hospitalized  (+ H1 H2 H3 H1_det3 H2_det3 H3_det3))
(func hosp_det  (+ H1_det3 H2_det3 H3_det3))
(func critical (+ C2 C3 C2_det3 C3_det3))
(func crit_det (+ C2_det3 C3_det3))
(func deaths (+ D3 D3_det3))
(func recovered (+ RAs RSym RH1 RC2 RAs_det1 RSym_det2 RH1_det3 RC2_det3))
(func recovered_det (+ RAs_det1 RSym_det2 RH1_det3 RC2_det3))

(func asymp_cumul (+ asymptomatic RAs RAs_det1 ))
(func asymp_det_cumul (+ As_det1 RAs_det1))

(func symp_mild_cumul (+ symptomatic_mild RSym RSym_det2))
(func symp_mild_det_cumul (+ symptomatic_mild_det RSym_det2 ))

(func symp_severe_cumul (+ symptomatic_severe hospitalized critical deaths RH1 RC2 RH1_det3 RC2_det3))
(func symp_severe_det_cumul (+ symptomatic_severe_det hosp_det crit_det D3_det3  RH1_det3 RC2_det3))

(func hosp_cumul (+ hospitalized critical deaths RH1 RC2 RH1_det3 RC2_det3))
(func hosp_det_cumul (+ H1_det3 H2_det3 H3_det3 C2_det3 C3_det3 D3_det3  RH1_det3  RC2_det3))
(func crit_cumul (+ deaths critical RC2 RC2_det3))
(func crit_det_cumul (+ C2_det3 C3_det3 D3_det3 RC2_det3))
(func detected_cumul (+ As_det1 Sym_det2 Sys_det3 H1_det3 H2_det3 C2_det3 C3_det3 RAs_det1 RSym_det2 RH1_det3 RC2_det3 D3_det3))
(func death_det_cumul D3_det3 )

(func infected (+ infectious_det infectious_undet H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))
(func infected_det (+ infectious_det H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))
(func infected_cumul (+ infected recovered deaths))      
    """

        expand_base_str = """
(func asymptomatic  (+ As As_det1))

(func symptomatic_mild  (+ Sym Sym_det2))
(func symptomatic_mild_det  ( Sym_det2))

(func symptomatic_severe  (+ Sys Sys_det3))
(func symptomatic_severe_det   ( Sys_det3))

(func detected (+ As_det1 Sym_det2 Sys_det3 H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))

(func infectious_undet (+ As P Sym Sys H1 H2 H3 C2 C3))
(func infectious_det (+ As_det1 P_det Sym_det2 Sys_det3 ))

(func infectious_det_symp (+ Sym_det2 Sys_det3 ))
(func infectious_det_AsP (+ As_det1 P_det))
    """

        expand_testDelay_SymSys_str = """
(func asymptomatic  (+ As As_det1))

(func symptomatic_mild  (+ Sym Sym_preD Sym_det2))
(func symptomatic_mild_det  (+  Sym_preD Sym_det2))

(func symptomatic_severe  (+ Sys Sys_preD Sys_det3))
(func symptomatic_severe_det  (+ Sys_preD Sys_det3))

(func detected (+ As_det1 Sym_det2 Sys_det3 H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))

(func infectious_undet (+ As P Sym_preD Sym Sys_preD Sys H1 H2 H3 C2 C3))
(func infectious_det (+ As_det1 P_det Sym_det2 Sys_det3 ))

(func infectious_det_symp (+ Sym_det2 Sys_det3 ))
(func infectious_det_AsP (+ As_det1 P_det))
    """

        expand_testDelay_AsSymSys_str = """
(func asymptomatic  (+ As_preD As As_det1))

(func symptomatic_mild  (+ Sym Sym_preD Sym_det2a Sym_det2b))
(func symptomatic_mild_det  (+ Sym_preD Sym_det2a Sym_det2b))

(func symptomatic_severe  (+ Sys Sys_preD Sys_det3a Sys_det3b))
(func symptomatic_severe_det  (+ Sys_preD Sys_det3a Sys_det3b))

(func detected (+ As_det1 Sym_det2a Sym_det2b Sys_det3a Sys_det3b H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))

(func infectious_undet (+ As_preD As P Sym Sym_preD Sys Sys_preD H1 H2 H3 C2 C3))
(func infectious_det (+ As_det1 P_det Sym_det2a Sym_det2b Sys_det3a Sys_det3b))

(func infectious_det_symp (+ Sym_det2a Sym_det2b Sys_det3a Sys_det3b ))
(func infectious_det_AsP (+ As_det1 P_det))
    """

        if self.expandModel == None:
            functions_str = expand_base_str + functions_str
        if self.expandModel == "testDelay_SymSys" or self.expandModel == "uniformtestDelay":
            functions_str = expand_testDelay_SymSys_str + functions_str
        if self.expandModel == "testDelay_AsSymSys":
            functions_str = expand_testDelay_AsSymSys_str + functions_str

        functions_str = functions_str.replace("  ", " ")
        return (functions_str)

    ###
    def write_params(self):
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

        if self.expandModel == None:
            params_str = params_str + expand_base_str
        if self.expandModel == "testDelay_SymSys":
            params_str = params_str + expand_testDelay_SymSys_str
        if self.expandModel == "uniformtestDelay":
            params_str = params_str + expand_uniformtestDelay_str
        if self.expandModel == "contactTracing":
            params_str = params_str + expand_base_str + expand_contactTracing_str
        if self.expandModel == "testDelay_AsSymSys":
            params_str = params_str + expand_testDelay_AsSymSys_str

        params_str = params_str.replace("  ", " ")

        return params_str

    ### Monitor time varying parameters
    def write_observed_param(self):
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

    def write_N_population(self):
        string1 = """\n(param N (+ @speciesS@ @initialAs@) )"""
        return string1

    def write_reactions(self):

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

        if self.expandModel == None:
            reaction_str = reaction_str_I + expand_base_str + reaction_str_III
        if self.expandModel == "testDelay_SymSys" or self.expandModel == "uniformtestDelay":
            reaction_str = reaction_str_I + expand_testDelay_SymSys_str + reaction_str_III
        if self.expandModel == 'testDelay_AsSymSys':
            reaction_str = reaction_str_I + expand_testDelay_AsSymSys_str + reaction_str_III

        reaction_str = reaction_str.replace("  ", " ")

        return reaction_str

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
        time_event_str = """(time-event contact_tracing_start @contact_tracing_start_1@ ( {change_param} ))""".format(
            change_param=change_param_str)

        contactTracing_str = d_Sym_ct_param_str + "\n" + time_event_str

        return contactTracing_str

    def write_interventions(self, total_string):

        param_change_str = """
(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@)))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@)))
(time-event detection4 @detection_time_4@ ((d_Sys @d_Sys_incr4@)))
(time-event detection5 @detection_time_5@ ((d_Sys @d_Sys_incr5@)))
(time-event detection6 @detection_time_6@ ((d_Sys @d_Sys_incr6@)))

(time-event frac_crit_adjust1 @crit_time_1@ ((fraction_critical @fraction_critical_incr1@) (fraction_hospitalized (- 1 (+ @fraction_critical_incr1@ fraction_dead))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) ))  
(time-event frac_crit_adjust2 @crit_time_2@ ((fraction_critical @fraction_critical_incr2@) (fraction_hospitalized (- 1 (+ @fraction_critical_incr2@ fraction_dead))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) ))
(time-event frac_crit_adjust3 @crit_time_3@ ((fraction_critical @fraction_critical_incr3@) (fraction_hospitalized (- 1 (+ @fraction_critical_incr3@ fraction_dead))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) )) 

(param cfr_change1 (* @cfr@ (/ 2 3) ) )
(param cfr_change2 (* @cfr@ (/ 1 3) ) )
(time-event cfr_adjust1 @cfr_time_1@ ((cfr cfr_change1) (fraction_dead (/ cfr fraction_severe)) (fraction_hospitalized (- 1 (+ fraction_critical fraction_dead))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) )) 
(time-event cfr_adjust2 @cfr_time_2@ ((cfr cfr_change2) (fraction_dead (/ cfr fraction_severe)) (fraction_hospitalized (- 1 (+ fraction_critical fraction_dead))) (Kh1 (/ fraction_hospitalized time_to_hospitalization)) (Kh2 (/ fraction_critical time_to_hospitalization )) (Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) (Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) )) 
"""

        ki_multiplier_change_str = """
(param Ki_red3a (* Ki @ki_multiplier_3a@))
(param Ki_red3b (* Ki @ki_multiplier_3b@))
(param Ki_red3c (* Ki @ki_multiplier_3c@))
(param Ki_red4 (* Ki @ki_multiplier_4@))
(param Ki_red5 (* Ki @ki_multiplier_5@))
(param Ki_red6 (* Ki @ki_multiplier_6@))
(param Ki_red7 (* Ki @ki_multiplier_7@))
(param Ki_red8 (* Ki @ki_multiplier_8@))
(param Ki_red9 (* Ki @ki_multiplier_9@))
(param Ki_red10 (* Ki @ki_multiplier_10@))
(param Ki_red11 (* Ki @ki_multiplier_11@))
(param Ki_red12 (* Ki @ki_multiplier_12@))
(param Ki_red13 (* Ki @ki_multiplier_13@))
(param Ki_red14 (* Ki @ki_multiplier_14@))
(param Ki_red15 (* Ki @ki_multiplier_15@))

(time-event ki_multiplier_change_3a @ki_multiplier_time_3a@ ((Ki Ki_red3a)))
(time-event ki_multiplier_change_3b @ki_multiplier_time_3b@ ((Ki Ki_red3b)))
(time-event ki_multiplier_change_3c @ki_multiplier_time_3c@ ((Ki Ki_red3c)))
(time-event ki_multiplier_change4 @ki_multiplier_time_4@ ((Ki Ki_red4)))
(time-event ki_multiplier_change5 @ki_multiplier_time_5@ ((Ki Ki_red5)))
(time-event ki_multiplier_change6 @ki_multiplier_time_6@ ((Ki Ki_red6)))
(time-event ki_multiplier_change7 @ki_multiplier_time_7@ ((Ki Ki_red7)))
(time-event ki_multiplier_change8 @ki_multiplier_time_8@ ((Ki Ki_red8)))
(time-event ki_multiplier_change9 @ki_multiplier_time_9@ ((Ki Ki_red9)))
(time-event ki_multiplier_change10 @ki_multiplier_time_10@ ((Ki Ki_red10)))
(time-event ki_multiplier_change11 @ki_multiplier_time_11@ ((Ki Ki_red11)))
(time-event ki_multiplier_change12 @ki_multiplier_time_12@ ((Ki Ki_red12)))
(time-event ki_multiplier_change13 @ki_multiplier_time_13@ ((Ki Ki_red13)))
(time-event ki_multiplier_change14 @ki_multiplier_time_14@ ((Ki Ki_red14)))
(time-event ki_multiplier_change15 @ki_multiplier_time_15@ ((Ki Ki_red15)))
                """
        rollback_str = """
(time-event ki_multiplier_change_rollback @socialDistance_rollback_time@ ((Ki Ki_red4)))
                    """

        rollbacktriggered_str = """
(state-event rollbacktrigger (and (> time @triggertime@) (> {channel} (* @trigger@ @capacity_multiplier@)) ) ((Ki Ki_red4)))
                        """.format(channel=self.trigger_channel)

        d_Sym_change_str = """
(time-event d_Sym_change1 @d_Sym_change_time_1@ ((d_Sym @d_Sym_change1@)))
(time-event d_Sym_change2 @d_Sym_change_time_2@ ((d_Sym @d_Sym_change2@)))
(time-event d_Sym_change3 @d_Sym_change_time_3@ ((d_Sym @d_Sym_change3@)))
(time-event d_Sym_change4 @d_Sym_change_time_4@ ((d_Sym @d_Sym_change4@)))
(time-event d_Sym_change5 @d_Sym_change_time_5@ ((d_Sym @d_Sym_change5@)))

(observe recovery_time_crit_t recovery_time_crit)
(time-event LOS_ICU_change_1 @recovery_time_crit_change_time_1@ ((recovery_time_crit @recovery_time_crit_change1@) (Kr_c (/ 1 @recovery_time_crit_change1@))))

(observe recovery_time_hosp_t recovery_time_hosp)
(time-event LOS_nonICU_change_1 @recovery_time_hosp_change_time_1@ ((recovery_time_hosp @recovery_time_hosp_change1@) (Kr_h (/ 1 @recovery_time_hosp_change1@))))
    """

        interventionSTOP_str = """
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
        # starting point is current level of transmission  Ki_red6
        interventionSTOP_adj2_str = """
(param Ki_back (+ Ki_red6 (* @backtonormal_multiplier@ (- Ki Ki_red6))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki Ki_back)))
            """

        gradual_reopening_str = """
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
        gradual_reopening2_str = """
(param Ki_back1 (+ Ki_red6 (* @reopening_multiplier_4@ 0.25 (- Ki Ki_red6))))
(param Ki_back2 (+ Ki_red6 (* @reopening_multiplier_4@ 0.50 (- Ki Ki_red6))))
(param Ki_back3 (+ Ki_red6 (* @reopening_multiplier_4@ 0.75 (- Ki Ki_red6))))
(param Ki_back4 (+ Ki_red6 (* @reopening_multiplier_4@ 1.00 (- Ki Ki_red6))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki Ki_back1)))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki Ki_back2)))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki Ki_back3)))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki Ki_back4)))
            """

        improveHS_str = covidModel.define_change_detection_and_isolation(reduced_inf_of_det_cases=False,
                                                                         d_As=False,
                                                                         d_P=False,
                                                                         d_Sym_ct=True)

        contactTracing_str = covidModel.define_change_detection_and_isolation(reduced_inf_of_det_cases=True,
                                                                              d_As=True,
                                                                              d_P=True,
                                                                              d_Sym_ct=False)

        contactTracing_improveHS_str = covidModel.define_change_detection_and_isolation(reduced_inf_of_det_cases=True,
                                                                                        d_As=True,
                                                                                        d_P=True,
                                                                                        d_Sym_ct=True)

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

        fittedTimeEvents_str = param_change_str + ki_multiplier_change_str + d_Sym_change_str

        if self.add_interventions == "interventionStop":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_str)
        if self.add_interventions == "interventionSTOP_adj":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj_str)
        if self.add_interventions == "interventionSTOP_adj2":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj2_str)
        if self.add_interventions == "gradual_reopening":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening_str)
        if self.add_interventions == "gradual_reopening2":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str)
        if self.add_interventions == "baseline":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str)
        if self.add_interventions == "rollback":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + rollback_str)
        if self.add_interventions == "reopen_rollback":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + interventionSTOP_adj2_str + rollback_str)
        if self.add_interventions == "reopen_contactTracing":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + gradual_reopening2_str + contactTracing_str)
        if self.add_interventions == "reopen_contactTracing_improveHS":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + gradual_reopening2_str + contactTracing_improveHS_str)
        if self.add_interventions == "reopen_improveHS":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + gradual_reopening2_str + improveHS_str)
        if self.add_interventions == "contactTracing":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + contactTracing_str)
        if self.add_interventions == "contactTracing_improveHS":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + contactTracing_improveHS_str)
        if self.add_interventions == "improveHS":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + improveHS_str)
        if self.add_interventions == "rollbacktriggered":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + rollbacktriggered_str)

        if self.change_testDelay != None:
            if self.change_testDelay == "uniform":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_uniformtestDelay_str)
            if self.change_testDelay == "As":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str)
            if self.change_testDelay == "Sym":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sym_str)
            if self.change_testDelay == "Sys":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sys_str)
            if self.change_testDelay == "AsSym":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]',
                                                    change_testDelay_As_str + '\n' + change_testDelay_Sym_str)
            if self.change_testDelay == "SymSys":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]',
                                                    change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)
            if self.change_testDelay == "AsP":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]',
                                                    change_testDelay_As_str + '\n' + change_testDelay_P_str)
            if self.change_testDelay == "AsSymSys":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]',
                                                    change_testDelay_As_str + '\n' + change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)

        return total_string

    def generate_emodl(self):

        if self.emodl_name is None:
            emodl_name = f'{self.model}_{self.add_interventions}'
            file_output = os.path.join(self.emodl_dir, f'{emodl_name}.emodl')
        else:
            file_output = os.path.join(self.emodl_dir, f'{self.emodl_name}.emodl')
        if (os.path.exists(file_output)):
            os.remove(file_output)

        model_name = "seir.emodl"
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

        total_string = total_string + covidModel.write_species(self)
        functions = covidModel.write_functions(self)
        observe_string = observe_string + covidModel.write_observe(self)
        reaction_string = reaction_string + covidModel.write_reactions(self)
        functions_string = functions_string + functions

        param_string = covidModel.write_params(self) + param_string + covidModel.write_observed_param(
            self) + covidModel.write_N_population(self)
        functions_string = functions_string
        intervention_string = ";[INTERVENTIONS]\n;[ADDITIONAL_TIMEEVENTS]"

        total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string + '\n\n' + reaction_string + '\n\n' + footer_str

        ### Custom adjustments for EMS 6 (earliest start date)
        total_string = total_string.replace('(species As::EMS_6 0)', '(species As::EMS_6 1)')
        ### Add interventions (optional)
        if self.add_interventions != None:
            total_string = covidModel.write_interventions(self, total_string)

        # print(total_string)
        emodl = open(file_output, "w")
        emodl.write(total_string)
        emodl.close()
        if (os.path.exists(file_output)):
            print("{} file was successfully created".format(file_output))
        else:
            print("{} file was NOT created".format(file_output))
        return emodl_name

    def showOptions():
        # import json
        model_options = {'expandModel': ("uniformtestDelay", "testDelay_SymSys", "testDelay_AsSymSys"),
                         'observeLevel': ('primary', 'secondary', 'tertiary', 'all'),
                         'add_interventions': ("baseline",
                                               "rollback",
                                               "reopen_rollback",
                                               "rollbacktriggered_delay",
                                               "gradual_reopening",
                                               "gradual_reopening2",
                                               "interventionSTOP",
                                               "interventionSTOP_adj",
                                               "rollbacktriggered",
                                               "contactTracing",
                                               "improveHS",
                                               "reopen_improveHS",
                                               "contactTracing_improveHS"
                                               "reopen_contactTracing_improveHS"),
                         'change_testDelay': ("None", "Sym", "AsSym"),
                         'trigger_channel': ("None", "critical", "crit_det", "hospitalized", "hosp_det")}
        return print(json.dumps(model_options, indent=4, sort_keys=True))
