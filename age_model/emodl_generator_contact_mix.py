import os
import subprocess
import csv
import itertools
from load_paths import load_box_paths


datapath, projectpath, wdir,exe_dir, git_dir = load_box_paths()

###

##making the age dict, assuming each age is [pop, 0, 1, 0]

def read_group_dictionary(filename='age_dic.csv', Testmode=True, ngroups=2):
    age_dic = {}
    with open(os.path.join(git_dir, filename)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            age_dic[row['age']] = [int(x) for x in row['val_list'].strip('][').split(', ')]

    if Testmode == True:
        age_dic = {k: age_dic[k] for k in sorted(age_dic.keys())[:ngroups]}

    return age_dic

def define_group_dictionary(totalPop, ageGroups,  ageGroupScale, initialAs, initialSy, initialH) :
    age_dic = {}
    for i, grp in enumerate(ageGroups):
        print(i, grp)
        age_dic[grp] = [totalPop * ageGroupScale[i], initialAs[i], initialSy[i], initialH[i]]
    return age_dic

def write_species_init(age_dic, age):
    S = "(species S_{} {})".format(age, age_dic[age][0])
    As = "(species As_{} {})".format(age, age_dic[age][1])
    Sy = "(species Sy_{} {})".format(age, age_dic[age][2])
    H = "(species H_{} {})".format(age, age_dic[age][3])
    species_init_str = S + '\n' + As + '\n' + Sy + '\n' + H + '\n'

    species_init_str = species_init_str.replace("  ", " ")
    return (species_init_str)


### WRITE EMODL CHUNKS
# eval(" 'age,' * 26") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
def write_species(grp):
   grp = str(grp)
   species_str = """
(species E_{} 0)
(species As_det1_{} 0)
(species Sy_det2_{} 0)
(species H_det2_{} 0)
(species H_det3_{} 0)
(species C_{} 0)
(species C_det2_{} 0)
(species C_det3_{} 0)
(species D_{} 0)
(species D_det2_{} 0)
(species D_det3_{} 0)
(species RAs_{} 0)
(species RAs_det1_{} 0)
(species RSy_{} 0)
(species RSy_det2_{} 0)
(species RH_{} 0)
(species RH_det2_{} 0)
(species RH_det3_{} 0)
(species RC_{} 0)
(species RC_det2_{} 0)
(species RC_det3_{} 0)
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
(observe detected_{} (sum As_det1_{} Sy_det2_{} H_det2_{} H_det3_{} C_det2_{} C_det3_{}))
(observe infected_{} (sum As_{} As_det1_{} Sy_{} Sy_det2_{} H_{} H_det2_{} H_det3_{} C_{} C_det2_{} C_det3_{}))
(observe asymptomatic_{} asymptomatic_{})
(observe symptomatic_{} symptomatic_{})
(observe hospitalized_{} hospitalized_{})
(observe critical_{} critical_{})
(observe deaths_{} deaths_{})
(observe recovered_{} recovered_{})
(observe asymp_cumul_{} (+ asymptomatic_{} RAs_{} RAs_det1_{} ))
(observe asymp_det_cumul_{} (+ As_det1_{} RAs_det1_{}))
(observe symp_cumul_{} (+ (sum RSy_{} RH_{} RC_{} RSy_det2_{} RH_det2_{} RH_det3_{} RC_det2_{} RC_det3_{}) deaths_{} critical_{} hospitalized_{} asymptomatic_{}))
(observe symp_det_cumul_{} (+ Sy_det2_{} H_det2_{} RSy_det2_{} C_det2_{} D_det2_{}))
(observe hosp_cumul_{} (+ deaths_{} critical_{} hospitalized_{} RH_{} RH_det2_{} RH_det3_{} RC_{} RC_det2_{} RC_det3_{}))
(observe hosp_det_cumul_{} (+ H_det2_{} H_det3_{} RH_det2_{} RH_det3_{} C_det2_{} C_det3_{} D_det2_{} D_det3_{} RC_det2_{} RC_det3_{}))
(observe crit_cumul_{} (+ deaths_{} critical_{} RC_{} RC_det2_{} RC_det3_{}))
(observe crit_det_cumul_{} (+ C_det2_{} C_det3_{} RC_det2_{} RC_det3_{} D_det2_{} D_det3_{}))
(observe detected_cumul_{} (+ (sum As_det1_{} Sy_det2_{} H_det2_{} H_det3_{} C_det2_{} C_det3_{}) RAs_det1_{} RSy_det2_{} RH_det2_{} RH_det3_{} RC_det2_{} RC_det3_{} D_det2_{} D_det3_{}))
""".format(grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
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
(func asymptomatic_{} (+ As_{} As_det1_{}))
(func symptomatic_{} (+ Sy_{} Sy_det2_{}))
(func hospitalized_{} (sum H_{} H_det2_{} H_det3_{}))
(func critical_{} (sum C_{} C_det2_{} C_det3_{}))
(func deaths_{} (sum D_{} D_det2_{} D_det3_{}))
(func recovered_{} (sum RAs_{} RSy_{} RH_{} RC_{} RAs_det1_{} RSy_det2_{} RH_det2_{} RH_det3_{} RC_det2_{} RC_det3_{}))
(func infectious_undet_{} (+ As_{} Sy_{}))
(func infectious_det_{} (+ As_det1_{} Sy_det2_{}))
""".format(grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp
           )
    functions_str = functions_str.replace("  ", "")
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
            string_i = "(param " + ki_dic[i][0] + " (/ Ki @s" + ki_dic[i][0] + "@ ))" + "\n"
        ki_mix_param = ki_mix_param + string_i

    return ki_mix_param


# If Ki mix is defined, Ki here can be set to 0 in script that generates the simulation
def write_params():
    params_str = """
(param incubation_pd @incubation_pd@)
(param time_to_hospitalization @time_to_hospitalization@)
(param time_to_critical @time_to_critical@)
(param time_to_death @time_to_death@)
(param recovery_rate @recovery_rate@)
(param fraction_hospitalized @fraction_hospitalized@)
(param fraction_symptomatic @fraction_symptomatic@)
(param fraction_critical @fraction_critical@ )
(param cfr @cfr@)
(param fraction_dead ( / cfr (* fraction_hospitalized fraction_critical)))
(param reduced_inf_of_det_cases @reduced_inf_of_det_cases@)
(param d_As @d_As@)
(param d_Sy @d_Sy@)
(param d_H @d_H@)
(param Ki @Ki@)
(param Kr (/ 1 recovery_rate))
(param Kl (/ (- 1 fraction_symptomatic ) incubation_pd))
(param Ks (/ fraction_symptomatic  incubation_pd))
(param Kh (/ fraction_hospitalized time_to_hospitalization))
(param Kc (/ fraction_critical time_to_critical ))
(param Km (/ fraction_dead  time_to_death))
 """
    params_str = params_str.replace("  ", " ")

    return (params_str)


###  age-specific infection rates and contacts
### need automatization (parked for now)
def write_exposure_reaction():
    exposure_reaction_str = """  
(reaction exposure_from_detected_ageU5 (S_ageU5) (E_ageU5) (sum (* Ki1_1 S_ageU5 infectious_det_ageU5) (* Ki1_2 S_ageU5 infectious_det_age5to17) (* Ki1_3 S_ageU5 infectious_det_age18to64) (* Ki1_4 S_ageU5 infectious_det_age64to100)))
(reaction exposure_from_detected_age5to17 (S_age5to17) (E_age5to17) (sum (* Ki2_1 S_age5to17 infectious_det_ageU5) (* Ki2_2 S_age5to17 infectious_det_age5to17) (* Ki2_3 S_age5to17 infectious_det_age18to64) (* Ki2_4 S_age5to17 infectious_det_age64to100)))
(reaction exposure_from_detected_age18to64 (S_age18to64) (E_age18to64) (sum (* Ki3_1 S_age18to64 infectious_det_ageU5) (* Ki3_2 S_age18to64 infectious_det_age5to17) (* Ki3_3 S_age18to64 infectious_det_age18to64) (* Ki3_4 S_age18to64 infectious_det_age64to100)))
(reaction exposure_from_detected_age64to100 (S_age64to100) (E_age64to100) (sum (* Ki4_1 S_age64to100 infectious_det_ageU5) (* Ki4_2 S_age64to100 infectious_det_age5to17) (* Ki4_3 S_age64to100 infectious_det_age18to64) (* Ki4_4 S_age64to100 infectious_det_age64to100)))

(reaction exposure_from_undetected_ageU5 (S_ageU5) (E_ageU5) (sum (* Ki1_1 S_ageU5 infectious_undet_ageU5) (* Ki1_2 S_ageU5 infectious_undet_age5to17) (* Ki1_3 S_ageU5 infectious_undet_age18to64) (* Ki1_4 S_ageU5 infectious_undet_age64to100)))
(reaction exposure_from_undetected_age5to17 (S_age5to17) (E_age5to17) (sum (* Ki2_1 S_age5to17 infectious_undet_ageU5) (* Ki2_2 S_age5to17 infectious_undet_age5to17) (* Ki2_3 S_age5to17 infectious_undet_age18to64) (* Ki2_4 S_age5to17 infectious_undet_age64to100)))
(reaction exposure_from_undetected_age18to64 (S_age18to64) (E_age18to64) (sum (* Ki3_1 S_age18to64 infectious_undet_ageU5) (* Ki3_2 S_age18to64 infectious_undet_age5to17) (* Ki3_3 S_age18to64 infectious_undet_age18to64) (* Ki3_4 S_age18to64 infectious_undet_age64to100)))
(reaction exposure_from_undetected_age64to100 (S_age64to100) (E_age64to100) (sum (* Ki4_1 S_age64to100 infectious_undet_ageU5) (* Ki4_2 S_age64to100 infectious_undet_age5to17) (* Ki4_3 S_age64to100 infectious_undet_age18to64) (* Ki4_4 S_age64to100 infectious_undet_age64to100)))
    """
    return exposure_reaction_str


# eval(" 'age,' * 105") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
# (reaction exposure_from_undetected_{} (S_{}) (E_{}) (* Ki S_{} infectious_undet_{}))
# (reaction exposure_from_detected_{} (S_{}) (E_{}) (* Ki S_{} infectious_det_{} reduced_inf_of_det_cases))
def write_reactions(grp):
    grp = str(grp)

    reaction_str = """
(reaction infection_{} (E_{}) (As_{}) (* Kl E_{}))
(reaction symptomatic_{} (E_{}) (Sy_{}) (* Ks E_{}))
(reaction hospitalization_{} (Sy_{}) (H_{}) (* Kh Sy_{}))
(reaction critical_{} (H_{}) (C_{}) (* Kc H_{}))
(reaction death_{} (C_{}) (D_{}) (* Km C_{}))
(reaction recovery_As_{} (As_{}) (RAs_{}) (* Kr As_{}))
(reaction recovery_Sy_{} (Sy_{}) (RSy_{}) (* Kr Sy_{}))
(reaction recovery_H_{} (H_{}) (RH_{}) (* Kr H_{}))
(reaction recovery_C_{} (C_{}) (RC_{}) (* Kr C_{}))
(reaction detect_As_{} (As_{}) (As_det1_{}) (* d_As As_{}))
(reaction detect_symp_{} (Sy_{}) (Sy_det2_{}) (* d_Sy Sy_{}))
(reaction detect_hosp_{} (H_{}) (H_det3_{}) (* d_H H_{}))
(reaction recovery_As_det_{} (As_det1_{}) (RAs_det1_{})  (* Kr As_det1_{}))
(reaction hospitalization_det2_{} (Sy_det2_{}) (H_det2_{}) (* Kh Sy_det2_{}))
(reaction critical_det2_{} (H_det2_{}) (C_det2_{}) (* Kc H_det2_{}))
(reaction death_det2_{} (C_det2_{}) (D_det2_{}) (* Km C_det2_{}))
(reaction recovery_Sy_det2_{} (Sy_det2_{}) (RSy_det2_{}) (* Kr  Sy_det2_{}))
(reaction recovery_H_det2_{} (H_det2_{}) (RH_det2_{}) (* Kr H_det2_{}))
(reaction recovery_C_det2_{} (C_det2_{}) (RC_det2_{}) (* Kr C_det2_{}))
(reaction critical_det3_{} (H_det3_{}) (C_det3_{}) (* Kc H_det3_{}))
(reaction death_det3_{} (C_det3_{}) (D_det3_{}) (* Km C_det3_{}))
(reaction recovery_H_det3_{} (H_det3_{}) (RH_det3_{}) (* Kr H_det3_{}))
(reaction recovery_C_det3_{} (C_det3_{}) (RC_det3_{}) (* Kr C_det3_{}))
""".format(grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp
           )

    reaction_str = reaction_str.replace("  ", " ")
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
age_dic = define_group_dictionary(totalPop = 3715523,   # from Central region service area/NMH catchment
                                      ageGroups = ['ageU5','age5to17','age18to64','age64to100'],
                                      ageGroupScale = [0.062, 0.203, 0.606, 0.129],
                                  initialAs= [1,1,1,1],
                                  initialSy= [0,0,0,0],
                                  initialH= [0,0,0,0])  ## scaled from Chicago population data shared in w7 channel

generate_extended_emodl(grp_dic=age_dic, file_output='age_extendedmodel_covid.emodl')


