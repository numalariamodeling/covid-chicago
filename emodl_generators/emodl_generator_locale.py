import os
import sys
import re
import json
import yaml
import pandas as pd

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

    def __init__(self, expandModel, observeLevel='primary', add_interventions='baseline',
                 change_testDelay=False, intervention_config='intervention_emodl_config.yaml',
                 add_migration=False, fit_params=None,emodl_name=None, git_dir=git_dir):
        self.model = 'locale'
        self.grpList = ['EMS_1', 'EMS_2', 'EMS_3', 'EMS_4', 'EMS_5', 'EMS_6', 'EMS_7', 'EMS_8', 'EMS_9', 'EMS_10',
                        'EMS_11']
        self.expandModel = expandModel
        self.add_migration = add_migration
        self.observeLevel = observeLevel
        self.add_interventions = add_interventions
        self.change_testDelay = change_testDelay
        self.intervention_config = intervention_config
        self.emodl_name = emodl_name
        self.startdate = pd.Timestamp('2020-02-13')
        self.emodl_dir = os.path.join(git_dir, 'emodl')
        self.fit_param = fit_params  # Currenly support single parameter only

    def get_configs(key, config_file='intervention_emodl_config.yaml'):
        yaml_file = open(os.path.join('./experiment_configs', config_file))
        config_dic = yaml.safe_load(yaml_file)
        config_dic = config_dic[key]
        return config_dic

    ## For postprocessing that splits by '_', it is easier if EMS are names EMS-1 not EMS_1
    ## This might change depending on the postprocessing
    def sub(x):
        xout = re.sub('_', '-', str(x), count=1)
        return xout

    def DateToTimestep(date, startdate):
        datediff = date - startdate
        timestep = datediff.days
        return timestep

    def write_species(self, grp):
        state_SE = ('S', 'E')
        state_nosymptoms = ('As', 'As_det1', 'P', 'P_det')
        state_symptoms = ('Sym', 'Sym_det2', 'Sys', 'Sys_det3')
        # state_hospitalized = ('H1', 'H2', 'H3', 'H1_det3', 'H2_det3', 'H3_det3')
        state_hospitalized = ('H1', 'H2pre', 'H2post', 'H3', 'H1_det3', 'H2pre_det3', 'H2post_det3', 'H3_det3')
        state_critical = ('C2', 'C3', 'C2_det3', 'C3_det3')
        state_deaths = ('D3', 'D3_det3')
        state_recoveries = ('RAs', 'RSym', 'RH1', 'RC2', 'RAs_det1', 'RSym_det2', 'RH1_det3', 'RC2_det3')
        state_testDelay_SymSys = ('Sym_preD', 'Sys_preD')
        state_testDelay_AsSymSys = (
        'As_preD', 'Sym_preD', 'Sym_det2a', 'Sym_det2b', 'Sys_preD', 'Sys_det3a', 'Sys_det3b')
        state_variables = state_SE + state_nosymptoms + state_symptoms + state_hospitalized + state_critical + state_deaths + state_recoveries

        if self.expandModel == "SymSys" or self.expandModel == "uniform":
            state_variables = state_variables + state_testDelay_SymSys
        if self.expandModel == "AsSymSys":
            state_variables = state_variables + state_testDelay_AsSymSys

        def write_species_emodl():
            grp_suffix = "::{grp}"
            grp_suffix2 = "_{grp}"

            species_emodl = ""
            for state in state_variables:
                if state == "S":
                    species_emodl = species_emodl + f'(species {state}{grp_suffix} @speciesS{grp_suffix2}@)\n'
                else:
                    species_emodl = species_emodl + f'(species {state}{grp_suffix} 0)\n'

            return species_emodl

        def write_species_str(species_emodl, grp):
            grp = str(grp)
            species_str = species_emodl.format(grp=grp)
            return species_str

        species_emodl = write_species_emodl()
        species_str = write_species_str(species_emodl, grp)
        return species_str

    def get_channels(self):
        """Channels to exclude from final list"""
        channels_not_observe = ['presymp_det','presymp_cumul','presymp_det_cumul']

        """Define channels to observe """
        primary_channels_notdet = ['susceptible','infected','recovered','symp_mild','symp_severe','hosp','crit','deaths']
        secondary_channels_notdet = ['exposed','asymp','presymp','detected']
        tertiary_channels = ['infectious_undet', 'infectious_det', 'infectious_det_symp', 'infectious_det_AsP']

        channels_notdet = primary_channels_notdet
        if self.observeLevel != 'primary':
            channels_notdet = channels_notdet + secondary_channels_notdet

        channels_det = [channel + '_det' for channel in channels_notdet if channel not in ['susceptible', 'exposed','detected']]
        channels_cumul = [channel + '_cumul' for channel in channels_notdet + channels_det
                          if channel not in ['susceptible','exposed', 'recovered', 'deaths', 'recovered_det']]

        channels = channels_notdet + channels_det + channels_cumul
        if self.observeLevel == 'tertiary':
            channels = channels + tertiary_channels

        channels = [channel for channel in channels if channel not in channels_not_observe]
        channels = channels + ['asymp_cumul','asymp_det_cumul'] #workarund for channel error message
        return  list(set(channels))

    def write_observe(self, grp):
        grp = str(grp)
        grpout = covidModel.sub(grp)

        channels = covidModel.get_channels(self)

        def write_observe_emodl():
            #grp_suffix = "::{grp}"
            #grp_suffix2 = "_{grp}"

            observe_emodl = ""
            for channel in channels:
                if channel == 'crit':
                    channel = 'critical'
                if channel == 'hosp':
                    channel = 'hospitalized'

                if channel == "susceptible":
                    observe_emodl = observe_emodl + f'(observe {channel}_{grpout} S::{grp})\n'
                elif channel == "exposed":
                    observe_emodl = observe_emodl + f'(observe {channel}_{grpout} E::{grp})\n'
                elif channel == "deaths_det":
                    observe_emodl = observe_emodl + f'(observe {channel}_{grpout} D3_det3::{grp})\n'
                else:
                    observe_emodl = observe_emodl + f'(observe {channel}_{grpout} {channel}_{grp})\n'

            return observe_emodl

        def write_observe_str(observe_emodl, grp):
            grp = str(grp)
            observe_str = observe_emodl.format(grp=grp)
            return observe_str

        observe_emodl = write_observe_emodl()
        observe_str = write_observe_str(observe_emodl, grp)
        return observe_str

    def write_functions(self, grp):
        grp = str(grp)

        func_dic = {'presymp_{grp}': ['P::{grp}', 'P_det::{grp}'],
                    'hospitalized_{grp}': ['H1::{grp}', 'H2pre::{grp}', 'H2post::{grp}', 'H3::{grp}', 'H1_det3::{grp}', 'H2pre_det3::{grp}', 'H2post_det3::{grp}', 'H3_det3::{grp}'],
                    'hosp_det_{grp}': ['H1_det3::{grp}', 'H2pre_det3::{grp}', 'H2post_det3::{grp}', 'H3_det3::{grp}'],
                    'critical_{grp}': ['C2::{grp}', 'C3::{grp}', 'C2_det3::{grp}', 'C3_det3::{grp}'],
                    'crit_det_{grp}': ['C2_det3::{grp}', 'C3_det3::{grp}'],
                    'deaths_{grp}': ['D3::{grp}', 'D3_det3::{grp}'],
                    'recovered_{grp}': ['RAs::{grp}', 'RSym::{grp}', 'RH1::{grp}', 'RC2::{grp}', 'RAs_det1::{grp}', 'RSym_det2::{grp}', 'RH1_det3::{grp}', 'RC2_det3::{grp}'],
                    'recovered_det_{grp}': ['RAs_det1::{grp}', 'RSym_det2::{grp}', 'RH1_det3::{grp}', 'RC2_det3::{grp}'],
                    'asymp_cumul_{grp}': ['asymp_{grp}', 'RAs::{grp}', 'RAs_det1::{grp}'],
                    'asymp_det_cumul_{grp}': ['As_det1::{grp}', 'RAs_det1::{grp}'],
                    'symp_mild_cumul_{grp}': ['symp_mild_{grp}', 'RSym::{grp}', 'RSym_det2::{grp}'],
                    'symp_mild_det_cumul_{grp}': ['symp_mild_det_{grp}', 'RSym_det2::{grp}'],
                    'symp_severe_cumul_{grp}': ['symp_severe_{grp}', 'hospitalized_{grp}', 'critical_{grp}', 'deaths_{grp}', 'RH1::{grp}', 'RC2::{grp}', 'RH1_det3::{grp}', 'RC2_det3::{grp}'],
                    'symp_severe_det_cumul_{grp}': ['symp_severe_det_{grp}', 'hosp_det_{grp}', 'crit_det_{grp}', 'D3_det3::{grp}', ' RH1_det3::{grp}', 'RC2_det3::{grp}'],
                    'hosp_cumul_{grp}': ['hospitalized_{grp}', 'critical_{grp}', 'deaths_{grp}', 'RH1::{grp}', 'RC2::{grp}', 'RH1_det3::{grp}', 'RC2_det3::{grp}'],
                    'hosp_det_cumul_{grp}': ['H1_det3::{grp}', 'H2pre_det3::{grp}', 'H2post_det3::{grp}', ' H3_det3::{grp}', 'C2_det3::{grp}', 'C3_det3::{grp}', 'D3_det3::{grp}', ' RH1_det3::{grp}', ' RC2_det3::{grp}'],
                    'crit_cumul_{grp}': ['deaths_{grp}', 'critical_{grp}', 'RC2::{grp}', 'RC2_det3::{grp}'],
                    'crit_det_cumul_{grp}': ['C2_det3::{grp}', 'C3_det3::{grp}', 'D3_det3::{grp}', 'RC2_det3::{grp}'],
                    'detected_cumul_{grp}': ['As_det1::{grp}', 'Sym_det2::{grp}', 'Sys_det3::{grp}', 'H1_det3::{grp}', 'H2pre_det3::{grp}', ' H2post_det3::{grp}', ' C2_det3::{grp}', 'C3_det3::{grp}', 'RAs_det1::{grp}', 'RSym_det2::{grp}', 'RH1_det3::{grp}', 'RC2_det3::{grp}', 'D3_det3::{grp}'],
                    'infected_{grp}': ['infectious_det_{grp}', 'infectious_undet_{grp}', 'H1_det3::{grp}', 'H2pre_det3::{grp}', 'H2post_det3::{grp}', 'H3_det3::{grp}', 'C2_det3::{grp}', 'C3_det3::{grp}'],
                    'infected_det_{grp}': ['infectious_det_{grp}', 'H1_det3::{grp}', 'H2pre_det3::{grp}', 'H2post_det3::{grp}',  'H3_det3::{grp}', 'C2_det3::{grp}', 'C3_det3::{grp}'],
                    'infected_cumul_{grp}': ['infected_{grp}', 'recovered_{grp}', 'deaths_{grp}'],
                    'infected_det_cumul_{grp}': ['infected_det_{grp}', 'recovered_det_{grp}', 'D3_det3::{grp}']
                    }

        func_dic_base = {'asymp_{grp}': ['As::{grp}', 'As_det1::{grp}'],
                         'symp_mild_{grp}': ['Sym::{grp}', 'Sym_det2::{grp}'],
                         'symp_severe_{grp}': ['Sys::{grp}', 'Sys_det3::{grp}'],
                         'detected_{grp}': ['As_det1::{grp}', 'Sym_det2::{grp}', 'Sys_det3::{grp}', 'H1_det3::{grp}', 'H2pre_det3::{grp}', 'H2post_det3::{grp}', ' H3_det3::{grp}', 'C2_det3::{grp}', 'C3_det3::{grp}'],
                         'infectious_undet_{grp}': ['As::{grp}', 'P::{grp}', 'Sym::{grp}', 'Sys::{grp}', 'H1::{grp}', 'H2pre::{grp}', 'H2post::{grp}', ' H3::{grp}', 'C2::{grp}', 'C3::{grp}'],
                         'infectious_det_{grp}': ['As_det1::{grp}', 'P_det::{grp}', 'Sym_det2::{grp}', 'Sys_det3::{grp}'],
                         'infectious_det_symp_{grp}': ['Sym_det2::{grp}', 'Sys_det3::{grp}'],
                         'infectious_det_AsP_{grp}': ['As_det1::{grp}', 'P_det::{grp}']
                         }

        func_dic_SymSys = {'asymp_{grp}': ['As::{grp}', 'As_det1::{grp}'],
                           'symp_mild_{grp}': ['Sym::{grp}', 'Sym_preD::{grp}', 'Sym_det2::{grp}'],
                           'symp_mild_det_{grp}': ['Sym_preD::{grp}', 'Sym_det2::{grp}'],
                           'symp_severe_{grp}': ['Sys::{grp}', 'Sys_preD::{grp}', 'Sys_det3::{grp}'],
                           'symp_severe_det_{grp}': ['Sys_preD::{grp}', 'Sys_det3::{grp}'],
                           'detected_{grp}': ['As_det1::{grp}', 'Sym_det2::{grp}', 'Sys_det3::{grp}', 'H1_det3::{grp}', 'H2pre_det3::{grp}', 'H2post_det3::{grp}', ' H3_det3::{grp}', 'C2_det3::{grp}', 'C3_det3::{grp}'],
                           'infectious_undet_{grp}': ['As::{grp}', 'P::{grp}', 'Sym_preD::{grp}', 'Sym::{grp}', 'Sys_preD::{grp}', 'Sys::{grp}', 'H1::{grp}', 'H2pre::{grp}', ' H2post::{grp}', ' H3::{grp}', 'C2::{grp}', 'C3::{grp}'],
                           'infectious_det_{grp}': ['As_det1::{grp}', 'P_det::{grp}', 'Sym_det2::{grp}', 'Sys_det3::{grp}'],
                           'infectious_det_symp_{grp}': ['Sym_det2::{grp}', 'Sys_det3::{grp}'],
                           'infectious_det_AsP_{grp}': ['As_det1::{grp}', 'P_det::{grp}']
                           }

        func_dic_AsSymSys = {'asymp_{grp}': ['As_preD::{grp}', 'As::{grp}', 'As_det1::{grp}'],
                             'symp_mild_{grp}': ['Sym::{grp}', 'Sym_preD::{grp}', 'Sym_det2a::{grp}', 'Sym_det2b::{grp}'],
                             'symp_mild_det_{grp}': ['Sym_preD::{grp}', 'Sym_det2a::{grp}', 'Sym_det2b::{grp}'],
                             'symp_severe_{grp}': ['Sys::{grp}', 'Sys_preD::{grp}', 'Sys_det3a::{grp}', 'Sys_det3b::{grp}'],
                             'symp_severe_det_{grp}': ['Sys_preD::{grp}', 'Sys_det3a::{grp}', 'Sys_det3b::{grp}'],
                             'detected_{grp}': ['As_det1::{grp}', 'Sym_det2a::{grp}', 'Sym_det2b::{grp}', 'Sys_det3a::{grp}', 'Sys_det3b::{grp}', 'H1_det3::{grp}', 'H2pre_det3::{grp}', 'H2post_det3::{grp}', 'H3_det3::{grp}', 'C2_det3::{grp}', 'C3_det3::{grp}'],
                             'infectious_undet_{grp}': ['As_preD::{grp}', 'As::{grp}', 'P::{grp}', 'Sym::{grp}', 'Sym_preD::{grp}', 'Sys::{grp}', 'Sys_preD::{grp}', 'H1::{grp}', 'H2pre::{grp}', 'H2post::{grp}', 'H3::{grp}', 'C2::{grp}', 'C3::{grp}'],
                             'infectious_det_{grp}': ['As_det1::{grp}', 'P_det::{grp}', 'Sym_det2a::{grp}', 'Sym_det2b::{grp}', 'Sys_det3a::{grp}', 'Sys_det3b::{grp}'],
                             'infectious_undet_symp_{grp}': ['P::{grp}', 'Sym::{grp}', 'Sym_preD::{grp}', 'Sys::{grp}', 'Sys_preD::{grp}', 'H1::{grp}', 'H2pre::{grp}', 'H2post::{grp}', 'H3::{grp}', 'C2::{grp}', 'C3::{grp}'],
                             'infectious_undet_As_{grp}': ['As_preD::{grp}', 'As::{grp}'],
                             'infectious_det_symp_{grp}': ['Sym_det2a::{grp}', 'Sym_det2b::{grp}', 'Sys_det3a::{grp}', 'Sys_det3b::{grp}'],
                             'infectious_det_AsP_{grp}': ['As_det1::{grp}', 'P_det::{grp}']
                             }

        func_str = f'(func deaths_det_cumul_{grp}  D3_det3::{grp})\n(func asymp_det_{grp}  As_det1::{grp} )'
        if self.expandModel == "SymSys" or self.expandModel == "uniform":
            func_dic_SymSys.update(func_dic)
            func_dic_all = func_dic_SymSys
        elif self.expandModel == "AsSymSys":
            func_dic_AsSymSys.update(func_dic)
            func_dic_all = func_dic_AsSymSys
        else:
            func_str = func_str + f'(func symp_mild_det_{grp}  Sym_det2::{grp})\n' \
                                  f'(func symp_severe_det_{grp}  Sys_det3::{grp})\n'
            func_dic_base.update(func_dic)
            func_dic_all = func_dic_base

        for key in func_dic_all.keys():
            func_str = func_str + f"(func {key} (+ {' '.join(func_dic_all[key])}))\n".format(grp=grp)

        return func_str

    ###
    def write_params(self):
        yaml_sampled_param = list(covidModel.get_configs(key ='sampled_parameters', config_file='extendedcobey_200428.yaml').keys())
        yaml_sampled_param_str = ''.join([f'(param {param} @{param}@)\n' for param in yaml_sampled_param])

        """calculated parameters"""
        param_dic = {'fraction_hospitalized' : '(- 1 (+ fraction_critical fraction_dead))',
                     'Kr_a' : '(/ 1 recovery_time_asymp)',
                     'Kr_m' : '(/ 1 recovery_time_mild)',
                     'Kl' : '(/ (- 1 fraction_symptomatic ) time_to_infectious)',
                     'Ks' :'(/ fraction_symptomatic  time_to_infectious)',
                     'Ksys' :'(* fraction_severe (/ 1 time_to_symptoms))',
                     'Ksym' :'(* (- 1 fraction_severe) (/ 1 time_to_symptoms))',
                     'Km' :'(/ 1 time_to_death)',
                     'Kc' :'(/ 1 time_to_critical)',
                     'Kr_hc' :'(/ 1 recovery_time_postcrit)',
                     'Kr_h' :'(/ 1 recovery_time_hosp)',
                     'Kr_c' :'(/ 1 recovery_time_crit)'
                     }

        param_dic_base = {'Kh1':'(/ fraction_hospitalized time_to_hospitalization)',
                          'Kh2':'(/ fraction_critical time_to_hospitalization )',
                          'Kh3':'(/ fraction_dead  time_to_hospitalization)'
                          }

        param_dic_uniform = {'time_D':'@time_to_detection@',
                             'Ksym_D':'(/ 1 time_D)',
                             'Ksys_D':'(/ 1 time_D)',
                             'Kh1':'(/ fraction_hospitalized time_to_hospitalization)',
                             'Kh2':'(/ fraction_critical time_to_hospitalization )',
                             'Kh3':'(/ fraction_dead  time_to_hospitalization)',
                             'Kh1_D':'(/ fraction_hospitalized (- time_to_hospitalization time_D))',
                             'Kh2_D':'(/ fraction_critical (- time_to_hospitalization time_D) )',
                             'Kh3_D':'(/ fraction_dead  (- time_to_hospitalization time_D))',
                             'Kr_m_D':'(/ 1 (- recovery_time_mild time_D ))'
                             }

        param_dic_SymSys = {'time_D_Sym':'@time_to_detection_Sym@',
                            'time_D_Sys':'@time_to_detection_Sys@',
                            'Ksym_D':'(/ 1 time_D_Sym)',
                            'Ksys_D':'(/ 1 time_D_Sys)',
                            'Kh1':'(/ fraction_hospitalized time_to_hospitalization)',
                            'Kh2':'(/ fraction_critical time_to_hospitalization )',
                            'Kh3':'(/ fraction_dead  time_to_hospitalization)',
                            'Kh1_D':'(/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))',
                            'Kh2_D':'(/ fraction_critical (- time_to_hospitalization time_D_Sys) )',
                            'Kh3_D':'(/ fraction_dead  (- time_to_hospitalization time_D_Sys))',
                            'Kr_m_D':'(/ 1 (- recovery_time_mild time_D_Sym ))'
                            }

        param_dic_AsSymSys = {'Kh1':'(/ fraction_hospitalized time_to_hospitalization)',
                              'Kh2':'(/ fraction_critical time_to_hospitalization )',
                              'Kh3':'(/ fraction_dead  time_to_hospitalization)',
                              'time_D_Sys':'@time_to_detection_Sys@',
                              'Ksys_D':'(/ 1 time_D_Sys)',
                              'Kh1_D':'(/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))',
                              'Kh2_D':'(/ fraction_critical (- time_to_hospitalization time_D_Sys) )',
                              'Kh3_D':'(/ fraction_dead  (- time_to_hospitalization time_D_Sys))',
                              'time_D_Sym':'@time_to_detection_Sym@',
                              'Ksym_D':'(/ 1 time_D_Sym)',
                              'Kr_m_D':'(/ 1 (- recovery_time_mild time_D_Sym ))',
                              'time_D_As':'@time_to_detection_As@',
                              'Kl_D':'(/ 1 time_D_As)',
                              'Kr_a_D':'(/ 1 (- recovery_time_asymp time_D_As ))'
                              }

        if self.expandModel == "SymSys":
            param_dic_expand = param_dic_SymSys
        elif self.expandModel == "uniform":
            param_dic_expand = param_dic_uniform
        elif self.expandModel == "AsSymSys":
            param_dic_expand = param_dic_AsSymSys
        else:
            param_dic_expand = param_dic_base

        calculated_params_str =  ''.join([f'(param {key} {param_dic[key]})\n' for key in list(param_dic.keys())])
        calculated_params_expand_str =  ''.join([f'(param {key} {param_dic_expand[key]})\n' for key in list(param_dic_expand.keys())])

        params_str = yaml_sampled_param_str + calculated_params_str + calculated_params_expand_str

        return params_str

    def write_migration_param(self):
        x1 = range(1, len(self.grpList) + 1)
        x2 = range(1, len(self.grpList) + 1)
        param_str = ""
        for x1_i in x1:
            param_str = param_str + "\n"
            for x2_i in x2:
                # x1_i=1
                param_str = param_str + f'(param toEMS_{x1_i}_from_EMS_{x2_i} @toEMS_{x1_i}_from_EMS_{x2_i}@)\n'
        return param_str

    def write_travel_reaction(grp, travelspeciesList=None):
        x1_i = int(grp.split("_")[1])
        x2 = list(range(1, 12))
        x2 = [i for i in x2 if i != x1_i]
        reaction_str = ""
        if travelspeciesList == None:
            travelspeciesList = ["S", "E", "As", "P"]

        for travelspecies in travelspeciesList:
            reaction_str = reaction_str + "\n"
            for x2_i in x2:
                # x1_i=1
                reaction_str = reaction_str + f'\n(reaction {travelspecies}_travel_EMS_{x2_i}to{x1_i}  ' \
                                              f'({travelspecies}::EMS_{x2_i}) ({travelspecies}::EMS_{x1_i}) ' \
                                              f'(* {travelspecies}::EMS_{x2_i} toEMS_{x1_i}_from_EMS_{x2_i} ' \
                                              f'(/ N_EMS_{x2_i} ' \
                                              f'(+ S::EMS_{x2_i} E::EMS_{x2_i} As::EMS_{x2_i} P::EMS_{x2_i} recovered_EMS_{x2_i})' \
                                              f')))\n'

        return reaction_str

    def write_Ki_timevents(grp):
        grp = str(grp)
        grpout = covidModel.sub(grp)
        params_str = f'(param Ki_{grp} @Ki_{grp}@)\n' \
                     f'(observe Ki_t_{grpout} Ki_{grp})\n' \
                     f'(time-event time_infection_import @time_infection_import_{grp}@ ' \
                     f'(' \
                     f'(As::{grp} @initialAs_{grp}@) ' \
                     f'(S::{grp} (- S::{grp} @initialAs_{grp}@))' \
                     f')' \
                     f')\n'

        return params_str

    def write_N_population(self):
        stringAll = ""
        for grp in self.grpList:
            string1 = f'(param N_{grp} (+ @speciesS_{grp}@ @initialAs_{grp}@))\n'
            stringAll = stringAll + string1

        string2 = f'(param N_All (+ {covidModel.repeat_string_by_grp("N_", self.grpList)}))\n'
        string3 = '(observe N_All N_All)\n'
        stringAll = stringAll + string2 + string3

        return stringAll

    def repeat_string_by_grp(fixedstring, grpList):
        stringAll = ""
        for grp in grpList:
            temp_string = " " + fixedstring + grp
            stringAll = stringAll + temp_string

        return stringAll

    def write_All(self):

        grpList = self.grpList
        observe_channels_All_str = ""
        channels = covidModel.get_channels(self)
        for channel in channels :
            if channel == 'crit':
                channel = 'critical'
            if channel == 'hosp':
                channel = 'hospitalized'

            if channel == "susceptible":
                temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('S::', grpList) + "))\n"
            elif channel == "deaths_det":
                temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('D3_det3::', grpList) + "))\n"
            elif channel == "exposed":
                temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('E::', grpList) + "))\n"
            elif channel == "asymp_det":
                temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('As_det1::', grpList) + "))\n"
            elif channel == "presymp":
                temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('P::',grpList) + "))\n"
            elif channel == "presymp_det":
                temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('P_det::', grpList) + "))\n"
            else:
                temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp(f'{channel}_', grpList) + "))\n"
            observe_channels_All_str = observe_channels_All_str + temp_str
            del temp_str

        return observe_channels_All_str

    def write_reactions(self, grp):
        grp = str(grp)

        reaction_str_I = f'(reaction exposure_{grp}   ' \
                         f'(S::{grp}) (E::{grp}) ' \
                         f'(* Ki_{grp} S::{grp} ' \
                         f'(/  ' \
                         f'(+ infectious_undet_symp_{grp} ' \
                         f'(* infectious_undet_As_{grp} reduced_infectious_As ) ' \
                         f'(* infectious_det_symp_{grp} reduced_inf_of_det_cases) ' \
                         f'(* infectious_det_AsP_{grp} reduced_inf_of_det_cases)' \
                         f') N_{grp} )' \
                         f'))\n'

        reaction_str_III = f'(reaction recovery_H1_{grp} (H1::{grp}) (RH1::{grp}) (* Kr_h_{grp} H1::{grp}))\n' \
                           f'(reaction recovery_C2_{grp} (C2::{grp}) (H2post::{grp}) (* Kr_c_{grp} C2::{grp}))\n' \
                           f'(reaction recovery_H2post_{grp} (H2post::{grp}) (RC2::{grp}) (* Kr_hc H2post::{grp}))\n' \
                           f'(reaction recovery_H1_det3_{grp} (H1_det3::{grp}) (RH1_det3::{grp}) (* Kr_h_{grp} H1_det3::{grp}))\n' \
                           f'(reaction recovery_C2_det3_{grp} (C2_det3::{grp}) (H2post_det3::{grp}) (* Kr_c_{grp} C2_det3::{grp}))\n' \
                           f'(reaction recovery_H2post_det3_{grp} (H2post_det3::{grp}) (RC2_det3::{grp}) (* Kr_hc H2post_det3::{grp}))\n'

        expand_base_str = f'(reaction infection_asymp_undet_{grp} (E::{grp}) (As::{grp}) (* Kl E::{grp} (- 1 d_As)))\n' \
                          f'(reaction infection_asymp_det_{grp} (E::{grp}) (As_det1::{grp}) (* Kl E::{grp} d_As))\n' \
                          f'(reaction presymptomatic_{grp} (E::{grp}) (P::{grp}) (* Ks E::{grp} (- 1 d_P)))\n' \
                          f'(reaction presymptomatic_{grp} (E::{grp}) (P_det::{grp}) (* Ks E::{grp} d_P))\n' \
                          f'(reaction mild_symptomatic_undet_{grp} (P::{grp}) (Sym::{grp}) (* Ksym P::{grp} (- 1 d_Sym)))\n' \
                          f'(reaction mild_symptomatic_det_{grp} (P::{grp}) (Sym_det2::{grp}) (* Ksym P::{grp} d_Sym))\n' \
                          f'(reaction severe_symptomatic_undet_{grp} (P::{grp}) (Sys::{grp}) (* Ksys P::{grp} (- 1 d_Sys)))\n' \
                          f'(reaction severe_symptomatic_det_{grp} (P::{grp}) (Sys_det3::{grp}) (* Ksys P::{grp} d_Sys))\n' \
                          f'(reaction mild_symptomatic_det_{grp} (P_det::{grp}) (Sym_det2::{grp}) (* Ksym P_det::{grp}))\n' \
                          f'(reaction severe_symptomatic_det_{grp} (P_det::{grp}) (Sys_det3::{grp}) (* Ksys P_det::{grp} ))\n' \
                          f'(reaction hospitalization_1_{grp} (Sys::{grp}) (H1::{grp}) (* Kh1 Sys::{grp}))\n' \
                          f'(reaction hospitalization_2_{grp} (Sys::{grp}) (H2pre::{grp}) (* Kh2 Sys::{grp}))\n' \
                          f'(reaction hospitalization_3_{grp} (Sys::{grp}) (H3::{grp}) (* Kh3 Sys::{grp}))\n' \
                          f'(reaction critical_2_{grp} (H2pre::{grp}) (C2::{grp}) (* Kc H2pre::{grp}))\n' \
                          f'(reaction critical_3_{grp} (H3::{grp}) (C3::{grp}) (* Kc H3::{grp}))\n' \
                          f'(reaction deaths_{grp} (C3::{grp}) (D3::{grp}) (* Km C3::{grp}))\n' \
                          f'(reaction hospitalization_1_det_{grp} (Sys_det3::{grp}) (H1_det3::{grp}) (* Kh1 Sys_det3::{grp}))\n' \
                          f'(reaction hospitalization_2_det_{grp} (Sys_det3::{grp}) (H2pre_det3::{grp}) (* Kh2 Sys_det3::{grp}))\n' \
                          f'(reaction hospitalization_3_det_{grp} (Sys_det3::{grp}) (H3_det3::{grp}) (* Kh3 Sys_det3::{grp}))\n' \
                          f'(reaction critical_2_det2_{grp} (H2pre_det3::{grp}) (C2_det3::{grp}) (* Kc H2pre_det3::{grp}))\n' \
                          f'(reaction critical_3_det2_{grp} (H3_det3::{grp}) (C3_det3::{grp}) (* Kc H3_det3::{grp}))\n' \
                          f'(reaction deaths_det3_{grp} (C3_det3::{grp}) (D3_det3::{grp}) (* Km C3_det3::{grp}))\n' \
                          f'(reaction recovery_As_{grp} (As::{grp}) (RAs::{grp}) (* Kr_a As::{grp}))\n' \
                          f'(reaction recovery_As_det_{grp} (As_det1::{grp}) (RAs_det1::{grp}) (* Kr_a As_det1::{grp}))\n' \
                          f'(reaction recovery_Sym_{grp} (Sym::{grp}) (RSym::{grp}) (* Kr_m  Sym::{grp}))\n' \
                          f'(reaction recovery_Sym_det2_{grp} (Sym_det2::{grp}) (RSym_det2::{grp}) (* Kr_m  Sym_det2::{grp}))\n'

        expand_testDelay_SymSys_str = f'(reaction infection_asymp_undet_{grp} (E::{grp}) (As::{grp}) (* Kl E::{grp} (- 1 d_As)))\n' \
                                      f'(reaction infection_asymp_det_{grp} (E::{grp}) (As_det1::{grp}) (* Kl E::{grp} d_As))\n' \
                                      f'(reaction presymptomatic_{grp} (E::{grp}) (P::{grp}) (* Ks E::{grp}))\n' \
                                      f'; developing symptoms - same time to symptoms as in master emodl\n' \
                                      f'(reaction mild_symptomatic_{grp} (P::{grp}) (Sym_preD::{grp}) (* Ksym P::{grp}))\n' \
                                      f'(reaction severe_symptomatic_{grp} (P::{grp}) (Sys_preD::{grp}) (* Ksys P::{grp}))\n' \
                                      f'; never detected \n' \
                                      f'(reaction mild_symptomatic_undet_{grp} (Sym_preD::{grp}) (Sym::{grp}) (* Ksym_D Sym_preD::{grp} (- 1 d_Sym)))\n' \
                                      f'(reaction severe_symptomatic_undet_{grp} (Sys_preD::{grp}) (Sys::{grp}) (* Ksys_D Sys_preD::{grp} (- 1 d_Sys)))\n' \
                                      f'; new detections  - time to detection is substracted from hospital time\n' \
                                      f'(reaction mild_symptomatic_det_{grp} (Sym_preD::{grp}) (Sym_det2::{grp}) (* Ksym_D Sym_preD::{grp} d_Sym))\n' \
                                      f'(reaction severe_symptomatic_det_{grp} (Sys_preD::{grp}) (Sys_det3::{grp}) (* Ksys_D Sys_preD::{grp} d_Sys))\n' \
                                      f'(reaction hospitalization_1_{grp} (Sys::{grp}) (H1::{grp}) (* Kh1_D Sys::{grp}))\n' \
                                      f'(reaction hospitalization_2_{grp} (Sys::{grp}) (H2pre::{grp}) (* Kh2_D Sys::{grp}))\n' \
                                      f'(reaction hospitalization_3_{grp} (Sys::{grp}) (H3::{grp}) (* Kh3_D Sys::{grp}))\n' \
                                      f'(reaction critical_2_{grp} (H2pre::{grp}) (C2::{grp}) (* Kc H2pre::{grp}))\n' \
                                      f'(reaction critical_3_{grp} (H3::{grp}) (C3::{grp}) (* Kc H3::{grp}))\n' \
                                      f'(reaction deaths_{grp} (C3::{grp}) (D3::{grp}) (* Km C3::{grp}))\n' \
                                      f'(reaction hospitalization_1_det_{grp} (Sys_det3::{grp}) (H1_det3::{grp}) (* Kh1_D Sys_det3::{grp}))\n' \
                                      f'(reaction hospitalization_2_det_{grp} (Sys_det3::{grp}) (H2pre_det3::{grp}) (* Kh2_D Sys_det3::{grp}))\n' \
                                      f'(reaction hospitalization_3_det_{grp} (Sys_det3::{grp}) (H3_det3::{grp}) (* Kh3_D Sys_det3::{grp}))\n' \
                                      f'(reaction critical_2_det2_{grp} (H2pre_det3::{grp}) (C2_det3::{grp}) (* Kc H2pre_det3::{grp}))\n' \
                                      f'(reaction critical_3_det2_{grp} (H3_det3::{grp}) (C3_det3::{grp}) (* Kc H3_det3::{grp}))\n' \
                                      f'(reaction deaths_det3_{grp} (C3_det3::{grp}) (D3_det3::{grp}) (* Km C3_det3::{grp}))\n' \
                                      f'(reaction recovery_As_{grp} (As::{grp}) (RAs::{grp}) (* Kr_a As::{grp}))\n' \
                                      f'(reaction recovery_As_det_{grp} (As_det1::{grp}) (RAs_det1::{grp}) (* Kr_a As_det1::{grp}))\n' \
                                      f'(reaction recovery_Sym_{grp} (Sym::{grp}) (RSym::{grp}) (* Kr_m_D Sym::{grp}))\n' \
                                      f'(reaction recovery_Sym_det2_{grp} (Sym_det2::{grp}) (RSym_det2::{grp}) (* Kr_m_D  Sym_det2::{grp}))\n'

        expand_testDelay_AsSymSys_str = f'(reaction infection_asymp_det_{grp} (E::{grp}) (As_preD::{grp}) (* Kl E::{grp}))\n' \
                                        f'(reaction infection_asymp_undet_{grp} (As_preD::{grp}) (As::{grp}) (* Kl_D As_preD::{grp} (- 1 d_As)))\n' \
                                        f'(reaction infection_asymp_det_{grp} (As_preD::{grp}) (As_det1::{grp}) (* Kl_D As_preD::{grp} d_As))\n' \
                                        f'(reaction presymptomatic_{grp} (E::{grp}) (P::{grp}) (* Ks E::{grp} (- 1 d_P)))\n' \
                                        f'(reaction presymptomatic_{grp} (E::{grp}) (P_det::{grp}) (* Ks E::{grp} d_P))\n' \
                                        f'; developing symptoms - same time to symptoms as in master emodl\n' \
                                        f'(reaction mild_symptomatic_{grp} (P::{grp}) (Sym_preD::{grp}) (* Ksym P::{grp}))\n' \
                                        f'(reaction severe_symptomatic_{grp} (P::{grp}) (Sys_preD::{grp}) (* Ksys P::{grp}))\n' \
                                        f'; never detected\n' \
                                        f'(reaction mild_symptomatic_undet_{grp} (Sym_preD::{grp}) (Sym::{grp}) (* Ksym_D Sym_preD::{grp} (- 1 d_Sym)))\n' \
                                        f'(reaction severe_symptomatic_undet_{grp} (Sys_preD::{grp}) (Sys::{grp})  (* Ksys_D Sys_preD::{grp} (- 1 d_Sys)))\n' \
                                        f'; new detections  - time to detection is subtracted from hospital time\n' \
                                        f'(reaction mild_symptomatic_det_{grp} (Sym_preD::{grp}) (Sym_det2a::{grp}) (* Ksym_D Sym_preD::{grp} d_Sym))\n' \
                                        f'(reaction severe_symptomatic_det_{grp} (Sys_preD::{grp}) (Sys_det3a::{grp}) (* Ksys_D Sys_preD::{grp} d_Sys))\n' \
                                        f'; developing symptoms - already detected, same time to symptoms as in master emodl\n' \
                                        f'(reaction mild_symptomatic_det_{grp} (P_det::{grp}) (Sym_det2b::{grp}) (* Ksym  P_det::{grp}))\n' \
                                        f'(reaction severe_symptomatic_det_{grp} (P_det::{grp}) (Sys_det3b::{grp}) (* Ksys  P_det::{grp} ))\n' \
                                        f'(reaction hospitalization_1_{grp} (Sys::{grp}) (H1::{grp}) (* Kh1_D Sys::{grp}))\n' \
                                        f'(reaction hospitalization_2_{grp} (Sys::{grp}) (H2pre::{grp}) (* Kh2_D Sys::{grp}))\n' \
                                        f'(reaction hospitalization_3_{grp} (Sys::{grp}) (H3::{grp}) (* Kh3_D Sys::{grp}))\n' \
                                        f'(reaction critical_2_{grp} (H2pre::{grp}) (C2::{grp}) (* Kc H2pre::{grp}))\n' \
                                        f'(reaction critical_3_{grp} (H3::{grp}) (C3::{grp}) (* Kc H3::{grp}))\n' \
                                        f'(reaction deaths_{grp} (C3::{grp}) (D3::{grp}) (* Km C3::{grp}))\n' \
                                        f'(reaction hospitalization_1_det_{grp} (Sys_det3a::{grp}) (H1_det3::{grp}) (* Kh1_D Sys_det3a::{grp}))\n' \
                                        f'(reaction hospitalization_2_det_{grp} (Sys_det3a::{grp}) (H2pre_det3::{grp}) (* Kh2_D Sys_det3a::{grp}))\n' \
                                        f'(reaction hospitalization_3_det_{grp} (Sys_det3a::{grp}) (H3_det3::{grp}) (* Kh3_D Sys_det3a::{grp}))\n' \
                                        f'(reaction hospitalization_1_det_{grp} (Sys_det3b::{grp}) (H1_det3::{grp}) (* Kh1 Sys_det3b::{grp}))\n' \
                                        f'(reaction hospitalization_2pre_det_{grp} (Sys_det3b::{grp}) (H2pre_det3::{grp}) (* Kh2 Sys_det3b::{grp}))\n' \
                                        f'(reaction hospitalization_3_det_{grp} (Sys_det3b::{grp}) (H3_det3::{grp}) (* Kh3 Sys_det3b::{grp}))\n' \
                                        f'(reaction critical_2_det2_{grp} (H2pre_det3::{grp}) (C2_det3::{grp}) (* Kc H2pre_det3::{grp}))\n' \
                                        f'(reaction critical_3_det2_{grp} (H3_det3::{grp}) (C3_det3::{grp}) (* Kc H3_det3::{grp}))\n' \
                                        f'(reaction deaths_det3_{grp} (C3_det3::{grp}) (D3_det3::{grp}) (* Km C3_det3::{grp}))\n' \
                                        f'(reaction recovery_As_{grp} (As::{grp}) (RAs::{grp}) (* Kr_a_D As::{grp}))\n' \
                                        f'(reaction recovery_As_det_{grp} (As_det1::{grp}) (RAs_det1::{grp}) (* Kr_a_D As_det1::{grp}))\n' \
                                        f'(reaction recovery_Sym_{grp} (Sym::{grp}) (RSym::{grp}) (* Kr_m_D  Sym::{grp}))\n' \
                                        f'(reaction recovery_Sym_det2a_{grp} (Sym_det2a::{grp}) (RSym_det2::{grp}) (* Kr_m_D Sym_det2a::{grp}))\n' \
                                        f'(reaction recovery_Sym_det2b_{grp} (Sym_det2b::{grp}) (RSym_det2::{grp}) (* Kr_m Sym_det2b::{grp}))\n'

        if self.expandModel == None:
            reaction_str = reaction_str_I + expand_base_str + reaction_str_III
        if self.expandModel == "SymSys" or self.expandModel == "uniform":
            reaction_str = reaction_str_I + expand_testDelay_SymSys_str + reaction_str_III
        if self.expandModel == 'AsSymSys':
            reaction_str = reaction_str_I + expand_testDelay_AsSymSys_str + reaction_str_III

        return reaction_str

    def write_time_varying_parameter(self, total_string):
        """Time varying parameter that have been fitted to data, or informed by local data.
            Parameters and corresponding sub-functions:
                - fraction_critical:  `write_frac_crit_change`
                - fraction_dead:  `write_fraction_dead_change`
                - dSys:  `write_dSys_change`
                - d_Sym:  `write_d_Sym_P_As_change`
                - dP_As:  `write_d_Sym_P_As_change`
                - Ki (monthly multipliers):  `write_ki_multiplier_change`
                - recovery_time_crit:  `write_recovery_time_crit_change`
                - recovery_time_hosp:  `write_recovery_time_hosp_change`
            All functions take required argument: nchanges, that defines number of updates.
            The default has been set within the function and currently would need to be edited manually.
        """

        def write_frac_crit_change(nchanges):
            n_frac_crit_change = range(1, nchanges+1)
            frac_crit_change_observe = '(observe frac_crit_t fraction_critical)'
            frac_crit_change_timeevent = ''.join([f'(time-event frac_crit_adjust{i} @crit_time_{i}@ '
                                                  f'('
                                                  f'(fraction_critical @fraction_critical_change{i}@) '
                                                  f'(fraction_hospitalized (- 1 (+ fraction_critical fraction_dead))) '
                                                  f'(Kh1 (/ fraction_hospitalized time_to_hospitalization)) '
                                                  f'(Kh2 (/ fraction_critical time_to_hospitalization )) '
                                                  f'(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) '
                                                  f'(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys)))'
                                                  f')'
                                                  f')'
                                                  f'\n' for i in n_frac_crit_change])

            return frac_crit_change_observe + frac_crit_change_timeevent

        def write_fraction_dead_change(nchanges):
            n_fraction_dead_change = range(1, nchanges+1)
            fraction_dead_change_observe = '(observe fraction_dead_t fraction_dead)\n' \
                                           '(observe fraction_hospitalized_t fraction_hospitalized)'

            fraction_dead_change_timeevent = ''.join([f'(time-event fraction_dead_adjust2 @fraction_dead_time_{i}@ '
                                                      f'('
                                                      f'(fraction_dead @fraction_dead_change{i}@) '
                                                      f'(fraction_hospitalized (- 1 (+ fraction_critical fraction_dead))) '
                                                      f'(Kh1 (/ fraction_hospitalized time_to_hospitalization)) '
                                                      f'(Kh2 (/ fraction_critical time_to_hospitalization )) '
                                                      f'(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) '
                                                      f'(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys)))'
                                                      f')'
                                                      f')'
                                                      f' \n' for i in n_fraction_dead_change])

            return fraction_dead_change_observe + fraction_dead_change_timeevent

        def write_dSys_change(nchanges):
            n_dSys_change = range(1, nchanges+1)
            dSys_change_observe = '(observe d_Sys_t d_Sys)'
            dSys_change_timeevent = ''.join([f'(time-event dSys_change{i} @d_Sys_change_time_{i}@ '
                                             f'((d_Sys @d_Sys_incr{i}@))'
                                             f')'
                                             f'\n' for i in n_dSys_change])
            return dSys_change_observe + dSys_change_timeevent

        def write_ki_multiplier_change(nchanges,fit_param):
            n_ki_multiplier = ['3a','3b','3c'] + list(range(4, nchanges+1))
            ki_multiplier_change_str = ''
            for grp in self.grpList:
                temp_str_param = ''.join([f'(param Ki_red{i}_{grp} '
                                          f'(* Ki_{grp} @ki_multiplier_{i}_{grp}@)'
                                          f')'
                                          f'\n' for i in n_ki_multiplier])

                temp_str_timeevent = ''.join([f'(time-event ki_multiplier_change_{i} @ki_multiplier_time_{i}@ '
                                              f'((Ki_{grp} Ki_red{i}_{grp}))'
                                              f')'
                                              f'\n' for i in n_ki_multiplier])

                if 'ki_multiplier' in fit_param:
                    i = fit_param.split('_')[-1]
                    temp_str_param = temp_str_param.replace(f'@ki_multiplier_{i}_{grp}@', f'(* @ki_multiplier_{i}_{grp}@ @scalingfactor@)')
                ki_multiplier_change_str = ki_multiplier_change_str + temp_str_param + temp_str_timeevent

            return ki_multiplier_change_str

        def write_d_Sym_P_As_change(nchanges):
            d_Sym_P_As_change_observe = '(observe d_Sym_t d_Sym)\n' \
                                        '(observe d_P_t d_P)\n' \
                                        '(observe d_As_t d_As)\n'

            n_d_PAs_changes = range(1,nchanges+1)
            d_Sym_P_As_change_param = ''.join([f'(param d_PAs_change{i} '
                                               f'(/ @d_Sym_change{i}@ dSym_dAsP_ratio)'
                                               f')'
                                               f'\n' for i in n_d_PAs_changes])

            d_Sym_P_As_change_timeevent = ''.join([f'(time-event d_Sym_change{i} @d_Sym_change_time_{i}@ '
                                                   f'('
                                                   f'(d_Sym @d_Sym_change{i}@) ' \
                                                   f'(d_P d_PAs_change1) ' \
                                                   f'(d_As d_PAs_change{i}))'
                                                   f')'
                                                   f'\n' for i in n_d_PAs_changes])
            return d_Sym_P_As_change_observe + d_Sym_P_As_change_param + d_Sym_P_As_change_timeevent

        def write_recovery_time_crit_change(nchanges):
            n_recovery_time_crit_change = range(1,nchanges+1)
            recovery_time_crit_change = ''
            for grp in self.grpList:
                grpout = covidModel.sub(grp)
                recovery_time_crit_change_param = f'(param recovery_time_crit_{grp} recovery_time_crit)\n' \
                                                  f'(param Kr_c_{grp} (/ 1 recovery_time_crit_{grp}))\n' \
                                                  f'(observe recovery_time_crit_t_{grpout} recovery_time_crit_{grp})' \
                                                  f'\n'

                recovery_time_crit_change_timeevent = ''.join([f'(time-event LOS_ICU_change_{i} @recovery_time_crit_change_time_{i}_{grp}@ '
                                                               f'('
                                                               f'(recovery_time_crit_{grp} @recovery_time_crit_change{i}_{grp}@) '
                                                               f'(Kr_c_{grp} '
                                                               f'(/ 1 @recovery_time_crit_change{i}_{grp}@))'
                                                               f')'
                                                               f')'
                                                               f'\n' for i in n_recovery_time_crit_change])

                recovery_time_crit_change = recovery_time_crit_change + \
                                            recovery_time_crit_change_param + \
                                            recovery_time_crit_change_timeevent

            return recovery_time_crit_change

        def write_recovery_time_hosp_change(nchanges):
            n_recovery_time_hosp_change = range(1, nchanges + 1)
            recovery_time_hosp_change = ''
            for grp in self.grpList:
                grpout = covidModel.sub(grp)
                recovery_time_hosp_change_param = f'(param recovery_time_hosp_{grp} recovery_time_hosp)\n' \
                                                  f'(param Kr_h_{grp} (/ 1 recovery_time_hosp_{grp}))\n' \
                                                  f'(observe recovery_time_hosp_t_{grpout} recovery_time_hosp_{grp})' \
                                                  f'\n'

                recovery_time_hosp_change_timeevent = ''.join(
                    [f'(time-event LOS_nonICU_change_{i} @recovery_time_hosp_change_time_{i}_{grp}@ '
                     f'('
                     f'(recovery_time_hosp_{grp} @recovery_time_hosp_change{i}_{grp}@) '
                     f'(Kr_h_{grp} (/ 1 @recovery_time_hosp_change{i}_{grp}@))'
                     f')'
                     f')'
                     f'\n' for i in n_recovery_time_hosp_change])

                recovery_time_hosp_change = recovery_time_hosp_change + recovery_time_hosp_change_param + recovery_time_hosp_change_timeevent
            return recovery_time_hosp_change

        config_dic = covidModel.get_configs(key ='time_varying_parameter', config_file='intervention_emodl_config.yaml')
        param_update_string = write_ki_multiplier_change(nchanges=config_dic['n_ki_multiplier'], fit_param = self.fit_param) + \
                              write_dSys_change(nchanges=config_dic['n_dSys_change']) + \
                              write_d_Sym_P_As_change(nchanges=config_dic['n_d_Sym_P_As_change']) + \
                              write_frac_crit_change(nchanges=config_dic['n_frac_crit_change']) + \
                              write_fraction_dead_change(nchanges=config_dic['n_fraction_dead_change']) + \
                              write_recovery_time_crit_change(nchanges=config_dic['n_recovery_time_crit_change']) + \
                              write_recovery_time_hosp_change(nchanges=config_dic['n_recovery_time_hosp_change'])

        total_string = total_string.replace(';[TIMEVARYING_PARAMETERS]', param_update_string)

        return total_string

    def get_intervention_dates(intervention_param):
        """intervention dates"""
        n_gradual_steps = intervention_param['n_gradual_steps']
        config_dic_dates = covidModel.get_configs(key ='time_parameters', config_file='extendedcobey_200428.yaml')
        #for i in range(1,len(scenario))
        intervention_start = pd.to_datetime(config_dic_dates['intervention1_start']['function_kwargs']['dates'])
        intervention_scaleupend = pd.to_datetime(config_dic_dates['intervention1_scaleupend']['function_kwargs']['dates'])
        #intervention_end = pd.to_datetime(config_dic_dates['intervention1_end']['function_kwargs']['dates'])
        if n_gradual_steps > 1:
            date_freq = (intervention_scaleupend - intervention_start) /(n_gradual_steps-1)
            intervention_dates = pd.date_range(start=intervention_start,end=intervention_scaleupend, freq=date_freq).tolist()
        else:
            intervention_dates = [intervention_start]

        return n_gradual_steps, intervention_dates

    def write_interventions(self, total_string):
        """ Write interventions
            Interventions defined in sub-functions:
                - bvariant: `write_bvariant`
                - intervention_stop: `write_intervention_stop`
                - transmission_increase: `write_transmission_increase`
                - rollback: `write_rollback`
                - gradual_reopening: `write_gradual_reopening`
        """

        """ Get intervention configurations """
        intervention_param = covidModel.get_configs(key ='interventions', config_file=self.intervention_config)


        def write_bvariant():
            emodl_str = ';COVID-19 bvariant scenario\n'

            read_from_csv = intervention_param['read_from_csv']
            if read_from_csv:
                csvfile = intervention_param['bvariant_csv']
                df = pd.read_csv(os.path.join("./experiment_configs", 'input_csv', csvfile))
                intervention_dates = list(df['Date'].values)
                fracinfect = list(df['variant_freq'].values)
                emodl_param = ''.join([f'(param Ki_bvariant_{i}_{grp} '
                                       f'(* Ki_{grp} @bvariant_infectivity@ ' \
                                       f'{fracinfect[i - 1]}' \
                                       f'))\n' for i, date in enumerate(intervention_dates, 1) for grp in self.grpList])
            else:
                n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param)
                #fracinfect = ['@bvariant_fracinfect@' for _ in range(len(intervention_dates))]
                emodl_param = ''.join([f'(param Ki_bvariant_{i}_{grp} '
                                       f'(* Ki_{grp} @bvariant_infectivity@ ' \
                                       f'(* @bvariant_fracinfect@ {(1 / (len(intervention_dates)) * i)}))' \
                                       f')\n' for i, date in enumerate(intervention_dates, 1) for grp in self.grpList ])

            emodl_timeevents = ''
            for i, date in enumerate(intervention_dates, 1):
                temp_str = f'(time-event ki_bvariant_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ('
                temp_str = temp_str + ''.join([f' (Ki_{grp} Ki_bvariant_{i}_{grp})' for grp in self.grpList ])
                temp_str = temp_str + f'))\n'
                emodl_timeevents = emodl_timeevents + temp_str
            bvariant_infectivity = emodl_param + emodl_timeevents

            """bvariant_severity Needs to be changed only once"""
            # FIXME: Affects total pop, regardless of bvariant prevalence
            # FIXME: Adjust fraction dead and critical? i.e. go back using cfr?
            #        f'(fraction_dead (/ cfr fraction_severe)) '

            bvariant_severity = f'(param fracsevere_bvariant1 (* fraction_severe @bvariant_severity@))\n' \
                                f'(time-event fracsevere_bvariant_change1 {covidModel.DateToTimestep(pd.Timestamp(intervention_dates[0]),self.startdate)} ' \
                                f'(' \
                                f'(fraction_severe fracsevere_bvariant1) ' \
                                f'(fraction_hospitalized (- 1 (+ fraction_critical fraction_dead))) ' \
                                f'(Kh1 (/ fraction_hospitalized time_to_hospitalization)) ' \
                                f'(Kh2 (/ fraction_critical time_to_hospitalization )) ' \
                                f'(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) ' \
                                f'(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) ))' \
                                f'))\n'

            emodl_str = emodl_str + bvariant_infectivity + bvariant_severity

            return emodl_str

        def write_rollback():
            emodl_str = ';COVID-19 rollback scenario\n'
            n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param)
            rollback_relative_to_initial = intervention_param['rollback_relative_to_initial']

            if rollback_relative_to_initial:
                emodl_param = ''.join([f'(param ki_rollback_{i}_{grp} '
                                       f'(- Ki_{grp}  (* (* @rollback_multiplier@ {(1 / (len(intervention_dates)) * i)}) (- @Ki_{grp}@  Ki_{grp})))' \
                                       f')\n' for i, date in enumerate(intervention_dates, 1) for grp in self.grpList ])

            else:
                emodl_param = ''.join([f'(param ki_rollback_{i}_{grp} '
                                       f'(* Ki_{grp}  (* @rollback_multiplier@ {(1 / (len(intervention_dates)) * i)}))' \
                                       f')\n' for i, date in enumerate(intervention_dates, 1) for grp in self.grpList ])

            emodl_timeevents = ''
            for i, date in enumerate(intervention_dates, 1):
                temp_str = f'(time-event ki_rollback_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ('
                temp_str = temp_str + ''.join([f' (Ki_{grp} ki_rollback_{i}_{grp})' for grp in self.grpList ])
                temp_str = temp_str + f'))\n'
                emodl_timeevents = emodl_timeevents + temp_str
            emodl_str = emodl_str + emodl_param + emodl_timeevents

            return emodl_str

        def write_triggeredrollback():
            emodl_str = ';COVID-19 triggeredrollback scenario\n'
            trigger_channel = intervention_param['trigger_channel']
            rollback_relative_to_initial = intervention_param['rollback_relative_to_initial']
            n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param)

            if rollback_relative_to_initial:
                ki_change_str = ''.join([f'(- Ki_{grp}  (* @rollback_multiplier@ (- @Ki_{grp}@  Ki_{grp})))' for grp in self.grpList ])
            else:
                ki_change_str = ''.join([f'(Ki_{grp} (* Ki_{grp} @rollback_multiplier@)) ' for grp in self.grpList])

            emodl_timeevents = ''.join([f'(param time_of_trigger_{grp} 10000)\n'
                                        f'(state-event rollbacktrigger_{grp} '
                                        f'(and (> time {covidModel.DateToTimestep(pd.Timestamp(intervention_dates[0]),self.startdate)}) (> {trigger_channel}_{grp} '
                                        f'(* @trigger_{grp}@ @capacity_multiplier@)) ) '
                                        f'((time_of_trigger_{grp} time))'
                                        f')\n'
                                        f'(func time_since_trigger_{grp} (- time time_of_trigger_{grp}))\n'
                                        f'(state-event apply_rollback_{grp} '
                                        f'(> (- time_since_trigger_{grp} @trigger_delay_days@) 0) ('
                                        f'{ki_change_str}'
                                        f'))\n'
                                        f'(observe triggertime_{covidModel.sub(grp)} time_of_trigger_{grp})\n' for grp in self.grpList])
            emodl_str = emodl_str + emodl_timeevents
            return emodl_str

        def write_reopen():
            emodl_str = ';COVID-19 reopen scenario\n'
            n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param)
            reopen_regionspecific = intervention_param['reopen_regionspecific']
            reopen_relative_to_initial = intervention_param['reopen_relative_to_initial']
            read_from_csv = intervention_param['read_from_csv']

            if read_from_csv:
                csvfile = intervention_param['reopen_csv']
                df = pd.read_csv(os.path.join("./experiment_configs", 'input_csv', csvfile))
                intervention_dates = list(df['Date'].values)
                perc_reopen = list(df['perc_reopen'].values)
            else:
                n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param)
                perc_reopen = ['@reopen_multiplier@' for _ in range(len(intervention_dates))]

            if reopen_relative_to_initial:
                emodl_param = ''.join([f'(param Ki_reopen_{i}_{grp} '
                                       f'(+ Ki_{grp} '
                                       f'(* {perc_reopen[i - 1]} '
                                       f'(- @Ki_{grp}@ Ki_{grp} )'
                                       f')))\n'
                                       for i, date in enumerate(intervention_dates, 1) for grp in self.grpList])
            else:
                emodl_param = ''.join([f'(param Ki_reopen_{i}_{grp} (+ Ki_{grp} (* {perc_reopen[i - 1]}  Ki_{grp})))\n'
                                       for i, date in enumerate(intervention_dates, 1) for grp in self.grpList])

            emodl_timeevents = ''
            for i, date in enumerate(intervention_dates, 1):
                temp_str = f'(time-event ki_reopen_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ('
                temp_str = temp_str + ''.join([f' (Ki_{grp} Ki_reopen_{i}_{grp})' for grp in self.grpList ])
                temp_str = temp_str + f'))\n'
                emodl_timeevents = emodl_timeevents + temp_str
            emodl_str = emodl_param + emodl_timeevents

            return emodl_str


        """Select intervention to add to emodl"""
        if self.add_interventions == "bvariant":
            intervention_str = write_bvariant()
        if self.add_interventions == "rollback":
            intervention_str = write_rollback()
        if self.add_interventions == "triggeredrollback":
            intervention_str = write_triggeredrollback()
        if self.add_interventions == "reopen":
            intervention_str = write_reopen()
        #if self.add_interventions == "vaccine":
        #    intervention_str = write_vaccine()

        return total_string.replace(';[INTERVENTIONS]', intervention_str )


    def write_change_test_delay(self, total_string):
        """ Write change in test delay (model extension)
            Possible extensions defined in strings:
                - uniform: `change_uniformtestDelay_str`
                - As: `change_testDelay_As_str`
                - Sym: `change_testDelay_Sym_str`
                - Sys: `change_testDelay_Sys_str`
                and combinations
                - AsSym: `change_testDelay_As_str` & `change_testDelay_Sym_str`
                - SymSys: `change_testDelay_Sym_str` & `change_testDelay_Sys_str`
                - AsSymSys: `change_testDelay_As_str` &  `change_testDelay_Sym_str` & `change_testDelay_Sys_str`
        """
        change_uniformtestDelay_str = '(time-event change_testDelay1 @change_testDelay_time1@ ' \
                                      '( ' \
                                      '(time_D @change_testDelay_1@) ' \
                                      '(Ksys_D (/ 1 time_D)) ' \
                                      '(Ksym_D (/ 1 time_D)) ' \
                                      '(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D))) ' \
                                      '(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D) )) ' \
                                      '(Kh3_D (/ fraction_dead (- time_to_hospitalization time_D))) ' \
                                      '(Kr_m_D (/ 1 (- recovery_time_mild time_D )))' \
                                      ')' \
                                      ')\n'

        change_testDelay_Sym_str = '(time-event change_testDelay1 @change_testDelay_time1@ ' \
                                   '( ' \
                                   '(time_D_Sym @change_testDelay_Sym_1@) ' \
                                   '(Ksym_D (/ 1 time_D_Sym)) ' \
                                   '(Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym )))' \
                                   ')' \
                                   ')\n'

        change_testDelay_Sys_str = '(time-event change_testDelay1 @change_testDelay_time1@ ' \
                                   '( ' \
                                   '(time_D_Sys @change_testDelay_Sys_1@) ' \
                                   '(Ksys_D (/ 1 time_D_Sys)) ' \
                                   '(Kh1_D (/ fraction_hospitalized (- time_to_hospitalization time_D_Sys))) ' \
                                   '(Kh2_D (/ fraction_critical (- time_to_hospitalization time_D_Sys) )) ' \
                                   '(Kh3_D (/ fraction_dead (- time_to_hospitalization time_D_Sys)))' \
                                   ')' \
                                   ')\n'

        change_testDelay_As_str = '(time-event change_testDelay1 @change_testDelay_time1@ ' \
                                  '( ' \
                                  '(time_D_As @change_testDelay_As_1@) ' \
                                  '(Kl_D (/ 1 time_D_As)) ' \
                                  '(Kr_a_D (/ 1 (- recovery_time_asymp time_D_As )))' \
                                  ')' \
                                  ')\n'

        if self.expandModel == "uniform":
            change_test_delay_str = change_uniformtestDelay_str
        if self.expandModel == "As":
            change_test_delay_str = change_testDelay_As_str
        if self.expandModel == "Sym":
            change_test_delay_str = change_testDelay_Sym_str
        if self.expandModel == "Sys":
            change_test_delay_str = change_testDelay_Sys_str
        if self.expandModel == "AsSym":
            change_test_delay_str = change_testDelay_As_str + change_testDelay_Sym_str
        if self.expandModel == "SymSys":
            change_test_delay_str = change_testDelay_Sym_str + change_testDelay_Sys_str
        if self.expandModel == "AsSymSys":
            change_test_delay_str = change_testDelay_As_str + change_testDelay_Sym_str + change_testDelay_Sys_str

        return total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_test_delay_str)

    def generate_emodl(self):

        if self.emodl_name is None:
            emodl_name = f'{self.model}_{self.add_interventions}'
            file_output = os.path.join(self.emodl_dir, f'{emodl_name}.emodl')
        else:
            file_output = os.path.join(self.emodl_dir, f'{self.emodl_name}.emodl')
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

        for grp in self.grpList:
            total_string = total_string + "\n(locale site-{})\n".format(grp)
            total_string = total_string + "(set-locale site-{})\n".format(grp)
            total_string = total_string + covidModel.write_species(self, grp)
            functions = covidModel.write_functions(self, grp)
            observe_string = observe_string + covidModel.write_observe(self, grp)
            if (self.add_migration):
                reaction_string = reaction_string + covidModel.write_travel_reaction(grp)
            reaction_string = reaction_string + covidModel.write_reactions(self, grp)
            functions_string = functions_string + functions
            param_string = param_string + covidModel.write_Ki_timevents(grp)

        param_string = covidModel.write_params(self) + param_string + covidModel.write_N_population(self)
        if (self.add_migration):
            param_string = param_string + covidModel.write_migration_param(self)
        functions_string = functions_string + covidModel.write_All(self)

        intervention_string = "\n;[TIMEVARYING_PARAMETERS]\n;[INTERVENTIONS]\n;[ADDITIONAL_TIMEEVENTS]"
        total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + param_string + '\n\n' + intervention_string + '\n\n' + reaction_string + '\n\n' + footer_str

        """Custom adjustments for EMS 6 (earliest start date)"""
        total_string = total_string.replace('(species As::EMS_6 0)', '(species As::EMS_6 1)')

        """Add time-events for time-varying parameters"""
        total_string = covidModel.write_time_varying_parameter(self, total_string)

        """Add change in test delay (optional)
            Note, per default assumes time to detection for the same populations as in expandModel changes 
            i.e. As, Sym, Sys, AsSymSys,  default structure AsSymSys.
            Initially expandModel and change_testDelay were separated
        """
        if self.change_testDelay:
            total_string = covidModel.write_change_test_delay(self, total_string)

        """Add interventions (optional)
           Note, interventions added IN ADDITION to monthly fitted Ki's
        """
        if self.add_interventions != None and self.add_interventions != 'baseline':
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
        model_options = {'expandModel': ("None","uniform", "As", "Sym","Sys","AsSym","AsSymSys"),
                         'observeLevel': ('primary', 'secondary', 'tertiary', 'all'),
                         'add_interventions': ("baseline",
                                               "bvariant",
                                               "interventionStop",
                                               "interventionSTOP_adj",
                                               "gradual_reopening",
                                               "rollback",
                                               #"gradual_reopening2",
                                               #"rollbacktriggered",
                                               #"contactTracing",
                                               #"improveHS",
                                               #"reopen_improveHS",
                                               #"contactTracing_improveHS"
                                               #"reopen_contactTracing_improveHS"
                                               ),
                         'change_testDelay': ("True","False"),
                         'trigger_channel': ("None", "crit", "crit_det", "hosp", "hosp_det"),
                         'add_migration': ('True', 'False')}
        return print(json.dumps(model_options, indent=4, sort_keys=True))
