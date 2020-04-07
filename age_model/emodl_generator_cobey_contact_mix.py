import os
import csv
import itertools
from load_paths import load_box_paths

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'age_model', 'emodl')

### WRITE EMODL CHUNKS
# eval(" 'age,' * 26") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
def write_species(grp):
   grp = str(grp)
   species_str = """
(species S_{} @speciesS_{}@)
(species As_{} @initialAs_{}@)
(species E_{} 0)
(species As_det1_{} 0)
(species P_{} 0)
(species Sym_{} 0)
(species Sym_det2_{} 0)
(species Sys_{} 0)
(species Sys_det3_{} 0)
(species H1_{} 0)
(species H2_{} 0)
(species H3_{} 0)
(species H1_det3_{} 0)
(species H2_det3_{} 0)
(species H3_det3_{} 0)
(species C2_{} 0)
(species C3_{} 0)
(species C2_det3_{} 0)
(species C3_det3_{} 0)
(species D3_{} 0)
(species D3_det3_{} 0)
(species RAs_{} 0)
(species RAs_det1_{} 0)
(species RSym_{} 0)
(species RSym_det2_{} 0)
(species RH1_{} 0)
(species RH1_det3_{} 0)
(species RC2_{} 0)
(species RC2_det3_{} 0)
""".format(grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp,grp, grp ,grp, grp
           )
   species_str = species_str.replace("  ", " ")
   return (species_str)


# eval(" 'age,' * 108") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
def write_observe(grp):
    grp = str(grp)

    observe_str = """
(observe susceptible_{} S_{})
(observe exposed_{} E_{})
(observe asymptomatic_{} asymptomatic_{})
(observe presymptomatic_{} P_{})
(observe symptomatic_mild_{} symptomatic_mild_{})
(observe symptomatic_severe_{} symptomatic_severe_{})
(observe hospitalized_{} hospitalized_{})
(observe critical_{} critical_{})
(observe deaths_{} deaths_{})
(observe recovered_{} recovered_{})
(observe asymp_cumul_{} (+ asymptomatic_{} RAs_{} RAs_det1_{} ))
(observe asymp_det_cumul_{} (+ As_det1_{} RAs_det1_{}))
(observe symp_mild_cumul_{} (+ symptomatic_mild_{} RSym_{} RSym_det2_{}))
(observe symp_severe_cumul_{} (+ symptomatic_severe_{} hospitalized_{} critical_{} deaths_{} RH1_{} RC2_{} RH1_det3_{} RC2_det3_{}))
(observe hosp_cumul_{} (+ hospitalized_{} critical_{} deaths_{} RH1_{} RC2_{} RH1_det3_{} RC2_det3_{}))
(observe hosp_det_cumul_{} (+ H1_det3_{} H2_det3_{} H3_det3_{} C2_det3_{} C3_det3_{} D3_det3_{} RH1_det3_{} RC2_det3_{}))
(observe crit_cumul_{} (+ deaths_{} critical_{} RC2_{} RC2_det3_{}))
(observe detected_cumul_{} (+ (+ As_det1_{} Sym_det2_{} Sys_det3_{} H1_det3_{} H2_det3_{} C2_det3_{} C3_det3_{}) RAs_det1_{} RSym_det2_{} RH1_det3_{} RC2_det3_{} D3_det3_{}))
(observe detected_{} (+ As_det1_{} Sym_det2_{} Sys_det3_{} H1_det3_{} H2_det3_{} H3_det3_{} C2_det3_{} C3_det3_{}))
(observe infected_{} (+ infectious_det_{} infectious_undet_{} H1_det3_{} H2_det3_{} H3_det3_{} C2_det3_{} C3_det3_{}))
""".format(grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp
           )
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


# eval(" 'age,' * 34") + "age"
def write_functions(grp):
    grp = str(grp)
    functions_str = """
(func asymptomatic_{}  (+ As_{} As_det1_{}))
(func symptomatic_mild_{}  (+ Sym_{} Sym_det2_{}))
(func symptomatic_severe_{}  (+ Sys_{} Sys_det3_{}))
(func hospitalized_{}  (+ H1_{} H2_{} H3_{} H1_det3_{} H2_det3_{} H3_det3_{}))
(func critical_{} (+ C2_{} C3_{} C2_det3_{} C3_det3_{}))
(func deaths_{} (+ D3_{} D3_det3_{}))
(func recovered_{} (+ RAs_{} RSym_{} RH1_{} RC2_{} RAs_det1_{} RSym_det2_{} RH1_det3_{} RC2_det3_{}))
(func infectious_undet_{} (+ As_{} P_{} Sym_{} Sys_{} H1_{} H2_{} H3_{} C2_{} C3_{}))
(func infectious_det_{} (+ As_det1_{} Sym_det2_{} Sys_det3_{} ))
""".format(grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp
           )
   # functions_str = functions_str.replace("  ", "")
    return (functions_str)


def write_ki_mix(nageGroups, scale=True):
    grp_x = range(1, nageGroups + 1)
    grp_y = reversed(grp_x)

    ki_dic = {}
    for i, xy in enumerate(itertools.product(grp_x, grp_y)):
        ki_dic[i] = ["Ki" + str(xy[0]) + '_' + str(xy[1])]

    ki_mix_param = ""
    for i in range(len(ki_dic.keys())):
        if scale == False :
            string_i = "(param " + ki_dic[i][0] + " @" + ki_dic[i][0] + "@ )" + "\n"
        elif scale == True :
            string_i = "(param " + ki_dic[i][0] + " (* Ki @s" + ki_dic[i][0] + "@ ))" + "\n"
        ki_mix_param = ki_mix_param + string_i

    return ki_mix_param


# If Ki mix is defined, Ki here can be set to 0 in script that generates the simulation
def write_params():
    params_str = """
(param incubation_pd @incubation_pd@)
(param time_to_symptoms @time_to_symptoms@)
(param time_to_hospitalization @time_to_hospitalization@)
(param time_to_critical @time_to_critical@)
(param time_to_death @time_to_death@)
(param recovery_rate_asymp @recovery_rate_asymp@)
(param recovery_rate_mild @recovery_rate_mild@)
(param recovery_rate_hosp @recovery_rate_hosp@)
(param recovery_rate_crit @recovery_rate_crit@)
(param fraction_symptomatic @fraction_symptomatic@)
(param fraction_severe @fraction_severe@)
(param fraction_hospitalized @fraction_hospitalized@)
(param fraction_critical @fraction_critical@ )
(param fraction_dead @fraction_dead@)
(param reduced_inf_of_det_cases @reduced_inf_of_det_cases@)
(param d_As @d_As@)
(param d_Sym @d_Sym@)
(param d_Sys @d_Sys@)
(param Ki @Ki@)
(param Kr_a (/ 1 recovery_rate_asymp))
(param Kr_m (/ 1 recovery_rate_mild))
(param Kr_h (/ 1 recovery_rate_hosp))
(param Kr_c (/ 1 recovery_rate_crit))
(param Kl (/ (- 1 fraction_symptomatic ) incubation_pd))
(param Ks (/ fraction_symptomatic  incubation_pd))
(param Ksys (* fraction_severe (/ 1 time_to_symptoms)))
(param Ksym (* (- 1 fraction_severe) (/ 1 time_to_symptoms)))
(param Kh1 (/ fraction_hospitalized time_to_hospitalization))
(param Kh2 (/ fraction_critical time_to_hospitalization ))
(param Kh3 (/ fraction_dead  time_to_hospitalization))
(param Kc (/ 1 time_to_critical))
(param Km (/ 1 time_to_death))
(param Ki_red1 (* Ki @social_multiplier_1@))
(param Ki_red2 (* Ki @social_multiplier_2@))
(param Ki_red3 (* Ki @social_multiplier_3@))

(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki Ki_red1)))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki Ki_red2)))
(time-event socialDistance_start @socialDistance_time3@ ((Ki Ki_red3)))
 """
    #params_str = params_str.replace("  ", " ")

    return (params_str)


###  age-specific infection rates and contacts
### need automatization (parked for now)
def write_exposure_reaction():
    exposure_reaction_str = """  
(reaction exposure_from_detected_ageU5 (S_ageU5) (E_ageU5) (* Ki1_1 S_ageU5 infectious_det_ageU5 reduced_inf_of_det_cases))
(reaction exposure_from_detected_ageU5 (S_ageU5) (E_ageU5) (* Ki1_2 S_ageU5 infectious_det_age5to17 reduced_inf_of_det_cases))
(reaction exposure_from_detected_ageU5 (S_ageU5) (E_ageU5) (* Ki1_3 S_ageU5 infectious_det_age18to64 reduced_inf_of_det_cases))
(reaction exposure_from_detected_ageU5 (S_ageU5) (E_ageU5) (* Ki1_4 S_ageU5 infectious_det_age64to100 reduced_inf_of_det_cases))

(reaction exposure_from_detected_age5to17 (S_age5to17) (E_age5to17) (* Ki2_1 S_age5to17 infectious_det_ageU5 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age5to17 (S_age5to17) (E_age5to17) (* Ki2_2 S_age5to17 infectious_det_age5to17 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age5to17 (S_age5to17) (E_age5to17) (* Ki2_3 S_age5to17 infectious_det_age18to64 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age5to17 (S_age5to17) (E_age5to17) (* Ki2_4 S_age5to17 infectious_det_age64to100 reduced_inf_of_det_cases))

(reaction exposure_from_detected_age18to64 (S_age18to64) (E_age18to64) (* Ki3_1 S_age18to64 infectious_det_ageU5 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age18to64 (S_age18to64) (E_age18to64) (* Ki3_2 S_age18to64 infectious_det_age5to17 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age18to64 (S_age18to64) (E_age18to64) (* Ki3_3 S_age18to64 infectious_det_age18to64 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age18to64 (S_age18to64) (E_age18to64) (* Ki3_4 S_age18to64 infectious_det_age64to100 reduced_inf_of_det_cases))

(reaction exposure_from_detected_age64to100 (S_age64to100) (E_age64to100) (* Ki4_1 S_age64to100 infectious_det_ageU5 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age64to100 (S_age64to100) (E_age64to100) (* Ki4_2 S_age64to100 infectious_det_age5to17 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age64to100 (S_age64to100) (E_age64to100) (* Ki4_3 S_age64to100 infectious_det_age18to64 reduced_inf_of_det_cases)) 
(reaction exposure_from_detected_age64to100 (S_age64to100) (E_age64to100) (* Ki4_4 S_age64to100 infectious_det_age64to100 reduced_inf_of_det_cases))


(reaction exposure_from_undetected_ageU5 (S_ageU5) (E_ageU5) (* Ki1_1 S_ageU5 infectious_undet_ageU5))
(reaction exposure_from_undetected_ageU5 (S_ageU5) (E_ageU5) (* Ki1_2 S_ageU5 infectious_undet_age5to17))
(reaction exposure_from_undetected_ageU5 (S_ageU5) (E_ageU5) (* Ki1_3 S_ageU5 infectious_undet_age18to64))
(reaction exposure_from_undetected_ageU5 (S_ageU5) (E_ageU5) (* Ki1_4 S_ageU5 infectious_undet_age64to100))

(reaction exposure_from_undetected_age5to17 (S_age5to17) (E_age5to17) (* Ki2_1 S_age5to17 infectious_undet_ageU5))
(reaction exposure_from_undetected_age5to17 (S_age5to17) (E_age5to17) (* Ki2_2 S_age5to17 infectious_undet_age5to17))
(reaction exposure_from_undetected_age5to17 (S_age5to17) (E_age5to17) (* Ki2_3 S_age5to17 infectious_undet_age18to64))
(reaction exposure_from_undetected_age5to17 (S_age5to17) (E_age5to17) (* Ki2_4 S_age5to17 infectious_undet_age64to100))

(reaction exposure_from_undetected_age18to64 (S_age18to64) (E_age18to64) (* Ki3_1 S_age18to64 infectious_undet_ageU5))
(reaction exposure_from_undetected_age18to64 (S_age18to64) (E_age18to64) (* Ki3_2 S_age18to64 infectious_undet_age5to17))
(reaction exposure_from_undetected_age18to64 (S_age18to64) (E_age18to64) (* Ki3_3 S_age18to64 infectious_undet_age18to64))
(reaction exposure_from_undetected_age18to64 (S_age18to64) (E_age18to64) (* Ki3_4 S_age18to64 infectious_undet_age64to100))

(reaction exposure_from_undetected_age64to100 (S_age64to100) (E_age64to100) (* Ki4_1 S_age64to100 infectious_undet_ageU5))
(reaction exposure_from_undetected_age64to100 (S_age64to100) (E_age64to100) (* Ki4_2 S_age64to100 infectious_undet_age5to17))
(reaction exposure_from_undetected_age64to100 (S_age64to100) (E_age64to100) (* Ki4_3 S_age64to100 infectious_undet_age18to64)) 
(reaction exposure_from_undetected_age64to100 (S_age64to100) (E_age64to100) (* Ki4_4 S_age64to100 infectious_undet_age64to100))
"""
    return exposure_reaction_str


def write_exposure_reaction2():
    exposure_reaction_str = """  
(reaction exposure_from_detected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_1 S_age0to19 infectious_det_age0to19 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_2 S_age0to19 infectious_det_age20to44 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_3 S_age0to19 infectious_det_age45to54 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_4 S_age0to19 infectious_det_age55to64 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_5 S_age0to19 infectious_det_age65to74 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_6 S_age0to19 infectious_det_age75to84 reduced_inf_of_det_cases))

(reaction exposure_from_detected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_1 S_age20to44 infectious_det_age0to19 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_2 S_age20to44 infectious_det_age20to44 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_3 S_age20to44 infectious_det_age45to54 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_4 S_age20to44 infectious_det_age55to64 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_5 S_age20to44 infectious_det_age65to74 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_6 S_age20to44 infectious_det_age75to84 reduced_inf_of_det_cases))

(reaction exposure_from_detected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_1 S_age45to54 infectious_det_age0to19 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_2 S_age45to54 infectious_det_age20to44 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_3 S_age45to54 infectious_det_age45to54 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_4 S_age45to54 infectious_det_age55to64 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_5 S_age45to54 infectious_det_age65to74 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_6 S_age45to54 infectious_det_age75to84 reduced_inf_of_det_cases))

(reaction exposure_from_detected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_1 S_age55to64 infectious_det_age0to19 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_2 S_age55to64 infectious_det_age20to44 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_3 S_age55to64 infectious_det_age45to54 reduced_inf_of_det_cases)) 
(reaction exposure_from_detected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_4 S_age55to64 infectious_det_age55to64 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_5 S_age55to64 infectious_det_age65to74 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_6 S_age55to64 infectious_det_age75to84 reduced_inf_of_det_cases))

(reaction exposure_from_detected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_1 S_age65to74 infectious_det_age0to19 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_2 S_age65to74 infectious_det_age20to44 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_3 S_age65to74 infectious_det_age45to54 reduced_inf_of_det_cases)) 
(reaction exposure_from_detected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_4 S_age65to74 infectious_det_age55to64 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_5 S_age65to74 infectious_det_age65to74 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_6 S_age65to74 infectious_det_age75to84 reduced_inf_of_det_cases))

(reaction exposure_from_detected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_1 S_age75to84 infectious_det_age0to19 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_2 S_age75to84 infectious_det_age20to44 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_3 S_age75to84 infectious_det_age45to54 reduced_inf_of_det_cases)) 
(reaction exposure_from_detected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_4 S_age75to84 infectious_det_age55to64 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_5 S_age75to84 infectious_det_age65to74 reduced_inf_of_det_cases))
(reaction exposure_from_detected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_6 S_age75to84 infectious_det_age75to84 reduced_inf_of_det_cases))


(reaction exposure_from_undetected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_1 S_age0to19 infectious_undet_age0to19 ))
(reaction exposure_from_undetected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_2 S_age0to19 infectious_undet_age20to44 ))
(reaction exposure_from_undetected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_3 S_age0to19 infectious_undet_age45to54 ))
(reaction exposure_from_undetected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_4 S_age0to19 infectious_undet_age55to64 ))
(reaction exposure_from_undetected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_5 S_age0to19 infectious_undet_age65to74 ))
(reaction exposure_from_undetected_age0to19 (S_age0to19) (E_age0to19) (* Ki1_6 S_age0to19 infectious_undet_age75to84 ))

(reaction exposure_from_undetected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_1 S_age20to44 infectious_undet_age0to19 ))
(reaction exposure_from_undetected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_2 S_age20to44 infectious_undet_age20to44 ))
(reaction exposure_from_undetected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_3 S_age20to44 infectious_undet_age45to54 ))
(reaction exposure_from_undetected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_4 S_age20to44 infectious_undet_age55to64 ))
(reaction exposure_from_undetected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_5 S_age20to44 infectious_undet_age65to74 ))
(reaction exposure_from_undetected_age20to44 (S_age20to44) (E_age20to44) (* Ki2_6 S_age20to44 infectious_undet_age75to84 ))

(reaction exposure_from_undetected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_1 S_age45to54 infectious_undet_age0to19 ))
(reaction exposure_from_undetected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_2 S_age45to54 infectious_undet_age20to44 ))
(reaction exposure_from_undetected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_3 S_age45to54 infectious_undet_age45to54 ))
(reaction exposure_from_undetected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_4 S_age45to54 infectious_undet_age55to64 ))
(reaction exposure_from_undetected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_5 S_age45to54 infectious_undet_age65to74 ))
(reaction exposure_from_undetected_age45to54 (S_age45to54) (E_age45to54) (* Ki3_6 S_age45to54 infectious_undet_age75to84 ))

(reaction exposure_from_undetected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_1 S_age55to64 infectious_undet_age0to19 ))
(reaction exposure_from_undetected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_2 S_age55to64 infectious_undet_age20to44 ))
(reaction exposure_from_undetected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_3 S_age55to64 infectious_undet_age45to54 )) 
(reaction exposure_from_undetected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_4 S_age55to64 infectious_undet_age55to64 ))
(reaction exposure_from_undetected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_5 S_age55to64 infectious_undet_age65to74 ))
(reaction exposure_from_undetected_age55to64 (S_age55to64) (E_age55to64) (* Ki4_6 S_age55to64 infectious_undet_age75to84 ))

(reaction exposure_from_undetected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_1 S_age65to74 infectious_undet_age0to19 ))
(reaction exposure_from_undetected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_2 S_age65to74 infectious_undet_age20to44 ))
(reaction exposure_from_undetected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_3 S_age65to74 infectious_undet_age45to54 )) 
(reaction exposure_from_undetected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_4 S_age65to74 infectious_undet_age55to64 ))
(reaction exposure_from_undetected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_5 S_age65to74 infectious_undet_age65to74 ))
(reaction exposure_from_undetected_age65to74 (S_age65to74) (E_age65to74) (* Ki5_6 S_age65to74 infectious_undet_age75to84 ))

(reaction exposure_from_undetected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_1 S_age75to84 infectious_undet_age0to19 ))
(reaction exposure_from_undetected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_2 S_age75to84 infectious_undet_age20to44 ))
(reaction exposure_from_undetected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_3 S_age75to84 infectious_undet_age45to54 )) 
(reaction exposure_from_undetected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_4 S_age75to84 infectious_undet_age55to64 ))
(reaction exposure_from_undetected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_5 S_age75to84 infectious_undet_age65to74 ))
(reaction exposure_from_undetected_age75to84 (S_age75to84) (E_age75to84) (* Ki6_6 S_age75to84 infectious_undet_age75to84 ))
"""
    return exposure_reaction_str


# eval(" 'age,' * 105") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
# (reaction exposure_from_undetected_{} (S_{}) (E_{}) (* Ki S_{} infectious_undet_{}))
# (reaction exposure_from_detected_{} (S_{}) (E_{}) (* Ki S_{} infectious_det_{} reduced_inf_of_det_cases))
def write_reactions(grp):
    grp = str(grp)

    reaction_str = """
(reaction infection_asymp_undet_{}  (E_{})   (As_{})   (* Kl E_{} (- 1 d_As)))
(reaction infection_asymp_det_{}  (E_{})   (As_det1_{})   (* Kl E_{} d_As))
(reaction presymptomatic_{} (E_{})   (P_{})   (* Ks E_{}))
(reaction mild_symptomatic_undet_{} (P_{})  (Sym_{}) (* Ksym P_{} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{} (P_{})  (Sym_det2_{}) (* Ksym P_{} d_Sym))
(reaction severe_symptomatic_undet_{} (P_{})  (Sys_{})  (* Ksys P_{} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{} (P_{})  (Sys_det3_{})  (* Ksys P_{} d_Sys))

(reaction hospitalization_1_{}   (Sys_{})   (H1_{})   (* Kh1 Sys_{}))
(reaction hospitalization_2_{}   (Sys_{})   (H2_{})   (* Kh2 Sys_{}))
(reaction hospitalization_3_{}   (Sys_{})   (H3_{})   (* Kh3 Sys_{}))
(reaction critical_2_{}   (H2_{})   (C2_{})   (* Kc H2_{}))
(reaction critical_3_{}   (H3_{})   (C3_{})   (* Kc H3_{}))
(reaction death_{}   (C3_{})   (D3_{})   (* Km C3_{}))

(reaction recovery_As_{}   (As_{})   (RAs_{})   (* Kr_a As_{}))
(reaction recovery_Sym_{}   (Sym_{})   (RSym_{})   (* Kr_m  Sym_{}))
(reaction recovery_H1_{}   (H1_{})   (RH1_{})   (* Kr_h H1_{}))
(reaction recovery_C2_{}   (C2_{})   (RC2_{})   (* Kr_c C2_{}))


(reaction recovery_As_det_{} (As_det1_{})   (RAs_det1_{})   (* Kr_a As_det1_{}))

(reaction hospitalization_1_det_{}   (Sys_det3_{})   (H1_det3_{})   (* Kh1 Sys_det3_{}))
(reaction hospitalization_2_det_{}   (Sys_det3_{})   (H2_det3_{})   (* Kh2 Sys_det3_{}))
(reaction hospitalization_3_det_{}   (Sys_det3_{})   (H3_det3_{})   (* Kh3 Sys_det3_{}))
(reaction critical_2_det2_{}   (H2_det3_{})   (C2_det3_{})   (* Kc H2_det3_{}))
(reaction critical_3_det2_{}   (H3_det3_{})   (C3_det3_{})   (* Kc H3_det3_{}))
(reaction death_det3_{}   (C3_det3_{})   (D3_det3_{})   (* Km C3_det3_{}))

(reaction recovery_Sym_det2_{}   (Sym_det2_{})   (RSym_det2_{})   (* Kr_m  Sym_det2_{}))
(reaction recovery_H1_det3_{}   (H1_det3_{})   (RH1_det3_{})   (* Kr_h H1_det3_{}))
(reaction recovery_C2_det3_{}   (C2_det3_{})   (RC2_det3_{})   (* Kr_c C2_det3_{}))
""".format(grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,grp,grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, 
           )

    #reaction_str = reaction_str.replace("  ", " ")
    return (reaction_str)


###

###stringing all of the functions together to make the file:
def generate_extended_emodl(grp, file_output):
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
    reaction_string = ""
    functions_string = ""
    total_string = total_string + header_str

    for key in grp:
        # key = 'age0to9'
        species = write_species(key)
        observe = write_observe(key)
        reaction = write_reactions(key)
        functions = write_functions(key)
        species_string = species_string + species
        observe_string = observe_string + observe
        reaction_string = reaction_string + reaction
        functions_string = functions_string + functions

    reaction_string_combined = write_exposure_reaction() + '\n' + reaction_string
    params = write_params() + write_ki_mix(len(grp))

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + params + '\n\n' + reaction_string_combined + '\n\n' + footer_str
    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


def generate_extended_emodl2(grp, file_output):
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
    reaction_string = ""
    functions_string = ""
    total_string = total_string + header_str

    for key in grp:
        # key = 'age0to9'
        species = write_species(key)
        observe = write_observe(key)
        reaction = write_reactions(key)
        functions = write_functions(key)
        species_string = species_string + species
        observe_string = observe_string + observe
        reaction_string = reaction_string + reaction
        functions_string = functions_string + functions

    reaction_string_combined = write_exposure_reaction2() + '\n' + reaction_string
    params = write_params() + write_ki_mix(len(grp))

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + params + '\n\n' + reaction_string_combined + '\n\n' + footer_str
    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


#if __name__ == '__main__':

age_grp4 = ['ageU5','age5to17','age18to64','age64to100']
generate_extended_emodl(grp=age_grp4, file_output=os.path.join(emodl_dir, 'extendedmodel_cobey_age_4grp.emodl'))

age_grp6 = ['age0to19', 'age20to44', 'age45to54', 'age55to64', 'age65to74','age75to84']
generate_extended_emodl2(grp=age_grp6, file_output=os.path.join(emodl_dir, 'extendedmodel_cobey_age_6grp.emodl'))