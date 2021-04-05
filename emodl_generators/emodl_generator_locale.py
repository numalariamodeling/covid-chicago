import os
import sys
import re
import json
import yaml
import pandas as pd
import numpy as np

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

    def __init__(self,subgroups, expandModel, observeLevel='primary', add_interventions='baseline',
                 change_testDelay=False, intervention_config='intervention_emodl_config.yaml',
                 add_migration=False, fit_params=None,emodl_name=None, git_dir=git_dir):
        self.model = 'locale'
        self.grpList = subgroups
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

    def get_trigger(grp, channel):
        grp_nr = grp.replace('EMS_','')

        file_path = os.path.join(datapath, 'covid_IDPH', 'Corona virus reports', 'hospital_capacity_thresholds')
        files = os.listdir(file_path)
        files = [name for name in files if not 'extra_thresholds' in name]
        filedates = [item.replace('capacity_weekday_average_', '') for item in files]
        filedates = [item.replace('.csv', '') for item in filedates]
        latest_filedate = max([int(x) for x in filedates])

        fname = 'capacity_weekday_average_' + str(latest_filedate) + '.csv'
        ems_fname = os.path.join(datapath, 'covid_IDPH/Corona virus reports/hospital_capacity_thresholds/', fname)
        df = pd.read_csv(ems_fname)
        df = df.drop_duplicates()
        df = df[df['geography_modeled'] == f'covidregion_{grp_nr}']

        df = df[df['overflow_threshold_percent'] == 1]
        df['ems'] = df['geography_modeled']
        df['ems'] = df['geography_modeled'].replace("covidregion_", "", regex=True)
        df = df[['ems', 'resource_type', 'avg_resource_available']]
        df = df.drop_duplicates()

        ## if conflicting numbers, take the lower ones!
        dups = df.groupby(["ems", "resource_type"])["avg_resource_available"].nunique()
        if int(dups.nunique()) > 1:
            print(f'{ems_fname} contains multiple capacity values, selecting the lower ones.')
            df = df.loc[df.groupby(["ems", "resource_type"])["avg_resource_available"].idxmax()]

        df = df.pivot(index='ems', columns='resource_type', values='avg_resource_available')
        df.index.name = 'ems'
        df.reset_index(inplace=True)

        df = df.rename(columns={ 'hb_availforcovid':'hosp_det',
                            'hb_availforcovid':'total_hosp_census',
                           'icu_availforcovid': 'crit_det',
                            'vent_availforcovid':'ventilators'})

        return int(df[channel])

    def get_species(self):
        state_SE = ['S', 'E']
        state_nosymptoms = ['As', 'As_det1', 'P', 'P_det']
        state_symptoms = ['Sym', 'Sym_det2', 'Sys', 'Sys_det3']
        # state_hospitalized = ['H1', 'H2', 'H3', 'H1_det3', 'H2_det3', 'H3_det3']
        state_hospitalized = ['H1', 'H2pre', 'H2post', 'H3', 'H1_det3', 'H2pre_det3', 'H2post_det3', 'H3_det3']
        state_critical = ['C2', 'C3', 'C2_det3', 'C3_det3']
        state_deaths = ['D3', 'D3_det3']
        state_recoveries = ['RAs', 'RSym', 'RH1', 'RC2', 'RAs_det1', 'RSym_det2', 'RH1_det3', 'RC2_det3']
        state_testDelay_SymSys = ['Sym_preD', 'Sys_preD']
        state_testDelay_AsSymSys = ['As_preD', 'Sym_preD', 'Sym_det2a', 'Sym_det2b', 'Sys_preD', 'Sys_det3a', 'Sys_det3b']
        state_variables = state_SE + state_nosymptoms + state_symptoms + state_hospitalized + state_critical + state_deaths + state_recoveries

        if self.expandModel == "SymSys" or self.expandModel == "uniform":
            state_variables = state_variables + state_testDelay_SymSys
        if self.expandModel == "AsSymSys":
            state_variables = state_variables + state_testDelay_AsSymSys

        if 'vaccine' in self.add_interventions:
            state_variables_vaccine = [f'{state}_V' for state in state_variables ]
            state_variables = state_variables + state_variables_vaccine
        return state_variables

    def write_species(self, grp):
        state_variables = covidModel.get_species(self)

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
        channels = list(set(channels))

        if 'vaccine' in self.add_interventions:
            channels_vaccine = [f'{channel}_V' for channel in channels]
            channels = channels + channels_vaccine

        return channels

    def write_observe(self, grp):
        grp = str(grp)
        grpout = covidModel.sub(grp)

        def write_observe_emodl():
            #grp_suffix = "::{grp}"
            #grp_suffix2 = "_{grp}"

            if 'vaccine' in self.add_interventions:
                channels = covidModel.get_channels(self)
                channels = channels[int(len(channels) / 2):]
                observe_emodl = f"(observe vaccinated_cumul_{grpout} vaccinated_cumul_{grp})\n"
                for channel in channels:
                    if channel == 'crit_V':
                        channel = 'critical_V'
                    if channel == 'hosp_V':
                        channel = 'hospitalized_V'

                    if channel == "susceptible_V":
                        observe_emodl = observe_emodl + f'(observe {channel}_{grpout} S_V::{grp})\n'
                    elif channel == "exposed_V":
                        observe_emodl = observe_emodl + f'(observe {channel}_{grpout} E_V::{grp})\n'
                    elif channel == "deaths_det_V":
                        observe_emodl = observe_emodl + f'(observe {channel}_{grpout} D3_det3_V::{grp})\n'
                    else:
                        observe_emodl = observe_emodl + f'(observe {channel}_{grpout} {channel}_{grp})\n'

                channels = covidModel.get_channels(self)
                channels = channels[:int(len(channels) / 2)]
                for channel in channels:
                    if channel == 'crit':
                        channel = 'critical'
                    if channel == 'hosp':
                        channel = 'hospitalized'

                    if channel == "susceptible":
                        observe_emodl = observe_emodl + f'(observe {channel}_{grpout} (+ S::{grp}  S_V::{grp}))\n'
                    elif channel == "exposed":
                        observe_emodl = observe_emodl + f'(observe {channel}_{grpout} (+ E::{grp} E_V::{grp}))\n'
                    elif channel == "deaths_det":
                        observe_emodl = observe_emodl + f'(observe {channel}_{grpout} (+ D3_det3::{grp} D3_det3_V::{grp}))\n'
                    else:
                        observe_emodl= observe_emodl + f'(observe {channel}_{grpout} (+ {channel}_{grp} {channel}_V_{grp}))\n'
            else:
                channels = covidModel.get_channels(self)
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

            """Observe all state variables over time"""
            if self.observeLevel=='all':
                state_variables = covidModel.get_species(self)
                for state in state_variables:
                    observe_emodl = observe_emodl + f'(observe {state}_{grp} {state}::{grp})\n'

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


        func_str = f'(func deaths_det_cumul_{grp}  D3_det3::{grp})\n(func asymp_det_{grp}  As_det1::{grp})\n'
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

        if 'vaccine' in self.add_interventions:
            vacc_cumul = f'(func vaccinated_cumul_{grp} (+ S_V::{grp}  infected_V_{grp} recovered_V_{grp}  deaths_V_{grp} ))\n'
            func_str_V = func_str.replace(f'_{grp}',f'_V_{grp}')
            func_str_V = func_str_V.replace(f'::{grp}',f'_V::{grp}')
            func_str = func_str + func_str_V
            func_dic_all_V = {}
            for key, value in func_dic_all.items():
                key_V = key.replace('_{grp}','_V_{grp}')
                func_dic_all_V[key_V] = [item.replace('_{grp}','_V_{grp}')  if '_{grp}' in item
                                         else item.replace('::{grp}','_V::{grp}') for item in func_dic_all[key]]
            func_dic_all.update(func_dic_all_V)

        for key in func_dic_all.keys():
            func_str = func_str + f"(func {key} (+ {' '.join(func_dic_all[key])}))\n".format(grp=grp)
        if 'vaccine' in self.add_interventions:
            func_str = func_str + vacc_cumul
        return func_str

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

        if 'vaccine' in self.add_interventions:
            #custom_param_vacc = ['fraction_symptomatic_V', 'fraction_severe_V']
            custom_param_vacc_str = '(param fraction_symptomatic_V (* fraction_symptomatic @reduced_fraction_Sym@))\n' \
                                    '(param fraction_severe_V (* fraction_severe @reduced_fraction_Sys@))\n'
            param_symptoms_dic_V = {'KlV ': '(/ (- 1 fraction_symptomatic_V  ) time_to_infectious)',
                                    'KsV ': '(/ fraction_symptomatic_V   time_to_infectious)',
                                    'KsysV ': '(* fraction_severe_V (/ 1 time_to_symptoms))',
                                    'KsymV ': '(* (- 1 fraction_severe_V ) (/ 1 time_to_symptoms))'
                                    }

            param_symptoms_str_V = ''.join([f'(param {key} {param_symptoms_dic_V[key]})\n' for key in list(param_symptoms_dic_V.keys())])
            params_str = params_str + custom_param_vacc_str + param_symptoms_str_V

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

    def write_observe_All(self):

        grpList = self.grpList
        if "vaccine" in self.add_interventions:
            observe_channels_All_str =  f"(observe vaccinated_cumul_All (+ " + covidModel.repeat_string_by_grp('vaccinated_cumul_',grpList) + "))\n"
            channels = covidModel.get_channels(self)
            channels = channels[:int(len(channels) / 2)]
            for channel in channels:
                if channel == 'crit':
                    channel = 'critical'
                if channel == 'hosp':
                    channel = 'hospitalized'

                if channel == "susceptible":
                    temp_str = f"(observe {channel}_All " \
                               f"(+ " +\
                               covidModel.repeat_string_by_grp('S::', grpList) + \
                               covidModel.repeat_string_by_grp('S_V::', grpList) + \
                               "))\n"
                elif channel == "deaths_det":
                    temp_str = f"(observe {channel}_All (+ " + \
                               covidModel.repeat_string_by_grp('D3_det3::', grpList) + \
                               covidModel.repeat_string_by_grp('D3_det3_V::', grpList) + \
                               "))\n"
                elif channel == "exposed":
                    temp_str = f"(observe {channel}_All (+ " + \
                               covidModel.repeat_string_by_grp('E::', grpList) + \
                               covidModel.repeat_string_by_grp('E_V::', grpList) + \
                               "))\n"
                elif channel == "asymp_det":
                    temp_str = f"(observe {channel}_All (+ " +\
                               covidModel.repeat_string_by_grp('As_det1::', grpList) + \
                               covidModel.repeat_string_by_grp('As_det1_V::', grpList) + \
                               "))\n"
                elif channel == "presymp":
                    temp_str = f"(observe {channel}_All (+ " + \
                               covidModel.repeat_string_by_grp('P::', grpList) + \
                               covidModel.repeat_string_by_grp('P_V::', grpList) + \
                               "))\n"
                elif channel == "presymp_det":
                    temp_str = f"(observe {channel}_All (+ " + \
                               covidModel.repeat_string_by_grp('P_det::',grpList) + \
                               covidModel.repeat_string_by_grp('P_det_V::', grpList) + \
                               "))\n"
                else:
                    temp_str = f"(observe {channel}_All (+ " + \
                               covidModel.repeat_string_by_grp(f'{channel}_', grpList) + \
                               covidModel.repeat_string_by_grp(f'{channel}_V_', grpList) + \
                               "))\n"
                observe_channels_All_str = observe_channels_All_str + temp_str
                del temp_str

            channels = covidModel.get_channels(self)
            channels = channels[int(len(channels) / 2):]
            for channel in channels:
                if channel == 'crit_V':
                    channel = 'critical_V'
                if channel == 'hosp_V':
                    channel = 'hospitalized_V'

                if channel == "susceptible_V":
                    temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('S_V::',grpList) + "))\n"
                elif channel == "deaths_det_V":
                    temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('D3_det3_V::', grpList) + "))\n"
                elif channel == "exposed_V":
                    temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('E_V::',grpList) + "))\n"
                elif channel == "asymp_det_V":
                    temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('As_det1_V::', grpList) + "))\n"
                elif channel == "presymp_V":
                    temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('P_V::', grpList) + "))\n"
                elif channel == "presymp_det_V":
                    temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp('P_det_V::', grpList) + "))\n"
                else:
                    temp_str = f"(observe {channel}_All (+ " + covidModel.repeat_string_by_grp(f'{channel}_', grpList) + "))\n"
                observe_channels_All_str = observe_channels_All_str + temp_str
                del temp_str

        else:
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

        reaction_str_I = f'\n(reaction exposure_{grp}   ' \
                         f'(S::{grp}) (E::{grp}) ' \
                         f'(* Ki_{grp} S::{grp} ' \
                         f'(/  ' \
                         f'(+ infectious_undet_symp_{grp} ' \
                         f'(* infectious_undet_As_{grp} reduced_infectious_As ) ' \
                         f'(* infectious_det_symp_{grp} reduced_inf_of_det_cases) ' \
                         f'(* infectious_det_AsP_{grp} reduced_inf_of_det_cases)' \
                         f') N_{grp} )' \
                         f'))\n'

        reaction_str_Ia = f'\n(reaction exposure_{grp}   ' \
                          f'(S::{grp}) (E::{grp}) ' \
                          f'(* Ki_{grp} S::{grp} ' \
                          f'(/  ' \
                          f'(+ infectious_undet_symp_{grp}' \
                          f'(* (+ infectious_undet_symp_V_{grp} infectious_undet_As_V_{grp} ) reduced_infectious_V ) ' \
                          f'(* infectious_undet_As_{grp} reduced_infectious_As ) ' \
                          f'(* infectious_det_symp_{grp} reduced_inf_of_det_cases) ' \
                          f'(* infectious_det_AsP_{grp} reduced_inf_of_det_cases)' \
                          f'(* infectious_det_symp_V_{grp} reduced_infectious_V reduced_inf_of_det_cases) ' \
                          f'(* infectious_det_AsP_V_{grp} reduced_infectious_V reduced_inf_of_det_cases)' \
                          f') N_{grp} )' \
                          f'))\n'

        reaction_str_Ib = f'\n(reaction exposure_{grp}   ' \
                          f'(S_V::{grp}) (E_V::{grp}) ' \
                          f'(* Ki_{grp} S_V::{grp} ' \
                          f'(/  ' \
                          f'(+ infectious_undet_symp_{grp}' \
                          f'(* (+ infectious_undet_symp_V_{grp} infectious_undet_As_V_{grp} ) reduced_infectious_V ) ' \
                          f'(* infectious_undet_As_{grp} reduced_infectious_As ) ' \
                          f'(* infectious_det_symp_{grp} reduced_inf_of_det_cases) ' \
                          f'(* infectious_det_AsP_{grp} reduced_inf_of_det_cases)' \
                          f'(* infectious_det_symp_V_{grp} reduced_infectious_V reduced_inf_of_det_cases) ' \
                          f'(* infectious_det_AsP_V_{grp} reduced_infectious_V reduced_inf_of_det_cases)' \
                          f') N_{grp} )' \
                          f'))\n'

        if 'vaccine' in self.add_interventions:
            reaction_str_I = f'(reaction vaccination_{grp}  (S::{grp}) (S_V::{grp}) (* Kv_{grp} S::{grp}))\n'
            reaction_str_I = reaction_str_I + reaction_str_Ia + reaction_str_Ib

        reaction_str_III = f'(reaction recovery_H1_{grp} (H1::{grp}) (RH1::{grp}) (* Kr_h{grp} H1::{grp}))\n' \
                           f'(reaction recovery_C2_{grp} (C2::{grp}) (H2post::{grp}) (* Kr_c{grp} C2::{grp}))\n' \
                           f'(reaction recovery_H2post_{grp} (H2post::{grp}) (RC2::{grp}) (* Kr_hc H2post::{grp}))\n' \
                           f'(reaction recovery_H1_det3_{grp} (H1_det3::{grp}) (RH1_det3::{grp}) (* Kr_h{grp} H1_det3::{grp}))\n' \
                           f'(reaction recovery_C2_det3_{grp} (C2_det3::{grp}) (H2post_det3::{grp}) (* Kr_c{grp} C2_det3::{grp}))\n' \
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
                                        f'(reaction mild_symptomatic_det_{grp} (P_det::{grp}) (Sym_det2b::{grp}) (* Ksym P_det::{grp}))\n' \
                                        f'(reaction severe_symptomatic_det_{grp} (P_det::{grp}) (Sys_det3b::{grp}) (* Ksys P_det::{grp} ))\n' \
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
            reaction_str = expand_base_str + reaction_str_III
        if self.expandModel == "SymSys" or self.expandModel == "uniform":
            reaction_str = expand_testDelay_SymSys_str + reaction_str_III
        if self.expandModel == 'AsSymSys':
            reaction_str = expand_testDelay_AsSymSys_str + reaction_str_III

        if 'vaccine' in self.add_interventions:
            reaction_str_V = reaction_str.replace(f'_{grp}',f'_V_{grp}')
            reaction_str_V = reaction_str_V.replace(f'::{grp}', f'_V::{grp}')
            reaction_str = reaction_str + reaction_str_V

            """Custom adjustments - not automated/integrated yet"""
            reaction_str = reaction_str.replace('_V_V', '_V')
            reaction_str = reaction_str.replace('Ki_V', 'Ki')
            reaction_str = reaction_str.replace('N_V', 'N')
            """Vaccinated-population specific parameters"""
            reaction_str = reaction_str.replace('Kl E_V::', 'KlV E_V::')
            reaction_str = reaction_str.replace('Ks E_V::', 'KsV E_V::')
            reaction_str = reaction_str.replace('Ksym P_V::', 'KsymV P_V::')
            reaction_str = reaction_str.replace('Ksys P_V::', 'KsysV P_V::')
            reaction_str = reaction_str.replace('Ksym P_det_V::', 'KsymV P_det_V::')
            reaction_str = reaction_str.replace('Ksys P_det_V::', 'KsysV P_det_V::')

        reaction_str = reaction_str_I + reaction_str
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
            frac_crit_change_observe = '(observe fraction_severe_t fraction_severe)\n(observe frac_crit_t fraction_critical)\n'
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
                                           '(observe fraction_hospitalized_t fraction_hospitalized)\n'

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
            dSys_change_observe = '(observe d_Sys_t d_Sys)\n'
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
                                                  f'(param Kr_c{grp} (/ 1 recovery_time_crit_{grp}))\n' \
                                                  f'(observe recovery_time_crit_t_{grpout} recovery_time_crit_{grp})' \
                                                  f'\n'

                recovery_time_crit_change_timeevent = ''.join([f'(time-event LOS_ICU_change_{i} @recovery_time_crit_change_time_{i}_{grp}@ '
                                                               f'('
                                                               f'(recovery_time_crit_{grp} @recovery_time_crit_change{i}_{grp}@) '
                                                               f'(Kr_c{grp} '
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
                                                  f'(param Kr_h{grp} (/ 1 recovery_time_hosp_{grp}))\n' \
                                                  f'(observe recovery_time_hosp_t_{grpout} recovery_time_hosp_{grp})' \
                                                  f'\n'

                recovery_time_hosp_change_timeevent = ''.join(
                    [f'(time-event LOS_nonICU_change_{i} @recovery_time_hosp_change_time_{i}_{grp}@ '
                     f'('
                     f'(recovery_time_hosp_{grp} @recovery_time_hosp_change{i}_{grp}@) '
                     f'(Kr_h{grp} (/ 1 @recovery_time_hosp_change{i}_{grp}@))'
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

    def get_intervention_dates(intervention_param,scen):
        """intervention dates"""
        n_gradual_steps = intervention_param['n_gradual_steps']
        config_dic_dates = covidModel.get_configs(key ='time_parameters', config_file='extendedcobey_200428.yaml') #FIXME args.masterconfig
        #FIXME more flexible read in and return of dates for any number of scenarios
        #for i in range(1,nscenarios)

        intervention_start = pd.to_datetime(config_dic_dates[f'{scen}_start']['function_kwargs']['dates'])
        intervention_scaleupend = pd.to_datetime(config_dic_dates[f'{scen}_scaleupend']['function_kwargs']['dates'])
        #intervention_end = pd.to_datetime(config_dic_dates[f'{scen}_end']['function_kwargs']['dates'])

        if n_gradual_steps > 1 and intervention_scaleupend < pd.Timestamp('2090-01-01') :
            date_freq = (intervention_scaleupend - intervention_start) /(n_gradual_steps-1)
            intervention_dates = pd.date_range(start=intervention_start,end=intervention_scaleupend, freq=date_freq).tolist()
        else:
            n_gradual_steps = 1
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

        def write_vaccine_generic():
            emodl_str = ';COVID-19 vaccine scenario\n'
            emodl_param_initial = '(param Kv 0)\n(observe daily_vaccinated  Kv)\n'

            read_from_csv = intervention_param['read_from_csv']
            csvfile = intervention_param['vaccination_csv']
            if read_from_csv and csvfile != "":
                df = pd.read_csv(os.path.join("./experiment_configs", 'input_csv', csvfile))
                intervention_dates = list(df['Date'].values)
                intervention_effectsizes = list(df['daily_cov'].values)
                emodl_timeevents = ''
                for i, date in enumerate(intervention_dates, 1):
                    temp_str = f'(time-event vaccination_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ((Kv {intervention_effectsizes[i-1]})))\n'
                    emodl_timeevents = emodl_timeevents + temp_str
            else:
                n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param,scen='vaccine')
                emodl_timeevents = ''
                for i, date in enumerate(intervention_dates, 1):
                    temp_str = f'(time-event vaccination_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ((Kv (*  @vacc_daily_cov@ {(1 / (len(intervention_dates)) * i)}) )))\n'
                    emodl_timeevents = emodl_timeevents + temp_str

            emodl_str = emodl_str + emodl_param_initial + emodl_timeevents
            return emodl_str

        def write_vaccine():
            emodl_str = ';COVID-19 vaccine scenario\n'
            read_from_csv = intervention_param['read_from_csv']
            csvfile = intervention_param['vaccination_csv']
            df = pd.read_csv(os.path.join("./experiment_configs", 'input_csv', csvfile))
            df['Date'] = pd.to_datetime(df['date'])
            emodl_str_grp = ""
            for grp in self.grpList:
                grp_num = grp.replace('EMS_','')
                df_grp = df[df['covid_region']==int(grp_num)]
                emodl_param_initial = f'(param Kv_{grp} 0)\n' \
                                      f'(observe n_daily_vaccinated_{grp}  (* Kv_{grp}  S::{grp} ))\n'
                intervention_dates = list(df_grp['Date'].values) + [max(df_grp['Date']) + pd.Timedelta(1,'days')]
                intervention_effectsizes = list(df_grp['daily_first_vacc_perc'].values) + [0]
                #intervention_effectsizes = list(df_grp['daily_first_vacc'].values) + [0]

                emodl_timeevents = ''
                for i, date in enumerate(intervention_dates, 1):
                    temp_str = f'(time-event daily_vaccinations_{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ((Kv_{grp} {intervention_effectsizes[i-1]})))\n'
                    emodl_timeevents = emodl_timeevents + temp_str
                emodl_str_grp = emodl_str_grp + emodl_param_initial + emodl_timeevents
                del df_grp

            """Adjust fraction severe"""
            df = pd.read_csv(os.path.join(git_dir,"experiment_configs", 'input_csv', 'vaccination_fractionSevere_adjustment_IL.csv'))
            df['Date'] = pd.to_datetime(df['date'])
            intervention_dates = df['Date'].unique()

            fraction_severe_notV = ''
            for i, date in enumerate(intervention_dates, 1):
                temp_str = f"(time-event fraction_severe_changeV_{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)}  (" \
                                   f"(fraction_severe (- @fraction_severe@ (* (- @fraction_severe@ (*  @fraction_severe@ reduced_fraction_Sys_notV)) {df['persons_above65_first_vaccinated_perc'][i-1]}))) " \
                                   "(Ksys (* fraction_severe (/ 1 time_to_symptoms))) " \
                                   "(Ksym (* (- 1 fraction_severe) (/ 1 time_to_symptoms)))))\n"
                fraction_severe_notV = fraction_severe_notV + temp_str


            emodl_str = fraction_severe_notV + emodl_str + emodl_str_grp
            return emodl_str

        def write_bvariant():
            emodl_str = ';COVID-19 bvariant scenario\n'

            read_from_csv = intervention_param['read_from_csv']
            csvfile = intervention_param['bvariant_csv']
            if read_from_csv and csvfile != "":
                df = pd.read_csv(os.path.join("./experiment_configs", 'input_csv', csvfile))
                intervention_dates = list(df['Date'].values)
                fracinfect = list(df['variant_freq'].values)

                fracinfect_timevent = ''.join([f'(time-event bvariant_fracinfect {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} '
                                               f'((bvariant_fracinfect {fracinfect[i - 1]})))\n'
                                               for i, date in enumerate(intervention_dates, 1)])

                emodl_timeevents = ''
                for i, date in enumerate(intervention_dates, 1):
                    temp_str = f'(time-event ki_bvariant_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ('
                    temp_str = temp_str + ''.join([f' (Ki_{grp} ( + Ki_{grp}  (* (* Ki_{grp} 0.5)  (* @bvariant_fracinfect@ {fracinfect[i - 1]} ))))' for grp in self.grpList])
                    temp_str = temp_str + f'))\n'
                    emodl_timeevents = emodl_timeevents + temp_str

            else:
                n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param,scen='bvariant')

                fracinfect_timevent = ''.join([f'(time-event bvariant_fracinfect {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)}'
                                               f' ((bvariant_fracinfect (* @bvariant_fracinfect@ '
                                               f'{(1 / (len(intervention_dates)) * i)})))'
                                               f')\n' for i, date in enumerate(intervention_dates, 1)])


                emodl_param = ''.join([ f'(param Ki_bvariant_initial_{grp} 0)\n'
                                        f'(time-event ki_bvariant_initial {covidModel.DateToTimestep(pd.Timestamp(intervention_dates[0])-pd.Timedelta(2,"days"), self.startdate)} ('
                                        f'(Ki_bvariant_initial_{grp} Ki_{grp})'
                                        f'))\n ' for grp in self.grpList])

                emodl_timeevents = ''
                for i, date in enumerate(intervention_dates, 1):
                    temp_str = f'(time-event ki_bvariant_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ('
                    temp_str = temp_str + ''.join([f' (Ki_{grp} ( + Ki_bvariant_initial_{grp}  (* (* Ki_bvariant_initial_{grp} @bvariant_infectivity@)  (* @bvariant_fracinfect@ {(1 / (len(intervention_dates)) * i)} ))))' for grp in self.grpList])
                    temp_str = temp_str + f'))\n'
                    emodl_timeevents = emodl_timeevents + temp_str

            bvariant_infectivity =  emodl_param + emodl_timeevents

            """keep track of fracinfect, and use for update symptom development reactions"""
            fracinfect_str = '(param bvariant_fracinfect 0)\n' \
                             '(observe bvariant_fracinfect_t bvariant_fracinfect)\n' + fracinfect_timevent

            """fraction severe adjustment over time"""
            frac_severe_timevent = ''.join([f'(time-event fraction_severe_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} '
                                            f'('
                                            f'(fraction_severe (+ '
                                            f'(* @fraction_severe@ (- 1 bvariant_fracinfect)) '
                                            f'(* fraction_severeB  bvariant_fracinfect )  '
                                            f')) '
                                            f'(Ksys ( * fraction_severe (/ 1 time_to_symptoms))) '
                                            f'(Ksym ( * (- 1 fraction_severe)(/ 1 time_to_symptoms)))'
                                            f')'
                                            f')\n' for i, date in enumerate(intervention_dates, 1)])

            frac_severe_str = '(param fraction_severeB (* @fraction_severe@ @bvariant_severity@))\n' + frac_severe_timevent

            if 'vaccine' in self.add_interventions:
                """fraction severe adjustment over time"""
                frac_severeV_timevent = ''.join([f'(time-event fraction_severe_V_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} '
                                                 f'('
                                                 f'(fraction_severe_V (+ '
                                                 f'(* @fraction_severe@ @reduced_fraction_Sys@ (- 1 bvariant_fracinfect)) '
                                                 f'(* fraction_severeB @reduced_fraction_Sys@ bvariant_fracinfect )  '
                                                 f')) '
                                                 f'(KsysV ( * fraction_severe_V (/ 1 time_to_symptoms))) '
                                                 f'(KsymV ( * (- 1 fraction_severe_V)(/ 1 time_to_symptoms)))'
                                                 f')'
                                                 f')\n' for i, date in enumerate(intervention_dates, 1)])

                frac_severeV_str = '(observe fraction_severe_V_t fraction_severe_V)\n' + frac_severeV_timevent
                frac_severe_str = frac_severe_str + frac_severeV_str


            emodl_str = emodl_str + bvariant_infectivity + fracinfect_str + frac_severe_str

            return emodl_str

        def write_rollback():
            emodl_str = ';COVID-19 reopen scenario\n'
            rollback_regionspecific = intervention_param['rollback_regionspecific']
            rollback_relative_to_initial = intervention_param['rollback_relative_to_initial']
            read_from_csv = intervention_param['read_from_csv']

            if read_from_csv:
                csvfile = intervention_param['rollback_csv']
                df = pd.read_csv(os.path.join("./experiment_configs", 'input_csv', csvfile))
                intervention_dates = list(df['Date'].values)
                perc_rollback = list(df['perc_reopen'].values)
            else:
                n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param,scen='rollback')
                perc_rollback = ['@rollback_multiplier@' for _ in range(len(intervention_dates))]

            emodl_param = ''.join([ f'(param Ki_rollback_initial_{grp} 0)\n'
                                    f'(time-event ki_rollback_initial_ {covidModel.DateToTimestep(pd.Timestamp(intervention_dates[0])-pd.Timedelta(2,"days"), self.startdate)} ('
                                    f'(Ki_rollback_initial_{grp} Ki_{grp})'
                                    f'))\n ' for grp in self.grpList])

            if rollback_relative_to_initial:
                emodl_timeevents = ''
                for i, date in enumerate(intervention_dates, 1):
                    temp_str = f'(time-event ki_rollback_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ('
                    temp_str = temp_str + ''.join([f' (Ki_{grp} (- Ki_rollback_initial_{grp} (* {perc_rollback[i - 1]} (- @Ki_{grp}@ Ki_rollback_initial_{grp} ))))' for grp in self.grpList ])
                    temp_str = temp_str + f'))\n'
                    emodl_timeevents = emodl_timeevents + temp_str

            else:
                emodl_timeevents = ''
                for i, date in enumerate(intervention_dates, 1):
                    temp_str = f'(time-event ki_rollback_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ('
                    temp_str = temp_str + ''.join([f' (Ki_{grp} (- Ki_rollback_initial_{grp} (* {perc_rollback[i - 1]}  Ki_rollback_initial_{grp})))' for grp in self.grpList ])
                    temp_str = temp_str + f'))\n'
                    emodl_timeevents = emodl_timeevents + temp_str

            emodl_str = emodl_str + emodl_param + emodl_timeevents

            return emodl_str

        def write_triggeredrollback():
            emodl_str = ';COVID-19 triggeredrollback scenario\n'
            trigger_channel = intervention_param['trigger_channel']
            rollback_relative_to_initial = intervention_param['rollback_relative_to_initial']
            n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param, scen='triggeredrollback')

            if rollback_relative_to_initial:
                emodl_timeevents = ''.join([f'(param time_of_trigger_{grp} 10000)\n'
                                            f'(state-event rollbacktrigger_{grp} '
                                            f'(and (> time {covidModel.DateToTimestep(pd.Timestamp(intervention_dates[0]), self.startdate)}) '
                                            f'(> {trigger_channel}_{grp} (* {covidModel.get_trigger(grp,trigger_channel)} @capacity_multiplier@))'
                                            f') '
                                            f'((time_of_trigger_{grp} time))'
                                            f')\n'
                                            f'(func time_since_trigger_{grp} (- time time_of_trigger_{grp}))\n'
                                            f'(state-event apply_rollback_{grp} '
                                            f'(> (- time_since_trigger_{grp} @trigger_delay_days@) 0) ('
                                            f'(Ki_{grp} (- Ki_{grp} (* @rollback_multiplier@ (- @Ki_{grp}@  Ki_{grp})))) '
                                            f'))\n'
                                            f'(observe triggertime_{covidModel.sub(grp)} time_of_trigger_{grp})\n' for
                                            grp in self.grpList])
            else:
                emodl_timeevents = ''.join([f'(param time_of_trigger_{grp} 10000)\n'
                                            f'(state-event rollbacktrigger_{grp} '
                                            f'(and (> time {covidModel.DateToTimestep(pd.Timestamp(intervention_dates[0]),self.startdate)}) '
                                            f'(> {trigger_channel}_{grp} (* {covidModel.get_trigger(grp,trigger_channel)} @capacity_multiplier@))'
                                            f') '
                                            f'((time_of_trigger_{grp} time))'
                                            f')\n'
                                            f'(func time_since_trigger_{grp} (- time time_of_trigger_{grp}))\n'
                                            f'(state-event apply_rollback_{grp} '
                                            f'(> (- time_since_trigger_{grp} @trigger_delay_days@) 0) ('
                                            f'(Ki_{grp} (* Ki_{grp} @rollback_multiplier@)) '
                                            f'))\n'
                                            f'(observe triggertime_{covidModel.sub(grp)} time_of_trigger_{grp})\n' for grp in self.grpList])


            emodl_str = emodl_str + emodl_timeevents
            return emodl_str

        def write_reopen():
            emodl_str = ';COVID-19 reopen scenario\n'
            reopen_regionspecific = intervention_param['reopen_regionspecific']
            reopen_relative_to_initial = intervention_param['reopen_relative_to_initial']
            read_from_csv = intervention_param['read_from_csv']

            if read_from_csv:
                csvfile = intervention_param['reopen_csv']
                df = pd.read_csv(os.path.join("./experiment_configs", 'input_csv', csvfile))
                intervention_dates = list(df['Date'].values)
                perc_reopen = list(df['perc_reopen'].values)
            else:
                n_gradual_steps, intervention_dates = covidModel.get_intervention_dates(intervention_param,scen='reopen')
                perc_reopen = ['@reopen_multiplier@' for _ in range(len(intervention_dates))]

            emodl_param = ''.join([ f'(param Ki_reopen_initial_{grp} 0)\n'
                                    f'(time-event ki_reopen_initial_ {covidModel.DateToTimestep(pd.Timestamp(intervention_dates[0])-pd.Timedelta(2,"days"), self.startdate)} ('
                                    f'(Ki_reopen_initial_{grp} Ki_{grp})'
                                    f'))\n ' for grp in self.grpList])


            if reopen_relative_to_initial:
                emodl_timeevents = ''
                for i, date in enumerate(intervention_dates, 1):
                    temp_str = f'(time-event ki_reopen_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ('
                    temp_str = temp_str + ''.join([f' (Ki_{grp} (+ Ki_reopen_initial_{grp} (* {perc_reopen[i - 1]} (- @Ki_{grp}@ Ki_reopen_initial_{grp}))))' for grp in self.grpList ])
                    temp_str = temp_str + f'))\n'
                    emodl_timeevents = emodl_timeevents + temp_str

            else:
                emodl_timeevents = ''
                for i, date in enumerate(intervention_dates, 1):
                    temp_str = f'(time-event ki_reopen_change{i} {covidModel.DateToTimestep(pd.Timestamp(date), self.startdate)} ('
                    temp_str = temp_str + ''.join([f' (Ki_{grp} (+ Ki_reopen_initial_{grp} (* {perc_reopen[i - 1]}  Ki_reopen_initial_{grp})))' for grp in self.grpList ])
                    temp_str = temp_str + f'))\n'
                    emodl_timeevents = emodl_timeevents + temp_str

            emodl_str = emodl_str + emodl_param + emodl_timeevents

            return emodl_str


        """Select intervention to add to emodl"""
        intervention_str = ""
        if "bvariant" in self.add_interventions:
            intervention_str = intervention_str + write_bvariant()
        if "rollback" in self.add_interventions and not "triggeredrollback" in self.add_interventions:
            intervention_str = intervention_str + write_rollback()
        if "triggeredrollback" in self.add_interventions:
            intervention_str = intervention_str + write_triggeredrollback()
        if "reopen" in self.add_interventions:
            intervention_str = intervention_str + write_reopen()
        if "vaccine" in self.add_interventions:
            intervention_str = intervention_str + write_vaccine()

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

        if len(self.grpList) > 1:
            functions_string = functions_string + covidModel.write_observe_All(self)

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
                                               "vaccine",
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
