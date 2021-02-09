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
                 change_testDelay=False, trigger_channel=None, add_migration=False, emodl_name=None, git_dir=git_dir):
        self.model = 'locale'
        self.grpList = ['EMS_1', 'EMS_2', 'EMS_3', 'EMS_4', 'EMS_5', 'EMS_6', 'EMS_7', 'EMS_8', 'EMS_9', 'EMS_10',
                        'EMS_11']
        self.expandModel = expandModel
        self.add_migration = add_migration
        self.observeLevel = observeLevel
        self.add_interventions = add_interventions
        self.change_testDelay = change_testDelay
        self.trigger_channel = trigger_channel
        self.emodl_name = emodl_name
        self.n_steps = 4
        self.emodl_dir = os.path.join(git_dir, 'emodl')

    def write_species(self, grp):
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
(species H2pre::{grp} 0)
(species H2post::{grp} 0)   
(species H3::{grp} 0)
(species H1_det3::{grp} 0)
(species H2pre_det3::{grp} 0)
(species H2post_det3::{grp} 0) 							 
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

        if self.expandModel == "SymSys" or self.expandModel == "uniform":
            species_str = species_str + expand_testDelay_SymSys_str
        if self.expandModel == "AsSymSys":
            species_str = species_str + expand_testDelay_AsSymSys_str

        return species_str

    ## For postprocessing that splits by '_', it is easier if EMS are names EMS-1 not EMS_1
    ## This might change depending on the postprocessing
    def sub(x):
        xout = re.sub('_', '-', str(x), count=1)
        return xout

    def write_observe(self, grp):
        grp = str(grp)
        grpout = covidModel.sub(grp)

        observe_primary_channels_str = """
(observe susceptible_{grpout} S::{grp})
(observe infected_{grpout} infected_{grp})
(observe infected_det_{grpout} infected_det_{grp})
(observe recovered_{grpout} recovered_{grp})
(observe infected_cumul_{grpout} infected_cumul_{grp})
(observe infected_det_cumul_{grpout} infected_det_cumul_{grp})

(observe asymp_cumul_{grpout} asymp_cumul_{grp} )
(observe asymp_det_cumul_{grpout} asymp_det_cumul_{grp})
(observe symptomatic_mild_{grpout} symptomatic_mild_{grp})
(observe symptomatic_severe_{grpout} symptomatic_severe_{grp})
(observe symp_mild_cumul_{grpout} symp_mild_cumul_{grp})
(observe symp_severe_cumul_{grpout} symp_severe_cumul_{grp})
(observe symp_mild_det_cumul_{grpout} symp_mild_det_cumul_{grp})
(observe symp_severe_det_cumul_{grpout} symp_severe_det_cumul_{grp})

(observe hosp_det_cumul_{grpout} hosp_det_cumul_{grp} )
(observe hosp_cumul_{grpout} hosp_cumul_{grp})
(observe detected_cumul_{grpout} detected_cumul_{grp} )

(observe crit_cumul_{grpout} crit_cumul_{grp})
(observe crit_det_cumul_{grpout} crit_det_cumul_{grp})
(observe death_det_cumul_{grpout} death_det_cumul_{grp} )

(observe deaths_det_{grpout} D3_det3::{grp})
(observe deaths_{grpout} deaths_{grp})

(observe crit_det_{grpout} crit_det_{grp})
(observe critical_{grpout} critical_{grp})
(observe hosp_det_{grpout} hosp_det_{grp})
(observe hospitalized_{grpout} hospitalized_{grp})
    """.format(grpout=grpout, grp=grp)

        observe_secondary_channels_str = """
(observe exposed_{grpout} E::{grp})

(observe asymptomatic_det_{grpout} As_det1::{grp})
(observe asymptomatic_{grpout} asymptomatic_{grp})

(observe presymptomatic_{grpout} presymptomatic_{grp})
(observe presymptomatic_det{grpout} P_det::{grp} )

(observe detected_{grpout} detected_{grp})

(observe symptomatic_mild_det_{grpout} symptomatic_mild_det_{grp})
(observe symptomatic_severe_det_{grpout} symptomatic_severe_det_{grp})
(observe recovered_det_{grpout} recovered_det_{grp})
    """.format(grpout=grpout, grp=grp)

        observe_tertiary_channels_str = """
(observe infectious_undet_{grpout} infectious_undet_{grp})
(observe infectious_det_{grpout} infectious_det_{grp})
(observe infectious_det_symp_{grpout} infectious_det_symp_{grp})
(observe infectious_det_AsP_{grpout} infectious_det_AsP_{grp})
    """.format(grpout=grpout, grp=grp)

        if self.observeLevel == 'primary':
            observe_str = observe_primary_channels_str
        if self.observeLevel == 'secondary':
            observe_str = observe_primary_channels_str + observe_secondary_channels_str
        if self.observeLevel == 'tertiary':
            observe_str = observe_primary_channels_str + observe_tertiary_channels_str
        if self.observeLevel == 'all':
            observe_str = observe_primary_channels_str + observe_secondary_channels_str + observe_tertiary_channels_str

        observe_str = observe_str.replace("  ", " ")
        return observe_str

    def write_functions(self, grp):
        grp = str(grp)
        functions_str = """
(func presymptomatic_{grp}  (+ P::{grp} P_det::{grp}))

(func hospitalized_{grp}  (+ H1::{grp} H2pre::{grp} H2post::{grp} H3::{grp} H1_det3::{grp} H2pre_det3::{grp} H2post_det3::{grp}  H3_det3::{grp}))
(func hosp_det_{grp}  (+ H1_det3::{grp} H2pre_det3::{grp} H2post_det3::{grp} H3_det3::{grp}))
(func critical_{grp} (+ C2::{grp} C3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func crit_det_{grp} (+ C2_det3::{grp} C3_det3::{grp}))
(func deaths_{grp} (+ D3::{grp} D3_det3::{grp}))
(func recovered_{grp} (+ RAs::{grp} RSym::{grp} RH1::{grp} RC2::{grp} RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func recovered_det_{grp} (+ RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp}))

(func asymp_cumul_{grp} (+ asymptomatic_{grp} RAs::{grp} RAs_det1::{grp} ))
(func asymp_det_cumul_{grp} (+ As_det1::{grp} RAs_det1::{grp}))

(func symp_mild_cumul_{grp} (+ symptomatic_mild_{grp} RSym::{grp} RSym_det2::{grp}))
(func symp_mild_det_cumul_{grp} (+ symptomatic_mild_det_{grp} RSym_det2::{grp} ))

(func symp_severe_cumul_{grp} (+ symptomatic_severe_{grp} hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func symp_severe_det_cumul_{grp} (+ symptomatic_severe_det_{grp} hosp_det_{grp} crit_det_{grp} D3_det3::{grp}  RH1_det3::{grp} RC2_det3::{grp}))

(func hosp_cumul_{grp} (+ hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func hosp_det_cumul_{grp} (+ H1_det3::{grp} H2pre_det3::{grp} H2post_det3::{grp}  H3_det3::{grp} C2_det3::{grp} C3_det3::{grp} D3_det3::{grp}  RH1_det3::{grp}  RC2_det3::{grp}))
(func crit_cumul_{grp} (+ deaths_{grp} critical_{grp} RC2::{grp} RC2_det3::{grp}))
(func crit_det_cumul_{grp} (+ C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RC2_det3::{grp}))
(func detected_cumul_{grp} (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2pre_det3::{grp}  H2post_det3::{grp}  C2_det3::{grp} C3_det3::{grp} RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp} D3_det3::{grp}))
(func death_det_cumul_{grp} D3_det3::{grp} )
(func infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3::{grp} H2pre_det3::{grp} H2post_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func infected_det_{grp} (+ infectious_det_{grp} H1_det3::{grp} H2pre_det3::{grp} H2post_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func infected_cumul_{grp} (+ infected_{grp} recovered_{grp} deaths_{grp}))   
(func infected_det_cumul_{grp} (+ infected_det_{grp} recovered_det_{grp} D3_det3::{grp}))    
    """.format(grp=grp)

        expand_base_str = """
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))

(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_det2::{grp}))
(func symptomatic_mild_det_{grp}  ( Sym_det2::{grp}))

(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_det3::{grp}))
(func symptomatic_severe_det_{grp}   ( Sys_det3::{grp}))

(func detected_{grp} (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2pre_det3::{grp} H2post_det3::{grp}  H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym::{grp} Sys::{grp} H1::{grp} H2pre::{grp} H2post::{grp}  H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} P_det::{grp} Sym_det2::{grp} Sys_det3::{grp} ))

(func infectious_det_symp_{grp} (+ Sym_det2::{grp} Sys_det3::{grp} ))
(func infectious_det_AsP_{grp} (+ As_det1::{grp} P_det::{grp}))
    """.format(grp=grp)

        expand_testDelay_SymSys_str = """
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))

(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_preD::{grp} Sym_det2::{grp}))
(func symptomatic_mild_det_{grp}  (+  Sym_preD::{grp} Sym_det2::{grp}))

(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_preD::{grp} Sys_det3::{grp}))
(func symptomatic_severe_det_{grp}  (+ Sys_preD::{grp} Sys_det3::{grp}))

(func detected_{grp} (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2pre_det3::{grp} H2post_det3::{grp}  H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym_preD::{grp} Sym::{grp} Sys_preD::{grp} Sys::{grp} H1::{grp} H2pre::{grp}  H2post::{grp}  H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} P_det::{grp} Sym_det2::{grp} Sys_det3::{grp} ))

(func infectious_det_symp_{grp} (+ Sym_det2::{grp} Sys_det3::{grp} ))
(func infectious_det_AsP_{grp} (+ As_det1::{grp} P_det::{grp}))
    """.format(grp=grp)

        expand_testDelay_AsSymSys_str = """
(func asymptomatic_{grp}  (+ As_preD::{grp} As::{grp} As_det1::{grp}))

(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_preD::{grp} Sym_det2a::{grp} Sym_det2b::{grp}))
(func symptomatic_mild_det_{grp}  (+ Sym_preD::{grp} Sym_det2a::{grp} Sym_det2b::{grp}))

(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_preD::{grp} Sys_det3a::{grp} Sys_det3b::{grp}))
(func symptomatic_severe_det_{grp}  (+ Sys_preD::{grp} Sys_det3a::{grp} Sys_det3b::{grp}))

(func detected_{grp} (+ As_det1::{grp} Sym_det2a::{grp} Sym_det2b::{grp} Sys_det3a::{grp} Sys_det3b::{grp} H1_det3::{grp} H2pre_det3::{grp} H2post_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func infectious_undet_{grp} (+ As_preD::{grp} As::{grp} P::{grp} Sym::{grp} Sym_preD::{grp} Sys::{grp} Sys_preD::{grp} H1::{grp} H2pre::{grp} H2post::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} P_det::{grp} Sym_det2a::{grp} Sym_det2b::{grp} Sys_det3a::{grp} Sys_det3b::{grp}))
(func infectious_undet_symp_{grp} (+ P::{grp} Sym::{grp} Sym_preD::{grp} Sys::{grp} Sys_preD::{grp} H1::{grp} H2pre::{grp} H2post::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_undet_As_{grp} (+ As_preD::{grp} As::{grp}))
(func infectious_det_symp_{grp} (+ Sym_det2a::{grp} Sym_det2b::{grp} Sys_det3a::{grp} Sys_det3b::{grp} ))
(func infectious_det_AsP_{grp} (+ As_det1::{grp} P_det::{grp}))
    """.format(grp=grp)

        if self.expandModel == None:
            functions_str = expand_base_str + functions_str
        if self.expandModel == "SymSys" or self.expandModel == "uniform":
            functions_str = expand_testDelay_SymSys_str + functions_str
        if self.expandModel == "AsSymSys":
            functions_str = expand_testDelay_AsSymSys_str + functions_str

        functions_str = functions_str.replace("  ", " ")
        return functions_str

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
(param recovery_time_postcrit @recovery_time_postcrit@)													   
(param fraction_symptomatic @fraction_symptomatic@)
(param fraction_severe @fraction_severe@)
(param fraction_critical @fraction_critical@ )

;(param fraction_dead (/ cfr fraction_severe))
(param fraction_dead @fraction_dead@ )
(param fraction_hospitalized (- 1 (+ fraction_critical fraction_dead)))

(param reduced_inf_of_det_cases @reduced_inf_of_det_cases@)
(param reduced_infectious_As @reduced_infectious_As@)													 
(param reduced_inf_of_det_cases_ct 0)

(param d_As @d_As@)
(param d_P @d_P@)
(param d_Sys @d_Sys@)
(param d_Sym @d_Sym@)					 
(param Kr_a (/ 1 recovery_time_asymp))
(param Kr_m (/ 1 recovery_time_mild))
(param Kl (/ (- 1 fraction_symptomatic ) time_to_infectious))
(param Ks (/ fraction_symptomatic  time_to_infectious))
(param Ksys (* fraction_severe (/ 1 time_to_symptoms)))
(param Ksym (* (- 1 fraction_severe) (/ 1 time_to_symptoms)))
(param Km (/ 1 time_to_death))
(param Kc (/ 1 time_to_critical))
(param Kr_hc (/ 1 recovery_time_postcrit))
; region specific
;(param Kr_h (/ 1 recovery_time_hosp))
;(param Kr_c (/ 1 recovery_time_crit))
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
        if self.expandModel == "SymSys":
            params_str = params_str + expand_testDelay_SymSys_str
        if self.expandModel == "uniform":
            params_str = params_str + expand_uniformtestDelay_str
        if self.expandModel == "AsSymSys":
            params_str = params_str + expand_testDelay_AsSymSys_str

        params_str = params_str.replace("  ", " ")

        return params_str

    def write_migration_param(self):
        x1 = range(1, len(self.grpList) + 1)
        x2 = range(1, len(self.grpList) + 1)
        param_str = ""
        for x1_i in x1:
            param_str = param_str + "\n"
            for x2_i in x2:
                # x1_i=1
                param_str = param_str + """\n(param toEMS_{x1_i}_from_EMS_{x2_i} @toEMS_{x1_i}_from_EMS_{x2_i}@)""".format(
                    x1_i=x1_i, x2_i=x2_i)
        return param_str

    def write_travel_reaction(grp, travelspeciesList=None):
        x1_i = int(grp.split("_")[1])
        x2 = list(range(1, 12))
        x2 = [i for i in x2 if i != x1_i]
        reaction_str = ""
        if travelspeciesList == None:
            travelspeciesList = ["S", "E", "As", "P"]

        for travelspecies in travelspeciesList:
            reaction_str = reaction_str + "\n"
            for x2_i in x2:
                # x1_i=1
                reaction_str = reaction_str + """\n(reaction {travelspecies}_travel_EMS_{x2_i}to{x1_i}  ({travelspecies}::EMS_{x2_i}) ({travelspecies}::EMS_{x1_i}) (* {travelspecies}::EMS_{x2_i} toEMS_{x1_i}_from_EMS_{x2_i} (/ N_EMS_{x2_i} (+ S::EMS_{x2_i} E::EMS_{x2_i} As::EMS_{x2_i} P::EMS_{x2_i} recovered_EMS_{x2_i}))))""".format(
                    travelspecies=travelspecies, x1_i=x1_i, x2_i=x2_i)

        return reaction_str

    def write_Ki_timevents(grp):
        grp = str(grp)
        grpout = covidModel.sub(grp)
        params_str = """
(param Ki_{grp} @Ki_{grp}@)
(observe Ki_t_{grpout} Ki_{grp})
(time-event time_infection_import @time_infection_import_{grp}@ ((As::{grp} @initialAs_{grp}@) (S::{grp} (- S::{grp} @initialAs_{grp}@))))
    """.format(grpout=grpout, grp=grp)
        params_str = params_str.replace("  ", " ")

        return params_str

    def write_N_population(self):
        stringAll = ""
        for key in self.grpList:
            string1 = """\n(param N_{grp} (+ @speciesS_{grp}@ @initialAs_{grp}@) )""".format(grp=key)
            stringAll = stringAll + string1

        string2 = "\n(param N_All (+ " + covidModel.repeat_string_by_grp('N_', self.grpList) + "))"
        string3 = "\n(observe N_All N_All)"
        stringAll = stringAll + string2 + string3

        return stringAll

    def repeat_string_by_grp(fixedstring, grpList):
        stringAll = ""
        for grp in grpList:
            temp_string = " " + fixedstring + grp
            stringAll = stringAll + temp_string

        return stringAll

    def write_All(self):

        grpList = self.grpList
        obs_primary_All_str = ""

        obs_primary_All_str = ""
        obs_primary_All_str = obs_primary_All_str + "\n(observe susceptible_All (+ " + covidModel.repeat_string_by_grp(
            'S::', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe infected_All (+ " + covidModel.repeat_string_by_grp(
            'infected_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe infected_det_All (+ " + covidModel.repeat_string_by_grp(
            'infected_det_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe recovered_All (+ " + covidModel.repeat_string_by_grp(
            'recovered_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe recovered_det_All (+ " + covidModel.repeat_string_by_grp(
            'recovered_det_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe infected_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'infected_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe infected_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'infected_det_cumul_', grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe asymp_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'asymp_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe asymp_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'asymp_det_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symptomatic_mild_All (+ " + covidModel.repeat_string_by_grp(
            'symptomatic_mild_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symptomatic_severe_All (+ " + covidModel.repeat_string_by_grp(
            'symptomatic_severe_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_mild_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'symp_mild_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_severe_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'symp_severe_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_mild_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'symp_mild_det_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_severe_det_cumul_All  (+ " + covidModel.repeat_string_by_grp(
            'symp_severe_det_cumul_', grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe hosp_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'hosp_det_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe hosp_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'hosp_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe detected_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'detected_cumul_', grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe crit_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'crit_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe crit_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'crit_det_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe death_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'death_det_cumul_', grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe deaths_det_All (+ " + covidModel.repeat_string_by_grp(
            'D3_det3::',
            grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe deaths_All (+ " + covidModel.repeat_string_by_grp(
            'deaths_',
            grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe crit_det_All (+ " + covidModel.repeat_string_by_grp(
            'crit_det_',
            grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe critical_All (+ " + covidModel.repeat_string_by_grp(
            'critical_',
            grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe hosp_det_All (+ " + covidModel.repeat_string_by_grp(
            'hosp_det_',
            grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe hospitalized_All (+ " + covidModel.repeat_string_by_grp(
            'hospitalized_', grpList) + "))"

        obs_secondary_All_str = ""
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe exposed_All (+ " + covidModel.repeat_string_by_grp(
            'E::',
            grpList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe asymptomatic_All (+ " + covidModel.repeat_string_by_grp(
            'asymptomatic_', grpList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe asymptomatic_det_All (+ " + covidModel.repeat_string_by_grp(
            'As_det1::', grpList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe presymptomatic_All (+ " + covidModel.repeat_string_by_grp(
            'P::', grpList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe presymptomatic_det_All (+ " + covidModel.repeat_string_by_grp(
            'P_det::', grpList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe detected_All (+ " + covidModel.repeat_string_by_grp(
            'detected_', grpList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe symptomatic_mild_det_All (+ " + covidModel.repeat_string_by_grp(
            'symptomatic_mild_det_', grpList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe symptomatic_severe_det_All (+ " + covidModel.repeat_string_by_grp(
            'symptomatic_severe_det_', grpList) + "))"

        obs_tertiary_All_str = ""
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_det_All (+ " + covidModel.repeat_string_by_grp(
            'infectious_det_', grpList) + "))"
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_undet_All (+ " + covidModel.repeat_string_by_grp(
            'infectious_undet_', grpList) + "))"
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_det_symp_All (+ " + covidModel.repeat_string_by_grp(
            'infectious_det_symp_', grpList) + "))"
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_det_AsP_All (+ " + covidModel.repeat_string_by_grp(
            'infectious_det_AsP_', grpList) + "))"

        if self.observeLevel == 'primary':
            obs_All_str = obs_primary_All_str
        if self.observeLevel == 'secondary':
            obs_All_str = obs_primary_All_str + obs_secondary_All_str
        if self.observeLevel == 'tertiary':
            obs_All_str = obs_primary_All_str + obs_tertiary_All_str
        if self.observeLevel == 'all':
            obs_All_str = obs_primary_All_str + obs_secondary_All_str + obs_tertiary_All_str

        obs_All_str = obs_All_str.replace("  ", " ")
        return obs_All_str

    def write_reactions(self, grp):
        grp = str(grp)

        reaction_str_I = """
(reaction exposure_{grp}   (S::{grp}) (E::{grp}) (* Ki_{grp} S::{grp} (/  (+ infectious_undet_symp_{grp} (* infectious_undet_As_{grp} reduced_infectious_As ) (* infectious_det_symp_{grp} reduced_inf_of_det_cases) (* infectious_det_AsP_{grp} reduced_inf_of_det_cases_ct)) N_{grp} )))
    """.format(grp=grp)

        reaction_str_III = """
(reaction recovery_H1_{grp}   (H1::{grp})   (RH1::{grp})   (* Kr_h_{grp} H1::{grp}))
(reaction recovery_C2_{grp}   (C2::{grp})   (H2post::{grp})   (* Kr_c_{grp} C2::{grp}))
(reaction recovery_H2post_{grp}   (H2post::{grp})   (RC2::{grp})   (* Kr_hc H2post::{grp}))
(reaction recovery_H1_det3_{grp}   (H1_det3::{grp})   (RH1_det3::{grp})   (* Kr_h_{grp} H1_det3::{grp}))
(reaction recovery_C2_det3_{grp}   (C2_det3::{grp})   (H2post_det3::{grp})   (* Kr_c_{grp} C2_det3::{grp}))
(reaction recovery_H2post_det3_{grp}   (H2post_det3::{grp})   (RC2_det3::{grp})   (* Kr_hc H2post_det3::{grp}))
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
(reaction hospitalization_2_{grp}   (Sys::{grp})   (H2pre::{grp})   (* Kh2 Sys::{grp}))
(reaction hospitalization_3_{grp}   (Sys::{grp})   (H3::{grp})   (* Kh3 Sys::{grp}))
(reaction critical_2_{grp}   (H2pre::{grp})   (C2::{grp})   (* Kc H2pre::{grp}))
(reaction critical_3_{grp}   (H3::{grp})   (C3::{grp})   (* Kc H3::{grp}))
(reaction death_{grp}   (C3::{grp})   (D3::{grp})   (* Km C3::{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3::{grp})   (H1_det3::{grp})   (* Kh1 Sys_det3::{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3::{grp})   (H2pre_det3::{grp})   (* Kh2 Sys_det3::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3::{grp})   (H3_det3::{grp})   (* Kh3 Sys_det3::{grp}))
(reaction critical_2_det2_{grp}   (H2pre_det3::{grp})   (C2_det3::{grp})   (* Kc H2pre_det3::{grp}))
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
(reaction hospitalization_2_{grp}   (Sys::{grp})   (H2pre::{grp})   (* Kh2_D Sys::{grp}))
(reaction hospitalization_3_{grp}   (Sys::{grp})   (H3::{grp})   (* Kh3_D Sys::{grp}))
(reaction critical_2_{grp}   (H2pre::{grp})   (C2::{grp})   (* Kc H2pre::{grp}))
(reaction critical_3_{grp}   (H3::{grp})   (C3::{grp})   (* Kc H3::{grp}))
(reaction death_{grp}   (C3::{grp})   (D3::{grp})   (* Km C3::{grp}))
(reaction hospitalization_1_det_{grp}   (Sys_det3::{grp})   (H1_det3::{grp})   (* Kh1_D Sys_det3::{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3::{grp})   (H2pre_det3::{grp})   (* Kh2_D Sys_det3::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3::{grp})   (H3_det3::{grp})   (* Kh3_D Sys_det3::{grp}))
(reaction critical_2_det2_{grp}   (H2pre_det3::{grp})   (C2_det3::{grp})   (* Kc H2pre_det3::{grp}))
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
(reaction mild_symptomatic_undet_{grp} (Sym_preD::{grp})  (Sym::{grp}) (* Ksym_D Sym_preD::{grp} (- 1 d_Sym)))
(reaction severe_symptomatic_undet_{grp} (Sys_preD::{grp})  (Sys::{grp})  (* Ksys_D Sys_preD::{grp} (- 1 d_Sys)))

; new detections  - time to detection is subtracted from hospital time
(reaction mild_symptomatic_det_{grp} (Sym_preD::{grp})  (Sym_det2a::{grp}) (* Ksym_D Sym_preD::{grp} d_Sym))
(reaction severe_symptomatic_det_{grp} (Sys_preD::{grp})  (Sys_det3a::{grp})  (* Ksys_D Sys_preD::{grp} d_Sys))

; developing symptoms - already detected, same time to symptoms as in master emodl
(reaction mild_symptomatic_det_{grp} (P_det::{grp})  (Sym_det2b::{grp}) (* Ksym  P_det::{grp}))
(reaction severe_symptomatic_det_{grp} (P_det::{grp})  (Sys_det3b::{grp})  (* Ksys  P_det::{grp} ))

(reaction hospitalization_1_{grp}  (Sys::{grp})   (H1::{grp})   (* Kh1_D Sys::{grp}))
(reaction hospitalization_2_{grp}   (Sys::{grp})   (H2pre::{grp})   (* Kh2_D Sys::{grp}))
(reaction hospitalization_3_{grp}   (Sys::{grp})   (H3::{grp})   (* Kh3_D Sys::{grp}))
(reaction critical_2_{grp}  (H2pre::{grp})   (C2::{grp})   (* Kc H2pre::{grp}))
(reaction critical_3_{grp}   (H3::{grp})   (C3::{grp})   (* Kc H3::{grp}))
(reaction death_{grp}   (C3::{grp})   (D3::{grp})   (* Km C3::{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3a::{grp})   (H1_det3::{grp})   (* Kh1_D Sys_det3a::{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3a::{grp})   (H2pre_det3::{grp})   (* Kh2_D Sys_det3a::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3a::{grp})   (H3_det3::{grp})   (* Kh3_D Sys_det3a::{grp}))
(reaction hospitalization_1_det_{grp}   (Sys_det3b::{grp})   (H1_det3::{grp})   (* Kh1 Sys_det3b::{grp}))
(reaction hospitalization_2pre_det_{grp}   (Sys_det3b::{grp})   (H2pre_det3::{grp})   (* Kh2 Sys_det3b::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3b::{grp})   (H3_det3::{grp})   (* Kh3 Sys_det3b::{grp}))

(reaction critical_2_det2_{grp}   (H2pre_det3::{grp})   (C2_det3::{grp})   (* Kc H2pre_det3::{grp}))
(reaction critical_3_det2_{grp}   (H3_det3::{grp})   (C3_det3::{grp})   (* Kc H3_det3::{grp}))
(reaction death_det3_{grp}   (C3_det3::{grp})   (D3_det3::{grp})   (* Km C3_det3::{grp}))

(reaction recovery_As_{grp}   (As::{grp})   (RAs::{grp})   (* Kr_a_D As::{grp}))
(reaction recovery_As_det_{grp} (As_det1::{grp})   (RAs_det1::{grp})   (* Kr_a_D As_det1::{grp}))

(reaction recovery_Sym_{grp}   (Sym::{grp})   (RSym::{grp})   (* Kr_m_D  Sym::{grp}))
(reaction recovery_Sym_det2a_{grp}   (Sym_det2a::{grp})   (RSym_det2::{grp})   (* Kr_m_D  Sym_det2a::{grp}))
(reaction recovery_Sym_det2b_{grp}   (Sym_det2b::{grp})   (RSym_det2::{grp})   (* Kr_m  Sym_det2b::{grp}))
     """.format(grp=grp)

        if self.expandModel == None:
            reaction_str = reaction_str_I + expand_base_str + reaction_str_III
        if self.expandModel == "SymSys" or self.expandModel == "uniform":
            reaction_str = reaction_str_I + expand_testDelay_SymSys_str + reaction_str_III
        if self.expandModel == 'AsSymSys':
            reaction_str = reaction_str_I + expand_testDelay_AsSymSys_str + reaction_str_III

        reaction_str = reaction_str.replace("  ", " ")

        return reaction_str


    def write_time_varying_parameter(self, total_string):
        """Time varying parameter that have been fitted to data, or informed by local data.
            Parameters and corresponding sub-functions:
                - fraction_critical:  `write_frac_crit_change`
                - fraction_dead:  `write_fraction_dead_change`
                - dSys:  `write_dSys_change`
                - d_Sym:  `write_d_Sym_P_As_change`
                - dP_As:  `write_d_Sym_P_As_change`
                - Ki (monthly multipliers):  `write_ki_multiplier_change`
                - recovery_time_crit:  `write_recovery_time_crit_change`
                - recovery_time_hosp:  `write_recovery_time_hosp_change`
            All functions take required argument: nchanges, that defines number of updates.
            The default has been set within the function and currently would need to be edited manually.
        """

        def write_frac_crit_change(nchanges):
            n_frac_crit_change = range(1, nchanges+1)
            frac_crit_change_observe = '(observe frac_crit_t fraction_critical)'
            frac_crit_change_timeevent = ''.join([f'(time-event frac_crit_adjust{i} @crit_time_{i}@ '
                                                  f'('
                                                  f'(fraction_critical @fraction_critical_change{i}@) '
                                                  f'(fraction_hospitalized (- 1 (+ fraction_critical fraction_dead))) '
                                                  f'(Kh1 (/ fraction_hospitalized time_to_hospitalization)) '
                                                  f'(Kh2 (/ fraction_critical time_to_hospitalization )) '
                                                  f'(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) '
                                                  f'(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys)))'
                                                  f')'
                                                  f')'
                                                  f'\n'.format(i=str(i)) for i in n_frac_crit_change])
            return frac_crit_change_observe + frac_crit_change_timeevent

        def write_fraction_dead_change(nchanges):
            n_fraction_dead_change = range(1, nchanges+1)
            fraction_dead_change_observe = '(observe fraction_dead_t fraction_dead)\n' \
                                           '(observe fraction_hospitalized_t fraction_hospitalized)'

            fraction_dead_change_timeevent = ''.join([f'(time-event fraction_dead_adjust2 @fraction_dead_time_{i}@ '
                                                      f'('
                                                      f'(fraction_dead @fraction_dead_change{i}@) '
                                                      f'(fraction_hospitalized (- 1 (+ fraction_critical fraction_dead))) '
                                                      f'(Kh1 (/ fraction_hospitalized time_to_hospitalization)) '
                                                      f'(Kh2 (/ fraction_critical time_to_hospitalization )) '
                                                      f'(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) '
                                                      f'(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys)))'
                                                      f')'
                                                      f')'
                                                      f' \n'.format(i=str(i)) for i in n_fraction_dead_change])
            return fraction_dead_change_observe + fraction_dead_change_timeevent

        def write_dSys_change(nchanges):
            n_dSys_change = range(1, nchanges+1)
            dSys_change_observe = '(observe d_Sys_t d_Sys)'
            dSys_change_timeevent = ''.join([f'(time-event dSys_change{i} @d_Sys_change_time_{i}@ '
                                             f'((d_Sys @d_Sys_incr{i}@))'
                                             f')'
                                             f'\n'.format(i=str(i)) for i in n_dSys_change])
            return dSys_change_observe + dSys_change_timeevent

        def write_ki_multiplier_change(nchanges):
            n_ki_multiplier = ['3a','3b','3c'] + list(range(4, nchanges+1))
            ki_multiplier_change_str = ''
            for grp in self.grpList:
                temp_str_param = ''.join([f'(param Ki_red{i}_{grp} '
                                          f'(* Ki_{grp} @ki_multiplier_{i}_{grp}@)'
                                          f')'
                                          f'\n'.format(grp=grp,i=str(i))
                                          for i in n_ki_multiplier])

                temp_str_timeevent = ''.join([f'(time-event ki_multiplier_change_{i} @ki_multiplier_time_{i}@ '
                                              f'((Ki_{grp} Ki_red{i}_{grp}))'
                                              f')'
                                              f'\n'.format(grp=grp,i=str(i))
                                              for i in n_ki_multiplier])

                ki_multiplier_change_str = ki_multiplier_change_str + temp_str_param + temp_str_timeevent

            return ki_multiplier_change_str

        def write_d_Sym_P_As_change(nchanges):
            d_Sym_P_As_change_observe = '(observe d_Sym_t d_Sym)\n' \
                                        '(observe d_P_t d_P)\n' \
                                        '(observe d_As_t d_As)\n' \
                                        '(param dSym_dAsP_ratio @dSym_dAsP_ratio@)\n'
            n_d_PAs_changes = range(1,nchanges+1)
            d_Sym_P_As_change_param = ''.join([f'(param d_PAs_change{i} '
                                               f'(/ @d_Sym_change{i}@ dSym_dAsP_ratio)'
                                               f')'
                                               f'\n'.format(i=str(i)) for i in n_d_PAs_changes])

            d_Sym_P_As_change_timeevent = ''.join([f'(time-event d_Sym_change{i} @d_Sym_change_time_{i}@ '
                                                   f'('
                                                   f'(d_Sym @d_Sym_change{i}@) ' \
                                                   f'(d_P d_PAs_change1) ' \
                                                   f'(d_As d_PAs_change{i}))'
                                                   f')'
                                                   f'\n'.format(i=str(i)) for i in n_d_PAs_changes])
            return d_Sym_P_As_change_observe + d_Sym_P_As_change_param + d_Sym_P_As_change_timeevent

        def write_recovery_time_crit_change(nchanges):
            n_recovery_time_crit_change = range(1,nchanges+1)
            recovery_time_crit_change = ''
            for grp in self.grpList:
                grpout = covidModel.sub(grp)
                recovery_time_crit_change_param = f'(param recovery_time_crit_{grp} recovery_time_crit)\n' \
                                                  f'(param Kr_c_{grp} (/ 1 recovery_time_crit_{grp}))\n' \
                                                  f'(observe recovery_time_crit_t_{grpout} recovery_time_crit_{grp})' \
                                                  f'\n'.format(grp=grp,grpout=grpout)

                recovery_time_crit_change_timeevent = ''.join([f'(time-event LOS_ICU_change_{i} @recovery_time_crit_change_time_{i}_{grp}@ '
                                                               f'('
                                                               f'(recovery_time_crit_{grp} @recovery_time_crit_change{i}_{grp}@) '
                                                               f'(Kr_c_{grp} '
                                                               f'(/ 1 @recovery_time_crit_change{i}_{grp}@))'
                                                               f')'
                                                               f')'
                                                               f'\n'.format(grp=grp,i=str(i)) for i in n_recovery_time_crit_change])

                recovery_time_crit_change = recovery_time_crit_change + recovery_time_crit_change_param + recovery_time_crit_change_timeevent
            return recovery_time_crit_change

        def write_recovery_time_hosp_change(nchanges):
            n_recovery_time_hosp_change = range(1, nchanges + 1)
            recovery_time_hosp_change = ''
            for grp in self.grpList:
                grpout = covidModel.sub(grp)
                recovery_time_hosp_change_param = f'(param recovery_time_hosp_{grp} recovery_time_hosp)\n' \
                                                  f'(param Kr_h_{grp} (/ 1 recovery_time_hosp_{grp}))\n' \
                                                  f'(observe recovery_time_hosp_t_{grpout} recovery_time_hosp_{grp})' \
                                                  f'\n'.format(grp=grp, grpout=grpout)

                recovery_time_hosp_change_timeevent = ''.join(
                    [f'(time-event LOS_nonICU_change_{i} @recovery_time_hosp_change_time_{i}_{grp}@ '
                     f'('
                     f'(recovery_time_hosp_{grp} @recovery_time_hosp_change{i}_{grp}@) '
                     f'(Kr_h_{grp} (/ 1 @recovery_time_hosp_change{i}_{grp}@))'
                     f')'
                     f')'
                     f'\n'.format(grp=grp, i=str(i)) for i in n_recovery_time_hosp_change])

                recovery_time_hosp_change = recovery_time_hosp_change + recovery_time_hosp_change_param + recovery_time_hosp_change_timeevent
            return recovery_time_hosp_change

        param_update_string = write_ki_multiplier_change(nchanges=13) + \
                              write_dSys_change(nchanges=8) + \
                              write_d_Sym_P_As_change(nchanges=8) + \
                              write_frac_crit_change(nchanges=10) + \
                              write_fraction_dead_change(nchanges=9) + \
                              write_recovery_time_crit_change(nchanges=1) + \
                              write_recovery_time_hosp_change(nchanges=1)

        total_string = total_string.replace(';[TIMEVARYING_PARAMETERS]', param_update_string)

        return total_string

    def write_interventions(self, total_string):
        """ Write interventions
            Interventions defined in sub-functions:
                - bvariant: `write_bvariant`
                - intervention_stop: `write_intervention_stop`
                - transmission_increase: `write_transmission_increase`
                - rollback: `write_rollback`
                - gradual_reopening: `write_gradual_reopening`
        """

        def write_bvariant():
            bvariant_infectivity = ''
            for grp in self.grpList:
                temp_str = f';COVID-19 B variant scenario\n' \
                           f'(param Ki_bvariant_1_{grp} (* Ki_{grp} @bvariant_infectivity@ @bvariant_fracinfect@))\n' \
                           f'(time-event ki_bvariant_change1 @today@ ((Ki_{grp} Ki_bvariant_1_{grp})))\n'.format(grp=grp)
                bvariant_str_I = bvariant_str_I + temp_str

            bvariant_severity = f'(param fracsevere_bvariant1 (* fraction_severe @bvariant_severity@))\n' \
                                f'(time-event fracsevere_bvariant_change1 @today@ ' \
                                f'(' \
                                f'(fraction_severe fracsevere_bvariant1) ' \
                                f'(fraction_dead (/ cfr fraction_severe)) ' \
                                f'(fraction_hospitalized (- 1 (+ fraction_critical fraction_dead))) ' \
                                f'(Kh1 (/ fraction_hospitalized time_to_hospitalization)) ' \
                                f'(Kh2 (/ fraction_critical time_to_hospitalization )) ' \
                                f'(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) ' \
                                f'(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) ))' \
                                f')' \
                                f')\n'
            return bvariant_infectivity + bvariant_severity

        def write_rollback():
            rollback = ''.join([f'(time-event rollback @rollback_time@ ((Ki_{grp} Ki_red4_{grp})))' for grp in self.grpList])
            rollback_trigger = ''.join([f'(state-event rollbacktrigger_{grp} '
                                          f'(and (> time @today@) (> {self.trigger_channel}_{grp} (* @trigger_{grp}@ @capacity_multiplier@))) '
                                          f'((Ki_{grp} Ki_red7_{grp}))'
                                          f')\n' for grp in self.grpList])

            rollback_trigger_delay = ''.join([f'(param time_of_trigger_{grp} 10000)\n'
                                              f'(state-event rollbacktrigger_{grp} '
                                              f'(and (> time @today@) (> crit_det_{grp} '
                                              f'(* @trigger_{grp}@ @capacity_multiplier@)) ) '
                                              f'((time_of_trigger_{grp} time))'
                                              f')\n'
                                              f'(func time_since_trigger_{grp} (- time time_of_trigger_{grp}))\n'
                                              f'(state-event apply_rollback_{grp} '
                                              f'(> (- time_since_trigger_{grp} @trigger_delay_days@) 0) '
                                              f'((Ki_{grp} Ki_red7_{grp}))'
                                              f')\n'
                                              f'(observe triggertime_{covidModel.sub(grp)} time_of_trigger_{grp})\n' for grp in self.grpList])
            return rollback_trigger_delay

        def write_intervention_stop():
            intervention_stop = ''.join(
                [f'(param Ki_back_{grp} (+ Ki_red13_{grp} (* @backtonormal_multiplier@ (- Ki_{grp} Ki_red13_{grp}))))\n'
                 f'(time-event intervention_stop @today@ ((Ki_{grp} Ki_back_{grp})))' for grp in self.grpList])

            return intervention_stop

        def write_transmission_increase():
            transmission_increase = ''.join([f'(param Ki_increased_{grp} (* Ki_{grp} @ki_increase_multiplier@))\n'
                                             f'(time-event ki_transmission_increase @today@ ((Ki_{grp} Ki_increased_{grp})))' for grp in self.grpList])
            return transmission_increase

        def write_gradual_reopening(nchanges=self.n_steps, region_specific=False):
            n_gradual_reopening = range(1, nchanges+1)
            gradual_pct = 1/nchanges
            gradual_reopening = ''
            reopening_multiplier = '@reopening_multiplier@'
            if region_specific :
                reopening_multiplier = '@reopening_multiplier_{grp}@'
            for grp in self.grpList:
                gradual_reopening_param = ''.join([f'(param Ki_back{i}_{grp} '
                                                   f'(+ Ki_red13_{grp} (* {reopening_multiplier} {gradual_pct * i} (- Ki_{grp} Ki_red13_{grp})))'
                                                   f')\n' for i in n_gradual_reopening])

                gradual_reopening_timeevent = ''.join([f'(time-event gradual_reopening{i} @gradual_reopening_time{i}@ ((Ki_{grp} Ki_back{i}_{grp}))'
                                                       f')\n' for i in n_gradual_reopening])
                gradual_reopening = gradual_reopening_param + gradual_reopening_timeevent

            return gradual_reopening

        if self.add_interventions == "bvariant":
            intervention_str = write_bvariant()
        if self.add_interventions == "interventionStop":
            intervention_str = write_transmission_increase()
        if self.add_interventions == "interventionSTOP_adj":
            intervention_str = write_intervention_stop()
        if self.add_interventions == "gradual_reopening":
            intervention_str = write_gradual_reopening(nchanges=nchanges)
        if self.add_interventions == "rollback":
            intervention_str = write_rollback()

        return total_string.replace(';[INTERVENTIONS]', intervention_str )

    def write_change_test_delay(self, total_string):
        """ Write change in test delay (model extension)
            Possible extensions defined in strings:
                - uniform: `change_uniformtestDelay_str`
                - As: `change_testDelay_As_str`
                - Sym: `change_testDelay_Sym_str`
                - Sys: `change_testDelay_Sys_str`
                and combinations
                - AsSym: `change_testDelay_As_str` & `change_testDelay_Sym_str`
                - SymSys: `change_testDelay_Sym_str` & `change_testDelay_Sys_str`
                - AsSymSys: `change_testDelay_As_str` &  `change_testDelay_Sym_str` & `change_testDelay_Sys_str`
        """
        change_uniformtestDelay_str = '(time-event change_testDelay1 @change_testDelay_time1@ ' \
                                      '( ' \
                                      '(time_D @change_testDelay_1@) ' \
                                      '(Ksys_D (/ 1 time_D)) ' \
                                      '(Ksym_D (/ 1 time_D)) ' \
                                      '(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D))) ' \
                                      '(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D) )) ' \
                                      '(Kh3_D (/ fraction_dead (- time_to_hospitalization time_D))) ' \
                                      '(Kr_m_D (/ 1 (- recovery_time_mild time_D )))' \
                                      ')' \
                                      ')\n'

        change_testDelay_Sym_str = '(time-event change_testDelay1 @change_testDelay_time1@ ' \
                                   '( ' \
                                   '(time_D_Sym @change_testDelay_Sym_1@) ' \
                                   '(Ksym_D (/ 1 time_D_Sym)) ' \
                                   '(Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym )))' \
                                   ')' \
                                   ')\n'

        change_testDelay_Sys_str = '(time-event change_testDelay1 @change_testDelay_time1@ ' \
                                   '( ' \
                                   '(time_D_Sys @change_testDelay_Sys_1@) ' \
                                   '(Ksys_D (/ 1 time_D_Sys)) ' \
                                   '(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) ' \
                                   '(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) ' \
                                   '(Kh3_D (/ fraction_dead (- time_to_hospitalization time_D_Sys)))' \
                                   ')' \
                                   ')\n'

        change_testDelay_As_str = '(time-event change_testDelay1 @change_testDelay_time1@ ' \
                                  '( ' \
                                  '(time_D_As @change_testDelay_As_1@) ' \
                                  '(Kl_D (/ 1 time_D_As)) ' \
                                  '(Kr_a_D (/ 1 (- recovery_time_asymp time_D_As )))' \
                                  ')' \
                                  ')\n'

        if self.expandModel == "uniform":
            change_test_delay_str = change_uniformtestDelay_str
        if self.expandModel == "As":
            change_test_delay_str = change_testDelay_As_str
        if self.expandModel == "Sym":
            change_test_delay_str = change_testDelay_Sym_str
        if self.expandModel == "Sys":
            change_test_delay_str = change_testDelay_Sys_str
        if self.expandModel == "AsSym":
            change_test_delay_str = change_testDelay_As_str + change_testDelay_Sym_str
        if self.expandModel == "SymSys":
            change_test_delay_str = change_testDelay_Sym_str + change_testDelay_Sys_str
        if self.expandModel == "AsSymSys":
            change_test_delay_str = change_testDelay_As_str + change_testDelay_Sym_str + change_testDelay_Sys_str

        return total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_test_delay_str)

    def generate_emodl(self):

        if self.emodl_name is None:
            emodl_name = f'{self.model}_{self.add_interventions}'
            file_output = os.path.join(self.emodl_dir, f'{emodl_name}.emodl')
        else:
            file_output = os.path.join(self.emodl_dir, f'{self.emodl_name}.emodl')
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

        for grp in self.grpList:
            total_string = total_string + "\n(locale site-{})\n".format(grp)
            total_string = total_string + "(set-locale site-{})\n".format(grp)
            total_string = total_string + covidModel.write_species(self, grp)
            functions = covidModel.write_functions(self, grp)
            observe_string = observe_string + covidModel.write_observe(self, grp)
            if (self.add_migration):
                reaction_string = reaction_string + covidModel.write_travel_reaction(grp)
            reaction_string = reaction_string + covidModel.write_reactions(self, grp)
            functions_string = functions_string + functions
            param_string = param_string + covidModel.write_Ki_timevents(self,grp)

        param_string = covidModel.write_params(self) + param_string + covidModel.write_N_population(self)
        if (self.add_migration):
            param_string = param_string + covidModel.write_migration_param(self)
        functions_string = functions_string + covidModel.write_All(self)

        intervention_string = "\n;[TIMEVARYING_PARAMETERS]\n;[INTERVENTIONS]\n;[ADDITIONAL_TIMEEVENTS]"
        total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string + '\n\n' + reaction_string + '\n\n' + footer_str

        """Custom adjustments for EMS 6 (earliest start date)"""
        total_string = total_string.replace('(species As::EMS_6 0)', '(species As::EMS_6 1)')

        """Add time-events for time-varying parameters"""
        total_string = covidModel.write_time_varying_parameter(self, total_string)

        """Add change in test delay (optional)
            Note, per default assumes time to detection for the same populations as in expandModel changes 
            i.e. As, Sym, Sys, AsSymSys,  default structure AsSymSys.
            Initially expandModel and change_testDelay were separated
        """
        if self.change_testDelay:
            total_string = covidModel.write_change_test_delay(self, total_string)

        """Add interventions (optional)
           Note, interventions added IN ADDITION to monthly fitted Ki's
        """
        if self.add_interventions != None and self.add_interventions != 'baseline':
            total_string = covidModel.write_interventions(self, total_string)

        emodl = open(file_output, "w")
        emodl.write(total_string)
        emodl.close()
        if (os.path.exists(file_output)):
            print("{} file was successfully created".format(file_output))
        else:
            print("{} file was NOT created".format(file_output))

        return emodl_name

    def showOptions():
        model_options = {'expandModel': ("None","uniform", "As", "Sym","Sys","AsSym","AsSymSys"),
                         'observeLevel': ('primary', 'secondary', 'tertiary', 'all'),
                         'add_interventions': ("baseline",
                                               "bvariant",
                                               "interventionStop",
                                               "interventionSTOP_adj",
                                               "gradual_reopening",
                                               "rollback",
                                               #"gradual_reopening2",
                                               #"rollbacktriggered",
                                               #"contactTracing",
                                               #"improveHS",
                                               #"reopen_improveHS",
                                               #"contactTracing_improveHS"
                                               #"reopen_contactTracing_improveHS"
                                               ),
                         'change_testDelay': ("True","False"),
                         'trigger_channel': ("None", "critical", "crit_det", "hospitalized", "hosp_det"),
                         'add_migration': ('True', 'False')}
        return print(json.dumps(model_options, indent=4, sort_keys=True))
