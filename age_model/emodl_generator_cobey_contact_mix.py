import os
import itertools
import sys
import re

sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()
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

(observe asymp_cumul_{grp} asymp_cumul_{grp})
(observe asymp_det_cumul_{grp} asymp_det_cumul_{grp})
(observe symp_mild_cumul_{grp} symp_mild_cumul_{grp})
(observe symp_mild_det_cumul_{grp} symp_mild_det_cumul_{grp})
(observe symp_severe_cumul_{grp} symp_severe_cumul_{grp})
(observe symp_severe_det_cumul_{grp} symp_severe_det_cumul_{grp})
(observe hosp_cumul_{grp} hosp_cumul_{grp})
(observe hosp_det_cumul_{grp} hosp_det_cumul_{grp})
(observe crit_cumul_{grp} crit_cumul_{grp})
(observe crit_det_cumul_{grp} crit_det_cumul_{grp})
(observe crit_det_{grp} crit_det_{grp})
(observe detected_cumul_{grp} detected_cumul_{grp})
(observe death_det_cumul_{grp} death_det_cumul_{grp} )

(observe detected_{grp} detected_{grp})
(observe infected_{grp} infected_{grp})
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

""".format(grp=grp)
    # functions_str = functions_str.replace("  ", "")
    return (functions_str)

def sub(x):
    xout = re.sub('_','', str(x), count=1)
    return(xout)

def write_ki_mix(nageGroups, scale=True):
    grp_x = range(1, nageGroups + 1)
    grp_y = reversed(grp_x)

    ki_dic = {}
    for i, xy in enumerate(itertools.product(grp_x, grp_y)):
        ki_dic[i] = ["C" + str(xy[0]) + '_' + str(xy[1])]

    ki_mix_param1 = ""
    ki_mix_param3 = ""
    for i in range(len(ki_dic.keys())):
        string_i = "\n(param " + sub(ki_dic[i][0]) + " @" + ki_dic[i][0] + "@ )"
        ki_mix_param1 = ki_mix_param1 + string_i
        
        string_i = "\n(param " + ki_dic[i][0]  + " (/ " + sub(ki_dic[i][0]) + " norm_factor))"
        ki_mix_param3 = ki_mix_param3 + string_i

    ## To do - remove hardcoding and if statement
    if nageGroups ==4 :
        ki_mix_param2 = "\n(param sum1 (+ C11 C12 C13 C14))"
        ki_mix_param2 = ki_mix_param2 +  "\n(param sum2  (+ C21 C22 C23 C24))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum3 (+ C31 C32 C33 C34))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum4 (+ C41 C42 C43 C44))"
        norm_factor = "\n(param norm_factor (+ (* sum1 p1) (* sum2  p2) (* sum3 p3) (* sum4  p4)))"

    if nageGroups ==8:
        ki_mix_param2 = "\n(param sum1 (+ C11 C12 C13 C14 C15 C16 C17 C18))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum2 (+ C21 C22 C23 C24 C25 C26 C27 C28))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum3 (+ C31 C32 C33 C34 C35 C36 C37 C38))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum4 (+ C41 C42 C43 C44 C45 C46 C47 C48))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum5 (+ C51 C52 C53 C54 C55 C56 C57 C58))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum6 (+ C61 C62 C63 C64 C65 C66 C67 C68))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum7 (+ C71 C72 C73 C74 C75 C76 C77 C78))"
        ki_mix_param2 = ki_mix_param2 + "\n(param sum8 (+ C81 C82 C83 C84 C85 C86 C87 C88))"
        norm_factor = "\n(param norm_factor (+ (* sum1 p1) (* sum2  p2) (* sum3 p3) (* sum4  p4) (* sum5  p5) (* sum6  p6) (* sum7  p7) (* sum8  p8)))"

    ki_mix_param = ki_mix_param1 +  "\n" +  ki_mix_param2 +  "\n" +  norm_factor +  "\n" +  ki_mix_param3

    return ki_mix_param
   

# If Ki mix is defined, Ki here can be set to 0 in script that generates the simulation
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
(param Ki @Ki@)
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
(param Ki_red1 (* Ki @social_multiplier_1@))
(param Ki_red2 (* Ki @social_multiplier_2@))
(param Ki_red3 (* Ki @social_multiplier_3@))

(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki Ki_red1)))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki Ki_red2)))
(time-event socialDistance_start @socialDistance_time3@ ((Ki Ki_red3)))

(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))  
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@))) 
 """
    # params_str = params_str.replace("  ", " ")

    return (params_str)


def write_N_population(grpList):
    stringAll = ""
    for key in grpList:
        string1 = """\n(param N_{grp} (+ @speciesS_{grp}@ @initialAs_{grp}@) )""".format(grp=key)
        stringAll = stringAll + string1

    string2 = "\n(param N_ageAll (+ " + repeat_string_by_grp('N_', grpList) + "))"
    stringAll = stringAll + string2

    for i, key in enumerate(grpList):
        string2 = """\n(param p{i} (/ N_{grp} N_ageAll))""".format(i=i+1, grp=key)
        stringAll = stringAll + string2

    return (stringAll)


def repeat_string_by_grp(fixedstring, grpList):
    stringAll = ""
    for grp in grpList:
        temp_string = " " + fixedstring + grp
        stringAll = stringAll + temp_string

    return stringAll


def write_ageAll(grpList):
    obs_ageAll_str = ""
    obs_ageAll_str = obs_ageAll_str + "\n(observe susceptible_ageAll (+ " + repeat_string_by_grp('S_', grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe exposed_ageAll (+ " + repeat_string_by_grp('E_', grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe asymptomatic_ageAll (+ " + repeat_string_by_grp('asymptomatic_',
                                                                                                  grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe presymptomatic_ageAll (+ " + repeat_string_by_grp('P_',
                                                                                                    grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe symptomatic_mild_ageAll (+ " + repeat_string_by_grp(
        'symptomatic_mild_', grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe symptomatic_severe_ageAll (+ " + repeat_string_by_grp(
        'symptomatic_severe_', grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe hospitalized_ageAll (+ " + repeat_string_by_grp('hospitalized_',
                                                                                                  grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe critical_ageAll (+ " + repeat_string_by_grp('critical_',
                                                                                              grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe deaths_ageAll (+ " + repeat_string_by_grp('deaths_', grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe recovered_ageAll (+ " + repeat_string_by_grp('recovered_',
                                                                                               grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe asymp_cumul_ageAll (+ " + repeat_string_by_grp('asymp_cumul_',
                                                                                                 grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe asymp_det_cumul_ageAll (+ " + repeat_string_by_grp('asymp_det_cumul_',
                                                                                                     grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe symp_mild_cumul_ageAll (+ " + repeat_string_by_grp('symp_mild_cumul_',
                                                                                                     grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe symp_mild_det_cumul_ageAll (+ " + repeat_string_by_grp(
        'symp_mild_det_cumul_', grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe symp_severe_cumul_ageAll (+ " + repeat_string_by_grp(
        'symp_severe_cumul_', grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe symp_severe_det_cumul_ageAll  (+ " + repeat_string_by_grp(
        'symp_severe_det_cumul_', grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe hosp_cumul_ageAll (+ " + repeat_string_by_grp('hosp_cumul_',
                                                                                                grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe hosp_det_cumul_ageAll (+ " + repeat_string_by_grp('hosp_det_cumul_',
                                                                                                    grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe crit_cumul_ageAll (+ " + repeat_string_by_grp('crit_cumul_',
                                                                                                grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe crit_det_cumul_ageAll (+ " + repeat_string_by_grp('crit_det_cumul_',
                                                                                                    grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe crit_det_ageAll (+ " + repeat_string_by_grp('crit_det_',
                                                                                              grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe detected_cumul_ageAll (+ " + repeat_string_by_grp('detected_cumul_',
                                                                                                    grpList) + "))"
    obs_ageAll_str = obs_ageAll_str + "\n(observe death_det_cumul_ageAll (+ " + repeat_string_by_grp('death_det_cumul_',
                                                                                                     grpList) + "))"

    return (obs_ageAll_str)


## homogeneous reactions for testing
def write_exposure_reaction_homogeneous(grp):
    grp = str(grp)
    exposure_reaction_str = """\n(reaction exposure_{grp}   (S_{grp}) (E_{grp}) (* Ki S_{grp} (/  (+ infectious_undet_ageAll (* infectious_det_ageAll reduced_inf_of_det_cases)) N_ageAll )))""".format(
        grp=grp)

    return exposure_reaction_str


def write_exposure_reaction4():
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


def write_exposure_reaction8():
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

    # reaction_str = reaction_str.replace("  ", " ")
    return (reaction_str)


###

###stringing all of the functions together to make the file:
def generate_extended_emodl(grpList, file_output, homogeneous=False):
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

    for key in grpList:
        species = write_species(key)
        observe = write_observe(key)
        reaction = write_reactions(key)
        functions = write_functions(key)
        species_string = species_string + species
        observe_string = observe_string + observe
        reaction_string = reaction_string + reaction
        functions_string = functions_string + functions

    if (homogeneous == False):
        if (len(grpList) == 4):
            reaction_string_combined = write_exposure_reaction4() + '\n' + reaction_string
        if (len(grpList) == 8):
            reaction_string_combined = write_exposure_reaction8() + '\n' + reaction_string

    elif (homogeneous == True):
        reaction_string_combined = ""
        for key in grpList:
            temp = write_exposure_reaction_homogeneous(key)
            reaction_string_combined = reaction_string_combined + temp

        reaction_string_combined = reaction_string_combined + '\n' + reaction_string

    params = write_params() + write_N_population(grpList) + write_ki_mix(len(grpList))
    functions_string = functions_string + write_ageAll(grpList)

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + params + '\n\n' + reaction_string_combined + '\n\n' + footer_str
    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


# if __name__ == '__main__':

age_grp4 = ['age0to19', 'age20to39', 'age40to59', 'age60to100']
generate_extended_emodl(grpList=age_grp4,
                        file_output=os.path.join(emodl_dir, 'extendedmodel_age4_homogeneous.emodl'),
                        homogeneous=True)

age_grp4 = ['age0to19', 'age20to39', 'age40to59', 'age60to100']
generate_extended_emodl(grpList=age_grp4, file_output=os.path.join(emodl_dir, 'extendedmodel_age4.emodl'))

age_grp8 = ["age0to9", "age10to19", "age20to29", "age30to39", "age40to49", "age50to59", "age60to69", "age70to100"]
generate_extended_emodl(grpList=age_grp8, file_output=os.path.join(emodl_dir, 'extendedmodel_age8.emodl'))