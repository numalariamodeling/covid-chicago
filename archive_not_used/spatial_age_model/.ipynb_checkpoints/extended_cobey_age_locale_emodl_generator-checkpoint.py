
"""
Author: Garrett Eickelberg
04/10/20
modified origional locale emodl generator to handle two groups (age groups and locale groups)

in general, the functions were converted to _2grp functions with two simple text replacements:
#replace _{county} -> {age}{county}
#replace :: -> _{age}::

also the final generator function had a subloop added in for age.
"""


import os
import subprocess
import sys
sys.path.append("C:\\Users\\garrett\\Documents\\GitHub\\covid-chicago") #added for the loadpaths for garrett

from load_paths import load_box_paths

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'spatial_model', 'emodl')

### FUNCTIONS
def read_group_dictionary(filename='county_dic.csv',grpname ='county', Testmode=True, ngroups=2):
    county_dic = {}
    with open(os.path.join(filename)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            county_dic[row[grpname]] = [int(x) for x in row['val_list'].strip('][').split(', ')]

    if Testmode == True:
        county_dic = {k: county_dic[k] for k in sorted(county_dic.keys())[:ngroups]}

    return county_dic

def define_group_dictionary(totalPop, countyGroups,  countyGroupScale, initialAs) :
    county_dic = {}
    for i, grp in enumerate(countyGroups):
        print(i, grp)
        county_dic[grp] = [totalPop * countyGroupScale[i], initialAs[i]]
    return county_dic


def write_species_init_2grp(age, county_dic, county):
    S = "(species S_{age}::{county} {county_val})".format(age=age, county=county, county_val=county_dic[county][0])
    As = "(species As_{age}::{county} {county_val})".format(age=age, county=county, county_val=county_dic[county][1])
    species_init_str = S + '\n' + As 
    species_init_str = species_init_str.replace("  ", " ")
    return (species_init_str)

def write_species_2grp(age,county):
    county = str(county)
    species_str = """
(species E_{age}::{county} 0)
(species As_det1_{age}::{county} 0)
(species P_{age}::{county} 0)
(species Sym_{age}::{county} 0)
(species Sym_det2_{age}::{county} 0)
(species Sys_{age}::{county} 0)
(species Sys_det3_{age}::{county} 0)
(species H1_{age}::{county} 0)
(species H2_{age}::{county} 0)
(species H3_{age}::{county} 0)
(species H1_det3_{age}::{county} 0)
(species H2_det3_{age}::{county} 0)
(species H3_det3_{age}::{county} 0)
(species C2_{age}::{county} 0)
(species C3_{age}::{county} 0)
(species C2_det3_{age}::{county} 0)
(species C3_det3_{age}::{county} 0)
(species D3_{age}::{county} 0)
(species D3_det3_{age}::{county} 0)
(species RAs_{age}::{county} 0)
(species RAs_det1_{age}::{county} 0)
(species RSym_{age}::{county} 0)
(species RSym_det2_{age}::{county} 0)
(species RH1_{age}::{county} 0)
(species RH1_det3_{age}::{county} 0)
(species RC2_{age}::{county} 0)
(species RC2_det3_{age}::{county} 0)
""".format(age=age, county=county)
    species_str = species_str.replace("  ", " ")
    return (species_str)

def write_observe_2grp(age,county):
    county = str(county)

    observe_str = """
(observe susceptible_{age}_{county} S_{age}::{county})
(observe exposed_{age}_{county} E_{age}::{county})
(observe asymptomatic_{age}_{county} asymptomatic_{age}_{county})
(observe presymptomatic_{age}_{county} P_{age}::{county})
(observe symptomatic_mild_{age}_{county} symptomatic_mild_{age}_{county})
(observe symptomatic_severe_{age}_{county} symptomatic_severe_{age}_{county})
(observe hospitalized_{age}_{county} hospitalized_{age}_{county})
(observe critical_{age}_{county} critical_{age}_{county})
(observe deaths_{age}_{county} deaths_{age}_{county})
(observe recovered_{age}_{county} recovered_{age}_{county})

(observe asymp_cumul_{age}_{county} (+ asymptomatic_{age}_{county} RAs_{age}::{county} RAs_det1_{age}::{county} ))
(observe asymp_det_cumul_{age}_{county} (+ As_det1_{age}::{county} RAs_det1_{age}::{county}))
(observe symp_mild_cumul_{age}_{county} (+ symptomatic_mild_{age}_{county} RSym_{age}::{county} RSym_det2_{age}::{county}))
(observe symp_mild_det_cumul_{age}_{county} (+ RSym_det2_{age}::{county} Sym_det2_{age}::{county}))
(observe symp_severe_cumul_{age}_{county} (+ symptomatic_severe_{age}_{county} hospitalized_{age}_{county} critical_{age}_{county} deaths_{age}_{county} RH1_{age}::{county} RC2_{age}::{county} RH1_det3_{age}::{county} RC2_det3_{age}::{county}))
(observe symp_severe_det_cumul_{age}_{county} (+ Sys_det3_{age}::{county} H1_det3_{age}::{county} H2_det3_{age}::{county} H3_det3_{age}::{county} C2_det3_{age}::{county} C3_det3_{age}::{county} D3_det3_{age}::{county} RH1_det3_{age}::{county} RC2_det3_{age}::{county}))
(observe hosp_cumul_{age}_{county} (+ hospitalized_{age}_{county} critical_{age}_{county} deaths_{age}_{county} RH1_{age}::{county} RC2_{age}::{county} RH1_det3_{age}::{county} RC2_det3_{age}::{county}))
(observe hosp_det_cumul_{age}_{county} (+ H1_det3_{age}::{county} H2_det3_{age}::{county} H3_det3_{age}::{county} C2_det3_{age}::{county} C3_det3_{age}::{county} D3_det3_{age}::{county} RH1_det3_{age}::{county} RC2_det3_{age}::{county}))
(observe crit_cumul_{age}_{county} (+ deaths_{age}_{county} critical_{age}_{county} RC2_{age}::{county} RC2_det3_{age}::{county}))
(observe crit_det_cumul_{age}_{county} (+ C2_det3_{age}::{county} C3_det3_{age}::{county} D3_det3_{age}::{county} RC2_det3_{age}::{county}))
(observe crit_det_{age}_{county} (+ C2_det3_{age}::{county} C3_det3_{age}::{county}))
(observe death_det_cumul_{age}_{county} D3_det3_{age}::{county} )
(observe detected_cumul_{age}_{county} (+ (+ As_det1_{age}::{county} Sym_det2_{age}::{county} Sys_det3_{age}::{county} H1_det3_{age}::{county} H2_det3_{age}::{county} C2_det3_{age}::{county} C3_det3_{age}::{county}) RAs_det1_{age}::{county} RSym_det2_{age}::{county} RH1_det3_{age}::{county} RC2_det3_{age}::{county} D3_det3_{age}::{county}))

(observe detected_{age}_{county} (+ As_det1_{age}::{county} Sym_det2_{age}::{county} Sys_det3_{age}::{county} H1_det3_{age}::{county} H2_det3_{age}::{county} H3_det3_{age}::{county} C2_det3_{age}::{county} C3_det3_{age}::{county}))
(observe infected_{age}_{county} (+ infectious_det_{age}_{county} infectious_undet_{age}_{county} H1_det3_{age}::{county} H2_det3_{age}::{county} H3_det3_{age}::{county} C2_det3_{age}::{county} C3_det3_{age}::{county}))
""".format(age=age, county=county
           )
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


def write_functions_2grp(age,county):
    county = str(county)
    functions_str = """
(func asymptomatic_{age}_{county}  (+ As_{age}::{county} As_det1_{age}::{county}))
(func symptomatic_mild_{age}_{county}  (+ Sym_{age}::{county} Sym_det2_{age}::{county}))
(func symptomatic_severe_{age}_{county}  (+ Sys_{age}::{county} Sys_det3_{age}::{county}))
(func hospitalized_{age}_{county}  (+ H1_{age}::{county} H2_{age}::{county} H3_{age}::{county} H1_det3_{age}::{county} H2_det3_{age}::{county} H3_det3_{age}::{county}))
(func critical_{age}_{county} (+ C2_{age}::{county} C3_{age}::{county} C2_det3_{age}::{county} C3_det3_{age}::{county}))
(func deaths_{age}_{county} (+ D3_{age}::{county} D3_det3_{age}::{county}))
(func recovered_{age}_{county} (+ RAs_{age}::{county} RSym_{age}::{county} RH1_{age}::{county} RC2_{age}::{county} RAs_det1_{age}::{county} RSym_det2_{age}::{county} RH1_det3_{age}::{county} RC2_det3_{age}::{county}))
(func infectious_undet_{age}_{county} (+ As_{age}::{county} P_{age}::{county} Sym_{age}::{county} Sys_{age}::{county} H1_{age}::{county} H2_{age}::{county} H3_{age}::{county} C2_{age}::{county} C3_{age}::{county}))
(func infectious_det_{age}_{county} (+ As_det1_{age}::{county} Sym_det2_{age}::{county} Sys_det3_{age}::{county} ))
""".format(age=age,county=county)
    functions_str = functions_str.replace("  ", "")
    return (functions_str)

###
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
    params_str = params_str.replace("  ", " ")

    return (params_str)

def write_reactions_2grp(age,county):
    county = str(county)

    reaction_str = """
(reaction exposure_{age}_{county}   (S_{age}::{county}) (E_{age}::{county}) (* Ki S_{age}::{county} (+ infectious_undet_{age}_{county} (* infectious_det_{age}_{county} reduced_inf_of_det_cases))))
(reaction infection_asymp_undet_{age}_{county}  (E_{age}::{county})   (As_{age}::{county})   (* Kl E_{age}::{county} (- 1 d_As)))
(reaction infection_asymp_det_{age}_{county}  (E_{age}::{county})   (As_det1_{age}::{county})   (* Kl E_{age}::{county} d_As))
(reaction presymptomatic_{age}_{county} (E_{age}::{county})   (P_{age}::{county})   (* Ks E_{age}::{county}))
(reaction mild_symptomatic_undet_{age}_{county} (P_{age}::{county})  (Sym_{age}::{county}) (* Ksym P_{age}::{county} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{age}_{county} (P_{age}::{county})  (Sym_det2_{age}::{county}) (* Ksym P_{age}::{county} d_Sym))
(reaction severe_symptomatic_undet_{age}_{county} (P_{age}::{county})  (Sys_{age}::{county})  (* Ksys P_{age}::{county} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{age}_{county} (P_{age}::{county})  (Sys_det3_{age}::{county})  (* Ksys P_{age}::{county} d_Sys))

(reaction hospitalization_1_{age}_{county}   (Sys_{age}::{county})   (H1_{age}::{county})   (* Kh1 Sys_{age}::{county}))
(reaction hospitalization_2_{age}_{county}   (Sys_{age}::{county})   (H2_{age}::{county})   (* Kh2 Sys_{age}::{county}))
(reaction hospitalization_3_{age}_{county}   (Sys_{age}::{county})   (H3_{age}::{county})   (* Kh3 Sys_{age}::{county}))
(reaction critical_2_{age}_{county}   (H2_{age}::{county})   (C2_{age}::{county})   (* Kc H2_{age}::{county}))
(reaction critical_3_{age}_{county}   (H3_{age}::{county})   (C3_{age}::{county})   (* Kc H3_{age}::{county}))
(reaction death_{age}_{county}   (C3_{age}::{county})   (D3_{age}::{county})   (* Km C3_{age}::{county}))

(reaction recovery_As_{age}_{county}   (As_{age}::{county})   (RAs_{age}::{county})   (* Kr_a As_{age}::{county}))
(reaction recovery_Sym_{age}_{county}   (Sym_{age}::{county})   (RSym_{age}::{county})   (* Kr_m  Sym_{age}::{county}))
(reaction recovery_H1_{age}_{county}   (H1_{age}::{county})   (RH1_{age}::{county})   (* Kr_h H1_{age}::{county}))
(reaction recovery_C2_{age}_{county}   (C2_{age}::{county})   (RC2_{age}::{county})   (* Kr_c C2_{age}::{county}))

(reaction recovery_As_det_{age}_{county} (As_det1_{age}::{county})   (RAs_det1_{age}::{county})   (* Kr_a As_det1_{age}::{county}))

(reaction hospitalization_1_det_{age}_{county}   (Sys_det3_{age}::{county})   (H1_det3_{age}::{county})   (* Kh1 Sys_det3_{age}::{county}))
(reaction hospitalization_2_det_{age}_{county}   (Sys_det3_{age}::{county})   (H2_det3_{age}::{county})   (* Kh2 Sys_det3_{age}::{county}))
(reaction hospitalization_3_det_{age}_{county}   (Sys_det3_{age}::{county})   (H3_det3_{age}::{county})   (* Kh3 Sys_det3_{age}::{county}))
(reaction critical_2_det2_{age}_{county}   (H2_det3_{age}::{county})   (C2_det3_{age}::{county})   (* Kc H2_det3_{age}::{county}))
(reaction critical_3_det2_{age}_{county}   (H3_det3_{age}::{county})   (C3_det3_{age}::{county})   (* Kc H3_det3_{age}::{county}))
(reaction death_det3_{age}_{county}   (C3_det3_{age}::{county})   (D3_det3_{age}::{county})   (* Km C3_det3_{age}::{county}))

(reaction recovery_Sym_det2_{age}_{county}   (Sym_det2_{age}::{county})   (RSym_det2_{age}::{county})   (* Kr_m  Sym_det2_{age}::{county}))
(reaction recovery_H1_det3_{age}_{county}   (H1_det3_{age}::{county})   (RH1_det3_{age}::{county})   (* Kr_h H1_det3_{age}::{county}))
(reaction recovery_C2_det3_{age}_{county}   (C2_det3_{age}::{county})   (RC2_det3_{age}::{county})   (* Kr_c C2_det3_{age}::{county}))
""".format(age=age, county= county)

    reaction_str = reaction_str.replace("  ", " ")
    return (reaction_str)


######stringing all of my functions together to make the file:###

## modifying for 2group:
def generate_locale_emodl_extended_2grp(age_list, county_dic, file_output):
    if (os.path.exists(file_output)):
        os.remove(file_output)


    model_name= "seir.emodl" ### can make this more flexible
    header_str="; simplemodel \n\n"+ "(import (rnrs) (emodl cmslib)) \n\n"+'(start-model "{}") \n\n'.format(model_name)
    footer_str ="(end-model)"
    
    #building up the .emodl string
    total_string = ""
    species_string = ""
    observe_string = ""
    reaction_string = ""
    functions_string = ""
    total_string = total_string + header_str

    for key in county_dic.keys():
        total_string= total_string+ "\n(locale site-{})\n".format(key)
        total_string= total_string+ "(set-locale site-{})\n".format(key)
        
        for age in age_list:
            species_init = write_species_init_2grp(age=age, county_dic=county_dic, county=key)
            species = write_species_2grp(county=key, age=age)
            total_string =total_string + species_init + species

    for key in county_dic.keys():
        for age in age_list:
            observe = write_observe_2grp( county=key, age=age)
            reaction = write_reactions_2grp( county=key, age=age)
            functions = write_functions_2grp( county=key, age=age)
            observe_string = observe_string + observe
            reaction_string = reaction_string + reaction
            functions_string = functions_string + functions
 
    params = write_params()
    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + params + '\n\n' + reaction_string + '\n\n' + footer_str
    print(total_string)
    
    
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))

        
if __name__ == '__main__':
#     county_dic = define_group_dictionary(totalPop=12741080,  #  12741080 based on IL_population_by_Age_2010_2018 (shared in w7 channel)
#                                       countyGroups=['EMS_0','EMS_1','EMS_2','EMS_3','EMS_4','EMS_5','EMS_6'],
#                                       countyGroupScale=[0.68, 0.05, 0.08,  0.04, 0.05,  0.03, 0.06],    ## proportion of total population, based on IL_population_by_Age_2010_2018
#                                       initialAs=[2, 2, 2, 2, 2, 2, 2]  # homogeneous distribution of inital cases ? Or "hot spot" in one area?
#                                       )

#     generate_locale_emodl_extended(county_dic=county_dic, file_output=os.path.join(emodl_dir,'extendedmodel_cobey_locale_EMS.emodl'))

    ###testing with 1age and 1 locale group:
    age_list =  ['age0to19']#, 'age40to59', 'age60to100']
    county_dic = define_group_dictionary(totalPop=12741080,  #  12741080 based on IL_population_by_Age_2010_2018 (shared in w7 channel)
                                      countyGroups=['EMS_0'],
                                      countyGroupScale=[0.68],    ## proportion of total population, based on IL_population_by_Age_2010_2018
                                      initialAs=[2]  # homogeneous distribution of inital cases ? Or "hot spot" in one area?
                                      )

    generate_locale_emodl_extended_2grp(age_list, county_dic, file_output='emodl//extendedmodel_cobey_locale_age_2grptest1.emodl')