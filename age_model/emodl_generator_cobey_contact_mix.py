import os
import csv
import itertools
from load_paths import load_box_paths

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'age_model', 'emodl')

# generate the age dict, assuming each age is [pop, 0, 1, 0]
def read_group_dictionary(filename='age_dic.csv', Testmode=True, ngroups=2):
    age_dic = {}
    with open(os.path.join(git_dir, filename)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            age_dic[row['age']] = [int(x) for x in row['val_list'].strip('][').split(', ')]

    if Testmode == True:
        age_dic = {k: age_dic[k] for k in sorted(age_dic.keys())[:ngroups]}

    return age_dic

def define_group_dictionary(totalPop, ageGroups,  ageGroupScale, initialAs) :
    age_dic = {}
    for i, grp in enumerate(ageGroups):
        print(i, grp)
        age_dic[grp] = [totalPop * ageGroupScale[i], initialAs[i]]
    return age_dic

def write_species_init(age_dic, age):
    S = "(species S_{} {})".format(age, age_dic[age][0])
    As = "(species As_{} {})".format(age, age_dic[age][1])
    species_init_str = S + '\n' + As + '\n'
    species_init_str = species_init_str.replace("  ", " ")
    return (species_init_str)


### WRITE EMODL CHUNKS
# eval(" 'age,' * 26") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
def write_species(grp):
   grp = str(grp)
   species_str = """
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
           grp, grp, grp, grp, grp, grp, grp
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

(reaction detect_As_{} (As_{}) (As_det1_{}) (* d_As As_{}))
(reaction detect_symp_{} (Sym_{}) (Sym_det2_{}) (* d_Sym Sym_{}))
(reaction detect_hosp_{} (Sys_{}) (Sys_det3_{}) (* d_Sys Sys_{}))

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
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp
           )

    #reaction_str = reaction_str.replace("  ", " ")
    return (reaction_str)


###

###stringing all of the functions together to make the file:

def generate_extended_emodl(grp_dic, file_output, verbose=False):
    if (os.path.exists(file_output)):
        os.remove(file_output)

    model_name = "seir.emodl"  ### can make this more flexible
    header_str = "; simplemodel \n\n" + "(import (rnrs) (emodl cmslib)) \n\n" + '(start-model "{}") \n\n'.format(
        model_name)
    footer_str = "(end-model)"

    # building up the .emodl string
    total_string = ""
    species_init_string = ""
    species_string = ""
    observe_string = ""
    reaction_string = ""
    functions_string = ""
    total_string = total_string + header_str

    for key in age_dic.keys():
        # key = 'age0to9'
        species_init = write_species_init(age_dic, key)
        species = write_species(key)
        observe = write_observe(key)
        reaction = write_reactions(key)
        functions = write_functions(key)
        species_init_string = species_init_string + species_init
        species_string = species_string + species
        observe_string = observe_string + observe
        reaction_string = reaction_string + reaction
        functions_string = functions_string + functions

    reaction_string_combined = write_exposure_reaction() + '\n' + reaction_string
    params = write_params() + write_ki_mix(len(age_dic.keys()))

    total_string = total_string + '\n\n' + species_init_string + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + params + '\n\n' + reaction_string_combined + '\n\n' + footer_str
    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


#if __name__ == '__main__':
#age_dic = read_group_dictionary(filename='age_dic_agg.csv', Testmode=False)
# Age scaling needs revision based on latest demography data
age_dic = define_group_dictionary(totalPop = 1000,      #2700000
                                  ageGroups=['ageU5', 'age5to17', 'age18to64', 'age64to100'],
                                  ageGroupScale=[0.062, 0.203, 0.606, 0.129],   ## scaled from Chicago population data shared in w7 channel
                                  initialAs= [3,3,3,3])    ## homogeneous distribution of  initial cases  in all age groups?

generate_extended_emodl(grp_dic=age_dic, file_output=os.path.join(emodl_dir, 'age_colbeymodel_covid_4agegrp_pop1000.emodl'))


