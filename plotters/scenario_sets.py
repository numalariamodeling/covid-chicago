"""Define mixed simulation scenarios across EMS regions grouped by 4 super-regions

loadEMSregions generates a dictionary of super-region and ems region, it returns either a single super-region, or the whole dictionary
paste_exp_name  pastes together the experiment name in the format of date + region + experiment suffix that characterizes the simulation
get_exp_names combines the exp_names of all EMS for one scenario mix in a list
def_scenario_set wrapper function that calls  loadEMSregions and get_exp_names to define 9 scenario mixes

script called in combine_csv.py, combine_process_for_civis.csv and EMS_combo_plotter.csv
"""

def loadEMSregions(regionname) :
    regions = {'Northwest' : ['EMS_1', 'EMS_2'],
               'Northeast' : ['EMS_7', 'EMS_8', 'EMS_9', 'EMS_10', 'EMS_11'],
               'Central' : ['EMS_3', 'EMS_6'],
               'Southern': ['EMS_4', 'EMS_5']
    }

    if regionname != "all" :
        out = regions[regionname]
    elif regionname == "all" :
        out = regions
    return out

def paste_exp_name(simdate, x, exp_suffix):
    return (simdate + "_" + x + "_" + exp_suffix)


def get_exp_names(sim_scenarios, simdate):
    exp_names = []
    for region in sim_scenarios.keys() :
        region_ems = loadEMSregions(region)
        exp_suffix = sim_scenarios[region]
        exp_names = exp_names + [paste_exp_name(simdate, ems, exp_suffix) for ems in region_ems]

    # Reorder exp names based on ems number (fixed for order in regions)
    exp_names = exp_names[:2] + [exp_names[7]] + exp_names[9:11] + [exp_names[8]] + exp_names[2:7]

    return exp_names

def def_scenario_set(simdate) :
    sim_scenarios_1 = get_exp_names({'Northwest': 'reopening_gradual',
                                        'Northeast': 'scenario3',
                                        'Central': 'reopening_gradual',
                                        'Southern': 'reopening_gradual'}, simdate)

    sim_scenarios_2 = get_exp_names({'Northwest': 'scenario3',
                                        'Northeast': 'scenario3',
                                        'Central': 'reopening_gradual',
                                        'Southern': 'reopening_gradual'}, simdate)

    sim_scenarios_3 = get_exp_names({'Northwest': 'scenario3',
                                        'Northeast': 'reopening_gradual',
                                        'Central': 'reopening_June1',
                                        'Southern': 'reopening_gradual'}, simdate)

    sim_scenarios_4 = get_exp_names({'Northwest': 'scenario2',
                                        'Northeast': 'scenario2',
                                        'Central': 'scenario2',
                                        'Southern': 'scenario2'}, simdate)

    sim_scenarios_5 = get_exp_names({'Northwest': 'scenario3',
                                        'Northeast': 'scenario3',
                                        'Central': 'scenario3',
                                        'Southern': 'scenario3'}, simdate)

    sim_scenarios_6 = get_exp_names({'Northwest': 'reopening_gradual_ct80',
                                        'Northeast': 'scenario3',
                                        'Central': 'reopening_gradual_ct80',
                                        'Southern': 'reopening_gradual_ct80'}, simdate)

    sim_scenarios_7 = get_exp_names({'Northwest': 'reopening_gradual_ct80',
                                        'Northeast': 'scenario3',
                                        'Central': 'reopening_gradual_ct80',
                                        'Southern': 'reopening_gradual_ct80'}, simdate)

    sim_scenarios_8 = get_exp_names({'Northwest': 'reopening_gradual_ct30',
                                        'Northeast': 'scenario3',
                                        'Central': 'reopening_gradual_ct30',
                                        'Southern': 'reopening_gradual_ct30'}, simdate)

    sim_scenarios_9 = get_exp_names({'Northwest': 'reopening_June1',
                                        'Northeast': 'reopening_June1',
                                        'Central': 'reopening_June1',
                                        'Southern': 'reopening_June1'}, simdate)

    sim_label = ["Set_1", "Set_2", "Set_3", "scenario2_all", "scenario3_all", "Set_1_ct80detinfect0", "Set_1_ct80",
                 "Set_1_ct30", "scenario1_all"]

    intervention_label = ["all reopening except NE",
                          "all reopening except NE and NW",
                          "S, NW reopening, NE continued SIP, C immediate reopen July 1",
                          "never SIP",
                          "continued SIP (baseline)",
                          "partial reopening + contact tracing I",
                          "partial reopening + contact tracing II",
                          "partial reopening + contact tracing III",
                          "end SIP June 1"]

    sim_scenarios = [sim_scenarios_1, sim_scenarios_2, sim_scenarios_3, sim_scenarios_4, sim_scenarios_5,
                     sim_scenarios_6,  sim_scenarios_7, sim_scenarios_8, sim_scenarios_9]

    return sim_scenarios, sim_label, intervention_label

