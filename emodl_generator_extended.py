import os
import subprocess
import csv
from load_paths import load_box_paths

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')

##making the grp dict, assuming each grp is [pop, 0, 1, 0]

def read_group_dictionary(filename='county_dic.csv',grpname ='county', Testmode=True, ngroups=2):
    grp_dic = {}
    with open(os.path.join(git_dir, filename)) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            grp_dic[row[grpname]] = [int(x) for x in row['val_list'].strip('][').split(', ')]

    if Testmode == True:
        grp_dic = {k: grp_dic[k] for k in sorted(grp_dic.keys())[:ngroups]}

    return grp_dic


def write_species_init(grp_dic, grp):
    S = "(species S_{} {})".format(grp, grp_dic[grp][0])
    As = "(species As_{} {})".format(grp, grp_dic[grp][1])
    Sy = "(species Sy_{} {})".format(grp, grp_dic[grp][2])
    H = "(species H_{} {})".format(grp, grp_dic[grp][3])
    species_init_str = S + '\n' + As + '\n' + Sy + '\n' + H + '\n'

    species_init_str = species_init_str.replace("  ", " ")
    return (species_init_str)


### WRITE EMODL CHUNKS
# eval(" 'grp,' * 26") + "grp"   ### need to add the number of grps pasted into format automatically depending on n groups
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


# eval(" 'grp,' * 108") + "grp"   ### need to add the number of grps pasted into format automatically depending on n groups
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
(observe symp_cumul_{} (+ (sum RSy_{} RH_{} RC_{} RSy_det2_{} RH_det2_{} RH_det3_{} RC_det2_{} RC_det3_{}) deaths_{} critical_{} hospitalized_{} symptomatic_{}))
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


# eval(" 'grp,' * 34") + "grp"
def write_functions(grp):
    grp = str(grp)
    functions_str = """
(func asymptomatic_{} (+ As_{} As_det1_{}))
(func symptomatic_{} (+ Sy_{} Sy_det2_{}))
(func hospitalized_{} (sum H_{} H_det2_{} H_det3_{}))
(func critical_{} (sum C_{} C_det2_{} C_det3_{}))
(func deaths_{} (sum D_{} D_det2_{} D_det3_{}))
(func recovered_{} (sum RAs_{} RSy_{} RH_{} RC_{} RAs_det1_{} RSy_det2_{} RH_det2_{} RH_det3_{} RC_det2_{} RC_det3_{}))
(func infectious_undet_{} (+ As_{} Sy_{} H_{} C_{}))
(func infectious_det_{} (+ As_det1_{} Sy_det2_{}))
""".format(grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp, grp, grp, grp,
           grp, grp, grp, grp, grp, grp, grp
           )
    functions_str = functions_str.replace("  ", "")
    return (functions_str)


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


# eval(" 'grp,' * 105") + "grp"   ### need to add the number of grps pasted into format automatically depending on n groups
## note, these lines need to be edited for grp-specific infection rates and contacts
# (reaction exposure_from_undetected_{} (S_{}) (E_{}) (* Ki S_{} infectious_undet_{}))
# (reaction exposure_from_detected_{} (S_{}) (E_{}) (* Ki S_{} infectious_det_{} reduced_inf_of_det_cases))
def write_reactions(grp):
    grp = str(grp)

    reaction_str = """
(reaction exposure_{} (S_{}) (E_{}) (+(* Ki S_{} infectious_undet_{}) (* Ki S_{} infectious_det_{} reduced_inf_of_det_cases)))
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

    for key in grp_dic.keys():
        species_init = write_species_init(grp_dic, grp=key)
        species = write_species(key)
        observe = write_observe(key)
        reaction = write_reactions(key)
        functions = write_functions(key)
        species_init_string = species_init_string + species_init
        species_string = species_string + species
        observe_string = observe_string + observe
        reaction_string = reaction_string + reaction
        functions_string = functions_string + functions
    params = write_params()
    total_string = total_string + '\n\n' + species_init_string + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + params + '\n\n' + reaction_string + '\n\n' + footer_str
    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


# Example run for county (not using locale version, not taking into account mixing between groups)
county_dic = read_group_dictionary(filename='county_dic.csv',grpname="county",Testmode=False)
generate_extended_emodl(grp_dic=county_dic, file_output=os.path.join(emodl_dir, 'county_model_covid.emodl'))

# Example run for age not taking into account mixing between groups!!!
age_dic = read_group_dictionary(filename='age_model/age_dic.csv',grpname="age", Testmode=False)
generate_extended_emodl(grp_dic=age_dic, file_output=os.path.join(emodl_dir, 'age_model_covid.emodl'))

