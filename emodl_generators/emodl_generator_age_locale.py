import os
import itertools
import sys
import re
import json

sys.path.append('../')
from load_paths import load_box_paths

try:
    print(Location)
except NameError:
    if os.name == "posix":
        Location = "NUCLUSTER"
    else:
        Location = "Local"

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)


class covidModel:

    def __init__(self, expandModel='testDelay_AsSymSys', observeLevel='primary', add_interventions='baseline',
                 change_testDelay=None, trigger_channel=None, add_migration=False,fit_params=None, emodl_name=None, git_dir=git_dir):
        self.model = 'agelocale'
        self.age_list = ["age0to9", "age10to19", "age20to29", "age30to39", "age40to49", "age50to59", "age60to69",
                         "age70to100"]
        self.region_list = ['EMS_1', 'EMS_2', 'EMS_3', 'EMS_4', 'EMS_5', 'EMS_6', 'EMS_7', 'EMS_8', 'EMS_9', 'EMS_10',
                            'EMS_11']
        self.travelspeciesList = ["S", "E", "As", "P"]
        self.expandModel = expandModel
        self.add_migration = add_migration
        self.observeLevel = observeLevel
        self.add_interventions = add_interventions
        self.change_testDelay = change_testDelay
        self.trigger_channel = trigger_channel
        self.emodl_name = emodl_name
        self.emodl_dir = os.path.join(git_dir, 'emodl')
        self.age_region_pop = {
            'EMS_1': [{"age0to9": 78641, "age10to19": 91701, "age20to29": 94681, "age30to39": 89371, "age40to49": 92396,
                       "age50to59": 110878, "age60to69": 92988, "age70to100": 89076}],
            'EMS_2': [
                {"age0to9": 114210, "age10to19": 132626, "age20to29": 150792, "age30to39": 141161, "age40to49": 140827
                    , "age50to59": 170321, "age60to69": 143642, "age70to100": 135817}],
            'EMS_3': [{"age0to9": 57069, "age10to19": 71489, "age20to29": 76506, "age30to39": 71437, "age40to49": 79844,
                       "age50to59": 101522, "age60to69": 82573, "age70to100": 81032}],
            'EMS_4': [{"age0to9": 72063, "age10to19": 84167, "age20to29": 89843, "age30to39": 88706, "age40to49": 89248,
                       "age50to59": 110692, "age60to69": 87058, "age70to100": 79757}],
            'EMS_5': [{"age0to9": 41533, "age10to19": 48068, "age20to29": 55005, "age30to39": 48713, "age40to49": 49212,
                       "age50to59": 64576, "age60to69": 54930, "age70to100": 57281}],
            'EMS_6': [
                {"age0to9": 78524, "age10to19": 92005, "age20to29": 119387, "age30to39": 96035, "age40to49": 94670,
                 "age50to59": 117353, "age60to69": 99559, "age70to100": 94750}],
            'EMS_7': [
                {"age0to9": 208260, "age10to19": 251603, "age20to29": 217013, "age30to39": 238956, "age40to49": 251248,
                 "age50to59": 280849, "age60to69": 206843, "age70to100": 171112}],
            'EMS_8': [
                {"age0to9": 187495, "age10to19": 218993, "age20to29": 204630, "age30to39": 235119, "age40to49": 233866,
                 "age50to59": 258661, "age60to69": 190207, "age70to100": 154577}],
            'EMS_9': [
                {"age0to9": 223250, "age10to19": 259507, "age20to29": 232036, "age30to39": 274367, "age40to49": 284363,
                 "age50to59": 307266, "age60to69": 221915, "age70to100": 177803}],
            'EMS_10': [
                {"age0to9": 113783, "age10to19": 138714, "age20to29": 118833, "age30to39": 134124, "age40to49": 147069,
                 "age50to59": 166857, "age60to69": 127055, "age70to100": 111866}],
            'EMS_11': [
                {"age0to9": 326312, "age10to19": 330144, "age20to29": 432323, "age30to39": 457425, "age40to49": 349783,
                 "age50to59": 347788, "age60to69": 270747, "age70to100": 230158}]
        }
        ## Earliest start date
        self.age_region_initialInfect = {
            'EMS_1': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_2': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_3': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_4': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_5': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_6': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_7': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_8': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_9': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_10': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                        "age60to69": 0, "age70to100": 0}],
            'EMS_11': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                        "age60to69": 0, "age70to100": 0}]
        }
        ## Later start dates for other EMS regions
        self.age_region_importedInfect = {
            'EMS_1': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_2': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_3': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_4': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_5': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_6': [{"age0to9": 0, "age10to19": 0, "age20to29": 0, "age30to39": 0, "age40to49": 0, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_7': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_8': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_9': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                       "age60to69": 0, "age70to100": 0}],
            'EMS_10': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                        "age60to69": 0, "age70to100": 0}],
            'EMS_11': [{"age0to9": 0, "age10to19": 0, "age20to29": 3, "age30to39": 3, "age40to49": 4, "age50to59": 0,
                        "age60to69": 0, "age70to100": 0}]
        }

    def write_N_population(self):
        regionList = self.region_list
        ageList = self.age_list
        pop_dic = self.age_region_pop
        stringAll = ""
        for age, region in [(x, y) for x in ageList for y in regionList]:
            string1 = """\n(param N_{age}_{region} {age_reg_pop} )""".format(age=age, region=region,
                                                                             age_reg_pop=pop_dic[region][0][age])
            stringAll = stringAll + string1

        string2 = ""
        for age_i in ageList:
            temp_str = "\n(param N_" + age_i + " (+ " + covidModel.repeat_string_by_grp(fixedstring='N_' + age_i + '_',
                                                                                        grpList1=regionList,
                                                                                        grpList2=None) + "))"
            string2 = string2 + temp_str

        ### Change order to N_age_region, fixedstring or loop needs to be separated
        # string3 = ""
        # for region_i in regionList:
        #  temp_str = "\n(param N_" + region_i + " (+ " + covidModel.repeat_string_by_grp(fixedstring='N_' + region_i + '_', grpList1=ageList, grpList2=None) + "))"
        #  string3 = string3 + temp_str

        string4 = "\n(param N_All (+ " + covidModel.repeat_string_by_grp('N_', ageList, regionList) + "))"

        stringAll = stringAll + "\n" + string2 + "\n" + string4  # + string3 + "\n"

        return (stringAll)

    def write_Ki_timevents(self, age, region):
        import_dic = self.age_region_initialInfect
        import_dic2 = self.age_region_importedInfect
        params_str = """
(time-event time_infection_import @time_infection_import_{region}@ ((As_{age}::{region} {age_reg_import}) (S_{age}::{region} (- S_{age}::{region} {age_reg_import}))))
    """.format(age=age, region=region, age_reg_import=import_dic2[region][0][age])
        params_str = params_str.replace("  ", " ")

        return params_str

    def set_population(self, age, region):
        import_dic = self.age_region_initialInfect
        import_dic2 = self.age_region_importedInfect
        pop_dic = self.age_region_pop
        initial_population_str = """
(species S_{age}::{region} {age_reg_pop})
(species As_{age}::{region} {age_reg_infect})
    """.format(age=age,
               region=region,
               age_reg_pop=pop_dic[region][0][age],
               age_reg_infect=import_dic[region][0][age])
        return initial_population_str

    def write_species(self, age, region):

        species_str = """
(species E_{age}::{region} 0)
(species As_det1_{age}::{region} 0)
(species P_{age}::{region} 0)
(species P_det_{age}::{region} 0)
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

        expand_testDelay_SymSys_str = """
(species Sym_preD_{age}::{region} 0)
(species Sys_preD_{age}::{region} 0)
    """.format(age=age, region=region)

        expand_testDelay_AsSymSys_str = """
(species As_preD_{age}::{region} 0)
(species Sym_preD_{age}::{region} 0)
(species Sym_det2a_{age}::{region} 0)
(species Sym_det2b_{age}::{region} 0)
(species Sys_preD_{age}::{region} 0)
(species Sys_det3a_{age}::{region} 0)
(species Sys_det3b_{age}::{region} 0)
    """.format(age=age, region=region)

        if self.expandModel == "testDelay_SymSys" or self.expandModel == "uniformtestDelay":
            species_str = species_str + expand_testDelay_SymSys_str
        if self.expandModel == "testDelay_AsSymSys":
            species_str = species_str + expand_testDelay_AsSymSys_str

        return species_str

    ## For postprocessing that splits by '_', it is easier if EMS are names EMS-1 not EMS_1
    ## This might change depending on the postprocessing
    def sub(x):
        xout = re.sub('_', '-', str(x), count=1)
        return xout

    def sub2(x):
        xout = re.sub('_', '', str(x), count=1)
        return xout

    def write_observe(self, age, region):
        region = str(region)
        grpout = covidModel.sub(region)

        observe_primary_channels_str = """
(observe susceptible_{age}_{grpout} S_{age}::{region})
(observe infected_{age}_{grpout} infected_{age}_{region})
(observe recovered_{age}_{grpout} recovered_{age}_{region})
(observe infected_cumul_{age}_{grpout} infected_cumul_{age}_{region})

(observe asymp_cumul_{age}_{grpout} asymp_cumul_{age}_{region} )
(observe asymp_det_cumul_{age}_{grpout} asymp_det_cumul_{age}_{region})
(observe symptomatic_mild_{age}_{grpout} symptomatic_mild_{age}_{region})
(observe symptomatic_severe_{age}_{grpout} symptomatic_severe_{age}_{region})
(observe symp_mild_cumul_{age}_{grpout} symp_mild_cumul_{age}_{region})
(observe symp_severe_cumul_{age}_{grpout} symp_severe_cumul_{age}_{region})
(observe symp_mild_det_cumul_{age}_{grpout} symp_mild_det_cumul_{age}_{region})
(observe symp_severe_det_cumul_{age}_{grpout} symp_severe_det_cumul_{age}_{region})

(observe hosp_det_cumul_{age}_{grpout} hosp_det_cumul_{age}_{region} )
(observe hosp_cumul_{age}_{grpout} hosp_cumul_{age}_{region})
(observe detected_cumul_{age}_{grpout} detected_cumul_{age}_{region} )

(observe crit_cumul_{age}_{grpout} crit_cumul_{age}_{region})
(observe crit_det_cumul_{age}_{grpout} crit_det_cumul_{age}_{region})
(observe death_det_cumul_{age}_{grpout} death_det_cumul_{age}_{region} )

(observe deaths_det_{age}_{grpout} D3_det3_{age}::{region})
(observe deaths_{age}_{grpout} deaths_{age}_{region})

(observe crit_det_{age}_{grpout} crit_det_{age}_{region})
(observe critical_{age}_{grpout} critical_{age}_{region})
(observe hosp_det_{age}_{grpout} hosp_det_{age}_{region})
(observe hospitalized_{age}_{grpout} hospitalized_{age}_{region})
    """.format(grpout=grpout, age=age, region=region)

        observe_secondary_channels_str = """
(observe exposed_{age}_{grpout} E_{age}::{region})

(observe asymptomatic_det_{age}_{grpout} As_det1_{age}::{region})
(observe asymptomatic_{age}_{grpout} asymptomatic_{age}_{region})

(observe presymptomatic_{age}_{grpout} presymptomatic_{age}_{region})
(observe presymptomatic_det_{age}_{grpout} P_det_{age}::{region} )

(observe detected_{age}_{grpout} detected_{age}_{region})

(observe symptomatic_mild_det_{age}_{grpout} symptomatic_mild_det_{age}_{region})
(observe symptomatic_severe_det_{age}_{grpout} symptomatic_severe_det_{age}_{region})
(observe recovered_det_{age}_{grpout} recovered_det_{age}_{region})
    """.format(grpout=grpout, age=age, region=region)

        observe_tertiary_channels_str = """
(observe infectious_undet_{age}_{grpout} infectious_undet_{age}_{region})
(observe infectious_det_{age}_{grpout} infectious_det_{age}_{region})
(observe infectious_det_symp_{age}_{grpout} infectious_det_symp_{age}_{region})
(observe infectious_det_AsP_{age}_{grpout} infectious_det_AsP_{age}_{region})
    """.format(grpout=grpout, age=age, region=region)

        if self.observeLevel == 'primary':
            observe_str = observe_primary_channels_str
        if self.observeLevel == 'secondary':
            observe_str = observe_primary_channels_str + observe_secondary_channels_str
        if self.observeLevel == 'tertiary':
            observe_str = observe_primary_channels_str + observe_tertiary_channels_str
        if self.observeLevel == 'all':
            observe_str = observe_primary_channels_str + observe_secondary_channels_str + observe_tertiary_channels_str

        observe_str = observe_str.replace("  ", " ")
        return observe_str

    ### Monitor time varying parameters
    def write_observed_param(self):

        observed_param_str = """  
(observe d_As_t d_As)
(observe d_P_t d_P)
(observe d_Sys_t d_Sys)
    """

        # for age, region in [(x, y) for x in ageList for y in regionList]:
        for region in self.region_list:
            region = str(region)
            temp_str = """
(param Ki_{region} @Ki_{region}@)
(observe Ki_{region}_t Ki_{region})
    """.format(region=region)
            observed_param_str = observed_param_str + temp_str

        return observed_param_str

    def write_functions(self, age, region):

        functions_str = """
(func presymptomatic_{age}_{region}  (+ P_{age}::{region} P_det_{age}::{region}))

(func hospitalized_{age}_{region}  (+ H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region}))
(func hosp_det_{age}_{region}  (+ H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region}))
(func critical_{age}_{region} (+ C2_{age}::{region} C3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
(func crit_det_{age}_{region} (+ C2_det3_{age}::{region} C3_det3_{age}::{region}))
(func deaths_{age}_{region} (+ D3_{age}::{region} D3_det3_{age}::{region}))
(func recovered_{age}_{region} (+ RAs_{age}::{region} RSym_{age}::{region} RH1_{age}::{region} RC2_{age}::{region} RAs_det1_{age}::{region} RSym_det2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(func recovered_det_{age}_{region} (+ RAs_det1_{age}::{region} RSym_det2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))

(func asymp_cumul_{age}_{region} (+ asymptomatic_{age}_{region} RAs_{age}::{region} RAs_det1_{age}::{region} ))
(func asymp_det_cumul_{age}_{region} (+ As_det1_{age}::{region} RAs_det1_{age}::{region}))

(func symp_mild_cumul_{age}_{region} (+ symptomatic_mild_{age}_{region} RSym_{age}::{region} RSym_det2_{age}::{region}))
(func symp_mild_det_cumul_{age}_{region} (+ symptomatic_mild_det_{age}_{region} RSym_det2_{age}::{region} ))

(func symp_severe_cumul_{age}_{region} (+ symptomatic_severe_{age}_{region} hospitalized_{age}_{region} critical_{age}_{region} deaths_{age}_{region} RH1_{age}::{region} RC2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(func symp_severe_det_cumul_{age}_{region} (+ symptomatic_severe_det_{age}_{region} hosp_det_{age}_{region} crit_det_{age}_{region} D3_det3_{age}::{region}  RH1_det3_{age}::{region} RC2_det3_{age}::{region}))

(func hosp_cumul_{age}_{region} (+ hospitalized_{age}_{region} critical_{age}_{region} deaths_{age}_{region} RH1_{age}::{region} RC2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region}))
(func hosp_det_cumul_{age}_{region} (+ H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region} D3_det3_{age}::{region}  RH1_det3_{age}::{region}  RC2_det3_{age}::{region}))
(func crit_cumul_{age}_{region} (+ deaths_{age}_{region} critical_{age}_{region} RC2_{age}::{region} RC2_det3_{age}::{region}))
(func crit_det_cumul_{age}_{region} (+ C2_det3_{age}::{region} C3_det3_{age}::{region} D3_det3_{age}::{region} RC2_det3_{age}::{region}))
(func detected_cumul_{age}_{region} (+ As_det1_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region} RAs_det1_{age}::{region} RSym_det2_{age}::{region} RH1_det3_{age}::{region} RC2_det3_{age}::{region} D3_det3_{age}::{region}))
(func death_det_cumul_{age}_{region} D3_det3_{age}::{region} )

(func infected_{age}_{region} (+ infectious_det_{age}_{region} infectious_undet_{age}_{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
(func infected_det_{age}_{region} (+ infectious_det_{age}_{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))
(func infected_cumul_{age}_{region} (+ infected_{age}_{region} recovered_{age}_{region} deaths_{age}_{region}))    
    """.format(age=age, region=region)

        expand_base_str = """
(func asymptomatic_{age}_{region}  (+ As_{age}::{region} As_det1_{age}::{region}))

(func symptomatic_mild_{age}_{region}  (+ Sym_{age}::{region} Sym_det2_{age}::{region}))
(func symptomatic_mild_det_{age}_{region}  (- symptomatic_mild_{age}_{region}  Sym_{age}::{region}))

(func symptomatic_severe_{age}_{region}  (+ Sys_{age}::{region} Sys_det3_{age}::{region}))
(func symptomatic_severe_det_{age}_{region}   (- symptomatic_severe_{age}_{region} Sys_{age}::{region}))

(func detected_{age}_{region} (+ As_det1_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))

(func infectious_undet_{age}_{region} (+ As_{age}::{region} P_{age}::{region} Sym_{age}::{region} Sys_{age}::{region} H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} C2_{age}::{region} C3_{age}::{region}))
(func infectious_det_{age}_{region} (+ As_det1_{age}::{region} P_det_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} ))

(func infectious_det_symp_{age}_{region} (+ Sym_det2_{age}::{region} Sys_det3_{age}::{region} ))
(func infectious_det_AsP_{age}_{region} (+ As_det1_{age}::{region} P_det_{age}::{region}))
    """.format(age=age, region=region)

        expand_testDelay_SymSys_str = """
(func asymptomatic_{age}_{region}  (+ As_{age}::{region} As_det1_{age}::{region}))

(func symptomatic_mild_{age}_{region}  (+ Sym_{age}::{region} Sym_preD_{age}::{region} Sym_det2_{age}::{region}))
(func symptomatic_mild_det_{age}_{region}  (-  symptomatic_mild_{age}_{region} Sym_{age}::{region} Sym_preD_{age}::{region} ))

(func symptomatic_severe_{age}_{region}  (+ Sys_{age}::{region} Sys_preD_{age}::{region} Sys_det3_{age}::{region}))
(func symptomatic_severe_det_{age}_{region}  (- symptomatic_severe_{age}_{region} Sys_{age}::{region} Sys_preD_{age}::{region} ))

(func detected_{age}_{region} (+ As_det1_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))

(func infectious_undet_{age}_{region} (+ As_{age}::{region} P_{age}::{region} Sym_preD_{age}::{region} Sym_{age}::{region} Sys_preD_{age}::{region} Sys_{age}::{region} H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} C2_{age}::{region} C3_{age}::{region}))
(func infectious_det_{age}_{region} (+ As_det1_{age}::{region} P_det_{age}::{region} Sym_det2_{age}::{region} Sys_det3_{age}::{region} ))

(func infectious_det_symp_{age}_{region} (+ Sym_det2_{age}::{region} Sys_det3_{age}::{region} ))
(func infectious_det_AsP_{age}_{region} (+ As_det1_{age}::{region} P_det_{age}::{region}))
    """.format(age=age, region=region)

        expand_testDelay_AsSymSys_str = """
(func asymptomatic_{age}_{region}  (+ As_preD_{age}::{region} As_{age}::{region} As_det1_{age}::{region}))

(func symptomatic_mild_{age}_{region}  (+ Sym_{age}::{region} Sym_preD_{age}::{region} Sym_det2a_{age}::{region} Sym_det2b_{age}::{region}))
(func symptomatic_mild_det_{age}_{region}  (- symptomatic_mild_{age}_{region} Sym_{age}::{region} Sym_preD_{age}::{region} ))

(func symptomatic_severe_{age}_{region}  (+ Sys_{age}::{region} Sys_preD_{age}::{region} Sys_det3a_{age}::{region} Sys_det3b_{age}::{region}))
(func symptomatic_severe_det_{age}_{region}  (- symptomatic_severe_{age}_{region} Sys_{age}::{region} Sys_preD_{age}::{region} ))

(func detected_{age}_{region} (+ As_det1_{age}::{region} Sym_det2a_{age}::{region} Sym_det2b_{age}::{region} Sys_det3a_{age}::{region} Sys_det3b_{age}::{region} H1_det3_{age}::{region} H2_det3_{age}::{region} H3_det3_{age}::{region} C2_det3_{age}::{region} C3_det3_{age}::{region}))

(func infectious_undet_{age}_{region} (+ As_preD_{age}::{region} As_{age}::{region} P_{age}::{region} Sym_{age}::{region} Sym_preD_{age}::{region} Sys_{age}::{region} Sys_preD_{age}::{region} H1_{age}::{region} H2_{age}::{region} H3_{age}::{region} C2_{age}::{region} C3_{age}::{region}))
(func infectious_det_{age}_{region} (+ As_det1_{age}::{region} P_det_{age}::{region} Sym_det2a_{age}::{region} Sym_det2b_{age}::{region} Sys_det3a_{age}::{region} Sys_det3b_{age}::{region}))

(func infectious_det_symp_{age}_{region} (+ Sym_det2a_{age}::{region} Sym_det2b_{age}::{region} Sys_det3a_{age}::{region} Sys_det3b_{age}::{region} ))
(func infectious_det_AsP_{age}_{region} (+ As_det1_{age}::{region} P_det_{age}::{region}))
    """.format(age=age, region=region)

        if self.expandModel == None:
            functions_str = expand_base_str + functions_str
        if self.expandModel == "testDelay_SymSys" or self.expandModel == "uniformtestDelay":
            functions_str = expand_testDelay_SymSys_str + functions_str
        if self.expandModel == "testDelay_AsSymSys":
            functions_str = expand_testDelay_AsSymSys_str + functions_str

        return functions_str

    ###
    # If Ki mix is defined, Ki here can be set to 0 in script that generates the simulation
    def write_params(self):
        params_str = """
(param time_to_infectious @time_to_infectious@)
(param time_to_symptoms @time_to_symptoms@)
(param time_to_hospitalization @time_to_hospitalization@)
(param time_to_critical @time_to_critical@)
(param time_to_death @time_to_death@)
(param recovery_time_asymp @recovery_time_asymp@)
(param recovery_time_mild @recovery_time_mild@)
(param recovery_time_crit @recovery_time_crit@)
(param reduced_inf_of_det_cases @reduced_inf_of_det_cases@)
(param d_As @d_As@)
(param d_P @d_P@)
(param d_Sys @d_Sys@)
(param Ki @Ki@)
(param Kr_a (/ 1 recovery_time_asymp))
(param Kr_m (/ 1 recovery_time_mild))
(param Kr_c (/ 1 recovery_time_crit))
(param Kc (/ 1 time_to_critical))
(param Km (/ 1 time_to_death))
    """

        expand_uniformtestDelay_str = """
(param time_D @time_to_detection@)
(param Ksym_D (/ 1 time_D))
(param Ksys_D (/ 1 time_D))

(param Kr_m_D (/ 1 (- recovery_time_mild time_D )))
    """

        expand_testDelay_SymSys_str = """
(param time_D_Sym @time_to_detection_Sym@)
(param time_D_Sys @time_to_detection_Sys@)
(param Ksym_D (/ 1 time_D_Sym))
(param Ksys_D (/ 1 time_D_Sys))

(param Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym )))
    """

        expand_testDelay_AsSymSys_str = """
(param time_D_Sys @time_to_detection_Sys@)
(param Ksys_D (/ 1 time_D_Sys))

(param time_D_Sym @time_to_detection_Sym@)
(param Ksym_D (/ 1 time_D_Sym))
(param Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym )))

(param time_D_As @time_to_detection_As@)
(param Kl_D (/ 1 time_D_As))
(param Kr_a_D (/ 1 (- recovery_time_asymp time_D_As )))
    """

        if self.expandModel == None:
            params_str = params_str
        if self.expandModel == "testDelay_SymSys":
            params_str = params_str + expand_testDelay_SymSys_str
        if self.expandModel == "uniformtestDelay":
            params_str = params_str + expand_uniformtestDelay_str
        if self.expandModel == "contactTracing":
            params_str = params_str + expand_contactTracing_str
        if self.expandModel == "testDelay_AsSymSys":
            params_str = params_str + expand_testDelay_AsSymSys_str

        params_str = params_str.replace("  ", " ")

        return params_str

    def write_age_specific_param(self, grp):
        grp = str(grp)

        params_str = """
    (param fraction_severe_{grp} @fraction_severe_{grp}@)
    (param Ksys{grp} (* fraction_severe_{grp} (/ 1 time_to_symptoms)))
    (param Ksym{grp} (* (- 1 fraction_severe_{grp}) (/ 1 time_to_symptoms))) 
    (param fraction_dead_{grp} @fraction_dead_{grp}@)
    (param fraction_critical_{grp} @fraction_critical_{grp}@ )
    (param fraction_hospitalized_{grp} @fraction_hospitalized_{grp}@)
    (param fraction_symptomatic_{grp} @fraction_symptomatic_{grp}@)
    (param Kl{grp} (/ (- 1 fraction_symptomatic_{grp} ) time_to_infectious))
    (param Ks{grp} (/ fraction_symptomatic_{grp}  time_to_infectious))
    (param recovery_time_hosp_{grp} @recovery_time_hosp_{grp}@)
    (param Kr_h{grp} (/ 1 recovery_time_hosp_{grp}))
        """.format(grp=grp)

        expand_base_str = """
    (param Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization))
    (param Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization ))
    (param Kh3{grp} (/ fraction_dead_{grp}  time_to_hospitalization))
        """.format(grp=grp)

        expand_uniformtestDelay_str = """
    (param Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization))
    (param Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization ))
    (param Kh3{grp} (/ fraction_dead_{grp}  time_to_hospitalization))
    (param Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D)))
    (param Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D) ))
    (param Kh3_D{grp} (/ fraction_dead_{grp}  (- time_to_hospitalization time_D)))
        """.format(grp=grp)

        expand_testDelay_SymSys_str = """
    (param Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization))
    (param Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization ))
    (param Kh3{grp} (/ fraction_dead_{grp}  time_to_hospitalization))
    (param Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys)))
    (param Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) ))
    (param Kh3_D{grp} (/ fraction_dead_{grp}  (- time_to_hospitalization time_D_Sys)))
        """.format(grp=grp)

        expand_testDelay_AsSymSys_str = """
    (param Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization))
    (param Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization ))
    (param Kh3{grp} (/ fraction_dead_{grp}  time_to_hospitalization))
    (param Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys)))
    (param Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) ))
    (param Kh3_D{grp} (/ fraction_dead_{grp}  (- time_to_hospitalization time_D_Sys)))
        """.format(grp=grp)

        if self.expandModel == None:
            params_str = params_str + expand_base_str
        if self.expandModel == "testDelay_SymSys":
            params_str = params_str + expand_testDelay_SymSys_str
        if self.expandModel == "uniformtestDelay":
            params_str = params_str + expand_uniformtestDelay_str
        if self.expandModel == "testDelay_AsSymSys":
            params_str = params_str + expand_testDelay_AsSymSys_str

        params_str = params_str.replace("  ", " ")

        return params_str

    def repeat_string_by_grp(fixedstring, grpList1, grpList2):
        stringAll = ""
        middlesymbol = "_"

        if fixedstring == "S_" or fixedstring == "E_" or fixedstring == "P_" or fixedstring == "P_det_" or fixedstring == "As_det1_" or fixedstring == "D3_det3_":
            middlesymbol = "::"

        if grpList2 != None:
            for age, region in [(x, y) for x in grpList1 for y in grpList2]:
                temp_string = " " + fixedstring + age + middlesymbol + region
                stringAll = stringAll + temp_string

        if grpList2 == None:
            for grp in grpList1:
                temp_string = " " + fixedstring + grp
                stringAll = stringAll + temp_string

        return stringAll

    def write_All(self):
        regionList = self.region_list
        ageList = self.age_list
        obs_primary_All_str = ""
        obs_primary_All_str = obs_primary_All_str + "\n(observe susceptible_All (+ " + covidModel.repeat_string_by_grp(
            'S_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe infected_All (+ " + covidModel.repeat_string_by_grp(
            'infected_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe recovered_All (+ " + covidModel.repeat_string_by_grp(
            'recovered_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe infected_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'infected_cumul_', ageList, regionList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe asymp_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'asymp_cumul_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe asymp_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'asymp_det_cumul_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symptomatic_mild_All (+ " + covidModel.repeat_string_by_grp(
            'symptomatic_mild_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symptomatic_severe_All (+ " + covidModel.repeat_string_by_grp(
            'symptomatic_severe_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_mild_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'symp_mild_cumul_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_severe_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'symp_severe_cumul_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_mild_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'symp_mild_det_cumul_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_severe_det_cumul_All  (+ " + covidModel.repeat_string_by_grp(
            'symp_severe_det_cumul_', ageList, regionList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe hosp_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'hosp_det_cumul_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe hosp_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'hosp_cumul_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe detected_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'detected_cumul_', ageList, regionList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe crit_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'crit_cumul_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe crit_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'crit_det_cumul_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe death_det_cumul_All (+ " + covidModel.repeat_string_by_grp(
            'death_det_cumul_', ageList, regionList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe deaths_det_All (+ " + covidModel.repeat_string_by_grp(
            'D3_det3_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe deaths_All (+ " + covidModel.repeat_string_by_grp(
            'deaths_', ageList, regionList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe crit_det_All (+ " + covidModel.repeat_string_by_grp(
            'crit_det_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe critical_All (+ " + covidModel.repeat_string_by_grp(
            'critical_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe hosp_det_All (+ " + covidModel.repeat_string_by_grp(
            'hosp_det_', ageList, regionList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe hospitalized_All (+ " + covidModel.repeat_string_by_grp(
            'hospitalized_', ageList, regionList) + "))"

        obs_secondary_All_str = ""
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe exposed_All (+ " + covidModel.repeat_string_by_grp(
            'E_', ageList, regionList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe asymptomatic_All (+ " + covidModel.repeat_string_by_grp(
            'asymptomatic_', ageList, regionList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe asymptomatic_det_All (+ " + covidModel.repeat_string_by_grp(
            'As_det1_', ageList, regionList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe presymptomatic_All (+ " + covidModel.repeat_string_by_grp(
            'P_', ageList, regionList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe presymptomatic_det_All (+ " + covidModel.repeat_string_by_grp(
            'P_det_', ageList, regionList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe detected_All (+ " + covidModel.repeat_string_by_grp(
            'detected_', ageList, regionList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe symptomatic_mild_det_All (+ " + covidModel.repeat_string_by_grp(
            'symptomatic_mild_det_', ageList, regionList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe symptomatic_severe_det_All (+ " + covidModel.repeat_string_by_grp(
            'symptomatic_severe_det_', ageList, regionList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe recovered_det_All (+ " + covidModel.repeat_string_by_grp(
            'recovered_det_', ageList, regionList) + "))"

        obs_tertiary_All_str = ""
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_det_All (+ " + covidModel.repeat_string_by_grp(
            'infectious_det_', ageList, regionList) + "))"
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_undet_All (+ " + covidModel.repeat_string_by_grp(
            'infectious_undet_', ageList, regionList) + "))"
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_det_symp_All (+ " + covidModel.repeat_string_by_grp(
            'infectious_det_symp_', ageList, regionList) + "))"
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_det_AsP_All (+ " + covidModel.repeat_string_by_grp(
            'infectious_det_AsP_', ageList, regionList) + "))"

        if self.observeLevel == 'primary':
            obs_All_str = obs_primary_All_str
        if self.observeLevel == 'secondary':
            obs_All_str = obs_primary_All_str + obs_secondary_All_str
        if self.observeLevel == 'tertiary':
            obs_All_str = obs_primary_All_str + obs_tertiary_All_str
        if self.observeLevel == 'all':
            obs_All_str = obs_primary_All_str + obs_secondary_All_str + obs_tertiary_All_str

        obs_All_str = obs_All_str.replace("  ", " ")
        return obs_All_str

    #### Locale specific migration
    def write_migration_param(self):
        x1 = range(1, len(self.region_list) + 1)
        x2 = range(1, len(self.region_list) + 1)
        param_str = ""
        for x1_i in x1:
            param_str = param_str + "\n"
            for x2_i in x2:
                # x1_i=1
                param_str = param_str + """\n(param toEMS_{x1_i}_from_EMS_{x2_i} @toEMS_{x1_i}_from_EMS_{x2_i}@)""".format(
                    x1_i=x1_i, x2_i=x2_i)
        return (param_str)

    def write_travel_reaction(self, age, region):
        x1_i = int(region.split("_")[1])
        x2 = list(range(1, 12))
        x2 = [i for i in x2 if i != x1_i]
        reaction_str = ""

        for travelspecies in self.travelspeciesList:
            reaction_str = reaction_str + "\n"
            for x2_i in x2:
                # x1_i=1
                reaction_str = reaction_str + """\n(reaction {travelspecies}_travel_{age}_EMS_{x2_i}to{x1_i}  ({travelspecies}_{age}::EMS_{x2_i}) ({travelspecies}_{age}::EMS_{x1_i}) (* {travelspecies}_{age}::EMS_{x2_i} toEMS_{x1_i}_from_EMS_{x2_i} (/ N_{age}_EMS_{x2_i} (+ S_{age}::EMS_{x2_i} E_{age}::EMS_{x2_i} As_{age}::EMS_{x2_i} P_{age}::EMS_{x2_i} recovered_{age}_EMS_{x2_i}))))""".format(
                    age=age, travelspecies=travelspecies, x1_i=x1_i, x2_i=x2_i)

        return reaction_str

    #### Age specific contact matric
    def write_contact_matrix(self):
        nageGroups = len(self.age_list)
        grp_x = range(1, nageGroups + 1)
        grp_y = reversed(grp_x)

        ki_dic = {}
        for i, xy in enumerate(itertools.product(grp_x, grp_y)):
            ki_dic[i] = ["C" + str(xy[0]) + '_' + str(xy[1])]

        ki_mix_param1 = ""
        ki_mix_param3 = ""
        for i in range(len(ki_dic.keys())):
            string_i = "\n(param " + covidModel.sub2(ki_dic[i][0]) + " @" + ki_dic[i][0] + "@ )"
            ki_mix_param1 = ki_mix_param1 + string_i

            string_i = "\n(param " + ki_dic[i][0] + " (/ " + covidModel.sub2(ki_dic[i][0]) + " norm_factor))"
            ki_mix_param3 = ki_mix_param3 + string_i

        ## To do - remove hardcoding and if statement
        if nageGroups == 4:
            ki_mix_param2 = "\n(param sum1 (+ C11 C12 C13 C14))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum2  (+ C21 C22 C23 C24))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum3 (+ C31 C32 C33 C34))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum4 (+ C41 C42 C43 C44))"
            norm_factor = "\n(param norm_factor (+ (* sum1 p1) (* sum2  p2) (* sum3 p3) (* sum4  p4)))"

        if nageGroups == 8:
            ki_mix_param2 = "\n(param sum1 (+ C11 C12 C13 C14 C15 C16 C17 C18))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum2 (+ C21 C22 C23 C24 C25 C26 C27 C28))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum3 (+ C31 C32 C33 C34 C35 C36 C37 C38))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum4 (+ C41 C42 C43 C44 C45 C46 C47 C48))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum5 (+ C51 C52 C53 C54 C55 C56 C57 C58))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum6 (+ C61 C62 C63 C64 C65 C66 C67 C68))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum7 (+ C71 C72 C73 C74 C75 C76 C77 C78))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum8 (+ C81 C82 C83 C84 C85 C86 C87 C88))"
            norm_factor = "\n(param norm_factor (+ (* sum1 p1) (* sum2  p2) (* sum3 p3) (* sum4  p4) (* sum5  p5) (* sum6  p6) (* sum7  p7) (* sum8  p8)))"

        stringAll = ""
        for i, age in enumerate(self.age_list):
            string2 = """\n(param p{i} (/ N_{age} N_All))""".format(i=i + 1, age=age)
            stringAll = stringAll + string2

        ki_mix_param = ki_mix_param1 + "\n" + ki_mix_param2 + "\n" + norm_factor + "\n" + ki_mix_param3

        ki_mix_param = stringAll + ki_mix_param

        return ki_mix_param

    def write_exposure_reaction8(region):
        exposure_reaction_str = """  
(reaction exposure_age0to9_{region}    (S_age0to9::{region})    (E_age0to9::{region})    (* Ki_{region} S_age0to9::{region}    (+ (* C1_1 (/ (+ infectious_undet_age0to9_{region} (* infectious_det_age0to9_{region} reduced_inf_of_det_cases)) N_age0to9_{region})) (* C1_2 (/ (+ infectious_undet_age10to19_{region} (* infectious_det_age10to19_{region} reduced_inf_of_det_cases)) N_age10to19_{region})) (* C1_3 (/ (+ infectious_undet_age20to29_{region} (* infectious_det_age20to29_{region} reduced_inf_of_det_cases)) N_age20to29_{region})) (* C1_4 (/ (+ infectious_undet_age30to39_{region} (* infectious_det_age30to39_{region} reduced_inf_of_det_cases)) N_age30to39_{region})) (* C1_5 (/ (+ infectious_undet_age40to49_{region} (* infectious_det_age40to49_{region} reduced_inf_of_det_cases)) N_age40to49_{region})) (* C1_6 (/ (+ infectious_undet_age50to59_{region} (* infectious_det_age50to59_{region} reduced_inf_of_det_cases)) N_age50to59_{region})) (* C1_7 (/ (+ infectious_undet_age60to69_{region} (* infectious_det_age60to69_{region} reduced_inf_of_det_cases)) N_age60to69_{region})) (* C1_8 (/ (+ infectious_undet_age70to100_{region} (* infectious_det_age70to100_{region} reduced_inf_of_det_cases)) N_age70to100_{region})))))
(reaction exposure_age10to19_{region}  (S_age10to19::{region})  (E_age10to19::{region})  (* Ki_{region} S_age10to19::{region}  (+ (* C2_1 (/ (+ infectious_undet_age0to9_{region} (* infectious_det_age0to9_{region} reduced_inf_of_det_cases)) N_age0to9_{region})) (* C2_2 (/ (+ infectious_undet_age10to19_{region} (* infectious_det_age10to19_{region} reduced_inf_of_det_cases)) N_age10to19_{region})) (* C2_3 (/ (+ infectious_undet_age20to29_{region} (* infectious_det_age20to29_{region} reduced_inf_of_det_cases)) N_age20to29_{region})) (* C2_4 (/ (+ infectious_undet_age30to39_{region} (* infectious_det_age30to39_{region} reduced_inf_of_det_cases)) N_age30to39_{region})) (* C2_5 (/ (+ infectious_undet_age40to49_{region} (* infectious_det_age40to49_{region} reduced_inf_of_det_cases)) N_age40to49_{region})) (* C2_6 (/ (+ infectious_undet_age50to59_{region} (* infectious_det_age50to59_{region} reduced_inf_of_det_cases)) N_age50to59_{region})) (* C2_7 (/ (+ infectious_undet_age60to69_{region} (* infectious_det_age60to69_{region} reduced_inf_of_det_cases)) N_age60to69_{region})) (* C2_8 (/ (+ infectious_undet_age70to100_{region} (* infectious_det_age70to100_{region} reduced_inf_of_det_cases)) N_age70to100_{region})))))
(reaction exposure_age20to29_{region}  (S_age20to29::{region})  (E_age20to29::{region})  (* Ki_{region} S_age20to29::{region}  (+ (* C3_1 (/ (+ infectious_undet_age0to9_{region} (* infectious_det_age0to9_{region} reduced_inf_of_det_cases)) N_age0to9_{region})) (* C3_2 (/ (+ infectious_undet_age10to19_{region} (* infectious_det_age10to19_{region} reduced_inf_of_det_cases)) N_age10to19_{region})) (* C3_3 (/ (+ infectious_undet_age20to29_{region} (* infectious_det_age20to29_{region} reduced_inf_of_det_cases)) N_age20to29_{region})) (* C3_4 (/ (+ infectious_undet_age30to39_{region} (* infectious_det_age30to39_{region} reduced_inf_of_det_cases)) N_age30to39_{region})) (* C3_5 (/ (+ infectious_undet_age40to49_{region} (* infectious_det_age40to49_{region} reduced_inf_of_det_cases)) N_age40to49_{region})) (* C3_6 (/ (+ infectious_undet_age50to59_{region} (* infectious_det_age50to59_{region} reduced_inf_of_det_cases)) N_age50to59_{region})) (* C3_7 (/ (+ infectious_undet_age60to69_{region} (* infectious_det_age60to69_{region} reduced_inf_of_det_cases)) N_age60to69_{region})) (* C3_8 (/ (+ infectious_undet_age70to100_{region} (* infectious_det_age70to100_{region} reduced_inf_of_det_cases)) N_age70to100_{region})))))
(reaction exposure_age30to39_{region}  (S_age30to39::{region})  (E_age30to39::{region})  (* Ki_{region} S_age30to39::{region}  (+ (* C4_1 (/ (+ infectious_undet_age0to9_{region} (* infectious_det_age0to9_{region} reduced_inf_of_det_cases)) N_age0to9_{region})) (* C4_2 (/ (+ infectious_undet_age10to19_{region} (* infectious_det_age10to19_{region} reduced_inf_of_det_cases)) N_age10to19_{region})) (* C4_3 (/ (+ infectious_undet_age20to29_{region} (* infectious_det_age20to29_{region} reduced_inf_of_det_cases)) N_age20to29_{region})) (* C4_4 (/ (+ infectious_undet_age30to39_{region} (* infectious_det_age30to39_{region} reduced_inf_of_det_cases)) N_age30to39_{region})) (* C4_5 (/ (+ infectious_undet_age40to49_{region} (* infectious_det_age40to49_{region} reduced_inf_of_det_cases)) N_age40to49_{region})) (* C4_6 (/ (+ infectious_undet_age50to59_{region} (* infectious_det_age50to59_{region} reduced_inf_of_det_cases)) N_age50to59_{region})) (* C4_7 (/ (+ infectious_undet_age60to69_{region} (* infectious_det_age60to69_{region} reduced_inf_of_det_cases)) N_age60to69_{region})) (* C4_8 (/ (+ infectious_undet_age70to100_{region} (* infectious_det_age70to100_{region} reduced_inf_of_det_cases)) N_age70to100_{region})))))
(reaction exposure_age40to49_{region}  (S_age40to49::{region})  (E_age40to49::{region})  (* Ki_{region} S_age40to49::{region}  (+ (* C5_1 (/ (+ infectious_undet_age0to9_{region} (* infectious_det_age0to9_{region} reduced_inf_of_det_cases)) N_age0to9_{region})) (* C5_2 (/ (+ infectious_undet_age10to19_{region} (* infectious_det_age10to19_{region} reduced_inf_of_det_cases)) N_age10to19_{region})) (* C5_3 (/ (+ infectious_undet_age20to29_{region} (* infectious_det_age20to29_{region} reduced_inf_of_det_cases)) N_age20to29_{region})) (* C5_4 (/ (+ infectious_undet_age30to39_{region} (* infectious_det_age30to39_{region} reduced_inf_of_det_cases)) N_age30to39_{region})) (* C5_5 (/ (+ infectious_undet_age40to49_{region} (* infectious_det_age40to49_{region} reduced_inf_of_det_cases)) N_age40to49_{region})) (* C5_6 (/ (+ infectious_undet_age50to59_{region} (* infectious_det_age50to59_{region} reduced_inf_of_det_cases)) N_age50to59_{region})) (* C5_7 (/ (+ infectious_undet_age60to69_{region} (* infectious_det_age60to69_{region} reduced_inf_of_det_cases)) N_age60to69_{region})) (* C5_8 (/ (+ infectious_undet_age70to100_{region} (* infectious_det_age70to100_{region} reduced_inf_of_det_cases)) N_age70to100_{region})))))
(reaction exposure_age50to59_{region}  (S_age50to59::{region})  (E_age50to59::{region})  (* Ki_{region} S_age50to59::{region}  (+ (* C6_1 (/ (+ infectious_undet_age0to9_{region} (* infectious_det_age0to9_{region} reduced_inf_of_det_cases)) N_age0to9_{region})) (* C6_2 (/ (+ infectious_undet_age10to19_{region} (* infectious_det_age10to19_{region} reduced_inf_of_det_cases)) N_age10to19_{region})) (* C6_3 (/ (+ infectious_undet_age20to29_{region} (* infectious_det_age20to29_{region} reduced_inf_of_det_cases)) N_age20to29_{region})) (* C6_4 (/ (+ infectious_undet_age30to39_{region} (* infectious_det_age30to39_{region} reduced_inf_of_det_cases)) N_age30to39_{region})) (* C6_5 (/ (+ infectious_undet_age40to49_{region} (* infectious_det_age40to49_{region} reduced_inf_of_det_cases)) N_age40to49_{region})) (* C6_6 (/ (+ infectious_undet_age50to59_{region} (* infectious_det_age50to59_{region} reduced_inf_of_det_cases)) N_age50to59_{region})) (* C6_7 (/ (+ infectious_undet_age60to69_{region} (* infectious_det_age60to69_{region} reduced_inf_of_det_cases)) N_age60to69_{region})) (* C6_8 (/ (+ infectious_undet_age70to100_{region} (* infectious_det_age70to100_{region} reduced_inf_of_det_cases)) N_age70to100_{region})))))
(reaction exposure_age60to69_{region}  (S_age60to69::{region})  (E_age60to69::{region})  (* Ki_{region} S_age60to69::{region}  (+ (* C7_1 (/ (+ infectious_undet_age0to9_{region} (* infectious_det_age0to9_{region} reduced_inf_of_det_cases)) N_age0to9_{region})) (* C7_2 (/ (+ infectious_undet_age10to19_{region} (* infectious_det_age10to19_{region} reduced_inf_of_det_cases)) N_age10to19_{region})) (* C7_3 (/ (+ infectious_undet_age20to29_{region} (* infectious_det_age20to29_{region} reduced_inf_of_det_cases)) N_age20to29_{region})) (* C7_4 (/ (+ infectious_undet_age30to39_{region} (* infectious_det_age30to39_{region} reduced_inf_of_det_cases)) N_age30to39_{region})) (* C7_5 (/ (+ infectious_undet_age40to49_{region} (* infectious_det_age40to49_{region} reduced_inf_of_det_cases)) N_age40to49_{region})) (* C7_6 (/ (+ infectious_undet_age50to59_{region} (* infectious_det_age50to59_{region} reduced_inf_of_det_cases)) N_age50to59_{region})) (* C7_7 (/ (+ infectious_undet_age60to69_{region} (* infectious_det_age60to69_{region} reduced_inf_of_det_cases)) N_age60to69_{region})) (* C7_8 (/ (+ infectious_undet_age70to100_{region} (* infectious_det_age70to100_{region} reduced_inf_of_det_cases)) N_age70to100_{region})))))
(reaction exposure_age70to100_{region} (S_age70to100::{region}) (E_age70to100::{region}) (* Ki_{region} S_age70to100::{region} (+ (* C8_1 (/ (+ infectious_undet_age0to9_{region} (* infectious_det_age0to9_{region} reduced_inf_of_det_cases)) N_age0to9_{region})) (* C8_2 (/ (+ infectious_undet_age10to19_{region} (* infectious_det_age10to19_{region} reduced_inf_of_det_cases)) N_age10to19_{region})) (* C8_3 (/ (+ infectious_undet_age20to29_{region} (* infectious_det_age20to29_{region} reduced_inf_of_det_cases)) N_age20to29_{region})) (* C8_4 (/ (+ infectious_undet_age30to39_{region} (* infectious_det_age30to39_{region} reduced_inf_of_det_cases)) N_age30to39_{region})) (* C8_5 (/ (+ infectious_undet_age40to49_{region} (* infectious_det_age40to49_{region} reduced_inf_of_det_cases)) N_age40to49_{region})) (* C8_6 (/ (+ infectious_undet_age50to59_{region} (* infectious_det_age50to59_{region} reduced_inf_of_det_cases)) N_age50to59_{region})) (* C8_7 (/ (+ infectious_undet_age60to69_{region} (* infectious_det_age60to69_{region} reduced_inf_of_det_cases)) N_age60to69_{region})) (* C8_8 (/ (+ infectious_undet_age70to100_{region} (* infectious_det_age70to100_{region} reduced_inf_of_det_cases)) N_age70to100_{region})))))
    """.format(region=region)
        return exposure_reaction_str

    def write_reactions(self, age, region):

        #    reaction_str_I = """
        # (reaction exposure_{age}_{region}   (S_{age}::{region}) (E_{age}::{region}) (* Ki_{region} S_{age}::{region} (/  (+ infectious_undet_{age}_{region} (* infectious_det_{age}_{region} reduced_inf_of_det_cases)) N_{age}_{region} )))
        # """.format(age=age, region=region)

        reaction_str_III = """
(reaction recovery_H1_{age}_{region}   (H1_{age}::{region})   (RH1_{age}::{region})   (* Kr_h{age} H1_{age}::{region}))
(reaction recovery_C2_{age}_{region}   (C2_{age}::{region})   (RC2_{age}::{region})   (* Kr_c C2_{age}::{region}))
(reaction recovery_H1_det3_{age}_{region}   (H1_det3_{age}::{region})   (RH1_det3_{age}::{region})   (* Kr_h{age} H1_det3_{age}::{region}))
(reaction recovery_C2_det3_{age}_{region}   (C2_det3_{age}::{region})   (RC2_det3_{age}::{region})   (* Kr_c C2_det3_{age}::{region}))
        """.format(age=age, region=region)

        expand_base_str = """
(reaction infection_asymp_undet_{age}_{region}  (E_{age}::{region})   (As_{age}::{region})   (* Kl{age} E_{age}::{region} (- 1 d_As)))
(reaction infection_asymp_det_{age}_{region}  (E_{age}::{region})   (As_det1_{age}::{region})   (* Kl{age} E_{age}::{region} d_As))
(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_{age}::{region})   (* Ks{age} E_{age}::{region} (- 1 d_P)))
(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_det_{age}::{region})   (* Ks{age} E_{age}::{region} d_P))

(reaction mild_symptomatic_undet_{age}_{region} (P_{age}::{region})  (Sym_{age}::{region}) (* Ksym{age} P_{age}::{region} (- 1 d_Sym_{region})))
(reaction mild_symptomatic_det_{age}_{region} (P_{age}::{region})  (Sym_det2_{age}::{region}) (* Ksym{age} P_{age}::{region} d_Sym_{region}))
(reaction severe_symptomatic_undet_{age}_{region} (P_{age}::{region})  (Sys_{age}::{region})  (* Ksys{age} P_{age}::{region} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{age}_{region} (P_{age}::{region})  (Sys_det3_{age}::{region})  (* Ksys{age} P_{age}::{region} d_Sys))

(reaction mild_symptomatic_det_{age}_{region} (P_det_{age}::{region})  (Sym_det2_{age}::{region}) (* Ksym{age} P_det_{age}::{region}))
(reaction severe_symptomatic_det_{age}_{region} (P_det_{age}::{region})  (Sys_det3_{age}::{region})  (* Ksys{age} P_det_{age}::{region} ))

(reaction hospitalization_1_{age}_{region}   (Sys_{age}::{region})   (H1_{age}::{region})   (* Kh1{age} Sys_{age}::{region}))
(reaction hospitalization_2_{age}_{region}   (Sys_{age}::{region})   (H2_{age}::{region})   (* Kh2{age} Sys_{age}::{region}))
(reaction hospitalization_3_{age}_{region}   (Sys_{age}::{region})   (H3_{age}::{region})   (* Kh3{age} Sys_{age}::{region}))
(reaction critical_2_{age}_{region}   (H2_{age}::{region})   (C2_{age}::{region})   (* Kc H2_{age}::{region}))
(reaction critical_3_{age}_{region}   (H3_{age}::{region})   (C3_{age}::{region})   (* Kc H3_{age}::{region}))
(reaction death_{age}_{region}   (C3_{age}::{region})   (D3_{age}::{region})   (* Km C3_{age}::{region}))

(reaction hospitalization_1_det_{age}_{region}   (Sys_det3_{age}::{region})   (H1_det3_{age}::{region})   (* Kh1{age} Sys_det3_{age}::{region}))
(reaction hospitalization_2_det_{age}_{region}   (Sys_det3_{age}::{region})   (H2_det3_{age}::{region})   (* Kh2{age} Sys_det3_{age}::{region}))
(reaction hospitalization_3_det_{age}_{region}   (Sys_det3_{age}::{region})   (H3_det3_{age}::{region})   (* Kh3{age} Sys_det3_{age}::{region}))
(reaction critical_2_det2_{age}_{region}   (H2_det3_{age}::{region})   (C2_det3_{age}::{region})   (* Kc H2_det3_{age}::{region}))
(reaction critical_3_det2_{age}_{region}   (H3_det3_{age}::{region})   (C3_det3_{age}::{region})   (* Kc H3_det3_{age}::{region}))
(reaction death_det3_{age}_{region}   (C3_det3_{age}::{region})   (D3_det3_{age}::{region})   (* Km C3_det3_{age}::{region}))

(reaction recovery_As_{age}_{region}   (As_{age}::{region})   (RAs_{age}::{region})   (* Kr_a As_{age}::{region}))
(reaction recovery_As_det_{age}_{region} (As_det1_{age}::{region})   (RAs_det1_{age}::{region})   (* Kr_a As_det1_{age}::{region}))

(reaction recovery_Sym_{age}_{region}   (Sym_{age}::{region})   (RSym_{age}::{region})   (* Kr_m  Sym_{age}::{region}))
(reaction recovery_Sym_det2_{age}_{region}   (Sym_det2_{age}::{region})   (RSym_det2_{age}::{region})   (* Kr_m  Sym_det2_{age}::{region}))
    """.format(age=age, region=region)

        expand_testDelay_SymSys_str = """
(reaction infection_asymp_undet_{age}_{region}  (E_{age}::{region})   (As_{age}::{region})   (* Kl{age} E_{age}::{region} (- 1 d_As)))
(reaction infection_asymp_det_{age}_{region}  (E_{age}::{region})   (As_det1_{age}::{region})   (* Kl{age} E_{age}::{region} d_As))
(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_{age}::{region})   (* Ks{age} E_{age}::{region}))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{age}_{region} (P_{age}::{region})  (Sym_preD_{age}::{region}) (* Ksym{age} P_{age}::{region}))
(reaction severe_symptomatic_{age}_{region} (P_{age}::{region})  (Sys_preD_{age}::{region})  (* Ksys{age} P_{age}::{region}))

; never detected 
(reaction mild_symptomatic_undet_{age}_{region} (Sym_preD_{age}::{region})  (Sym_{age}::{region}) (* Ksym_D Sym_preD_{age}::{region} (- 1 d_Sym_{region})))
(reaction severe_symptomatic_undet_{age}_{region} (Sys_preD_{age}::{region})  (Sys_{age}::{region})  (* Ksys_D Sys_preD_{age}::{region} (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det_{age}_{region} (Sym_preD_{age}::{region})  (Sym_det2_{age}::{region}) (* Ksym_D Sym_preD_{age}::{region} d_Sym_{region}))
(reaction severe_symptomatic_det_{age}_{region} (Sys_preD_{age}::{region})  (Sys_det3_{age}::{region})  (* Ksys_D Sys_preD_{age}::{region} d_Sys))

(reaction hospitalization_1_{age}_{region}   (Sys_{age}::{region})   (H1_{age}::{region})   (* Kh1_D{age} Sys_{age}::{region}))
(reaction hospitalization_2_{age}_{region}   (Sys_{age}::{region})   (H2_{age}::{region})   (* Kh2_D{age} Sys_{age}::{region}))
(reaction hospitalization_3_{age}_{region}   (Sys_{age}::{region})   (H3_{age}::{region})   (* Kh3_D{age} Sys_{age}::{region}))
(reaction critical_2_{age}_{region}   (H2_{age}::{region})   (C2_{age}::{region})   (* Kc H2_{age}::{region}))
(reaction critical_3_{age}_{region}   (H3_{age}::{region})   (C3_{age}::{region})   (* Kc H3_{age}::{region}))
(reaction death_{age}_{region}   (C3_{age}::{region})   (D3_{age}::{region})   (* Km C3_{age}::{region}))

(reaction hospitalization_1_det_{age}_{region}   (Sys_det3_{age}::{region})   (H1_det3_{age}::{region})   (* Kh1_D{age} Sys_det3_{age}::{region}))
(reaction hospitalization_2_det_{age}_{region}   (Sys_det3_{age}::{region})   (H2_det3_{age}::{region})   (* Kh2_D{age} Sys_det3_{age}::{region}))
(reaction hospitalization_3_det_{age}_{region}   (Sys_det3_{age}::{region})   (H3_det3_{age}::{region})   (* Kh3_D{age} Sys_det3_{age}::{region}))
(reaction critical_2_det2_{age}_{region}   (H2_det3_{age}::{region})   (C2_det3_{age}::{region})   (* Kc H2_det3_{age}::{region}))
(reaction critical_3_det2_{age}_{region}   (H3_det3_{age}::{region})   (C3_det3_{age}::{region})   (* Kc H3_det3_{age}::{region}))
(reaction death_det3_{age}_{region}   (C3_det3_{age}::{region})   (D3_det3_{age}::{region})   (* Km C3_det3_{age}::{region}))

(reaction recovery_As_{age}_{region}   (As_{age}::{region})   (RAs_{age}::{region})   (* Kr_a As_{age}::{region}))
(reaction recovery_As_det_{age}_{region} (As_det1_{age}::{region})   (RAs_det1_{age}::{region})   (* Kr_a As_det1_{age}::{region}))
(reaction recovery_Sym_{age}_{region}   (Sym_{age}::{region})   (RSym_{age}::{region})   (* Kr_m_D  Sym_{age}::{region}))
(reaction recovery_Sym_det2_{age}_{region}   (Sym_det2_{age}::{region})   (RSym_det2_{age}::{region})   (* Kr_m_D  Sym_det2_{age}::{region}))
    
    """.format(age=age, region=region)

        expand_testDelay_AsSymSys_str = """
(reaction infection_asymp_det_{age}_{region}  (E_{age}::{region})   (As_preD_{age}::{region})   (* Kl{age} E_{age}::{region}))
(reaction infection_asymp_undet_{age}_{region}  (As_preD_{age}::{region})   (As_{age}::{region})   (* Kl_D As_preD_{age}::{region} (- 1 d_As)))
(reaction infection_asymp_det_{age}_{region}  (As_preD_{age}::{region})   (As_det1_{age}::{region})   (* Kl_D As_preD_{age}::{region} d_As))

(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_{age}::{region})   (* Ks{age}  E_{age}::{region} (- 1 d_P)))
(reaction presymptomatic_{age}_{region} (E_{age}::{region})   (P_det_{age}::{region})   (* Ks{age}  E_{age}::{region} d_P))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{age}_{region} (P_{age}::{region})  (Sym_preD_{age}::{region}) (* Ksym{age} P_{age}::{region}))
(reaction severe_symptomatic_{age}_{region} (P_{age}::{region})  (Sys_preD_{age}::{region})  (* Ksys{age} P_{age}::{region}))
                                                                   
; never detected 
(reaction mild_symptomatic_undet_{age}_{region} (Sym_preD_{age}::{region})  (Sym_{age}::{region}) (* Ksym_D Sym_preD_{age}::{region} (- 1 d_Sym_{region})))
(reaction severe_symptomatic_undet_{age}_{region} (Sys_preD_{age}::{region})  (Sys_{age}::{region})  (* Ksys_D Sys_preD_{age}::{region} (- 1 d_Sys)))

; new detections  - time to detection is subtracted from hospital time
(reaction mild_symptomatic_det_{age}_{region} (Sym_preD_{age}::{region})  (Sym_det2a_{age}::{region}) (* Ksym_D Sym_preD_{age}::{region} d_Sym_{region}))
(reaction severe_symptomatic_det_{age}_{region} (Sys_preD_{age}::{region})  (Sys_det3a_{age}::{region})  (* Ksys_D Sys_preD_{age}::{region} d_Sys))

; developing symptoms - already detected, same time to symptoms as in master emodl
(reaction mild_symptomatic_det_{age}_{region} (P_det_{age}::{region})  (Sym_det2b_{age}::{region}) (* Ksym{age}  P_det_{age}::{region}))
(reaction severe_symptomatic_det_{age}_{region} (P_det_{age}::{region})  (Sys_det3b_{age}::{region})  (* Ksys{age}  P_det_{age}::{region} ))

(reaction hospitalization_1_{age}_{region}  (Sys_{age}::{region})   (H1_{age}::{region})   (* Kh1_D{age} Sys_{age}::{region}))
(reaction hospitalization_2_{age}_{region}   (Sys_{age}::{region})   (H2_{age}::{region})   (* Kh2_D{age} Sys_{age}::{region}))
(reaction hospitalization_3_{age}_{region}   (Sys_{age}::{region})   (H3_{age}::{region})   (* Kh3_D{age} Sys_{age}::{region}))
(reaction critical_2_{age}_{region}  (H2_{age}::{region})   (C2_{age}::{region})   (* Kc H2_{age}::{region}))
(reaction critical_3_{age}_{region}   (H3_{age}::{region})   (C3_{age}::{region})   (* Kc H3_{age}::{region}))
(reaction death_{age}_{region}   (C3_{age}::{region})   (D3_{age}::{region})   (* Km C3_{age}::{region}))

(reaction hospitalization_1_det_{age}_{region}   (Sys_det3a_{age}::{region})   (H1_det3_{age}::{region})   (* Kh1_D{age} Sys_det3a_{age}::{region}))
(reaction hospitalization_2_det_{age}_{region}   (Sys_det3a_{age}::{region})   (H2_det3_{age}::{region})   (* Kh2_D{age} Sys_det3a_{age}::{region}))
(reaction hospitalization_3_det_{age}_{region}   (Sys_det3a_{age}::{region})   (H3_det3_{age}::{region})   (* Kh3_D{age} Sys_det3a_{age}::{region}))

(reaction hospitalization_1_det_{age}_{region}   (Sys_det3b_{age}::{region})   (H1_det3_{age}::{region})   (* Kh1{age} Sys_det3b_{age}::{region}))
(reaction hospitalization_2_det_{age}_{region}   (Sys_det3b_{age}::{region})   (H2_det3_{age}::{region})   (* Kh2{age} Sys_det3b_{age}::{region}))
(reaction hospitalization_3_det_{age}_{region}   (Sys_det3b_{age}::{region})   (H3_det3_{age}::{region})   (* Kh3{age} Sys_det3b_{age}::{region}))

(reaction critical_2_det2_{age}_{region}   (H2_det3_{age}::{region})   (C2_det3_{age}::{region})   (* Kc H2_det3_{age}::{region}))
(reaction critical_3_det2_{age}_{region}   (H3_det3_{age}::{region})   (C3_det3_{age}::{region})   (* Kc H3_det3_{age}::{region}))
(reaction death_det3_{age}_{region}   (C3_det3_{age}::{region})   (D3_det3_{age}::{region})   (* Km C3_det3_{age}::{region}))

(reaction recovery_As_{age}_{region}   (As_{age}::{region})   (RAs_{age}::{region})   (* Kr_a_D As_{age}::{region}))
(reaction recovery_As_det_{age}_{region} (As_det1_{age}::{region})   (RAs_det1_{age}::{region})   (* Kr_a_D As_det1_{age}::{region}))

(reaction recovery_Sym_{age}_{region}   (Sym_{age}::{region})   (RSym_{age}::{region})   (* Kr_m_D  Sym_{age}::{region}))
(reaction recovery_Sym_det2a_{age}_{region}   (Sym_det2a_{age}::{region})   (RSym_det2_{age}::{region})   (* Kr_m_D  Sym_det2a_{age}::{region}))
(reaction recovery_Sym_det2b_{age}_{region}   (Sym_det2b_{age}::{region})   (RSym_det2_{age}::{region})   (* Kr_m  Sym_det2b_{age}::{region}))
     """.format(age=age, region=region)

        if self.expandModel == None:
            reaction_str = expand_base_str + reaction_str_III
        if self.expandModel == "testDelay_SymSys" or self.expandModel == "uniformtestDelay":
            reaction_str = expand_testDelay_SymSys_str + reaction_str_III
        if self.expandModel == 'testDelay_AsSymSys':
            reaction_str = expand_testDelay_AsSymSys_str + reaction_str_III

        reaction_str = reaction_str.replace("  ", " ")

        return reaction_str

    def define_change_detection_and_isolation(grpList=None,
                                              reduced_inf_of_det_cases=True,
                                              d_As=True,
                                              d_P=True,
                                              d_Sym_ct=True,
                                              d_Sym_grp=False,
                                              d_Sym_grp_option=None):

        """ Write the emodl chunk for changing detection rates and reduced infectiousness
        to approximate contact tracing or improved health system interventions.
        Helper function called by write_interventions

        Parameters
        ----------
        grpList: list
            List that contains the groupnames for which parameters are repeated
        reduced_inf_of_det_cases : boolean
            Boolean to add a change in infectiousness of As and P detected cases if set to True
        d_As : boolean
            Boolean to add a change in detection of asymptomatic cases if set to True
        d_P : boolean
            Boolean to add a change in detection of presymptomatic cases if set to True
        d_Sym_ct : boolean
            Boolean to add a change in detection of symptomatic cases if set to True
        d_Sym_grp : boolean
            Boolean to denote whether dSym is group specific or generic
        d_Sym_grp_option : character
            Chracter used to flag which increase option to select, possible characters are:
            increase_to_grp_target (select for each group a specific target to reach),
            increase_to_common_target (use same target for all groups),
            common_increase (rather than replacing the old detection level, increase by a specified percentage),
            grp_specific_increase (define a group specific increase, i.e. group 1 by 10%, group 2 by 50%).
            Default is increase_to_common_target
        """

        observe_str = """
(observe d_As_t d_As)
(observe d_P_t d_P)
    """

        reduced_inf_of_det_cases_str = ""
        d_As_str = ""
        d_P_str = ""
        d_Sym_ct_param_str = ""
        d_Sym_ct_str = ""

        if reduced_inf_of_det_cases:
            reduced_inf_of_det_cases_str = """(reduced_inf_of_det_cases_ct @reduced_inf_of_det_cases_ct1@ )"""
        if d_As:
            d_As_str = """(d_As @d_AsP_ct1@)"""
        if d_P:
            d_P_str = """(d_P @d_AsP_ct1@)"""

        if d_Sym_ct:

            ### Simple, not group specific
            if d_Sym_ct and not d_Sym_grp:
                d_Sym_ct_str = """(d_Sym @d_Sym_ct1@)"""

            ### Group specific
            if d_Sym_grp:

                for grp in grpList:

                    if d_Sym_grp_option == 'increase_to_grp_target':
                        d_Sym_ct_param_str = d_Sym_ct_param_str + """(param d_Sym_ct1_{grp} @d_Sym_ct1_{grp}@)""".format(
                            grp=grp)

                    if d_Sym_grp_option == 'increase_to_common_target':
                        d_Sym_ct_param_str = d_Sym_ct_param_str + "\n" + """(param d_Sym_ct1_{grp} @d_Sym_ct1@)""".format(
                            grp=grp)

                    if d_Sym_grp_option == 'common_increase':
                        d_Sym_ct_param_str = d_Sym_ct_param_str + "\n" + """(param d_Sym_ct1_{grp} (+ @d_Sym_change5_{grp}@ (* @d_Sym_change5_{grp}@ @d_Sym_ct1@ )))""".format(
                            grp=grp)

                    if d_Sym_grp_option == 'grp_specific_increase':
                        d_Sym_ct_param_str = d_Sym_ct_param_str + "\n" + """(param d_Sym_ct1_{grp} (+ @d_Sym_change5_{grp}@ (* @d_Sym_change5_{grp}@ @d_Sym_ct1_{grp}@ )))""".format(
                            grp=grp)

                    d_Sym_ct_str = d_Sym_ct_str + """(d_Sym_{grp} d_Sym_ct1_{grp})""".format(grp=grp)

        observe_str = observe_str + "\n" + d_Sym_ct_param_str
        change_param_str = reduced_inf_of_det_cases_str + d_As_str + d_P_str + d_Sym_ct_str
        time_event_str = """(time-event contact_tracing_start @contact_tracing_start_1@ ( {change_param} ))""".format(
            change_param=change_param_str)

        contactTracing_str = observe_str + "\n" + time_event_str

        return (contactTracing_str)

    def write_interventions(self, total_string):

        param_change_str = """
(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@)))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@)))
(time-event detection4 @detection_time_4@ ((d_Sys @d_Sys_incr4@)))
(time-event detection5 @detection_time_5@ ((d_Sys @d_Sys_incr5@)))
(time-event detection6 @detection_time_6@ ((d_Sys @d_Sys_incr6@)))
(time-event detection5 @detection_time_7@ ((d_Sys @d_Sys_incr7@)))
    """

        # TODO results in negative counts
        # (param cfr_change1_{age} (* @cfr_{age}@ (/ 2 3) ) )
        # (param cfr_change2_{age} (* @cfr_{age}@ (/ 1 3) ) )
        # (observe cfr_t_{age} cfr_{age})
        # (time-event cfr_adjust1_{age} @cfr_time_1@ ((cfr_{age} cfr_change1_{age}) (fraction_dead_{age} (/ cfr fraction_severe_{age})) (fraction_hospitalized_{age} (- 1 (+ fraction_critical fraction_dead_{age}))) (Kh1{age} (/ fraction_hospitalized_{age} time_to_hospitalization)) (Kh2{age} (/ fraction_critical_{age} time_to_hospitalization )) (Kh1_D{age} (/ fraction_hospitalized_{age} (- time_to_hospitalization time_D_Sys))) (Kh2_D{age} (/ fraction_critical_{age} (- time_to_hospitalization time_D_Sys) )) ))
        # (time-event cfr_adjust2_{age} @cfr_time_2@ ((cfr_{age} cfr_change2_{age}) (fraction_dead_{age} (/ cfr fraction_severe_{age})) (fraction_hospitalized_{age} (- 1 (+ fraction_critical fraction_dead_{age}))) (Kh1{age} (/ fraction_hospitalized_{age} time_to_hospitalization)) (Kh2{age} (/ fraction_critical_{age} time_to_hospitalization )) (Kh1_D{age} (/ fraction_hospitalized_{age} (- time_to_hospitalization time_D_Sys))) (Kh2_D{age} (/ fraction_critical_{age} (- time_to_hospitalization time_D_Sys) )) ))

        param_change_age_specific_str = ""
        for age in self.age_list:
            temp_str = """
(observe frac_crit_t_{age} fraction_critical_{age})
(observe fraction_hospitalized_t_{age} fraction_hospitalized_{age})
(observe fraction_dead_t_{age} fraction_dead_{age})

(time-event frac_crit_adjust1_{age} @crit_time_1@ ((fraction_critical_{age} @fraction_critical_incr1@) (fraction_hospitalized_{age} (- 1 (+ @fraction_critical_incr1@ fraction_dead_{age}))) (Kh1{age} (/ fraction_hospitalized_{age} time_to_hospitalization)) (Kh2{age} (/ fraction_critical_{age} time_to_hospitalization )) (Kh1_D{age} (/ fraction_hospitalized_{age} (- time_to_hospitalization time_D_Sys))) (Kh2_D{age} (/ fraction_critical_{age} (- time_to_hospitalization time_D_Sys) )) ))  
(time-event frac_crit_adjust2_{age} @crit_time_2@ ((fraction_critical_{age} @fraction_critical_incr2@) (fraction_hospitalized_{age} (- 1 (+ @fraction_critical_incr2@ fraction_dead_{age}))) (Kh1{age} (/ fraction_hospitalized_{age} time_to_hospitalization)) (Kh2{age} (/ fraction_critical_{age} time_to_hospitalization )) (Kh1_D{age} (/ fraction_hospitalized_{age} (- time_to_hospitalization time_D_Sys))) (Kh2_D{age} (/ fraction_critical_{age} (- time_to_hospitalization time_D_Sys) )) ))
(time-event frac_crit_adjust3_{age} @crit_time_3@ ((fraction_critical_{age} @fraction_critical_incr3@) (fraction_hospitalized_{age} (- 1 (+ @fraction_critical_incr3@ fraction_dead_{age}))) (Kh1{age} (/ fraction_hospitalized_{age} time_to_hospitalization)) (Kh2{age} (/ fraction_critical_{age} time_to_hospitalization )) (Kh1_D{age} (/ fraction_hospitalized_{age} (- time_to_hospitalization time_D_Sys))) (Kh2_D{age} (/ fraction_critical_{age} (- time_to_hospitalization time_D_Sys) )) )) 

(param fraction_dead_change1_{age} (* @fraction_dead_{age}@ (/ 2 3) ) )
(param fraction_dead_change2_{age} (* @fraction_dead_{age}@ (/ 1 3) ) )
(time-event fraction_dead_adjust1_{age} @cfr_time_1@ ((fraction_dead_{age} fraction_dead_change1_{age}) (fraction_hospitalized_{age} (- 1 (+ fraction_critical_{age} fraction_dead_{age}))) (Kh1{age} (/ fraction_hospitalized_{age} time_to_hospitalization)) (Kh2{age} (/ fraction_critical_{age} time_to_hospitalization )) (Kh1_D{age} (/ fraction_hospitalized_{age} (- time_to_hospitalization time_D_Sys))) (Kh2_D{age} (/ fraction_critical_{age} (- time_to_hospitalization time_D_Sys) )) )) 
(time-event fraction_dead_adjust2_{age} @cfr_time_2@ ((fraction_dead_{age} fraction_dead_change2_{age}) (fraction_hospitalized_{age} (- 1 (+ fraction_critical_{age} fraction_dead_{age}))) (Kh1{age} (/ fraction_hospitalized_{age} time_to_hospitalization)) (Kh2{age} (/ fraction_critical_{age} time_to_hospitalization )) (Kh1_D{age} (/ fraction_hospitalized_{age} (- time_to_hospitalization time_D_Sys))) (Kh2_D{age} (/ fraction_critical_{age} (- time_to_hospitalization time_D_Sys) )) )) 
    """.format(age=age)
            param_change_age_specific_str = param_change_age_specific_str + temp_str

        # TODO results in worse fitting?
        # param_change_str = param_change_str + param_change_age_specific_str

        ki_multiplier_change_str = ""
        for region in self.region_list:
            temp_str = """
(param Ki_red3a_{region} (* Ki_{region} @ki_multiplier_3a_{region}@))
(param Ki_red3b_{region} (* Ki_{region} @ki_multiplier_3b_{region}@))
(param Ki_red3c_{region} (* Ki_{region} @ki_multiplier_3c_{region}@))
(param Ki_red4_{region} (* Ki_{region} @ki_multiplier_4_{region}@))
(param Ki_red5_{region} (* Ki_{region} @ki_multiplier_5_{region}@))
(param Ki_red6_{region} (* Ki_{region} @ki_multiplier_6_{region}@))
(param Ki_red7_{region} (* Ki_{region} @ki_multiplier_7_{region}@))
(param Ki_red8_{region} (* Ki_{region} @ki_multiplier_8_{region}@))
(param Ki_red9_{region} (* Ki_{region} @ki_multiplier_9_{region}@))
(param Ki_red10_{region} (* Ki_{region} @ki_multiplier_10_{region}@))
(param Ki_red11_{region} (* Ki_{region} @ki_multiplier_11_{region}@))
(param Ki_red12_{region} (* Ki_{region} @ki_multiplier_12_{region}@))
(param Ki_red13_{region} (* Ki_{region} @ki_multiplier_13_{region}@))

(param backtonormal_multiplier_1_{region}  (/ (- Ki_red6_{region}  Ki_red4_{region} ) (- Ki_{region} Ki_red4_{region} ) ) )  
(observe backtonormal_multiplier_1_{region} backtonormal_multiplier_1_{region})

(time-event ki_multiplier_change_3a @ki_multiplier_time_3a@ ((Ki_{region} Ki_red3a_{region})))
(time-event ki_multiplier_change_3b @ki_multiplier_time_3b@ ((Ki_{region} Ki_red3b_{region})))
(time-event ki_multiplier_change_3c @ki_multiplier_time_3c@ ((Ki_{region} Ki_red3c_{region})))
(time-event ki_multiplier_change_4 @ki_multiplier_time_4@ ((Ki_{region} Ki_red4_{region})))
(time-event ki_multiplier_change_5 @ki_multiplier_time_5@ ((Ki_{region} Ki_red5_{region})))
(time-event ki_multiplier_change_6 @ki_multiplier_time_6@ ((Ki_{region} Ki_red6_{region})))
(time-event ki_multiplier_change_7 @ki_multiplier_time_7@ ((Ki_{region} Ki_red7_{region})))
(time-event ki_multiplier_change_8 @ki_multiplier_time_8@ ((Ki_{region} Ki_red8_{region})))
(time-event ki_multiplier_change_9 @ki_multiplier_time_9@ ((Ki_{region} Ki_red9_{region})))
(time-event ki_multiplier_change_10 @ki_multiplier_time_10@ ((Ki_{region} Ki_red10_{region})))
(time-event ki_multiplier_change_11 @ki_multiplier_time_11@ ((Ki_{region} Ki_red11_{region})))
(time-event ki_multiplier_change_12 @ki_multiplier_time_12@ ((Ki_{region} Ki_red12_{region})))
(time-event ki_multiplier_change_13 @ki_multiplier_time_13@ ((Ki_{region} Ki_red13_{region})))
                """.format(region=region)
            ki_multiplier_change_str = ki_multiplier_change_str + temp_str

        rollback_str = ""
        for region in self.region_list:
            temp_str = """
(time-event ki_multiplier_change_rollback @socialDistance_rollback_time@ ((Ki_{region} Ki_red7_{region})))
                    """.format(region=region)
            rollback_str = rollback_str + temp_str

        rollbacktriggered_str = ""
        for region in self.region_list:
            temp_str = """
(state-event rollbacktrigger_{region} (and (> time @today@) (> {channel}_{region} (* @trigger_{region}@ @capacity_multiplier@)) ) ((Ki_{region} Ki_red7_{region})))
                        """.format(channel=self.trigger_channel, region=region)
            rollbacktriggered_str = rollbacktriggered_str + temp_str

        rollbacktriggered_delay_str = ""
        for region in self.region_list:
            regionout = covidModel.sub(region)
            temp_str = """
(param time_of_trigger_{region} 10000)
(state-event rollbacktrigger_{region} (and (> time @today@) (> crit_det_{region} (* @trigger_{region}@ @capacity_multiplier@)) ) ((time_of_trigger_{region} time)))
(func time_since_trigger_{region} (- time time_of_trigger_{region}))
(state-event apply_rollback_{region} (> (- time_since_trigger_{region} @trigger_delay_days@) 0) ((Ki_{region} Ki_red7_{region})))   
(observe triggertime_{regionout} time_of_trigger_{region})
                       """.format(channel=self.trigger_channel, regionout=regionout, region=region)
            rollbacktriggered_delay_str = rollbacktriggered_delay_str + temp_str

        d_Sym_change_str = """
(param d_Sym @d_Sym@)
(observe d_Sym_t d_Sym)

(time-event d_Sym_change1 @d_Sym_change_time_1@ ((d_Sym @d_Sym_change1@)))
(time-event d_Sym_change2 @d_Sym_change_time_2@ ((d_Sym @d_Sym_change2@)))
(time-event d_Sym_change3 @d_Sym_change_time_3@ ((d_Sym @d_Sym_change3@)))
(time-event d_Sym_change4 @d_Sym_change_time_4@ ((d_Sym @d_Sym_change4@)))
(time-event d_Sym_change5 @d_Sym_change_time_5@ ((d_Sym @d_Sym_change5@)))
    """

        interventionSTOP_str = ""
        for region in self.region_list:
            temp_str = """
(param Ki_back_{region} (* Ki_{region} @backtonormal_multiplier@))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{region} Ki_back_{region})))
            """.format(region=region)
            interventionSTOP_str = interventionSTOP_str + temp_str

        # % change from lowest transmission level - immediate
        # starting point is lowest level of transmission  Ki_red4
        interventionSTOP_adj_str = ""
        for region in self.region_list:
            temp_str = """
(param Ki_back_{region} (+ Ki_red7_{region} (* @backtonormal_multiplier@ (- Ki_{region} Ki_red7_{region}))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{region} Ki_back_{region})))
            """.format(region=region)
            interventionSTOP_adj_str = interventionSTOP_adj_str + temp_str

        # % change from current transmission level - immediate
        # starting point is current level of transmission  Ki_red6
        interventionSTOP_adj2_str = ""
        for region in self.region_list:
            temp_str = """
(param Ki_back_{region} (+ Ki_red7_{region} (* @backtonormal_multiplier@ (- Ki_{region} Ki_red7_{region}))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki_{region} Ki_back_{region})))
            """.format(region=region)
            interventionSTOP_adj2_str = interventionSTOP_adj2_str + temp_str

        # gradual reopening from 'lowest' transmission level,  Ki_red6 == Ki_back1
        gradual_reopening_str = ""
        for region in self.region_list:
            temp_str = """
(param backtonormal_multiplier_1_adj_{region}  (- @backtonormal_multiplier@ backtonormal_multiplier_1_{region} ))
(observe backtonormal_multiplier_1_adj_{region}  backtonormal_multiplier_1_adj_{region})

(param Ki_back2_{region} (+ Ki_red6_{region} (* backtonormal_multiplier_1_adj_{region} 0.3333 (- Ki_{region} Ki_red4_{region}))))
(param Ki_back3_{region} (+ Ki_red6_{region} (* backtonormal_multiplier_1_adj_{region} 0.6666 (- Ki_{region} Ki_red4_{region}))))
(param Ki_back4_{region} (+ Ki_red6_{region} (* backtonormal_multiplier_1_adj_{region} 1.00 (- Ki_{region} Ki_red4_{region}))))
(time-event gradual_reopening2 @gradual_reopening_time1@ ((Ki_{region} Ki_back2_{region})))
(time-event gradual_reopening3 @gradual_reopening_time2@ ((Ki_{region} Ki_back3_{region})))
(time-event gradual_reopening4 @gradual_reopening_time3@ ((Ki_{region} Ki_back4_{region})))
            """.format(region=region)
            gradual_reopening_str = gradual_reopening_str + temp_str

        # gradual reopening from 'current' transmission level
        gradual_reopening2_str = ""
        for region in self.region_list:
            temp_str = """
(param Ki_back1_{region} (+ Ki_red7_{region} (* @reopening_multiplier_4@ 0.25 (- Ki_{region} Ki_red7_{region}))))
(param Ki_back2_{region} (+ Ki_red7_{region} (* @reopening_multiplier_4@ 0.50 (- Ki_{region} Ki_red7_{region}))))
(param Ki_back3_{region} (+ Ki_red7_{region} (* @reopening_multiplier_4@ 0.75 (- Ki_{region} Ki_red7_{region}))))
(param Ki_back4_{region} (+ Ki_red7_{region} (* @reopening_multiplier_4@ 1.00 (- Ki_{region} Ki_red7_{region}))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki_{region} Ki_back1_{region})))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki_{region} Ki_back2_{region})))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki_{region} Ki_back3_{region})))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki_{region} Ki_back4_{region})))
            """.format(region=region)
            gradual_reopening2_str = gradual_reopening2_str + temp_str

        # gradual reopening from 'current' transmission level with region-specific reopening
        gradual_reopening3_str = ""
        for region in self.region_list:
            temp_str = """
(param Ki_back1_{region} (+ Ki_red7_{region} (* @reopening_multiplier_4_{region}@ 0.25 (- Ki_{region} Ki_red7_{region}))))
(param Ki_back2_{region} (+ Ki_red7_{region} (* @reopening_multiplier_4_{region}@ 0.50 (- Ki_{region} Ki_red7_{region}))))
(param Ki_back3_{region} (+ Ki_red7_{region} (* @reopening_multiplier_4_{region}@ 0.75 (- Ki_{region} Ki_red7_{region}))))
(param Ki_back4_{region} (+ Ki_red7_{region} (* @reopening_multiplier_4_{region}@ 1.00 (- Ki_{region} Ki_red7_{region}))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki_{region} Ki_back1_{region})))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki_{region} Ki_back2_{region})))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki_{region} Ki_back3_{region})))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki_{region} Ki_back4_{region})))
            """.format(region=region)
            gradual_reopening3_str = gradual_reopening3_str + temp_str

        improveHS_str = covidModel.define_change_detection_and_isolation(grpList=self.region_list,
                                                                         reduced_inf_of_det_cases=False,
                                                                         d_As=False,
                                                                         d_P=False,
                                                                         d_Sym_ct=True,
                                                                         d_Sym_grp=True,
                                                                         d_Sym_grp_option='increase_to_common_target')

        contactTracing_str = covidModel.define_change_detection_and_isolation(grpList=self.region_list,
                                                                              reduced_inf_of_det_cases=True,
                                                                              d_As=True,
                                                                              d_P=True,
                                                                              d_Sym_ct=False,
                                                                              d_Sym_grp=False,
                                                                              d_Sym_grp_option=None)

        contactTracing_improveHS_str = covidModel.define_change_detection_and_isolation(grpList=self.region_list,
                                                                                        reduced_inf_of_det_cases=True,
                                                                                        d_As=True,
                                                                                        d_P=True,
                                                                                        d_Sym_ct=True,
                                                                                        d_Sym_grp=True,
                                                                                        d_Sym_grp_option='increase_to_common_target')

        change_uniformtestDelay_str = """
    (time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} {} {} {} {} ))
        """.format("(time_D @change_testDelay_1@)",
                   "(Ksys_D (/ 1 time_D))",
                   "(Ksym_D (/ 1 time_D))",
                   "(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D)))",
                   "(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D) ))",
                   "(Kh3_D (/ fraction_dead_{age} (- time_to_hospitalization time_D)))",
                   "(Kr_m_D (/ 1 (- recovery_time_mild time_D )))")

        change_testDelay_Sym_str = """
    (time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} ))
        """.format("(time_D_Sym @change_testDelay_Sym_1@)",
                   "(Ksym_D (/ 1 time_D_Sym))",
                   "(Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym )))")

        change_testDelay_Sys_str = """
    (time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} {} {} ))
        """.format("(time_D_Sys @change_testDelay_Sys_1@)",
                   "(Ksys_D (/ 1 time_D_Sys))",
                   "(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys)))",
                   "(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) ))",
                   "(Kh3_D (/ fraction_dead_{age} (- time_to_hospitalization time_D_Sys)))")

        change_testDelay_As_str = """
    (time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} ))
        """.format("(time_D_As @change_testDelay_As_1@)",
                   "(Kl_D (/ 1 time_D_As))",
                   "(Kr_a_D (/ 1 (- recovery_time_asymp time_D_As )))")

        fittedTimeEvents_str = param_change_str + ki_multiplier_change_str + d_Sym_change_str

        if self.add_interventions == "interventionStop":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_str)
        if self.add_interventions == "interventionSTOP_adj":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj_str)
        if self.add_interventions == "interventionSTOP_adj2":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj2_str)
        if self.add_interventions == "gradual_reopening":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening_str)
        if self.add_interventions == "gradual_reopening2":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str)
        if self.add_interventions == "gradual_reopening3":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening3_str)
        if self.add_interventions == "baseline":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str)
        if self.add_interventions == "rollback":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + rollback_str)
        if self.add_interventions == "reopen_rollback":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + interventionSTOP_adj2_str + rollback_str)
        if self.add_interventions == "reopen_contactTracing":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + gradual_reopening2_str + contactTracing_str)
        if self.add_interventions == "reopen_contactTracing_improveHS":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + gradual_reopening2_str + contactTracing_improveHS_str)
        if self.add_interventions == "reopen_improveHS":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + gradual_reopening2_str + improveHS_str)
        if self.add_interventions == "contactTracing":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + contactTracing_str)
        if self.add_interventions == "contactTracing_improveHS":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + contactTracing_improveHS_str)
        if self.add_interventions == "improveHS":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + improveHS_str)
        if self.add_interventions == "rollbacktriggered":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + gradual_reopening2_str + rollbacktriggered_str)
        if self.add_interventions == "rollbacktriggered_delay":
            total_string = total_string.replace(';[INTERVENTIONS]',
                                                fittedTimeEvents_str + gradual_reopening3_str + rollbacktriggered_delay_str)

        # if scenarioName == "gradual_contactTracing" :
        #    total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + contactTracing_gradual_str)

        if self.change_testDelay != None:
            if self.change_testDelay == "uniform":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_uniformtestDelay_str)
            if self.change_testDelay == "As":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str)
            if self.change_testDelay == "Sym":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sym_str)
            if self.change_testDelay == "Sys":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sys_str)
            if self.change_testDelay == "AsSym":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]',
                                                    change_testDelay_As_str + '\n' + change_testDelay_Sym_str)
            if self.change_testDelay == "SymSys":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]',
                                                    change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)
            if self.change_testDelay == "AsSymSys":
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]',
                                                    change_testDelay_As_str + '\n' + change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)

        return total_string

    def generate_emodl(self):

        if self.emodl_name is None:
            emodl_name = f'{self.model}_{self.add_interventions}'
            file_output = os.path.join(self.emodl_dir, f'{emodl_name}.emodl')
        else:
            file_output = os.path.join(self.emodl_dir, f'{self.emodl_name}.emodl')
        if os.path.exists(file_output):
            os.remove(file_output)

        model_name = "seir.emodl"
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
        age_specific_param_string = ""
        total_string = total_string + header_str

        for region in self.region_list:
            total_string = total_string + "\n(locale site-{})\n".format(region)
            total_string = total_string + "(set-locale site-{})\n".format(region)
            reaction_string = covidModel.write_exposure_reaction8(region) + '\n' + reaction_string

            for age in self.age_list:
                # species_init = write_species_init_2grp(age=age, region_dic=region_dic, region=key)
                species_init = covidModel.set_population(self, age, region)
                species = covidModel.write_species(self, age, region)
                total_string = total_string + species_init + species

        for age, region in [(x, y) for x in self.age_list for y in self.region_list]:
            observe_string = observe_string + covidModel.write_observe(self, age, region)
            if self.add_migration:
                if age == "age20to29" or age == "age30to39" or age == "age40to49" or age == "age50to59" or age == "age60to69":
                    reaction_string = reaction_string + covidModel.write_travel_reaction(self, age, region)
            reaction_string = reaction_string + covidModel.write_reactions(self, age, region)
            functions_string = functions_string + covidModel.write_functions(self, age, region)
            param_string = param_string + covidModel.write_Ki_timevents(self, age, region)

        for age in self.age_list:
            age_specific_param_string = age_specific_param_string + covidModel.write_age_specific_param(self, age)

        param_string = covidModel.write_params(self) + \
                       age_specific_param_string + param_string + \
                       covidModel.write_observed_param(self) + \
                       covidModel.write_N_population(self) + \
                       covidModel.write_contact_matrix(self)

        if self.add_migration:
            param_string = param_string + covidModel.write_migration_param(self)

        functions_string = functions_string + covidModel.write_All(self)
        intervention_string = ";[INTERVENTIONS]\n;[ADDITIONAL_TIMEEVENTS]"

        total_string = f'{total_string}\n\n' \
                       f'{species_string}\n\n' \
                       f'{functions_string}\n\n' \
                       f'{observe_string}\n\n' \
                       f'{param_string}\n\n' \
                       f'{intervention_string}\n\n' \
                       f'{reaction_string}\n\n' \
                       f'{footer_str}\n\n'

        ### Custom adjustments for EMS 6 (earliest start date)
        # total_string = total_string.replace('(species As::EMS_6 0)', '(species As::EMS_6 1)')
        ### Add interventions (optional)
        if self.add_interventions != None:
            total_string = covidModel.write_interventions(self, total_string)

        emodl = open(file_output, "w")
        emodl.write(total_string)
        emodl.close()
        if (os.path.exists(file_output)):
            print("{} file was successfully created".format(file_output))
        else:
            print("{} file was NOT created".format(file_output))
        return emodl_name

    def showOptions():
        # import json
        model_options = {'expandModel': ("uniformtestDelay", "testDelay_SymSys", "testDelay_AsSymSys"),
                         'observeLevel': ('primary', 'secondary', 'tertiary', 'all'),
                         'add_migration': ('True', 'False'),
                         'add_interventions': ("baseline",
                                               "rollback",
                                               "reopen_rollback",
                                               "rollbacktriggered_delay",
                                               "gradual_reopening",
                                               "gradual_reopening2",
                                               "interventionSTOP",
                                               "interventionSTOP_adj",
                                               "rollbacktriggered",
                                               "contactTracing",
                                               "improveHS",
                                               "reopen_improveHS",
                                               "contactTracing_improveHS"
                                               "reopen_contactTracing_improveHS"),
                         'change_testDelay': ("None", "Sym", "AsSym"),
                         'trigger_channel': ("None", "critical", "crit_det", "hospitalized", "hosp_det")}
        return print(json.dumps(model_options, indent=4, sort_keys=True))
