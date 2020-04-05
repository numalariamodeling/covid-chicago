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

def define_group_dictionary(totalPop, countyGroups,  countyGroupScale, initialAs) :
    county_dic = {}
    for i, grp in enumerate(countyGroups):
        print(i, grp)
        county_dic[grp] = [totalPop * countyGroupScale[i], initialAs[i]]
    return county_dic


def write_species_init(county_dic, county):
    S = "(species S::{} {})".format(county, county_dic[county][0])
    As = "(species As::{} {})".format(county, county_dic[county][1])
    species_init_str = S + '\n' + As 
    species_init_str = species_init_str.replace("  ", " ")
    return (species_init_str)


def write_species(county):
    county = str(county)
    species_str = """
(species E::{} 0)
(species As_det1::{} 0)
(species P::{} 0)
(species Sym::{} 0)
(species Sym_det2::{} 0)
(species Sys::{} 0)
(species Sys_det3::{} 0)
(species H1::{} 0)
(species H2::{} 0)
(species H3::{} 0)
(species H1_det3::{} 0)
(species H2_det3::{} 0)
(species H3_det3::{} 0)
(species C2::{} 0)
(species C3::{} 0)
(species C2_det3::{} 0)
(species C3_det3::{} 0)
(species D3::{} 0)
(species D3_det3::{} 0)
(species RAs::{} 0)
(species RAs_det1::{} 0)
(species RSym::{} 0)
(species RSym_det2::{} 0)
(species RH1::{} 0)
(species RH1_det3::{} 0)
(species RC2::{} 0)
(species RC2_det3::{} 0)
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
(observe asymptomatic_{} asymptomatic_{})
(observe presymptomatic_{} P::{})
(observe symptomatic_mild_{} symptomatic_mild_{})
(observe symptomatic_severe_{} symptomatic_severe_{})
(observe hospitalized_{} hospitalized_{})
(observe critical_{} critical_{})
(observe deaths_{} deaths_{})
(observe recovered_{} recovered_{})
(observe asymp_cumul_{} (+ asymptomatic_{} RAs::{} RAs_det1::{} ))
(observe asymp_det_cumul_{} (+ As_det1::{} RAs_det1::{}))
(observe symp_mild_cumul_{} (+ symptomatic_mild_{} RSym::{} RSym_det2::{}))
(observe symp_severe_cumul_{} (+ symptomatic_severe_{} hospitalized_{} critical_{} deaths_{} RH1::{} RC2::{} RH1_det3::{} RC2_det3::{}))
(observe hosp_cumul_{} (+ hospitalized_{} critical_{} deaths_{} RH1::{} RC2::{} RH1_det3::{} RC2_det3::{}))
(observe hosp_det_cumul_{} (+ H1_det3::{} H2_det3::{} H3_det3::{} C2_det3::{} C3_det3::{} D3_det3::{} RH1_det3::{} RC2_det3::{}))
(observe crit_cumul_{} (+ deaths_{} critical_{} RC2::{} RC2_det3::{}))
(observe detected_cumul_{} (+ (+ As_det1::{} Sym_det2::{} Sys_det3::{} H1_det3::{} H2_det3::{} C2_det3::{} C3_det3::{}) RAs_det1::{} RSym_det2::{} RH1_det3::{} RC2_det3::{} D3_det3::{}))
(observe detected_{} (+ As_det1::{} Sym_det2::{} Sys_det3::{} H1_det3::{} H2_det3::{} H3_det3::{} C2_det3::{} C3_det3::{}))
(observe infected_{} (+ infectious_det_{} infectious_undet_{} H1_det3::{} H2_det3::{} H3_det3::{} C2_det3::{} C3_det3::{}))
""".format(county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county, county
           )
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)

def write_functions(county):
    county = str(county)
    functions_str = """
(func asymptomatic_{}  (+ As::{} As_det1::{}))
(func symptomatic_mild_{}  (+ Sym::{} Sym_det2::{}))
(func symptomatic_severe_{}  (+ Sys::{} Sys_det3::{}))
(func hospitalized_{}  (+ H1::{} H2::{} H3::{} H1_det3::{} H2_det3::{} H3_det3::{}))
(func critical_{} (+ C2::{} C3::{} C2_det3::{} C3_det3::{}))
(func deaths_{} (+ D3::{} D3_det3::{}))
(func recovered_{} (+ RAs::{} RSym::{} RH1::{} RC2::{} RAs_det1::{} RSym_det2::{} RH1_det3::{} RC2_det3::{}))
(func infectious_undet_{} (+ As::{} P::{} Sym::{} Sys::{} H1::{} H2::{} H3::{} C2::{} C3::{}))
(func infectious_det_{} (+ As_det1::{} Sym_det2::{} Sys_det3::{} ))
""".format(county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county
           )
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

# Reaction without contact matrix
def write_reactions(county):
    county = str(county)

    reaction_str = """
(reaction exposure_{}   (S::{}) (E::{}) (* Ki S::{} (+ infectious_undet_{} (* infectious_det_{} reduced_inf_of_det_cases))))
(reaction infection_asymp_undet_{}  (E::{})   (As::{})   (* Kl E::{} (- 1 d_As)))
(reaction infection_asymp_det_{}  (E::{})   (As_det1::{})   (* Kl E::{} d_As))
(reaction presymptomatic_{} (E::{})   (P::{})   (* Ks E::{}))
(reaction mild_symptomatic_undet_{} (P::{})  (Sym::{}) (* Ksym P::{} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{} (P::{})  (Sym_det2::{}) (* Ksym P::{} d_Sym))
(reaction severe_symptomatic_undet_{} (P::{})  (Sys::{})  (* Ksys P::{} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{} (P::{})  (Sys_det3::{})  (* Ksys P::{} d_Sys))

(reaction hospitalization_1_{}   (Sys::{})   (H1::{})   (* Kh1 Sys::{}))
(reaction hospitalization_2_{}   (Sys::{})   (H2::{})   (* Kh2 Sys::{}))
(reaction hospitalization_3_{}   (Sys::{})   (H3::{})   (* Kh3 Sys::{}))
(reaction critical_2_{}   (H2::{})   (C2::{})   (* Kc H2::{}))
(reaction critical_3_{}   (H3::{})   (C3::{})   (* Kc H3::{}))
(reaction death_{}   (C3::{})   (D3::{})   (* Km C3::{}))

(reaction recovery_As_{}   (As::{})   (RAs::{})   (* Kr_a As::{}))
(reaction recovery_Sym_{}   (Sym::{})   (RSym::{})   (* Kr_m  Sym::{}))
(reaction recovery_H1_{}   (H1::{})   (RH1::{})   (* Kr_h H1::{}))
(reaction recovery_C2_{}   (C2::{})   (RC2::{})   (* Kr_c C2::{}))

(reaction detect_As_{} (As::{}) (As_det1::{}) (* d_As As::{}))
(reaction detect_symp_{} (Sym::{}) (Sym_det2::{}) (* d_Sym Sym::{}))
(reaction detect_hosp_{} (Sys::{}) (Sys_det3::{}) (* d_Sys Sys::{}))

(reaction recovery_As_det_{} (As_det1::{})   (RAs_det1::{})   (* Kr_a As_det1::{}))

(reaction hospitalization_1_det_{}   (Sys_det3::{})   (H1_det3::{})   (* Kh1 Sys_det3::{}))
(reaction hospitalization_2_det_{}   (Sys_det3::{})   (H2_det3::{})   (* Kh2 Sys_det3::{}))
(reaction hospitalization_3_det_{}   (Sys_det3::{})   (H3_det3::{})   (* Kh3 Sys_det3::{}))
(reaction critical_2_det2_{}   (H2_det3::{})   (C2_det3::{})   (* Kc H2_det3::{}))
(reaction critical_3_det2_{}   (H3_det3::{})   (C3_det3::{})   (* Kc H3_det3::{}))
(reaction death_det3_{}   (C3_det3::{})   (D3_det3::{})   (* Km C3_det3::{}))

(reaction recovery_Sym_det2_{}   (Sym_det2::{})   (RSym_det2::{})   (* Kr_m  Sym_det2::{}))
(reaction recovery_H1_det3_{}   (H1_det3::{})   (RH1_det3::{})   (* Kr_h H1_det3::{}))
(reaction recovery_C2_det3_{}   (C2_det3::{})   (RC2_det3::{})   (* Kr_c C2_det3::{}))
""".format(county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county, county,
           county, county, county, county, county, county, county, county, county, county, county, county
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
                                      countyGroups=['EMS1','EMS2','EMS3'],
                                      countyGroupScale=[0.25, 0.25, 0.25],     ## scaled population per area for testing only, put in EMS true population or true proportions
                                      initialAs=[10,0,0]  # homogeneous distribution of inital cases ? Or "hot spot" in one area?
                                      )


    generate_locale_emodl_extended(county_dic=county_dic, file_output=os.path.join('locale_extendedmodel_covid_test.emodl'))


