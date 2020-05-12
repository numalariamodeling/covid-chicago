
"""
Author: Garrett Eickelberg
04/10/20
modified origional locale emodl generator to handle two groups (age groups and locale groups)

in general, the functions were converted to _2grp functions with two simple text replacements:
#replace _{region} -> {age}{region}
#replace :: -> _{age}::

also the final generator function had a subloop added in for age.
"""


import os
import subprocess
import sys
sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')

### FUNCTIONS
def read_group_dictionary(filename='region_dic.csv',grpname ='region', Testmode=True, ngroups=2):
    region_dic = {}
    with open(os.path.join(filename)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            region_dic[row[grpname]] = [int(x) for x in row['val_list'].strip('][').split(', ')]

    if Testmode == True:
        region_dic = {k: region_dic[k] for k in sorted(region_dic.keys())[:ngroups]}

    return region_dic

def define_group_dictionary(totalPop, regionGroups,  regionGroupScale, initialAs) :
    region_dic = {}
    for i, grp in enumerate(regionGroups):
        print(i, grp)
        region_dic[grp] = [totalPop * regionGroupScale[i], initialAs[i]]
    return region_dic


#def write_species_init_2grp(age, region_dic, region):
#    S = "(species S_{age}::{region} {region_val})".format(age=age, region=region, region_val=region_dic[region][0])
#    As = "(species As_{age}::{region} {region_val})".format(age=age, region=region, region_val=region_dic[region][1])
#    species_init_str = S + '\n' + As
#    species_init_str = species_init_str.replace("  ", " ")
#    return (species_init_str)

def write_species_2grp(age,region):
    region = str(region)
    species_str = """
(species S_{age}::{region}  @speciesS_{age}_{region}@ )
(species As_{age}::{region}  @speciesAs_{age}_{region}@ )
(species E_{age}::{region} 0)
(species As_det1_{age}::{region} 0)
(species P_{age}::{region} 0)
(species Sym_{age}::{region} 0)
(species Sym_det2_{age}::{region} 0)
(species Sys_{age}::{region} 0)
(species Sys_det3_{age}::{region} 0)
(species H1_{age}::{region} 0)
(species H2_{age}::{region} 0)
(species H3_{age}::{region} 0)
(species H1_det3_{age}::{region} 0)
(species H2_det3_{age}::{region} 0)
(species H3_det3_{age}::{region} 0)
(species C2_{age}::{region} 0)
(species C3_{age}::{region} 0)
(species C2_det3_{age}::{region} 0)
(species C3_det3_{age}::{region} 0)
(species D3_{age}::{region} 0)
(species D3_det3_{age}::{region} 0)
(species RAs_{age}::{region} 0)
(species RAs_det1_{age}::{region} 0)
(species RSym_{age}::{region} 0)
(species RSym_det2_{age}::{region} 0)
(species RH1_{age}::{region} 0)
(species RH1_det3_{age}::{region} 0)
(species RC2_{age}::{region} 0)
(species RC2_det3_{age}::{region} 0)
""".format(age=age, region=region)
    species_str = species_str.replace("  ", " ")
    return (species_str)

def write_observe_2grp(age,region):
    region = str(region)

    observe_str = """
(observe susceptible_{age}_{region} S_{age}::{region})
(observe exposed_{age}_{region} E_{age}::{region})
(observe asymptomatic_{age}_{region} asymptomatic_{age}_{region})
(observe presymptomatic_{age}_{region} P_{age}::{region})
(observe symptomatic_mild_{age}_{region} symptomatic_mild_{age}_{region})
(observe symptomatic_severe_{age}_{region} symptomatic_severe_{age}_{region})
(observe hospitalized_{age}_{region} hospitalized_{age}_{region})
(observe critical_{age}_{region} critical_{age}_{region})
(observe deaths_{age}_{region} deaths_{age}_{region})
(observe recovered_{age}_{region} recovered_{age}_{region})

(observe asymp_cumul_{age}_{region} (+ asymptomatic_{age}_{region} RAs_{age}::{region} RAs_det1_{age}::{region} ))
(observe asymp_det_cumul_{age}_{region} (+ As_det1_{age}::{region} RAs_det1_{age}::{region}))
(observe symp_mild_cumul_{age}_{region} (+ symptomatic_mild_{age}_{region} RSym_{age}::{region} RSym_det2_{age}::{region}))
(observe symp_mild_det_cumul_{age}_{region} (+ RSym_det2_{age}::{region} Sym_det2_{age}::{region}))
(observe symp_severe_cumul_{age}_{region} (+ symptomatic_severe_{age}_{region} hospitalized_{age}_{region} critical_{age}_{region} deaths_{age}_{region} RH1_{age}::{region} RC2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(observe symp_severe_det_cumul_{age}_{region} (+ Sys_det3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region} D3_det3_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(observe hosp_cumul_{age}_{region} (+ hospitalized_{age}_{region} critical_{age}_{region} deaths_{age}_{region} RH1_{age}::{region} RC2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(observe hosp_det_cumul_{age}_{region} (+ H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region} D3_det3_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(observe crit_cumul_{age}_{region} (+ deaths_{age}_{region} critical_{age}_{region} RC2_{age}::{region} RC2_det3_{age}::{region}))
(observe crit_det_cumul_{age}_{region} (+ C2_det3_{age}::{region} C3_det3_{age}::{region} D3_det3_{age}::{region} RC2_det3_{age}::{region}))
(observe crit_det_{age}_{region} (+ C2_det3_{age}::{region} C3_det3_{age}::{region}))
(observe death_det_cumul_{age}_{region} D3_det3_{age}::{region} )
(observe detected_cumul_{age}_{region} (+ (+ As_det1_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}) RAs_det1_{age}::{region} RSym_det2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region} D3_det3_{age}::{region}))

(observe detected_{age}_{region} (+ As_det1_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
(observe infected_{age}_{region} (+ infectious_det_{age}_{region} infectious_undet_{age}_{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
""".format(age=age, region=region
           )
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


def write_functions_2grp(age,region):
    region = str(region)
    functions_str = """
(func asymptomatic_{age}_{region}  (+ As_{age}::{region} As_det1_{age}::{region}))
(func symptomatic_mild_{age}_{region}  (+ Sym_{age}::{region} Sym_det2_{age}::{region}))
(func symptomatic_severe_{age}_{region}  (+ Sys_{age}::{region} Sys_det3_{age}::{region}))
(func hospitalized_{age}_{region}  (+ H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region}))
(func critical_{age}_{region} (+ C2_{age}::{region} C3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
(func deaths_{age}_{region} (+ D3_{age}::{region} D3_det3_{age}::{region}))
(func recovered_{age}_{region} (+ RAs_{age}::{region} RSym_{age}::{region} RH1_{age}::{region} RC2_{age}::{region} RAs_det1_{age}::{region} RSym_det2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(func infectious_undet_{age}_{region} (+ As_{age}::{region} P_{age}::{region} Sym_{age}::{region} Sys_{age}::{region} H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} C2_{age}::{region} C3_{age}::{region}))
(func infectious_det_{age}_{region} (+ As_det1_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} ))

(param N_{age}_{region} (+  @speciesS_{age}_{region}@   @speciesAs_{age}_{region}@  ))
""".format(age=age,region=region)
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

(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))  
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@))) 
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@))) 
 """
    params_str = params_str.replace("  ", " ")

    return (params_str)

def write_reactions_2grp(age,region):
    region = str(region)

    reaction_str = """
(reaction exposure_{age}_{region}   (S_{age}::{region}) (E_{age}::{region}) (* Ki S_{age}::{region} (/ (+ infectious_undet_{age}_{region} (* infectious_det_{age}_{region} reduced_inf_of_det_cases)) N_{age}_{region} )))
(reaction infection_asymp_undet_{age}_{region}  (E_{age}::{region})   (As_{age}::{region})   (* Kl E_{age}::{region} (- 1 d_As)))
(reaction infection_asymp_det_{age}_{region}  (E_{age}::{region})   (As_det1_{age}::{region})   (* Kl E_{age}::{region} d_As))
(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_{age}::{region})   (* Ks E_{age}::{region}))
(reaction mild_symptomatic_undet_{age}_{region} (P_{age}::{region})  (Sym_{age}::{region}) (* Ksym P_{age}::{region} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{age}_{region} (P_{age}::{region})  (Sym_det2_{age}::{region}) (* Ksym P_{age}::{region} d_Sym))
(reaction severe_symptomatic_undet_{age}_{region} (P_{age}::{region})  (Sys_{age}::{region})  (* Ksys P_{age}::{region} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{age}_{region} (P_{age}::{region})  (Sys_det3_{age}::{region})  (* Ksys P_{age}::{region} d_Sys))

(reaction hospitalization_1_{age}_{region}   (Sys_{age}::{region})   (H1_{age}::{region})   (* Kh1 Sys_{age}::{region}))
(reaction hospitalization_2_{age}_{region}   (Sys_{age}::{region})   (H2_{age}::{region})   (* Kh2 Sys_{age}::{region}))
(reaction hospitalization_3_{age}_{region}   (Sys_{age}::{region})   (H3_{age}::{region})   (* Kh3 Sys_{age}::{region}))
(reaction critical_2_{age}_{region}   (H2_{age}::{region})   (C2_{age}::{region})   (* Kc H2_{age}::{region}))
(reaction critical_3_{age}_{region}   (H3_{age}::{region})   (C3_{age}::{region})   (* Kc H3_{age}::{region}))
(reaction death_{age}_{region}   (C3_{age}::{region})   (D3_{age}::{region})   (* Km C3_{age}::{region}))

(reaction recovery_As_{age}_{region}   (As_{age}::{region})   (RAs_{age}::{region})   (* Kr_a As_{age}::{region}))
(reaction recovery_Sym_{age}_{region}   (Sym_{age}::{region})   (RSym_{age}::{region})   (* Kr_m  Sym_{age}::{region}))
(reaction recovery_H1_{age}_{region}   (H1_{age}::{region})   (RH1_{age}::{region})   (* Kr_h H1_{age}::{region}))
(reaction recovery_C2_{age}_{region}   (C2_{age}::{region})   (RC2_{age}::{region})   (* Kr_c C2_{age}::{region}))

(reaction recovery_As_det_{age}_{region} (As_det1_{age}::{region})   (RAs_det1_{age}::{region})   (* Kr_a As_det1_{age}::{region}))

(reaction hospitalization_1_det_{age}_{region}   (Sys_det3_{age}::{region})   (H1_det3_{age}::{region})   (* Kh1 Sys_det3_{age}::{region}))
(reaction hospitalization_2_det_{age}_{region}   (Sys_det3_{age}::{region})   (H2_det3_{age}::{region})   (* Kh2 Sys_det3_{age}::{region}))
(reaction hospitalization_3_det_{age}_{region}   (Sys_det3_{age}::{region})   (H3_det3_{age}::{region})   (* Kh3 Sys_det3_{age}::{region}))
(reaction critical_2_det2_{age}_{region}   (H2_det3_{age}::{region})   (C2_det3_{age}::{region})   (* Kc H2_det3_{age}::{region}))
(reaction critical_3_det2_{age}_{region}   (H3_det3_{age}::{region})   (C3_det3_{age}::{region})   (* Kc H3_det3_{age}::{region}))
(reaction death_det3_{age}_{region}   (C3_det3_{age}::{region})   (D3_det3_{age}::{region})   (* Km C3_det3_{age}::{region}))

(reaction recovery_Sym_det2_{age}_{region}   (Sym_det2_{age}::{region})   (RSym_det2_{age}::{region})   (* Kr_m  Sym_det2_{age}::{region}))
(reaction recovery_H1_det3_{age}_{region}   (H1_det3_{age}::{region})   (RH1_det3_{age}::{region})   (* Kr_h H1_det3_{age}::{region}))
(reaction recovery_C2_det3_{age}_{region}   (C2_det3_{age}::{region})   (RC2_det3_{age}::{region})   (* Kr_c C2_det3_{age}::{region}))
""".format(age=age, region= region)

    reaction_str = reaction_str.replace("  ", " ")
    return (reaction_str)


######stringing all of my functions together to make the file:###

## modifying for 2group:
def generate_locale_emodl_extended_2grp(age_list, region_dic, file_output):
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

    for key in region_list:
        total_string= total_string+ "\n(locale site-{})\n".format(key)
        total_string= total_string+ "(set-locale site-{})\n".format(key)
        
        for age in age_list:
            #species_init = write_species_init_2grp(age=age, region_dic=region_dic, region=key)
            species = write_species_2grp(region=key, age=age)
            total_string =total_string +  species  #species_init

    for key in region_list:
        for age in age_list:
            observe = write_observe_2grp( region=key, age=age)
            reaction = write_reactions_2grp( region=key, age=age)
            functions = write_functions_2grp( region=key, age=age)
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

    age_list = ['age0to19', 'age20to39', 'age40to59', 'age60to100']
    region_list = ['EMS_1', 'EMS_1', 'EMS_2', 'EMS_3', 'EMS_4', 'EMS_5', 'EMS_6', 'EMS_7', 'EMS_8', 'EMS_9', 'EMS_10','EMS_11']

    generate_locale_emodl_extended_2grp(age_list, region_list, file_output=os.path.join(emodl_dir, 'extendedmodel_cobey_locale_age_test.emodl'))