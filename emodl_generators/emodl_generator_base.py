import os
import sys
import re

sys.path.append('../')
from load_paths import load_box_paths

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()
emodl_dir = os.path.join(git_dir, 'emodl')


def write_species(grp):
    grp = str(grp)
    species_str = """
(species S @speciesS@)
(species As 0)
(species E 0)
(species As_det1 0)
(species P 0)
(species Sym 0)
(species Sym_det2 0)
(species Sys 0)
(species Sys_det3 0)
(species H1 0)
(species H2 0)
(species H3 0)
(species H1_det3 0)
(species H2_det3 0)
(species H3_det3 0)
(species C2 0)
(species C3 0)
(species C2_det3 0)
(species C3_det3 0)
(species D3 0)
(species D3_det3 0)
(species RAs 0)
(species RAs_det1 0)
(species RSym 0)
(species RSym_det2 0)
(species RH1 0)
(species RH1_det3 0)
(species RC2 0)
(species RC2_det3 0)
""".format(grp=grp)
    species_str = species_str.replace("  ", " ")
    return (species_str)


def sub(x):
    xout = re.sub('_', '-', str(x), count=1)
    return (xout)


def write_observe(grp):
    grp = str(grp)
    grpout = sub(grp)

    observe_str = """
(observe susceptible S)
(observe exposed E)
(observe asymptomatic asymptomatic)
(observe presymptomatic P)
(observe symptomatic_mild symptomatic_mild)
(observe symptomatic_severe symptomatic_severe)
(observe hospitalized hospitalized)
(observe critical critical)
(observe deaths deaths)
(observe recovered recovered)

(observe asymp_cumul (+ asymptomatic RAs RAs_det1 ))
(observe asymp_det_cumul (+ As_det1 RAs_det1))
(observe symp_mild_cumul (+ symptomatic_mild RSym RSym_det2))
(observe symp_mild_det_cumul (+ RSym_det2 Sym_det2))
(observe symp_severe_cumul (+ symptomatic_severe hospitalized critical deaths RH1 RC2 RH1_det3 RC2_det3))
(observe symp_severe_det_cumul (+ Sys_det3 H1_det3 H2_det3 H3_det3 C2_det3 C3_det3 D3_det3 RH1_det3 RC2_det3))
(observe hosp_cumul (+ hospitalized critical deaths RH1 RC2 RH1_det3 RC2_det3))
(observe hosp_det_cumul (+ H1_det3 H2_det3 H3_det3 C2_det3 C3_det3 D3_det3 RH1_det3 RC2_det3))
(observe crit_cumul (+ deaths critical RC2 RC2_det3))
(observe crit_det_cumul (+ C2_det3 C3_det3 D3_det3 RC2_det3))
(observe crit_det (+ C2_det3 C3_det3))
(observe death_det_cumul D3_det3 )
(observe detected_cumul (+ (+ As_det1 Sym_det2 Sys_det3 H1_det3 H2_det3 C2_det3 C3_det3) RAs_det1 RSym_det2 RH1_det3 RC2_det3 D3_det3))

(observe detected (+ As_det1 Sym_det2 Sys_det3 H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))
(observe infected (+ infectious_det infectious_undet H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))
""".format(grpout=grpout, grp=grp)
    observe_str = observe_str.replace("  ", " ")
    return (observe_str)


def write_functions(grp):
    grp = str(grp)
    functions_str = """
(func asymptomatic  (+ As As_det1))
(func symptomatic_mild  (+ Sym Sym_det2))
(func symptomatic_severe  (+ Sys Sys_det3))
(func hospitalized  (+ H1 H2 H3 H1_det3 H2_det3 H3_det3))
(func critical (+ C2 C3 C2_det3 C3_det3))
(func deaths (+ D3 D3_det3))
(func recovered (+ RAs RSym RH1 RC2 RAs_det1 RSym_det2 RH1_det3 RC2_det3))
(func infectious_undet (+ As P Sym Sys H1 H2 H3 C2 C3))
(func infectious_det (+ As_det1 Sym_det2 Sys_det3 ))

(func asymp_cumul (+ asymptomatic RAs RAs_det1 ))
(func asymp_det_cumul (+ As_det1 RAs_det1))
(func symp_mild_cumul (+ symptomatic_mild RSym RSym_det2))
(func symp_mild_det_cumul (+ RSym_det2 Sym_det2))
(func symp_severe_cumul (+ symptomatic_severe hospitalized critical deaths RH1 RC2 RH1_det3 RC2_det3))
(func symp_severe_det_cumul (+ Sys_det3 H1_det3 H2_det3 H3_det3 C2_det3 C3_det3 D3_det3 RH1_det3 RC2_det3))
(func hosp_cumul (+ hospitalized critical deaths RH1 RC2 RH1_det3 RC2_det3))
(func hosp_det_cumul (+ H1_det3 H2_det3 H3_det3 C2_det3 C3_det3 D3_det3 RH1_det3 RC2_det3))
(func crit_cumul (+ deaths critical RC2 RC2_det3))
(func crit_det_cumul (+ C2_det3 C3_det3 D3_det3 RC2_det3))
(func crit_det (+ C2_det3 C3_det3))
(func detected_cumul (+ (+ As_det1 Sym_det2 Sys_det3 H1_det3 H2_det3 C2_det3 C3_det3) RAs_det1 RSym_det2 RH1_det3 RC2_det3 D3_det3))
(func death_det_cumul D3_det3 )

(func detected (+ As_det1 Sym_det2 Sys_det3 H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))
(func infected (+ infectious_det infectious_undet H1_det3 H2_det3 H3_det3 C2_det3 C3_det3))


""".format(grp=grp)
    functions_str = functions_str.replace("  ", "")
    return (functions_str)


###
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

(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))  
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@)))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@))) 
"""

    params_str = params_str.replace("  ", " ")

    return (params_str)


def write_N_population(grpList):
    stringAll = ""
    for key in grpList:
        string1 = """\n(param N (+ @speciesS@ @initialAs@) )""".format(grp=key)
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
    obs_regionAll_str = obs_regionAll_str + "\n(observe susceptible_regionAll (+ " + repeat_string_by_grp('S_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe exposed_regionAll (+ " + repeat_string_by_grp('E_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe asymptomatic_regionAll (+ " + repeat_string_by_grp('asymptomatic_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe presymptomatic_regionAll (+ " + repeat_string_by_grp('P_',    grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symptomatic_mild_regionAll (+ " + repeat_string_by_grp( 'symptomatic_mild_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symptomatic_severe_regionAll (+ " + repeat_string_by_grp('symptomatic_severe_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe hospitalized_regionAll (+ " + repeat_string_by_grp( 'hospitalized_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe critical_regionAll (+ " + repeat_string_by_grp('critical_',  grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe deaths_regionAll (+ " + repeat_string_by_grp('deaths_',   grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe recovered_regionAll (+ " + repeat_string_by_grp('recovered_',   grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe asymp_cumul_regionAll (+ " + repeat_string_by_grp( 'asymp_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe asymp_det_cumul_regionAll (+ " + repeat_string_by_grp('asymp_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symp_mild_cumul_regionAll (+ " + repeat_string_by_grp(  'symp_mild_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symp_mild_det_cumul_regionAll (+ " + repeat_string_by_grp( 'symp_mild_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symp_severe_cumul_regionAll (+ " + repeat_string_by_grp( 'symp_severe_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe symp_severe_det_cumul_regionAll  (+ " + repeat_string_by_grp( 'symp_severe_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe hosp_cumul_regionAll (+ " + repeat_string_by_grp('hosp_cumul_',  grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe hosp_det_cumul_regionAll (+ " + repeat_string_by_grp( 'hosp_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe crit_cumul_regionAll (+ " + repeat_string_by_grp('crit_cumul_',   grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe crit_det_cumul_regionAll (+ " + repeat_string_by_grp(  'crit_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe crit_det_regionAll (+ " + repeat_string_by_grp('crit_det_',    grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe detected_cumul_regionAll (+ " + repeat_string_by_grp( 'detected_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe death_det_cumul_regionAll (+ " + repeat_string_by_grp(    'death_det_cumul_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(func infectious_det_regionAll (+ " + repeat_string_by_grp( 'infectious_det_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(func infectious_undet_regionAll (+ " + repeat_string_by_grp(   'infectious_undet_', grpList) + "))"
    obs_regionAll_str = obs_regionAll_str + "\n(observe infectious_det_regionAll infectious_det_regionAll)"
    obs_regionAll_str = obs_regionAll_str + "\n(observe infectious_undet_regionAll infectious_undet_regionAll)"

    return (obs_regionAll_str)


# Reaction without contact matrix
# (reaction exposure   (S) (E) (* Ki S (/  (+ infectious_undet_regionAll (* infectious_det_regionAll reduced_inf_of_det_cases)) N_regionAll )))

def write_reactions(grp):
    grp = str(grp)

    reaction_str = """
(reaction exposure   (S) (E) (* Ki S (/  (+ infectious_undet (* infectious_det reduced_inf_of_det_cases)) N )))
(reaction infection_asymp_undet  (E)   (As)   (* Kl E (- 1 d_As)))
(reaction infection_asymp_det  (E)   (As_det1)   (* Kl E d_As))
(reaction presymptomatic (E)   (P)   (* Ks E))
(reaction mild_symptomatic_undet (P)  (Sym) (* Ksym P (- 1 d_Sym)))
(reaction mild_symptomatic_det (P)  (Sym_det2) (* Ksym P d_Sym))
(reaction severe_symptomatic_undet (P)  (Sys)  (* Ksys P (- 1 d_Sys)))
(reaction severe_symptomatic_det (P)  (Sys_det3)  (* Ksys P d_Sys))

(reaction hospitalization_1   (Sys)   (H1)   (* Kh1 Sys))
(reaction hospitalization_2   (Sys)   (H2)   (* Kh2 Sys))
(reaction hospitalization_3   (Sys)   (H3)   (* Kh3 Sys))
(reaction critical_2   (H2)   (C2)   (* Kc H2))
(reaction critical_3   (H3)   (C3)   (* Kc H3))
(reaction death   (C3)   (D3)   (* Km C3))

(reaction recovery_As   (As)   (RAs)   (* Kr_a As))
(reaction recovery_Sym   (Sym)   (RSym)   (* Kr_m  Sym))
(reaction recovery_H1   (H1)   (RH1)   (* Kr_h H1))
(reaction recovery_C2   (C2)   (RC2)   (* Kr_c C2))

(reaction recovery_As_det (As_det1)   (RAs_det1)   (* Kr_a As_det1))

(reaction hospitalization_1_det   (Sys_det3)   (H1_det3)   (* Kh1 Sys_det3))
(reaction hospitalization_2_det   (Sys_det3)   (H2_det3)   (* Kh2 Sys_det3))
(reaction hospitalization_3_det   (Sys_det3)   (H3_det3)   (* Kh3 Sys_det3))
(reaction critical_2_det2   (H2_det3)   (C2_det3)   (* Kc H2_det3))
(reaction critical_3_det2   (H3_det3)   (C3_det3)   (* Kc H3_det3))
(reaction death_det3   (C3_det3)   (D3_det3)   (* Km C3_det3))

(reaction recovery_Sym_det2   (Sym_det2)   (RSym_det2)   (* Kr_m  Sym_det2))
(reaction recovery_H1_det3   (H1_det3)   (RH1_det3)   (* Kr_h H1_det3))
(reaction recovery_C2_det3   (C2_det3)   (RC2_det3)   (* Kr_c C2_det3))
""".format(grp=grp)

    reaction_str = reaction_str.replace("  ", " ")
    return (reaction_str)

def write_interventions(grpList, total_string, scenarioName) :

    continuedSIP_str = """
(param Ki_red1 (* Ki @social_multiplier_1@))
(param Ki_red2 (* Ki @social_multiplier_2@))
(param Ki_red3 (* Ki @social_multiplier_3@))
(time-event socialDistance_no_large_events_start @ socialDistance_time1@ ((Ki Ki_red1)))
(time-event socialDistance_school_closure_start @socialDistance_time2@ ((Ki Ki_red2)))
(time-event socialDistance_start @socialDistance_time3@ ((Ki Ki_red3)))
 """

    interventiopnSTOP_str = """
(param Ki_back (* Ki @backtonormal_multiplier@))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki Ki_back)))
        """

    gradual_reopening_str = """
(param Ki_back1 (* Ki @reopening_multiplier_1@))
(param Ki_back2 (* Ki @reopening_multiplier_2@))
(param Ki_back3 (* Ki @reopening_multiplier_3@))
(param Ki_back4 (* Ki @reopening_multiplier_4@))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki Ki_back1)))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki Ki_back2)))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki Ki_back3)))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki Ki_back4)))
    """

    ### contact tracing not working yet, as P_det is missing in emodl structure
    ### placeholder only
    contactTracing_str = """
(time-event contact_tracing_start @contact_tracing_start_1@ ((d_As d_As_ct1) (d_P d_As_ct1) (d_Sym d_Sym_ct1)))
;(time-event contact_tracing_end @contact_tracing_stop1@ ((d_As @d_As@) (d_P @d_P@) (d_Sym @d_Sym@)))
;(time-event contact_tracing_start @contact_tracing_start_1@ ((S (* S (- 1 d_SQ))) (Q (* S d_SQ))))
;(time-event contact_tracing_end @contact_tracing_stop1@ ((S (+ S Q)) (Q 0)))
        """

    if scenarioName == "interventionStop" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + interventiopnSTOP_str)
    if scenarioName == "gradual_reopening" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + gradual_reopening_str)
    if scenarioName == "contactTracing" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str + contactTracing_str)
    if scenarioName == "continuedSIP" :
        total_string = total_string.replace(';[INTERVENTIONS]', continuedSIP_str)

    return (total_string)



###stringing all of my functions together to make the file:

def generate_locale_emodl_extended(grpList, file_output, add_interventions):
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

    for grp in grpList:
        total_string = total_string + write_species(grp)
        functions = write_functions(grp)
        observe_string = observe_string + write_observe(grp)
        reaction_string = reaction_string + write_reactions(grp)
        functions_string = functions_string + functions
        param_string = param_string


    param_string = write_params() + param_string + write_N_population(grpList)
    functions_string = functions_string + write_regionAll(grpList)
    intervention_string = ";[INTERVENTIONS]"

    total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string +  '\n\n' + reaction_string + '\n\n' + footer_str

    ### Add interventions (optional)
    if add_interventions != None :
        total_string = write_interventions(grpList, total_string, add_interventions)

    print(total_string)
    emodl = open(file_output, "w")  ## again, can make this more dynamic
    emodl.write(total_string)
    emodl.close()
    if (os.path.exists(file_output)):
        print("{} file was successfully created".format(file_output))
    else:
        print("{} file was NOT created".format(file_output))


if __name__ == '__main__':
    no_grp = ['']
    generate_locale_emodl_extended(grpList=no_grp, add_interventions=None,file_output=os.path.join(emodl_dir, 'test_neverSIP.emodl'))
    generate_locale_emodl_extended(grpList=no_grp, add_interventions='continuedSIP', file_output=os.path.join(emodl_dir, 'test_base.emodl'))
    generate_locale_emodl_extended(grpList=no_grp, add_interventions='interventionStop', file_output=os.path.join(emodl_dir, 'test_interventiopnStop.emodl'))
    generate_locale_emodl_extended(grpList=no_grp, add_interventions='gradual_reopening', file_output=os.path.join(emodl_dir, 'test_gradual_reopening.emodl'))