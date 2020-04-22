import os
import itertools
import sys
sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')

### WRITE EMODL CHUNKS
# eval(" 'age,' * 26") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
def write_species(grp):
   grp = str(grp)
   species_str = """
(species S_{grp} @speciesS_{grp}@)
(species As_{grp} @initialAs_{grp}@)
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
   return (species_str)


# eval(" 'age,' * 108") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
def write_observe(grp):
    grp = str(grp)

    observe_str = """
(observe susceptible_{grp} S_{grp})
(observe exposed_{grp} E_{grp})
(observe asymptomatic_{grp} asymptomatic_{grp})
(observe presymptomatic_{grp} P_{grp})
(observe symptomatic_mild_{grp} symptomatic_mild_{grp})
(observe symptomatic_severe_{grp} symptomatic_severe_{grp})
(observe hospitalized_{grp} hospitalized_{grp})
(observe critical_{grp} critical_{grp})
(observe deaths_{grp} deaths_{grp})
(observe recovered_{grp} recovered_{grp})

(observe asymp_cumul_{grp} (+ asymptomatic_{grp} RAs_{grp} RAs_det1_{grp} ))
(observe asymp_det_cumul_{grp} (+ As_det1_{grp} RAs_det1_{grp}))
(observe symp_mild_cumul_{grp} (+ symptomatic_mild_{grp} RSym_{grp} RSym_det2_{grp}))
(observe symp_mild_det_cumul_{grp} (+ RSym_det2_{grp} Sym_det2_{grp}))
(observe symp_severe_cumul_{grp} (+ symptomatic_severe_{grp} hospitalized_{grp} critical_{grp} deaths_{grp} RH1_{grp} RC2_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(observe symp_severe_det_cumul_{grp} (+ Sys_det3_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp} D3_det3_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(observe hosp_cumul_{grp} (+ hospitalized_{grp} critical_{grp} deaths_{grp} RH1_{grp} RC2_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(observe hosp_det_cumul_{grp} (+ H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp} D3_det3_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(observe crit_cumul_{grp} (+ deaths_{grp} critical_{grp} RC2_{grp} RC2_det3_{grp}))
(observe crit_det_cumul_{grp} (+ C2_det3_{grp} C3_det3_{grp} D3_det3_{grp} RC2_det3_{grp}))
(observe crit_det_{grp} (+ C2_det3_{grp} C3_det3_{grp}))
(observe detected_cumul_{grp} (+ (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} H1_det3_{grp} H2_det3_{grp} C2_det3_{grp} C3_det3_{grp}) RAs_det1_{grp} RSym_det2_{grp} RH1_det3_{grp} RC2_det3_{grp} D3_det3_{grp}))
(observe death_det_cumul_{grp} D3_det3_{grp} )

(observe detected_{grp} (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))
(observe infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))
""".format(grp=grp)
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


# eval(" 'age,' * 34") + "age"
def write_functions(grp):
    grp = str(grp)
    functions_str = """
(func asymptomatic_{grp}  (+ As_{grp} As_det1_{grp}))
(func symptomatic_mild_{grp}  (+ Sym_{grp} Sym_det2_{grp}))
(func symptomatic_severe_{grp}  (+ Sys_{grp} Sys_det3_{grp}))
(func hospitalized_{grp}  (+ H1_{grp} H2_{grp} H3_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp}))
(func critical_{grp} (+ C2_{grp} C3_{grp} C2_det3_{grp} C3_det3_{grp}))
(func deaths_{grp} (+ D3_{grp} D3_det3_{grp}))
(func recovered_{grp} (+ RAs_{grp} RSym_{grp} RH1_{grp} RC2_{grp} RAs_det1_{grp} RSym_det2_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(func infectious_undet_{grp} (+ As_{grp} P_{grp} Sym_{grp} Sys_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infectious_det_{grp} (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} ))

(param N_{grp} (+  @speciesS_{grp}@  @initialAs_{grp}@) )
""".format(grp=grp)
   # functions_str = functions_str.replace("  ", "")
    return (functions_str)


def write_ki_mix(nageGroups, scale=True):
    grp_x = range(1, nageGroups + 1)
    grp_y = reversed(grp_x)

    ki_dic = {}
    for i, xy in enumerate(itertools.product(grp_x, grp_y)):
        ki_dic[i] = ["C" + str(xy[0]) + '_' + str(xy[1])]

    ki_mix_param = ""
    for i in range(len(ki_dic.keys())):
        string_i = "(param " + ki_dic[i][0] + " @" + ki_dic[i][0] + "@ )" + "\n"
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

## homogeneous reactions for testing
def write_exposure_reaction_homogeneous():
    exposure_reaction_str = """  
(func infectious_det_All (+ infectious_det_age0to19 infectious_det_age20to39 infectious_det_age40to59 infectious_det_age60to100 ))
(func infectious_undet_All (+ infectious_undet_age0to19 infectious_undet_age20to39 infectious_undet_age40to59 infectious_undet_age60to100 ))

(reaction exposure_from_detected_age0to19 (S_age0to19) (E_age0to19) (* Ki S_age0to19 infectious_det_All reduced_inf_of_det_cases))
(reaction exposure_from_detected_age20to39 (S_age20to39) (E_age20to39) (* Ki S_age20to39 infectious_det_All reduced_inf_of_det_cases))
(reaction exposure_from_detected_age40to59 (S_age40to59 ) (E_age40to59 ) (* Ki S_age40to59 infectious_det_All reduced_inf_of_det_cases))
(reaction exposure_from_detected_age60to100 (S_age60to100 ) (E_age60to100) (* Ki S_age60to100 infectious_det_All reduced_inf_of_det_cases))

(reaction exposure_from_undetected_age0to19 (S_age0to19) (E_age0to19) (* Ki S_age0to19 infectious_undet_All))
(reaction exposure_from_undetected_age20to39 (S_age20to39) (E_age20to39) (* Ki S_age20to39 infectious_undet_All))
(reaction exposure_from_undetected_age40to59 (S_age40to59 ) (E_age40to59 ) (* Ki S_age40to59 infectious_undet_All))
(reaction exposure_from_undetected_age60to100 (S_age60to100 ) (E_age60to100) (* Ki S_age60to100 infectious_undet_All))
"""
    return exposure_reaction_str

def write_exposure_reaction():
    exposure_reaction_str = """  
(reaction exposure_from_detected_age0to19 (S_age0to19) (E_age0to19) (* Ki S_age0to19 (+ (* C1_1 (/ infectious_det_age0to19 N_age0to19)) (* C1_2 (/ infectious_det_age20to39 N_age20to39)) (* C1_3  (/ infectious_det_age40to59 N_age40to59)) (* C1_4 (/ infectious_det_age60to100 N_age60to100)) reduced_inf_of_det_cases )))
(reaction exposure_from_detected_age20to39 (S_age20to39) (E_age20to39) (* Ki S_age20to39 (+ (* C2_1 (/ infectious_det_age0to19 N_age0to19)) (* C2_2 (/ infectious_det_age20to39 N_age20to39)) (* C2_3 (/  infectious_det_age40to59 N_age40to59)) (* C2_4  (/ infectious_det_age60to100 N_age60to100)) reduced_inf_of_det_cases )))
(reaction exposure_from_detected_age40to59 (S_age40to59 ) (E_age40to59 ) (* Ki S_age40to59 (+ (* C3_1 (/ infectious_det_age0to19 N_age0to19)) (* C3_2 (/ infectious_det_age20to39 N_age20to39)) (* C3_3 (/  infectious_det_age40to59 N_age40to59)) (* C3_4  (/ infectious_det_age60to100 N_age60to100)) reduced_inf_of_det_cases )))
(reaction exposure_from_detected_age60to100 (S_age60to100 ) (E_age60to100) (* Ki S_age60to100 (+ (* C4_1 (/ infectious_det_age0to19 N_age0to19)) (* C4_2 (/ infectious_det_age20to39 N_age20to39)) (* C4_3 (/ infectious_det_age40to59 N_age40to59)) (* C4_4  (/ infectious_det_age60to100 N_age60to100)) reduced_inf_of_det_cases )))

(reaction exposure_from_undetected_age0to19 (S_age0to19) (E_age0to19) (* Ki S_age0to19 (+ (* C1_1 (/ infectious_undet_age0to19 N_age0to19)) (* C1_2 (/ infectious_undet_age20to39 N_age20to39)) (* C1_3  (/ infectious_undet_age40to59 N_age40to59)) (* C1_4 (/ infectious_undet_age60to100 N_age60to100)))))
(reaction exposure_from_undetected_age20to39 (S_age20to39) (E_age20to39) (* Ki S_age20to39 (+ (* C2_1 (/ infectious_undet_age0to19 N_age0to19)) (* C2_2 (/ infectious_undet_age20to39 N_age20to39)) (* C2_3 (/  infectious_undet_age40to59 N_age40to59)) (* C2_4  (/ infectious_undet_age60to100 N_age60to100)) )))
(reaction exposure_from_undetected_age40to59 (S_age40to59 ) (E_age40to59 ) (* Ki S_age40to59 (+ (* C3_1 (/ infectious_undet_age0to19 N_age0to19)) (* C3_2 (/ infectious_undet_age20to39 N_age20to39)) (* C3_3 (/  infectious_undet_age40to59 N_age40to59)) (* C3_4  (/ infectious_undet_age60to100 N_age60to100)) )))
(reaction exposure_from_undetected_age60to100 (S_age60to100 ) (E_age60to100 ) (* Ki S_age60to100 (+ (* C4_1 (/ infectious_undet_age0to19 N_age0to19)) (* C4_2 (/ infectious_undet_age20to39 N_age20to39)) (* C4_3 (/ infectious_undet_age40to59 N_age40to59)) (* C4_4  (/ infectious_undet_age60to100 N_age60to100)) )))
"""
    return exposure_reaction_str


def write_exposure_reaction2():
    exposure_reaction_str = """  
(reaction exposure_from_detected_age0to9 (S_age0to9) (E_age0to9) (* Ki S_age0to9   (+ (* C1_1 (/ infectious_det_age0to9 N_age0to9)) (* C1_1 (/ infectious_det_age10to19 N_age10to19)) (* C1_3 (/ infectious_det_age20to29 N_age20to29)) (* C1_4 (/ infectious_det_age30to39 N_age30to39)) (* C1_5 (/ infectious_det_age40to49 N_age40to49)) (* C1_6 (/ infectious_det_age50to59 N_age50to59)) (* C1_7 (/ infectious_det_age60to69 N_age60to69)) (* C1_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases)))
(reaction exposure_from_detected_age10to19 (S_age10to19) (E_age10to19) (* Ki S_age10to19 (+ (* C2_1 (/ infectious_det_age0to9 N_age0to9)) (* C2_2 (/ infectious_det_age10to19 N_age10to19)) (* C2_3 (/ infectious_det_age20to29 N_age20to29)) (* C2_4 (/ infectious_det_age30to39 N_age30to39)) (* C2_5 (/ infectious_det_age40to49 N_age40to49)) (* C2_6 (/ infectious_det_age50to59 N_age50to59)) (* C2_7 (/ infectious_det_age60to69 N_age60to69)) (* C2_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases)))
(reaction exposure_from_detected_age20to29 (S_age20to29) (E_age20to29) (* Ki S_age20to29 (+ (* C3_1 (/ infectious_det_age0to9 N_age0to9)) (* C3_2 (/ infectious_det_age10to19 N_age10to19)) (* C3_3 (/ infectious_det_age20to29 N_age20to29)) (* C3_4 (/ infectious_det_age30to39 N_age30to39)) (* C3_5 (/ infectious_det_age40to49 N_age40to49)) (* C3_6 (/ infectious_det_age50to59 N_age50to59)) (* C3_7 (/ infectious_det_age60to69 N_age60to69)) (* C3_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases)))
(reaction exposure_from_detected_age30to39 (S_age30to39) (E_age30to39) (* Ki S_age30to39 (+ (* C4_1 (/ infectious_det_age0to9 N_age0to9)) (* C4_2 (/ infectious_det_age10to19 N_age10to19)) (* C4_3 (/ infectious_det_age20to29 N_age20to29)) (* C4_4 (/ infectious_det_age30to39 N_age30to39)) (* C4_5 (/ infectious_det_age40to49 N_age40to49)) (* C4_6 (/ infectious_det_age50to59 N_age50to59)) (* C4_7 (/ infectious_det_age60to69 N_age60to69)) (* C4_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases)))
(reaction exposure_from_detected_age40to49 (S_age40to49) (E_age40to49) (* Ki S_age40to49 (+ (* C5_1 (/ infectious_det_age0to9 N_age0to9)) (* C5_2 (/ infectious_det_age10to19 N_age10to19)) (* C5_3 (/ infectious_det_age20to29 N_age20to29)) (* C5_4 (/ infectious_det_age30to39 N_age30to39)) (* C5_5 (/ infectious_det_age40to49 N_age40to49)) (* C5_6 (/ infectious_det_age50to59 N_age50to59)) (* C5_7 (/ infectious_det_age60to69 N_age60to69)) (* C5_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases)))
(reaction exposure_from_detected_age50to59 (S_age50to59) (E_age50to59) (* Ki S_age50to59 (+ (* C6_1 (/ infectious_det_age0to9 N_age0to9)) (* C6_2 (/ infectious_det_age10to19 N_age10to19)) (* C6_3 (/ infectious_det_age20to29 N_age20to29)) (* C6_4 (/ infectious_det_age30to39 N_age30to39)) (* C6_5 (/ infectious_det_age40to49 N_age40to49)) (* C6_6 (/ infectious_det_age50to59 N_age50to59)) (* C6_7 (/ infectious_det_age60to69 N_age60to69)) (* C6_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases)))
(reaction exposure_from_detected_age60to69 (S_age60to69) (E_age60to69) (* Ki S_age60to69 (+ (* C7_1 (/ infectious_det_age0to9 N_age0to9)) (* C7_2 (/ infectious_det_age10to19 N_age10to19)) (* C7_3 (/ infectious_det_age20to29 N_age20to29)) (* C7_4 (/ infectious_det_age30to39 N_age30to39)) (* C7_5 (/ infectious_det_age40to49 N_age40to49)) (* C7_6 (/ infectious_det_age50to59 N_age50to59)) (* C7_7 (/ infectious_det_age60to69 N_age60to69)) (* C7_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases)))
(reaction exposure_from_detected_age70to100 (S_age70to100) (E_age70to100) (* Ki S_age70to100 (+ (* C8_1 (/ infectious_det_age0to9 N_age0to9)) (* C8_2 (/ infectious_det_age10to19 N_age10to19)) (* C8_3 (/ infectious_det_age20to29 N_age20to29)) (* C8_4 (/ infectious_det_age30to39 N_age30to39)) (* C8_5 (/ infectious_det_age40to49 N_age40to49)) (* C8_6 (/ infectious_det_age50to59 N_age50to59)) (* C8_7 (/ infectious_det_age60to69 N_age60to69)) (* C8_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases)))


(reaction exposure_from_undetected_age0to9 (S_age0to9) (E_age0to9) (* Ki S_age0to9 (+ (* C1_1 (/ infectious_undet_age0to9 N_age0to9)) (* C1_2 (/ infectious_undet_age10to19 N_age10to19)) (* C1_3 (/ infectious_undet_age20to29 N_age20to29)) (* C1_4 (/ infectious_undet_age30to39 N_age30to39)) (* C1_5 (/ infectious_undet_age40to49 N_age40to49)) (* C1_6 (/ infectious_undet_age50to59 N_age50to59)) (* C1_7 (/ infectious_undet_age60to69 N_age60to69)) (* C1_8 (/ infectious_undet_age70to100 N_age70to100)))))
(reaction exposure_from_undetected_age10to19 (S_age10to19) (E_age10to19) (* Ki S_age10to19 (+ (* C2_1 (/ infectious_undet_age0to9 N_age0to9)) (* C2_2 (/ infectious_undet_age10to19 N_age10to19)) (* C2_3 (/ infectious_undet_age20to29 N_age20to29)) (* C2_4 (/ infectious_undet_age30to39 N_age30to39)) (* C2_5 (/ infectious_undet_age40to49 N_age40to49)) (* C2_6 (/ infectious_undet_age50to59 N_age50to59)) (* C2_7 (/ infectious_undet_age60to69 N_age60to69)) (* C2_8 (/ infectious_undet_age70to100 N_age70to100)))))
(reaction exposure_from_undetected_age20to29 (S_age20to29) (E_age20to29) (* Ki S_age20to29 (+ (* C3_1 (/ infectious_undet_age0to9 N_age0to9)) (* C3_2 (/ infectious_undet_age10to19 N_age10to19)) (* C3_3 (/ infectious_undet_age20to29 N_age20to29)) (* C3_4 (/ infectious_undet_age30to39 N_age30to39)) (* C3_5 (/ infectious_undet_age40to49 N_age40to49)) (* C3_6 (/ infectious_undet_age50to59 N_age50to59)) (* C3_7 (/ infectious_undet_age60to69 N_age60to69)) (* C3_8 (/ infectious_undet_age70to100 N_age70to100)))))
(reaction exposure_from_undetected_age30to39 (S_age30to39) (E_age30to39) (* Ki S_age30to39 (+ (* C4_1 (/ infectious_undet_age0to9 N_age0to9)) (* C4_2 (/ infectious_undet_age10to19 N_age10to19)) (* C4_3 (/ infectious_undet_age20to29 N_age20to29)) (* C4_4 (/ infectious_undet_age30to39 N_age30to39)) (* C4_5 (/ infectious_undet_age40to49 N_age40to49)) (* C4_6 (/ infectious_undet_age50to59 N_age50to59)) (* C4_7 (/ infectious_undet_age60to69 N_age60to69)) (* C4_8 (/ infectious_undet_age70to100 N_age70to100)))))
(reaction exposure_from_undetected_age40to49 (S_age40to49) (E_age40to49) (* Ki S_age40to49 (+ (* C5_1 (/ infectious_undet_age0to9 N_age0to9)) (* C5_2 (/ infectious_undet_age10to19 N_age10to19)) (* C5_3 (/ infectious_undet_age20to29 N_age20to29)) (* C5_4 (/ infectious_undet_age30to39 N_age30to39)) (* C5_5 (/ infectious_undet_age40to49 N_age40to49)) (* C5_6 (/ infectious_undet_age50to59 N_age50to59)) (* C5_7 (/ infectious_undet_age60to69 N_age60to69)) (* C5_8 (/ infectious_undet_age70to100 N_age70to100)))))
(reaction exposure_from_undetected_age50to59 (S_age50to59) (E_age50to59) (* Ki S_age50to59 (+ (* C6_1 (/ infectious_undet_age0to9 N_age0to9)) (* C6_2 (/ infectious_undet_age10to19 N_age10to19)) (* C6_3 (/ infectious_undet_age20to29 N_age20to29)) (* C6_4 (/ infectious_undet_age30to39 N_age30to39)) (* C6_5 (/ infectious_undet_age40to49 N_age40to49)) (* C6_6 (/ infectious_undet_age50to59 N_age50to59)) (* C6_7 (/ infectious_undet_age60to69 N_age60to69)) (* C6_8 (/ infectious_undet_age70to100 N_age70to100)))))
(reaction exposure_from_undetected_age60to69 (S_age60to69) (E_age60to69) (* Ki S_age60to69 (+ (* C7_1 (/ infectious_undet_age0to9 N_age0to9)) (* C7_2 (/ infectious_undet_age10to19 N_age10to19)) (* C7_3 (/ infectious_undet_age20to29 N_age20to29)) (* C7_4 (/ infectious_undet_age30to39 N_age30to39)) (* C7_5 (/ infectious_undet_age40to49 N_age40to49)) (* C7_6 (/ infectious_undet_age50to59 N_age50to59)) (* C7_7 (/ infectious_undet_age60to69 N_age60to69)) (* C7_8 (/ infectious_undet_age70to100 N_age70to100)))))
(reaction exposure_from_undetected_age70to100 (S_age70to100) (E_age70to100) (* Ki S_age70to100 (+ (* C8_1 (/ infectious_undet_age0to9 N_age0to9)) (* C8_2 (/ infectious_undet_age10to19 N_age10to19)) (* C8_3 (/ infectious_undet_age20to29 N_age20to29)) (* C8_4 (/ infectious_undet_age30to39 N_age30to39)) (* C8_5 (/ infectious_undet_age40to49 N_age40to49)) (* C8_6 (/ infectious_undet_age50to59 N_age50to59)) (* C8_7 (/ infectious_undet_age60to69 N_age60to69)) (* C8_8 (/ infectious_undet_age70to100 N_age70to100)))))

"""
    return exposure_reaction_str


# eval(" 'age,' * 105") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
# (reaction exposure_from_undetected_{grp} (S_{grp}) (E_{grp}) (* Ki S_{grp} infectious_undet_{grp}))
# (reaction exposure_from_detected_{grp} (S_{grp}) (E_{grp}) (* Ki S_{grp} infectious_det_{grp} reduced_inf_of_det_cases))
def write_reactions(grp):
    grp = str(grp)

    reaction_str = """
(reaction infection_asymp_undet_{grp}  (E_{grp})   (As_{grp})   (* Kl E_{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (E_{grp})   (As_det1_{grp})   (* Kl E_{grp} d_As))
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

(reaction recovery_As_{grp}   (As_{grp})   (RAs_{grp})   (* Kr_a As_{grp}))
(reaction recovery_Sym_{grp}   (Sym_{grp})   (RSym_{grp})   (* Kr_m  Sym_{grp}))
(reaction recovery_H1_{grp}   (H1_{grp})   (RH1_{grp})   (* Kr_h H1_{grp}))
(reaction recovery_C2_{grp}   (C2_{grp})   (RC2_{grp})   (* Kr_c C2_{grp}))


(reaction recovery_As_det_{grp} (As_det1_{grp})   (RAs_det1_{grp})   (* Kr_a As_det1_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3_{grp})   (H1_det3_{grp})   (* Kh1 Sys_det3_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3_{grp})   (H2_det3_{grp})   (* Kh2 Sys_det3_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3_{grp})   (H3_det3_{grp})   (* Kh3 Sys_det3_{grp}))
(reaction critical_2_det2_{grp}   (H2_det3_{grp})   (C2_det3_{grp})   (* Kc H2_det3_{grp}))
(reaction critical_3_det2_{grp}   (H3_det3_{grp})   (C3_det3_{grp})   (* Kc H3_det3_{grp}))
(reaction death_det3_{grp}   (C3_det3_{grp})   (D3_det3_{grp})   (* Km C3_det3_{grp}))

(reaction recovery_Sym_det2_{grp}   (Sym_det2_{grp})   (RSym_det2_{grp})   (* Kr_m  Sym_det2_{grp}))
(reaction recovery_H1_det3_{grp}   (H1_det3_{grp})   (RH1_det3_{grp})   (* Kr_h H1_det3_{grp}))
(reaction recovery_C2_det3_{grp}   (C2_det3_{grp})   (RC2_det3_{grp})   (* Kr_c C2_det3_{grp}))
""".format(grp=grp)

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


age_grp4 = ['age0to19', 'age20to39', 'age40to59', 'age60to100']
generate_extended_emodl(grp=age_grp4, file_output=os.path.join(emodl_dir, 'extendedmodel_cobey_age_4grp.emodl'))

age_grp8 = ["age0to9" , "age10to19" , "age20to29", "age30to39", "age40to49", "age50to59", "age60to69", "age70to100"]
generate_extended_emodl2(grp=age_grp8, file_output=os.path.join(emodl_dir, 'extendedmodel_cobey_age_8grp.emodl'))