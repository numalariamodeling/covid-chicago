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
(observe symp_mild_det_cumul_{} (+ RSym_det2_{} Sym_det2_{}))
(observe symp_severe_cumul_{} (+ symptomatic_severe_{} hospitalized_{} critical_{} deaths_{} RH1_{} RC2_{} RH1_det3_{} RC2_det3_{}))
(observe symp_severe_det_cumul_{} (+ Sys_det3_{} H1_det3_{} H2_det3_{} H3_det3_{} C2_det3_{} C3_det3_{} D3_det3_{} RH1_det3_{} RC2_det3_{}))
(observe hosp_cumul_{} (+ hospitalized_{} critical_{} deaths_{} RH1_{} RC2_{} RH1_det3_{} RC2_det3_{}))
(observe hosp_det_cumul_{} (+ H1_det3_{} H2_det3_{} H3_det3_{} C2_det3_{} C3_det3_{} D3_det3_{} RH1_det3_{} RC2_det3_{}))
(observe crit_cumul_{} (+ deaths_{} critical_{} RC2_{} RC2_det3_{}))
(observe crit_det_cumul_{} (+ C2_det3_{} C3_det3_{} D3_det3_{} RC2_det3_{}))
(observe crit_det_{} (+ C2_det3_{} C3_det3_{}))
(observe detected_cumul_{} (+ (+ As_det1_{} Sym_det2_{} Sys_det3_{} H1_det3_{} H2_det3_{} C2_det3_{} C3_det3_{}) RAs_det1_{} RSym_det2_{} RH1_det3_{} RC2_det3_{} D3_det3_{}))
(observe death_det_cumul_{} D3_det3_{} )

(observe detected_{} (+ As_det1_{} Sym_det2_{} Sys_det3_{} H1_det3_{} H2_det3_{} H3_det3_{} C2_det3_{} C3_det3_{}))
(observe infected_{} (+ infectious_det_{} infectious_undet_{} H1_det3_{} H2_det3_{} H3_det3_{} C2_det3_{} C3_det3_{}))
""".format(grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp
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
            string_i = "(param " + ki_dic[i][0] + " (* Ki @" + ki_dic[i][0] + "@ ))" + "\n"
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
(reaction exposure_from_detected_age0to9 (S_age0to9) (E_age0to9) (* Ki S_age0to9  (+ (* C1_age1 (/ infectious_det_age0to9 N_age0to9)) (* C1_1 (/ infectious_det_age10to19 N_age10to19)) (* C1_age3 infectious_det_age20to29 N_age20to29)) (* C1_4 (/ infectious_det_age30to39 N_age30to39)) (* C1_5 (/ infectious_det_age40to49 N_age40to49)) (* C1_6 (/ infectious_det_age50to59 N_age50to59)) (* C1_7 (/ infectious_det_age60to69 N_age60to69)) (* C1_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases))
(reaction exposure_from_detected_age10to19 (S_age10to19) (E_age10to19) (* Ki S_age10to19 (+ (* C2_1 (/ infectious_det_age0to9 N_age0to9)) (* C2_2 (/ infectious_det_age10to19 N_age10to19)) (* C2_age3 infectious_det_age20to29 N_age20to29)) (* C2_4 (/ infectious_det_age30to39 N_age30to39)) (* C2_5 (/ infectious_det_age40to49 N_age40to49)) (* C2_6 (/ infectious_det_age50to59 N_age50to59)) (* C2_7 (/ infectious_det_age60to69 N_age60to69)) (* C2_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases))
(reaction exposure_from_detected_age20to29 (S_age20to29) (E_age20to29) (* Ki S_age20to29 (+ (* C3_1 (/ infectious_det_age0to9 N_age0to9)) (* C3_2 (/ infectious_det_age10to19 N_age10to19)) (* C3_age3 infectious_det_age20to29 N_age20to29)) (* C3_4 (/ infectious_det_age30to39 N_age30to39)) (* C3_5 (/ infectious_det_age40to49 N_age40to49)) (* C3_6 (/ infectious_det_age50to59 N_age50to59)) (* C3_7 (/ infectious_det_age60to69 N_age60to69)) (* C3_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases))
(reaction exposure_from_detected_age30to39 (S_age30to39) (E_age30to39) (* Ki S_age30to39 (+ (* C4_1 (/ infectious_det_age0to9 N_age0to9)) (* C4_2 (/ infectious_det_age10to19 N_age10to19)) (* C4_age3 infectious_det_age20to29 N_age20to29)) (* C4_4 (/ infectious_det_age30to39 N_age30to39)) (* C4_5 (/ infectious_det_age40to49 N_age40to49)) (* C4_6 (/ infectious_det_age50to59 N_age50to59)) (* C4_7 (/ infectious_det_age60to69 N_age60to69)) (* C4_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases))
(reaction exposure_from_detected_age40to49 (S_age40to49) (E_age40to49) (* Ki S_age40to49 (+ (* C5_1 (/ infectious_det_age0to9 N_age0to9)) (* C5_2 (/ infectious_det_age10to19 N_age10to19)) (* C5_age3 infectious_det_age20to29 N_age20to29)) (* C5_4 (/ infectious_det_age30to39 N_age30to39)) (* C5_5 (/ infectious_det_age40to49 N_age40to49)) (* C5_6 (/ infectious_det_age50to59 N_age50to59)) (* C5_7 (/ infectious_det_age60to69 N_age60to69)) (* C5_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases))
(reaction exposure_from_detected_age50to59 (S_age50to59) (E_age50to59) (* Ki S_age50to59 (+ (* C6_1 (/ infectious_det_age0to9 N_age0to9)) (* C6_2 (/ infectious_det_age10to19 N_age10to19)) (* C6_age3 infectious_det_age20to29 N_age20to29)) (* C6_4 (/ infectious_det_age30to39 N_age30to39)) (* C6_5 (/ infectious_det_age40to49 N_age40to49)) (* C6_6 (/ infectious_det_age50to59 N_age50to59)) (* C6_7 (/ infectious_det_age60to69 N_age60to69)) (* C6_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases))
(reaction exposure_from_detected_age60to69 (S_age60to69) (E_age60to69) (* Ki S_age60to69 (+ (* C7_1 (/ infectious_det_age0to9 N_age0to9)) (* C7_2 (/ infectious_det_age10to19 N_age10to19)) (* C7_age3 infectious_det_age20to29 N_age20to29)) (* C7_4 (/ infectious_det_age30to39 N_age30to39)) (* C7_5 (/ infectious_det_age40to49 N_age40to49)) (* C7_6 (/ infectious_det_age50to59 N_age50to59)) (* C7_7 (/ infectious_det_age60to69 N_age60to69)) (* C7_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases))
(reaction exposure_from_detected_age70to100 (S_age70to100) (E_age70to100) (* Ki S_age70to100 (+ (* C8_1 (/ infectious_det_age0to9 N_age0to9)) (* C8_2 (/ infectious_det_age10to19 N_age10to19)) (* C8_age3 infectious_det_age20to29 N_age20to29)) (* C8_4 (/ infectious_det_age30to39 N_age30to39)) (* C8_5 (/ infectious_det_age40to49 N_age40to49)) (* C8_6 (/ infectious_det_age50to59 N_age50to59)) (* C8_7 (/ infectious_det_age60to69 N_age60to69)) (* C8_8 (/ infectious_det_age70to100 N_age70to100)) reduced_inf_of_det_cases))


(reaction exposure_from_undetected_age0to9 (S_age0to9) (E_age0to9) (* Ki S_age0to9  (* C1_1 (/ infectious_undet_age0to9 N_age0to9)) (* C1_2 (/ infectious_undet_age10to19 N_age10to19)) (* C1_3 infectious_undet_age20to29 N_age20to29)) (* C1_4 (/ infectious_undet_age30to39 ) (* C1_5 (/ infectious_undet_age40to49 N_age40to49)) (* C1_6 (/ infectious_undet_age50to59 N_age50to59)) (* C1_7 (/ infectious_undet_age60to69 N_age60to69)) (* C1_8 (/ infectious_undet_age70to100 N_age70to100))))
(reaction exposure_from_undetected_age10to19 (S_age10to19) (E_age10to19) (* Ki S_age10to19 (* C2_1 (/ infectious_undet_age0to9 N_age0to9)) (* C2_2 (/ infectious_undet_age10to19 N_age10to19)) (* C2_3 infectious_undet_age20to29 N_age20to29)) (* C2_4 (/ infectious_undet_age30to39 ) (* C2_5 (/ infectious_undet_age40to49 N_age40to49)) (* C2_6 (/ infectious_undet_age50to59 N_age50to59)) (* C2_7 (/ infectious_undet_age60to69 N_age60to69)) (* C2_8 (/ infectious_undet_age70to100 N_age70to100))))
(reaction exposure_from_undetected_age20to29 (S_age20to29) (E_age20to29) (* Ki S_age20to29 (* C3_1 (/ infectious_undet_age0to9 N_age0to9)) (* C3_2 (/ infectious_undet_age10to19 N_age10to19)) (* C3_3 infectious_undet_age20to29 N_age20to29)) (* C3_4 (/ infectious_undet_age30to39 ) (* C3_5 (/ infectious_undet_age40to49 N_age40to49)) (* C3_6 (/ infectious_undet_age50to59 N_age50to59)) (* C3_7 (/ infectious_undet_age60to69 N_age60to69)) (* C3_8 (/ infectious_undet_age70to100 N_age70to100))))
(reaction exposure_from_undetected_age30to39 (S_age30to39) (E_age30to39) (* Ki S_age30to39 (* C4_1 (/ infectious_undet_age0to9 N_age0to9)) (* C4_2 (/ infectious_undet_age10to19 N_age10to19)) (* C4_3 infectious_undet_age20to29 N_age20to29)) (* C4_4 (/ infectious_undet_age30to39 ) (* C4_5 (/ infectious_undet_age40to49 N_age40to49)) (* C4_6 (/ infectious_undet_age50to59 N_age50to59)) (* C4_7 (/ infectious_undet_age60to69 N_age60to69)) (* C4_8 (/ infectious_undet_age70to100 N_age70to100))))
(reaction exposure_from_undetected_age40to49 (S_age40to49) (E_age40to49) (* Ki S_age40to49 (* C5_1 (/ infectious_undet_age0to9 N_age0to9)) (* C5_2 (/ infectious_undet_age10to19 N_age10to19)) (* C5_3 infectious_undet_age20to29 N_age20to29)) (* C5_4 (/ infectious_undet_age30to39 ) (* C5_5 (/ infectious_undet_age40to49 N_age40to49)) (* C5_6 (/ infectious_undet_age50to59 N_age50to59)) (* C5_7 (/ infectious_undet_age60to69 N_age60to69)) (* C5_8 (/ infectious_undet_age70to100 N_age70to100))))
(reaction exposure_from_undetected_age50to59 (S_age50to59) (E_age50to59) (* Ki S_age50to59 (* C6_1 (/ infectious_undet_age0to9 N_age0to9)) (* C6_2 (/ infectious_undet_age10to19 N_age10to19)) (* C6_3 infectious_undet_age20to29 N_age20to29)) (* C6_4 (/ infectious_undet_age30to39 ) (* C6_5 (/ infectious_undet_age40to49 N_age40to49)) (* C6_6 (/ infectious_undet_age50to59 N_age50to59)) (* C6_7 (/ infectious_undet_age60to69 N_age60to69)) (* C6_8 (/ infectious_undet_age70to100 N_age70to100))))
(reaction exposure_from_undetected_age60to69 (S_age60to69) (E_age60to69) (* Ki S_age60to69 (* C7_1 (/ infectious_undet_age0to9 N_age0to9)) (* C7_2 (/ infectious_undet_age10to19 N_age10to19)) (* C7_3 infectious_undet_age20to29 N_age20to29)) (* C7_4 (/ infectious_undet_age30to39 ) (* C7_5 (/ infectious_undet_age40to49 N_age40to49)) (* C7_6 (/ infectious_undet_age50to59 N_age50to59)) (* C7_7 (/ infectious_undet_age60to69 N_age60to69)) (* C7_8 (/ infectious_undet_age70to100 N_age70to100))))
(reaction exposure_from_undetected_age70to100 (S_age70to100) (E_age70to100) (* Ki S_age70to100 (* C8_1 (/ infectious_undet_age0to9 N_age0to9)) (* C8_2 (/ infectious_undet_age10to19 N_age10to19)) (* C8_3 infectious_undet_age20to29 N_age20to29)) (* C8_4 (/ infectious_undet_age30to39 ) (* C8_5 (/ infectious_undet_age40to49 N_age40to49)) (* C8_6 (/ infectious_undet_age50to59 N_age50to59)) (* C8_7 (/ infectious_undet_age60to69 N_age60to69)) (* C8_8 (/ infectious_undet_age70to100 N_age70to100))))

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

age_grp4 =  ['age0to19', 'age20to39', 'age40to59', 'age60to100']
generate_extended_emodl(grp=age_grp4, file_output=os.path.join(emodl_dir, 'extendedmodel_cobey_age_4grp.emodl'))

age_grp8 = ["0to9" , "10to19" , "20to29", "30to39", "40to49", "50to59", "60to69", "70to100"]
generate_extended_emodl2(grp=age_grp8, file_output=os.path.join(emodl_dir, 'extendedmodel_cobey_age_8grp.emodl'))