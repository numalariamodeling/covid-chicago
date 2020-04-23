import os
import sys

sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')


def write_species(grp):
    grp = str(grp)
    species_str = """
(species S::{grp} @speciesS_{grp}@)
(species As::{grp} 0)
(species E::{grp} 0)
(species As_det1::{grp} 0)
(species P::{grp} 0)
(species Sym::{grp} 0)
(species Sym_det2::{grp} 0)
(species Sys::{grp} 0)
(species Sys_det3::{grp} 0)
(species H1::{grp} 0)
(species H2::{grp} 0)
(species H3::{grp} 0)
(species H1_det3::{grp} 0)
(species H2_det3::{grp} 0)
(species H3_det3::{grp} 0)
(species C2::{grp} 0)
(species C3::{grp} 0)
(species C2_det3::{grp} 0)
(species C3_det3::{grp} 0)
(species D3::{grp} 0)
(species D3_det3::{grp} 0)
(species RAs::{grp} 0)
(species RAs_det1::{grp} 0)
(species RSym::{grp} 0)
(species RSym_det2::{grp} 0)
(species RH1::{grp} 0)
(species RH1_det3::{grp} 0)
(species RC2::{grp} 0)
(species RC2_det3::{grp} 0)
""".format(grp=grp)
    species_str = species_str.replace("  ", " ")
    return (species_str)


def write_observe(grp):
    grp = str(grp)

    observe_str = """
(observe susceptible_{grp} S::{grp})
(observe exposed_{grp} E::{grp})
(observe asymptomatic_{grp} asymptomatic_{grp})
(observe presymptomatic_{grp} P::{grp})
(observe symptomatic_mild_{grp} symptomatic_mild_{grp})
(observe symptomatic_severe_{grp} symptomatic_severe_{grp})
(observe hospitalized_{grp} hospitalized_{grp})
(observe critical_{grp} critical_{grp})
(observe deaths_{grp} deaths_{grp})
(observe recovered_{grp} recovered_{grp})

(observe asymp_cumul_{grp} (+ asymptomatic_{grp} RAs::{grp} RAs_det1::{grp} ))
(observe asymp_det_cumul_{grp} (+ As_det1::{grp} RAs_det1::{grp}))
(observe symp_mild_cumul_{grp} (+ symptomatic_mild_{grp} RSym::{grp} RSym_det2::{grp}))
(observe symp_mild_det_cumul_{grp} (+ RSym_det2::{grp} Sym_det2::{grp}))
(observe symp_severe_cumul_{grp} (+ symptomatic_severe_{grp} hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(observe symp_severe_det_cumul_{grp} (+ Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(observe hosp_cumul_{grp} (+ hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(observe hosp_det_cumul_{grp} (+ H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(observe crit_cumul_{grp} (+ deaths_{grp} critical_{grp} RC2::{grp} RC2_det3::{grp}))
(observe crit_det_cumul_{grp} (+ C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RC2_det3::{grp}))
(observe crit_det_{grp} (+ C2_det3::{grp} C3_det3::{grp}))
(observe death_det_cumul_{grp} D3_det3::{grp} )
(observe detected_cumul_{grp} (+ (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} C2_det3::{grp} C3_det3::{grp}) RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp} D3_det3::{grp}))

(observe detected_{grp} (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(observe infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
""".format(grp=grp)
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


def write_functions(grp):
    grp = str(grp)
    functions_str = """
(func asymptomatic_{grp}  (+ As::{grp} As_det1::{grp}))
(func symptomatic_mild_{grp}  (+ Sym::{grp} Sym_det2::{grp}))
(func symptomatic_severe_{grp}  (+ Sys::{grp} Sys_det3::{grp}))
(func hospitalized_{grp}  (+ H1::{grp} H2::{grp} H3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp}))
(func critical_{grp} (+ C2::{grp} C3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func deaths_{grp} (+ D3::{grp} D3_det3::{grp}))
(func recovered_{grp} (+ RAs::{grp} RSym::{grp} RH1::{grp} RC2::{grp} RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func infectious_undet_{grp} (+ As::{grp} P::{grp} Sym::{grp} Sys::{grp} H1::{grp} H2::{grp} H3::{grp} C2::{grp} C3::{grp}))
(func infectious_det_{grp} (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} ))

(func asymp_cumul_{grp} (+ asymptomatic_{grp} RAs::{grp} RAs_det1::{grp} ))
(func asymp_det_cumul_{grp} (+ As_det1::{grp} RAs_det1::{grp}))
(func symp_mild_cumul_{grp} (+ symptomatic_mild_{grp} RSym::{grp} RSym_det2::{grp}))
(func symp_mild_det_cumul_{grp} (+ RSym_det2::{grp} Sym_det2::{grp}))
(func symp_severe_cumul_{grp} (+ symptomatic_severe_{grp} hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func symp_severe_det_cumul_{grp} (+ Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func hosp_cumul_{grp} (+ hospitalized_{grp} critical_{grp} deaths_{grp} RH1::{grp} RC2::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func hosp_det_cumul_{grp} (+ H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RH1_det3::{grp} RC2_det3::{grp}))
(func crit_cumul_{grp} (+ deaths_{grp} critical_{grp} RC2::{grp} RC2_det3::{grp}))
(func crit_det_cumul_{grp} (+ C2_det3::{grp} C3_det3::{grp} D3_det3::{grp} RC2_det3::{grp}))
(func crit_det_{grp} (+ C2_det3::{grp} C3_det3::{grp}))
(func detected_cumul_{grp} (+ (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} C2_det3::{grp} C3_det3::{grp}) RAs_det1::{grp} RSym_det2::{grp} RH1_det3::{grp} RC2_det3::{grp} D3_det3::{grp}))
(func death_det_cumul_{grp} D3_det3::{grp} )

(func detected_{grp} (+ As_det1::{grp} Sym_det2::{grp} Sys_det3::{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))
(func infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3::{grp} H2_det3::{grp} H3_det3::{grp} C2_det3::{grp} C3_det3::{grp}))


""".format(grp=grp)
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
;(param Ki @Ki@)
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
"""

    params_str = params_str.replace("  ", " ")

    return (params_str)



def write_grp_params(grp):
    grp = str(grp)
    params_str = """
(param Ki_{grp} @Ki_{grp}@)

(time-event time_infection_import @time_infection_import_{grp}@ ((As::{grp} @initialAs_{grp}@) (S::{grp} (- S::{grp} @initialAs_{grp}@))))

(param Ki_red1_{grp} (* Ki_{grp} @social_multiplier_1_{grp}@))
(param Ki_red2_{grp} (* Ki_{grp} @social_multiplier_2_{grp}@))
(param Ki_red3_{grp} (* Ki_{grp} @social_multiplier_3_{grp}@))



(time-event socialDistance_no_large_events_start @socialDistance_time1@ ((Ki_{grp} Ki_red1_{grp})))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki_{grp} Ki_red2_{grp})))
(time-event socialDistance_start @socialDistance_time3@ ((Ki_{grp} Ki_red3_{grp})))
""".format(grp=grp)
    params_str = params_str.replace("  ", " ")

    return (params_str)



def write_N_population(grpList):
    stringAll = ""
    for key in grpList:
        string1 = """\n(param N_{grp} (+ @speciesS_{grp}@ @initialAs_{grp}@) )""".format(grp=key)
        stringAll = stringAll + string1

    string2 = "\n(param N_regionAll (+ " + repeat_string_by_grp('N_', grpList) + "))"
    stringAll = stringAll + string2

    return (stringAll)


def repeat_string_by_grp(fixedstring, grpList):
    stringAll = ""
    for grp in grpList:
        temp_string = " " + fixedstring + grp
        stringAll = stringAll + temp_string

    return stringAll


def write_regionAll(grpList):
    obs_regionAll_str = ""
    obs_regionAll_str = obs_regionAll_str + "\n(observe susceptible_regionAll (+ " + repeat_string_by_grp('S::',
                                                                                                          grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe exposed_regionAll (+ " + repeat_string_by_grp('E::',
                                                                                                      grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe asymptomatic_regionAll (+ " + repeat_string_by_grp(
        'asymptomatic_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe presymptomatic_regionAll (+ " + repeat_string_by_grp('P::',
                                                                                                             grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symptomatic_mild_regionAll (+ " + repeat_string_by_grp(
        'symptomatic_mild_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symptomatic_severe_regionAll (+ " + repeat_string_by_grp(
        'symptomatic_severe_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe hospitalized_regionAll (+ " + repeat_string_by_grp(
        'hospitalized_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe critical_regionAll (+ " + repeat_string_by_grp('critical_',
                                                                                                       grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe deaths_regionAll (+ " + repeat_string_by_grp('deaths_',
                                                                                                     grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe recovered_regionAll (+ " + repeat_string_by_grp('recovered_',
                                                                                                        grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe asymp_cumul_regionAll (+ " + repeat_string_by_grp(
        'asymp_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe asymp_det_cumul_regionAll (+ " + repeat_string_by_grp(
        'asymp_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symp_mild_cumul_regionAll (+ " + repeat_string_by_grp(
        'symp_mild_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symp_mild_det_cumul_regionAll (+ " + repeat_string_by_grp(
        'symp_mild_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symp_severe_cumul_regionAll (+ " + repeat_string_by_grp(
        'symp_severe_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symp_severe_det_cumul_regionAll  (+ " + repeat_string_by_grp(
        'symp_severe_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe hosp_cumul_regionAll (+ " + repeat_string_by_grp('hosp_cumul_',
                                                                                                         grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe hosp_det_cumul_regionAll (+ " + repeat_string_by_grp(
        'hosp_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe crit_cumul_regionAll (+ " + repeat_string_by_grp('crit_cumul_',
                                                                                                         grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe crit_det_cumul_regionAll (+ " + repeat_string_by_grp(
        'crit_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe crit_det_regionAll (+ " + repeat_string_by_grp('crit_det_',
                                                                                                       grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe detected_cumul_regionAll (+ " + repeat_string_by_grp(
        'detected_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe death_det_cumul_regionAll (+ " + repeat_string_by_grp(
        'death_det_cumul_', grpList) + "))"

    obs_regionAll_str = obs_regionAll_str + "\n(func infectious_det_regionAll (+ " + repeat_string_by_grp(
        'infectious_det_', grpList) + "))"

    obs_regionAll_str = obs_regionAll_str + "\n(func infectious_undet_regionAll (+ " + repeat_string_by_grp(
        'infectious_undet_', grpList) + "))"

    obs_regionAll_str = obs_regionAll_str + "\n(observe infectious_det_regionAll infectious_det_regionAll)"

    obs_regionAll_str = obs_regionAll_str + "\n(observe infectious_undet_regionAll infectious_undet_regionAll)"


    return (obs_regionAll_str)


# Reaction without contact matrix
def write_reactions(grp):
    grp = str(grp)

    reaction_str = """
(reaction exposure_{grp}   (S::{grp}) (E::{grp}) (* Ki_{grp} S::{grp} (/  (+ infectious_undet_regionAll (* infectious_det_regionAll reduced_inf_of_det_cases)) N_regionAll )))
(reaction infection_asymp_undet_{grp}  (E::{grp})   (As::{grp})   (* Kl E::{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (E::{grp})   (As_det1::{grp})   (* Kl E::{grp} d_As))
(reaction presymptomatic_{grp} (E::{grp})   (P::{grp})   (* Ks E::{grp}))
(reaction mild_symptomatic_undet_{grp} (P::{grp})  (Sym::{grp}) (* Ksym P::{grp} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{grp} (P::{grp})  (Sym_det2::{grp}) (* Ksym P::{grp} d_Sym))
(reaction severe_symptomatic_undet_{grp} (P::{grp})  (Sys::{grp})  (* Ksys P::{grp} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{grp} (P::{grp})  (Sys_det3::{grp})  (* Ksys P::{grp} d_Sys))

(reaction hospitalization_1_{grp}   (Sys::{grp})   (H1::{grp})   (* Kh1 Sys::{grp}))
(reaction hospitalization_2_{grp}   (Sys::{grp})   (H2::{grp})   (* Kh2 Sys::{grp}))
(reaction hospitalization_3_{grp}   (Sys::{grp})   (H3::{grp})   (* Kh3 Sys::{grp}))
(reaction critical_2_{grp}   (H2::{grp})   (C2::{grp})   (* Kc H2::{grp}))
(reaction critical_3_{grp}   (H3::{grp})   (C3::{grp})   (* Kc H3::{grp}))
(reaction death_{grp}   (C3::{grp})   (D3::{grp})   (* Km C3::{grp}))

(reaction recovery_As_{grp}   (As::{grp})   (RAs::{grp})   (* Kr_a As::{grp}))
(reaction recovery_Sym_{grp}   (Sym::{grp})   (RSym::{grp})   (* Kr_m  Sym::{grp}))
(reaction recovery_H1_{grp}   (H1::{grp})   (RH1::{grp})   (* Kr_h H1::{grp}))
(reaction recovery_C2_{grp}   (C2::{grp})   (RC2::{grp})   (* Kr_c C2::{grp}))

(reaction recovery_As_det_{grp} (As_det1::{grp})   (RAs_det1::{grp})   (* Kr_a As_det1::{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3::{grp})   (H1_det3::{grp})   (* Kh1 Sys_det3::{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3::{grp})   (H2_det3::{grp})   (* Kh2 Sys_det3::{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3::{grp})   (H3_det3::{grp})   (* Kh3 Sys_det3::{grp}))
(reaction critical_2_det2_{grp}   (H2_det3::{grp})   (C2_det3::{grp})   (* Kc H2_det3::{grp}))
(reaction critical_3_det2_{grp}   (H3_det3::{grp})   (C3_det3::{grp})   (* Kc H3_det3::{grp}))
(reaction death_det3_{grp}   (C3_det3::{grp})   (D3_det3::{grp})   (* Km C3_det3::{grp}))

(reaction recovery_Sym_det2_{grp}   (Sym_det2::{grp})   (RSym_det2::{grp})   (* Kr_m  Sym_det2::{grp}))
(reaction recovery_H1_det3_{grp}   (H1_det3::{grp})   (RH1_det3::{grp})   (* Kr_h H1_det3::{grp}))
(reaction recovery_C2_det3_{grp}   (C2_det3::{grp})   (RC2_det3::{grp})   (* Kr_c C2_det3::{grp}))
""".format(grp=grp)

    reaction_str = reaction_str.replace("  ", " ")
    return (reaction_str)


###stringing all of my functions together to make the file:

def generate_locale_emodl_extended(grp, file_output):
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
    param_string = ""
    reaction_string = ""
    functions_string = ""
    total_string = total_string + header_str

    for key in grp:
        total_string = total_string + "\n(locale site-{})\n".format(key)
        total_string = total_string + "(set-locale site-{})\n".format(key)
        total_string = total_string +  write_species(key)
        functions = write_functions(key)
        observe_string = observe_string + write_observe(key)
        reaction_string = reaction_string + write_reactions(key)
        functions_string = functions_string + functions
        param_string = param_string + write_grp_params(key) 
        
    param_string =  write_params() + param_string  +  write_N_population(grp)
    functions_string = functions_string + write_regionAll(grp)

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + reaction_string + '\n\n' + footer_str
    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


def generate_locale_cfg(cfg_filename, nruns, filepath):
    # generate the CFG file
    cfg = """{
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

    file1 = open(filepath, "w")
    file1.write(cfg)
    file1.close()


if __name__ == '__main__':
    ems_grp = ['EMS_1', 'EMS_2', 'EMS_3', 'EMS_4', 'EMS_5', 'EMS_6', 'EMS_7', 'EMS_8', 'EMS_9', 'EMS_10', 'EMS_11']
    generate_locale_emodl_extended(grp=ems_grp,
                                   file_output=os.path.join(emodl_dir, 'extendedmodel_cobey_locale_EMS.emodl'))


