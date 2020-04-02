import os
import subprocess

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

def define_group_dictionary(totalPop, countyGroups,  countyGroupScale, initialAs, initialSy, initialH) :
    county_dic = {}
    for i, grp in enumerate(countyGroups):
        print(i, grp)
        county_dic[grp] = [totalPop * countyGroupScale[i], initialAs[i], initialSy[i], initialH[i]]
    return county_dic


def write_species_init(county_dic, county):
    S = "(species S_{} {})".format(county, county_dic[county][0])
    As = "(species As_{} {})".format(county, county_dic[county][1])
    Sy = "(species Sy_{} {})".format(county, county_dic[county][2])
    H = "(species H_{} {})".format(county, county_dic[county][3])
    species_init_str = S + '\n' + As + '\n' + Sy + '\n' + H + '\n'

    species_init_str = species_init_str.replace("  ", " ")
    return (species_init_str)


def write_species(county):
    county = str(county)
    species_str = """
(species E::{} 0)
(species As_det1::{} 0)
(species Sy_det2::{} 0)
(species H_det2::{} 0)
(species H_det3::{} 0)
(species C::{} 0)
(species C_det2::{} 0)
(species C_det3::{} 0)
(species D::{} 0)
(species D_det2::{} 0)
(species D_det3::{} 0)
(species RAs::{} 0)
(species RAs_det1::{} 0)
(species RSy::{} 0)
(species RSy_det2::{} 0)
(species RH::{} 0)
(species RH_det2::{} 0)
(species RH_det3::{} 0)
(species RC::{} 0)
(species RC_det2::{} 0)
(species RC_det3::{} 0)
""".format(county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county
           )
    species_str = species_str.replace("  ", " ")
    return (species_str)
    

def write_observe(county):
    county = str(county)

    observe_str = """
(observe susceptible_{} S::{})
(observe exposed_{} E::{})
(observe detected_{} (sum As_det1::{} Sy_det2::{} H_det2::{} H_det3::{} C_det2::{} C_det3::{}))
(observe infected_{} (sum As::{} As_det1::{} Sy::{} Sy_det2::{} H::{} H_det2::{} H_det3::{} C::{} C_det2::{} C_det3::{}))
(observe asymptomatic_{} asymptomatic::{})
(observe symptomatic_{} symptomatic::{})
(observe hospitalized_{} hospitalized::{})
(observe critical_{} critical::{})
(observe deaths_{} deaths::{})
(observe recovered_{} recovered::{})
(observe asymp_cumul_{} (+ asymptomatic::{} RAs::{} RAs_det1::{} ))
(observe asymp_det_cumul_{} (+ As_det1::{} RAs_det1::{}))
(observe symp_cumul_{} (+ (sum RSy::{} RH::{} RC::{} RSy_det2::{} RH_det2::{} RH_det3::{} RC_det2::{} RC_det3::{}) deaths::{} critical::{} hospitalized::{} asymptomatic::{}))
(observe symp_det_cumul_{} (+ Sy_det2::{} H_det2::{} RSy_det2::{} C_det2::{} D_det2::{}))
(observe hosp_cumul_{} (+ deaths::{} critical::{} hospitalized::{} RH::{} RH_det2::{} RH_det3::{} RC::{} RC_det2::{} RC_det3::{}))
(observe hosp_det_cumul_{} (+ H_det2::{} H_det3::{} RH_det2::{} RH_det3::{} C_det2::{} C_det3::{} D_det2::{} D_det3::{} RC_det2::{} RC_det3::{}))
(observe crit_cumul_{} (+ deaths::{} critical::{} RC::{} RC_det2::{} RC_det3::{}))
(observe crit_det_cumul_{} (+ C_det2::{} C_det3::{} RC_det2::{} RC_det3::{} D_det2::{} D_det3::{}))
(observe detected_cumul_{} (+ (sum As_det1::{} Sy_det2::{} H_det2::{} H_det3::{} C_det2::{} C_det3::{}) RAs_det1::{} RSy_det2::{} RH_det2::{} RH_det3::{} RC_det2::{} RC_det3::{} D_det2::{} D_det3::{}))
""".format(county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county
           )
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)

def write_functions(county):
    county = str(county)
    functions_str = """
(func asymptomatic_{} (+ As::{} As_det1::{}))
(func symptomatic_{} (+ Sy::{} Sy_det2::{}))
(func hospitalized_{} (sum H::{} H_det2::{} H_det3::{}))
(func critical_{} (sum C::{} C_det2::{} C_det3::{}))
(func deaths_{} (sum D::{} D_det2::{} D_det3::{}))
(func recovered_{} (sum RAs::{} RSy::{} RH::{} RC::{} RAs_det1::{} RSy_det2::{} RH_det2::{} RH_det3::{} RC_det2::{} RC_det3::{}))
(func infectious_undet_{} (+ As::{} Sy::{}))
(func infectious_det_{} (+ As_det1::{} Sy_det2::{}))
""".format(county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county
           )
    functions_str = functions_str.replace("  ", "")
    return (functions_str)

###
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

def write_reactions(county):
    county = str(county)

    reaction_str = """
(reaction exposure_from_undetected_{} (S::{}) (E::{}) (* Ki S::{} infectious_undet::{}))
(reaction exposure_from_detected_{} (S::{}) (E::{}) (* Ki S::{} infectious_det::{} reduced_inf_of_det_cases))
(reaction infection_{} (E::{}) (As::{}) (* Kl E::{}))
(reaction symptomatic_{} (E::{}) (Sy::{}) (* Ks E::{}))
(reaction hospitalization::{} (Sy::{}) (H::{}) (* Kh Sy::{}))
(reaction critical_{} (H::{}) (C::{}) (* Kc H::{}))
(reaction death_{} (C::{}) (D::{}) (* Km C::{}))
(reaction recovery_As_{} (As::{}) (RAs::{}) (* Kr As::{}))
(reaction recovery_Sy_{} (Sy::{}) (RSy::{}) (* Kr Sy::{}))
(reaction recovery_H_{} (H::{}) (RH::{}) (* Kr H::{}))
(reaction recovery_C_{} (C::{}) (RC::{}) (* Kr C::{}))
(reaction detect_As_{} (As::{}) (As_det1::{}) (* d_As As::{}))
(reaction detect_symp_{} (Sy::{}) (Sy_det2::{}) (* d_Sy Sy::{}))
(reaction detect_hosp_{} (H::{}) (H_det3::{}) (* d_H H::{}))
(reaction recovery_As_det_{} (As_det1::{}) (RAs_det1::{})  (* Kr As_det1::{}))
(reaction hospitalization_det2_{} (Sy_det2::{}) (H_det2::{}) (* Kh Sy_det2::{}))
(reaction critical_det2_{} (H_det2::{}) (C_det2::{}) (* Kc H_det2::{}))
(reaction death_det2_{} (C_det2::{}) (D_det2::{}) (* Km C_det2::{}))
(reaction recovery_Sy_det2_{} (Sy_det2::{}) (RSy_det2::{}) (* Kr  Sy_det2::{}))
(reaction recovery_H_det2_{} (H_det2::{}) (RH_det2::{}) (* Kr H_det2::{}))
(reaction recovery_C_det2_{} (C_det2::{}) (RC_det2::{}) (* Kr C_det2::{}))
(reaction critical_det3_{} (H_det3::{}) (C_det3::{}) (* Kc H_det3::{}))
(reaction death_det3_{} (C_det3::{}) (D_det3::{}) (* Km C_det3::{}))
(reaction recovery_H_det3_{} (H_det3::{}) (RH_det3::{}) (* Kr H_det3::{}))
(reaction recovery_C_det3_{} (C_det3::{}) (RC_det3::{}) (* Kr C_det3::{}))
""".format(county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county
           )

    reaction_str = reaction_str.replace("  ", " ")
    return (reaction_str)

###stringing all of my functions together to make the file:

def generate_locale_emodl_extended(county_dic, file_output):
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
        species_init = write_species_init(county_dic, county=key)
        species = write_species(key)
        total_string =total_string + species_init + species

    for key in county_dic.keys():
        observe = write_observe(key)
        reaction = write_reactions(key)
        functions = write_functions(key)
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
       

    
def generate_locale_cfg(cfg_filename,nruns, filepath):
    
    # generate the CFG file
    cfg="""{
        "duration" : 60,
        "runs" : %s,
        "samples" : 60,
        "solver" : "R",
        "output" : {
             "prefix": "%s",
             "headers" : true
        },
        "tau-leaping" : {
            "epsilon" : 0.01
        },
        "r-leaping" : {}
    }""" % (nruns, cfg_filename)

    file1 = open(filepath,"w") 
    file1.write(cfg)
    file1.close()
    
    

if __name__ == '__main__':
    county_dic = define_group_dictionary(totalPop=1000,  # 3715523 from Central region service area/NMH catchment
                                      countyGroups=['EMS1', 'EMS2', 'EMS3', 'EMS4'],
                                      countyGroupScale=[0.062, 0.203, 0.606, 0.129],
                                      initialAs=[1, 1, 1, 1],
                                      initialSy=[0, 0, 0, 0],
                                      initialH=[0, 0, 0,
                                                0])  ## scaled from Chicago population data shared in w7 channel

    generate_locale_emodl_extended(county_dic=county_dic, file_output=os.path.join('locale_extendedmodel_covid.emodl'))


