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
    if os.name == "posix": Location ="NUCLUSTER"
    else: Location ="Local"

datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths(Location=Location)

class covidModel:

    def __init__(self,expandModel='testDelay_AsSymSys',observeLevel='primary', add_interventions='baseline',
                 change_testDelay=None,homogeneous=False,add_ageShift_2ndWave=False,trigger_channel=None,emodl_name=None,git_dir=git_dir):
        self.model = 'age'
        self.grpList = ["age0to9", "age10to19", "age20to29", "age30to39", "age40to49", "age50to59", "age60to69", "age70to100"]
        self.expandModel = expandModel
        self.observeLevel = observeLevel
        self.add_interventions = add_interventions
        self.change_testDelay = change_testDelay
        self.homogeneous = homogeneous
        self.add_ageShift_2ndWave = add_ageShift_2ndWave
        self.trigger_channel = trigger_channel
        self.emodl_name = emodl_name
        self.emodl_dir = os.path.join(git_dir, 'emodl')

    def write_species(self, grp):
        grp = str(grp)
        species_str = """
    (species S_{grp} @speciesS_{grp}@)
    (species As_{grp}  @initialAs_{grp}@)
    (species E_{grp} 0)
    (species As_det1_{grp} 0)
    (species P_{grp} 0)
    (species P_det_{grp} 0)
    (species Sym_{grp} 0)
    (species Sym_det2_{grp} 0)
    (species Sys_{grp} 0)
    (species Sys_det3_{grp} 0)
    (species H1_{grp} 0)
    (species H2_{grp} 0)
    (species H3_{grp} 0)
    (species H1_det3_{grp} 0)
    (species H2_det3_{grp} 0)
    (species H3_det3_{grp} 0)
    (species C2_{grp} 0)
    (species C3_{grp} 0)
    (species C2_det3_{grp} 0)
    (species C3_det3_{grp} 0)
    (species D3_{grp} 0)
    (species D3_det3_{grp} 0)
    (species RAs_{grp} 0)
    (species RAs_det1_{grp} 0)
    (species RSym_{grp} 0)
    (species RSym_det2_{grp} 0)
    (species RH1_{grp} 0)
    (species RH1_det3_{grp} 0)
    (species RC2_{grp} 0)
    (species RC2_det3_{grp} 0)
    """.format(grp=grp)
        species_str = species_str.replace("  ", " ")

        expand_testDelay_SymSys_str = """
(species Sym_preD_{grp} 0)
(species Sys_preD_{grp} 0)
    """.format(grp=grp)


        expand_testDelay_AsSymSys_str = """
(species As_preD_{grp} 0)
(species Sym_preD_{grp} 0)
(species Sym_det2a_{grp} 0)
(species Sym_det2b_{grp} 0)
(species Sys_preD_{grp} 0)
(species Sys_det3a_{grp} 0)
(species Sys_det3b_{grp} 0)
    """.format(grp=grp)



        if self.expandModel == "testDelay_SymSys" or  self.expandModel == "uniformtestDelay" :
            species_str = species_str + expand_testDelay_SymSys_str
        if self.expandModel == "testDelay_AsSymSys":
            species_str = species_str + expand_testDelay_AsSymSys_str

        return (species_str)

    # eval(" 'age,' * 108") + "age"   ### need to add the number of ages pasted into format automatically depending on n groups
    def write_observe(self, grp):
        grp = str(grp)

        observe_primary_channels_str = """
(observe susceptible_{grp} S_{grp})
(observe infected_{grp} infected_{grp})
(observe recovered_{grp} recovered_{grp})
(observe infected_cumul_{grp} infected_cumul_{grp})

(observe asymp_cumul_{grp} asymp_cumul_{grp} )
(observe asymp_det_cumul_{grp} asymp_det_cumul_{grp})
(observe symptomatic_mild_{grp} symptomatic_mild_{grp})
(observe symptomatic_severe_{grp} symptomatic_severe_{grp})
(observe symp_mild_cumul_{grp} symp_mild_cumul_{grp})
(observe symp_severe_cumul_{grp} symp_severe_cumul_{grp})
(observe symp_mild_det_cumul_{grp} symp_mild_det_cumul_{grp})
(observe symp_severe_det_cumul_{grp} symp_severe_det_cumul_{grp})

(observe hosp_det_cumul_{grp} hosp_det_cumul_{grp} )
(observe hosp_cumul_{grp} hosp_cumul_{grp})
(observe detected_cumul_{grp} detected_cumul_{grp} )

(observe crit_cumul_{grp} crit_cumul_{grp})
(observe crit_det_cumul_{grp} crit_det_cumul_{grp})
(observe death_det_cumul_{grp} death_det_cumul_{grp} )

(observe deaths_det_{grp} D3_det3_{grp})
(observe deaths_{grp} deaths_{grp})

(observe crit_det_{grp} crit_det_{grp})
(observe critical_{grp} critical_{grp})
(observe hosp_det_{grp} hosp_det_{grp})
(observe hospitalized_{grp} hospitalized_{grp})
    """.format(grp=grp)


        observe_secondary_channels_str = """
(observe exposed_{grp} E_{grp})

(observe asymptomatic_det_{grp} As_det1_{grp})
(observe asymptomatic_{grp} asymptomatic_{grp})

(observe presymptomatic_{grp} presymptomatic_{grp})
(observe presymptomatic_det{grp} P_det_{grp} )

(observe detected_{grp} detected_{grp})

(observe symptomatic_mild_det_{grp} symptomatic_mild_det_{grp})
(observe symptomatic_severe_det_{grp} symptomatic_severe_det_{grp})
(observe recovered_det_{grp} recovered_det_{grp})
    """.format(grp=grp)

        observe_tertiary_channels_str = """
(observe infectious_undet_{grp} infectious_undet_{grp})
(observe infectious_det_{grp} infectious_det_{grp})
(observe infectious_det_symp_{grp} infectious_det_symp_{grp})
(observe infectious_det_AsP_{grp} infectious_det_AsP_{grp})
    """.format(grp=grp)

        if self.observeLevel == 'primary' :
            observe_str = observe_primary_channels_str
        if self.observeLevel == 'secondary' :
            observe_str = observe_primary_channels_str + observe_secondary_channels_str
        if self.observeLevel == 'tertiary' :
            observe_str = observe_primary_channels_str +  observe_tertiary_channels_str
        if self.observeLevel == 'all' :
            observe_str = observe_primary_channels_str + observe_secondary_channels_str + observe_tertiary_channels_str

        observe_str = observe_str.replace("  ", " ")
        return observe_str

    def write_functions(self,grp):
        grp = str(grp)
        functions_str = """
(func presymptomatic_{grp}  (+ P_{grp} P_det_{grp}))

(func hospitalized_{grp}  (+ H1_{grp} H2_{grp} H3_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp}))
(func hosp_det_{grp}  (+ H1_det3_{grp} H2_det3_{grp} H3_det3_{grp}))
(func critical_{grp} (+ C2_{grp} C3_{grp} C2_det3_{grp} C3_det3_{grp}))
(func crit_det_{grp} (+ C2_det3_{grp} C3_det3_{grp}))
(func deaths_{grp} (+ D3_{grp} D3_det3_{grp}))
(func recovered_{grp} (+ RAs_{grp} RSym_{grp} RH1_{grp} RC2_{grp} RAs_det1_{grp} RSym_det2_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(func recovered_det_{grp} (+ RAs_det1_{grp} RSym_det2_{grp} RH1_det3_{grp} RC2_det3_{grp}))

(func asymp_cumul_{grp} (+ asymptomatic_{grp} RAs_{grp} RAs_det1_{grp} ))
(func asymp_det_cumul_{grp} (+ As_det1_{grp} RAs_det1_{grp}))

(func symp_mild_cumul_{grp} (+ symptomatic_mild_{grp} RSym_{grp} RSym_det2_{grp}))
(func symp_mild_det_cumul_{grp} (+ symptomatic_mild_det_{grp} RSym_det2_{grp} ))

(func symp_severe_cumul_{grp} (+ symptomatic_severe_{grp} hospitalized_{grp} critical_{grp} deaths_{grp} RH1_{grp} RC2_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(func symp_severe_det_cumul_{grp} (+ symptomatic_severe_det_{grp} hosp_det_{grp} crit_det_{grp} D3_det3_{grp}  RH1_det3_{grp} RC2_det3_{grp}))

(func hosp_cumul_{grp} (+ hospitalized_{grp} critical_{grp} deaths_{grp} RH1_{grp} RC2_{grp} RH1_det3_{grp} RC2_det3_{grp}))
(func hosp_det_cumul_{grp} (+ H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp} D3_det3_{grp}  RH1_det3_{grp}  RC2_det3_{grp}))
(func crit_cumul_{grp} (+ deaths_{grp} critical_{grp} RC2_{grp} RC2_det3_{grp}))
(func crit_det_cumul_{grp} (+ C2_det3_{grp} C3_det3_{grp} D3_det3_{grp} RC2_det3_{grp}))
(func detected_cumul_{grp} (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} H1_det3_{grp} H2_det3_{grp} C2_det3_{grp} C3_det3_{grp} RAs_det1_{grp} RSym_det2_{grp} RH1_det3_{grp} RC2_det3_{grp} D3_det3_{grp}))
(func death_det_cumul_{grp} D3_det3_{grp} )

(func infected_{grp} (+ infectious_det_{grp} infectious_undet_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))
(func infected_det_{grp} (+ infectious_det_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))
(func infected_cumul_{grp} (+ infected_{grp} recovered_{grp} deaths_{grp}))    
    """.format(grp=grp)


        expand_base_str = """
(func asymptomatic_{grp}  (+ As_{grp} As_det1_{grp}))

(func symptomatic_mild_{grp}  (+ Sym_{grp} Sym_det2_{grp}))
(func symptomatic_mild_det_{grp}  ( Sym_det2_{grp}))

(func symptomatic_severe_{grp}  (+ Sys_{grp} Sys_det3_{grp}))
(func symptomatic_severe_det_{grp}   ( Sys_det3_{grp}))

(func detected_{grp} (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))

(func infectious_undet_{grp} (+ As_{grp} P_{grp} Sym_{grp} Sys_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infectious_det_{grp} (+ As_det1_{grp} P_det_{grp} Sym_det2_{grp} Sys_det3_{grp} ))

(func infectious_det_symp_{grp} (+ Sym_det2_{grp} Sys_det3_{grp} ))
(func infectious_det_AsP_{grp} (+ As_det1_{grp} P_det_{grp}))
    """.format(grp=grp)


        expand_testDelay_SymSys_str = """
(func asymptomatic_{grp}  (+ As_{grp} As_det1_{grp}))

(func symptomatic_mild_{grp}  (+ Sym_{grp} Sym_preD_{grp} Sym_det2_{grp}))
(func symptomatic_mild_det_{grp}  (+  Sym_preD_{grp} Sym_det2_{grp}))

(func symptomatic_severe_{grp}  (+ Sys_{grp} Sys_preD_{grp} Sys_det3_{grp}))
(func symptomatic_severe_det_{grp}  (+ Sys_preD_{grp} Sys_det3_{grp}))

(func detected_{grp} (+ As_det1_{grp} Sym_det2_{grp} Sys_det3_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))

(func infectious_undet_{grp} (+ As_{grp} P_{grp} Sym_preD_{grp} Sym_{grp} Sys_preD_{grp} Sys_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infectious_det_{grp} (+ As_det1_{grp} P_det_{grp} Sym_det2_{grp} Sys_det3_{grp} ))

(func infectious_det_symp_{grp} (+ Sym_det2_{grp} Sys_det3_{grp} ))
(func infectious_det_AsP_{grp} (+ As_det1_{grp} P_det_{grp}))
    """.format(grp=grp)


        expand_testDelay_AsSymSys_str = """
(func asymptomatic_{grp}  (+ As_preD_{grp} As_{grp} As_det1_{grp}))

(func symptomatic_mild_{grp}  (+ Sym_{grp} Sym_preD_{grp} Sym_det2a_{grp} Sym_det2b_{grp}))
(func symptomatic_mild_det_{grp}  (+ Sym_preD_{grp} Sym_det2a_{grp} Sym_det2b_{grp}))

(func symptomatic_severe_{grp}  (+ Sys_{grp} Sys_preD_{grp} Sys_det3a_{grp} Sys_det3b_{grp}))
(func symptomatic_severe_det_{grp}  (+ Sys_preD_{grp} Sys_det3a_{grp} Sys_det3b_{grp}))

(func detected_{grp} (+ As_det1_{grp} Sym_det2a_{grp} Sym_det2b_{grp} Sys_det3a_{grp} Sys_det3b_{grp} H1_det3_{grp} H2_det3_{grp} H3_det3_{grp} C2_det3_{grp} C3_det3_{grp}))

(func infectious_undet_{grp} (+ As_preD_{grp} As_{grp} P_{grp} Sym_{grp} Sym_preD_{grp} Sys_{grp} Sys_preD_{grp} H1_{grp} H2_{grp} H3_{grp} C2_{grp} C3_{grp}))
(func infectious_det_{grp} (+ As_det1_{grp} P_det_{grp} Sym_det2a_{grp} Sym_det2b_{grp} Sys_det3a_{grp} Sys_det3b_{grp}))

(func infectious_det_symp_{grp} (+ Sym_det2a_{grp} Sym_det2b_{grp} Sys_det3a_{grp} Sys_det3b_{grp} ))
(func infectious_det_AsP_{grp} (+ As_det1_{grp} P_det_{grp}))
    """.format(grp=grp)


        if self.expandModel == None:
            functions_str = expand_base_str + functions_str
        if self.expandModel == "testDelay_SymSys" or  self.expandModel == "uniformtestDelay" :
            functions_str =  expand_testDelay_SymSys_str + functions_str
        if self.expandModel == "testDelay_AsSymSys":
            functions_str = expand_testDelay_AsSymSys_str + functions_str

        return functions_str

    def sub(x, sub_str='_', sub_new=''):
        xout = re.sub(sub_str,sub_new, str(x), count=1)
        return xout

    def write_contact_matrix(nageGroups, scale=True):
        grp_x = range(1, nageGroups + 1)
        grp_y = reversed(grp_x)

        ki_dic = {}
        for i, xy in enumerate(itertools.product(grp_x, grp_y)):
            ki_dic[i] = ["C" + str(xy[0]) + '_' + str(xy[1])]

        ki_mix_param1 = ""
        ki_mix_param3 = ""
        for i in range(len(ki_dic.keys())):
            string_i = "\n(param " + covidModel.sub(ki_dic[i][0]) + " @" + ki_dic[i][0] + "@ )"
            ki_mix_param1 = ki_mix_param1 + string_i

            string_i = "\n(param " + ki_dic[i][0]  + " (/ " +  covidModel.sub(ki_dic[i][0]) + " norm_factor))"
            ki_mix_param3 = ki_mix_param3 + string_i

        ## To do - remove hardcoding and if statement
        if nageGroups ==4 :
            ki_mix_param2 = "\n(param sum1 (+ C11 C12 C13 C14))"
            ki_mix_param2 = ki_mix_param2 +  "\n(param sum2  (+ C21 C22 C23 C24))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum3 (+ C31 C32 C33 C34))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum4 (+ C41 C42 C43 C44))"
            norm_factor = "\n(param norm_factor (+ (* sum1 p1) (* sum2  p2) (* sum3 p3) (* sum4  p4)))"

        if nageGroups ==8:
            ki_mix_param2 = "\n(param sum1 (+ C11 C12 C13 C14 C15 C16 C17 C18))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum2 (+ C21 C22 C23 C24 C25 C26 C27 C28))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum3 (+ C31 C32 C33 C34 C35 C36 C37 C38))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum4 (+ C41 C42 C43 C44 C45 C46 C47 C48))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum5 (+ C51 C52 C53 C54 C55 C56 C57 C58))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum6 (+ C61 C62 C63 C64 C65 C66 C67 C68))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum7 (+ C71 C72 C73 C74 C75 C76 C77 C78))"
            ki_mix_param2 = ki_mix_param2 + "\n(param sum8 (+ C81 C82 C83 C84 C85 C86 C87 C88))"
            norm_factor = "\n(param norm_factor (+ (* sum1 p1) (* sum2  p2) (* sum3 p3) (* sum4  p4) (* sum5  p5) (* sum6  p6) (* sum7  p7) (* sum8  p8)))"

        ki_mix_param = ki_mix_param1 +  "\n" +  ki_mix_param2 +  "\n" +  norm_factor +  "\n" +  ki_mix_param3

        return ki_mix_param


    def write_ageShift_2ndWave(nageGroups, scale=True):
        grp_x = range(1, nageGroups + 1)
        grp_y = reversed(grp_x)

        if nageGroups ==8:
            ki_mix_param2 = "\n(param C88_2ndWave (* C88 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C87_2ndWave (* C87 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C86_2ndWave (* C86 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C85_2ndWave (* C85 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C84_2ndWave (* C84 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C83_2ndWave (* C83 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C82_2ndWave (* C82 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C81_2ndWave (* C81 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n"
            ki_mix_param2 = ki_mix_param2 + "\n(param C78_2ndWave (* C78 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C77_2ndWave (* C77 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C76_2ndWave (* C76 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C75_2ndWave (* C75 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C74_2ndWave (* C74 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C73_2ndWave (* C73 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C72_2ndWave (* C72 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C71_2ndWave (* C71 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n"
            ki_mix_param2 = ki_mix_param2 + "\n(param C18_2ndWave (* C18 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C28_2ndWave (* C28 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C38_2ndWave (* C38 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C48_2ndWave (* C48 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C58_2ndWave (* C58 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C68_2ndWave (* C68 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n"
            ki_mix_param2 = ki_mix_param2 + "\n(param C17_2ndWave (* C17 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C27_2ndWave (* C27 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C37_2ndWave (* C37 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C47_2ndWave (* C47 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C57_2ndWave (* C57 @multiplier_elderly@))"
            ki_mix_param2 = ki_mix_param2 + "\n(param C67_2ndWave (* C67 @multiplier_elderly@))"
            norm_factor1 = "\n(param sum7_2ndWave (+ C71_2ndWave C72_2ndWave C73_2ndWave C74_2ndWave C75_2ndWave C76_2ndWave C77_2ndWave C78_2ndWave))"
            norm_factor2 = "\n(param sum8_2ndWave (+ C81_2ndWave C82_2ndWave C83_2ndWave C84_2ndWave C85_2ndWave C86_2ndWave C87_2ndWave C88_2ndWave))"
            norm_factor3 = "\n(param norm_factor_2ndWave (+ (* sum1 p1) (* sum2  p2) (* sum3 p3) (* sum4  p4) (* sum5  p5) (* sum6  p6) (* sum7_2ndWave  p7) (* sum8_2ndWave  p8)))"
            norm_factor =  norm_factor1 + norm_factor2 + norm_factor3

            ki_dic = {}
            for i, xy in enumerate(itertools.product(grp_x, grp_y)):
                if int(xy[0]) <7 :
                    ki_dic[i] = ["C" + str(xy[0]) + '_' + str(xy[1])]
                if int(xy[0]) >=7 :
                    ki_dic[i] = ["C" + str(xy[0]) + '_' + str(xy[1]) + '_2ndWave']

            ki_mix_param3 = ""
            ki_mix_timeEvent = ""
            for i in range(len(ki_dic.keys())):
                term1 = ki_dic[i][0] + "_2ndWave"
                term1 =  covidModel.sub(term1, sub_str="_2ndWave_2ndWave", sub_new = "_2ndWave")
                string_i = "\n(param " + term1 + " (/ " +  covidModel.sub(ki_dic[i][0]) + " norm_factor_2ndWave))"
                ki_mix_param3 = ki_mix_param3 + string_i

                string_t = "\n(time-event secondWaveTransmission @start_time_2ndWave@ ((" +  covidModel.sub(ki_dic[i][0],sub_str="_2ndWave") + " " +  covidModel.sub(ki_dic[i][0],sub_str="_2ndWave") + "_2ndWave)))"
                ki_mix_timeEvent = ki_mix_timeEvent + string_t

            ki_ageShift_2ndWave_param =  ki_mix_param2 + "\n" + norm_factor + "\n" + ki_mix_param3  +  "\n" +  ki_mix_timeEvent

        return ki_ageShift_2ndWave_param


    # If Ki mix is defined, Ki here can be set to 0 in script that generates the simulation
    def write_params(self):
        params_str = """
(param time_to_infectious @time_to_infectious@)
(param time_to_symptoms @time_to_symptoms@)
(param time_to_hospitalization @time_to_hospitalization@)
(param time_to_death @time_to_death@)
(param recovery_time_asymp @recovery_time_asymp@)
(param recovery_time_mild @recovery_time_mild@)
(param recovery_time_crit @recovery_time_crit@)
(param reduced_inf_of_det_cases @reduced_inf_of_det_cases@)
(param d_As @d_As@)
(param d_P @d_P@)
(param d_Sym @d_Sym@)
(param d_Sys @d_Sys@)
(param Ki @Ki@)
(param Kr_a (/ 1 recovery_time_asymp))
(param Kr_m (/ 1 recovery_time_mild))
(param Kr_c (/ 1 recovery_time_crit))
(param Km (/ 1 time_to_death))

(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@) ))  
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@) ))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@) )) 
(time-event detection4 @detection_time_4@ ((d_Sys @d_Sys_incr4@) )) 
(time-event detection5 @detection_time_5@ ((d_Sys @d_Sys_incr5@) )) 
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
        if self.expandModel == "contactTracing" :
            params_str = params_str  + expand_contactTracing_str
        if self.expandModel == "testDelay_AsSymSys" :
            params_str = params_str + expand_testDelay_AsSymSys_str

        params_str = params_str.replace("  ", " ")

        return params_str


    def write_age_specific_param(self,grp):
        grp = str(grp)
        params_str =  """
(param fraction_severe_{grp} @fraction_severe_{grp}@)
(param Ksys{grp} (* fraction_severe_{grp} (/ 1 time_to_symptoms)))
(param Ksym{grp} (* (- 1 fraction_severe_{grp}) (/ 1 time_to_symptoms))) 
(param fraction_critical_{grp} @fraction_critical_{grp}@ )

; Direct input or calculate from cfr and fraction severe as in base emodl (negative counts!)
(param fraction_dead_{grp} @fraction_dead_{grp}@)
(param fraction_hospitalized_{grp} @fraction_hospitalized_{grp}@)

(param fraction_symptomatic_{grp} @fraction_symptomatic_{grp}@)
(param Kl{grp} (/ (- 1 fraction_symptomatic_{grp} ) time_to_infectious))
(param Ks{grp} (/ fraction_symptomatic_{grp}  time_to_infectious))

(param recovery_time_hosp_{grp} @recovery_time_hosp_{grp}@)
(param Kr_h{grp} (/ 1 recovery_time_hosp_{grp}))

(param time_to_critical_{grp} @time_to_critical_{grp}@)
(param Kc{grp}  (/ 1 time_to_critical_{grp}))
    
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
        if self.expandModel == "testDelay_AsSymSys" :
            params_str = params_str + expand_testDelay_AsSymSys_str

        params_str = params_str.replace("  ", " ")

        return params_str

    def write_observed_param(self):
        observed_param_str = """  
(observe Ki_t Ki)
(observe d_Sym_t d_Sym)
(observe d_Sys_t d_Sys)
    """

    ## If age specific parameters would change over time and should be tracked
    #    observed_ageparam_str=""
    #    for grp in grpList:
    #        grp = str(grp)
    #        temp_str = """
    #(observe fraction_dead_{grp}_t fraction_dead_{grp})
    #""".format(grp=grp)
    #        observed_ageparam_str = observed_ageparam_str + temp_str
        return observed_param_str



    def write_N_population(self):
        stringAll = ""
        for key in self.grpList:
            string1 = """\n(param N_{grp} (+ @speciesS_{grp}@ @initialAs_{grp}@) )""".format(grp=key)
            stringAll = stringAll + string1

        string2 = "\n(param N_All (+ " + covidModel.repeat_string_by_grp('N_', self.grpList) + "))"
        stringAll = stringAll + string2

        for i, key in enumerate(self.grpList):
            string2 = """\n(param p{i} (/ N_{grp} N_All))""".format(i=i+1, grp=key)
            stringAll = stringAll + string2

        return (stringAll)


    def repeat_string_by_grp(fixedstring, grpList):
        stringAll = ""
        for grp in grpList:
            temp_string = " " + fixedstring + grp
            stringAll = stringAll + temp_string

        return stringAll


    def write_All(self):
        grpList = self.grpList
        obs_primary_All_str = ""
        obs_primary_All_str = obs_primary_All_str + "\n(observe susceptible_All (+ " + covidModel.repeat_string_by_grp('S_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe infected_All (+ " + covidModel.repeat_string_by_grp('infected_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe recovered_All (+ " + covidModel.repeat_string_by_grp('recovered_',    grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe infected_cumul_All (+ " + covidModel.repeat_string_by_grp('infected_cumul_', grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe asymp_cumul_All (+ " + covidModel.repeat_string_by_grp( 'asymp_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe asymp_det_cumul_All (+ " + covidModel.repeat_string_by_grp( 'asymp_det_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symptomatic_mild_All (+ " + covidModel.repeat_string_by_grp(  'symptomatic_mild_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symptomatic_severe_All (+ " + covidModel.repeat_string_by_grp( 'symptomatic_severe_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_mild_cumul_All (+ " + covidModel.repeat_string_by_grp( 'symp_mild_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_severe_cumul_All (+ " + covidModel.repeat_string_by_grp( 'symp_severe_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_mild_det_cumul_All (+ " + covidModel.repeat_string_by_grp( 'symp_mild_det_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe symp_severe_det_cumul_All  (+ " + covidModel.repeat_string_by_grp(  'symp_severe_det_cumul_', grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe hosp_det_cumul_All (+ " + covidModel.repeat_string_by_grp( 'hosp_det_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe hosp_cumul_All (+ " + covidModel.repeat_string_by_grp('hosp_cumul_',  grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe detected_cumul_All (+ " + covidModel.repeat_string_by_grp( 'detected_cumul_', grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe crit_cumul_All (+ " + covidModel.repeat_string_by_grp('crit_cumul_',   grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe crit_det_cumul_All (+ " + covidModel.repeat_string_by_grp(  'crit_det_cumul_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe death_det_cumul_All (+ " + covidModel.repeat_string_by_grp('death_det_cumul_', grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe deaths_det_All (+ " + covidModel.repeat_string_by_grp('D3_det3_',  grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe deaths_All (+ " + covidModel.repeat_string_by_grp('deaths_',   grpList) + "))"

        obs_primary_All_str = obs_primary_All_str + "\n(observe crit_det_All (+ " + covidModel.repeat_string_by_grp('crit_det_',    grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe critical_All (+ " + covidModel.repeat_string_by_grp('critical_',    grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe hosp_det_All (+ " + covidModel.repeat_string_by_grp('hosp_det_', grpList) + "))"
        obs_primary_All_str = obs_primary_All_str + "\n(observe hospitalized_All (+ " + covidModel.repeat_string_by_grp('hospitalized_', grpList) + "))"


        obs_secondary_All_str = ""
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe exposed_All (+ " + covidModel.repeat_string_by_grp('E_',  grpList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe asymptomatic_All (+ " + covidModel.repeat_string_by_grp( 'asymptomatic_', grpList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe asymptomatic_det_All (+ "  + covidModel.repeat_string_by_grp('As_det1_',  grpList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe presymptomatic_All (+ " + covidModel.repeat_string_by_grp('P_', grpList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe presymptomatic_det_All (+ " + covidModel.repeat_string_by_grp('P_det_', grpList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe detected_All (+ " + covidModel.repeat_string_by_grp( 'detected_', grpList) + "))"

        obs_secondary_All_str = obs_secondary_All_str + "\n(observe symptomatic_mild_det_All (+ " + covidModel.repeat_string_by_grp(  'symptomatic_mild_det_', grpList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe symptomatic_severe_det_All (+ " + covidModel.repeat_string_by_grp( 'symptomatic_severe_det_', grpList) + "))"
        obs_secondary_All_str = obs_secondary_All_str + "\n(observe recovered_det_All (+ " + covidModel.repeat_string_by_grp('recovered_det_',    grpList) + "))"

        obs_tertiary_All_str = ""
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_det_All (+ " + covidModel.repeat_string_by_grp('infectious_det_', grpList) + "))"
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_undet_All (+ " + covidModel.repeat_string_by_grp( 'infectious_undet_', grpList) + "))"
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_det_symp_All (+ " + covidModel.repeat_string_by_grp('infectious_det_symp_', grpList) + "))"
        obs_tertiary_All_str = obs_tertiary_All_str + "\n(observe infectious_det_AsP_All (+ " + covidModel.repeat_string_by_grp( 'infectious_det_AsP_', grpList) + "))"

        if self.observeLevel == 'primary' :
            obs_All_str = obs_primary_All_str
        if self.observeLevel == 'secondary' :
            obs_All_str = obs_primary_All_str + obs_secondary_All_str
        if self.observeLevel == 'tertiary' :
            obs_All_str = obs_primary_All_str +  obs_tertiary_All_str
        if self.observeLevel == 'all' :
            obs_All_str = obs_primary_All_str + obs_secondary_All_str + obs_tertiary_All_str

        obs_All_str = obs_All_str.replace("  ", " ")
        return obs_All_str

    ## homogeneous reactions for testing
    def write_exposure_reaction_homogeneous(grp):
        grp = str(grp)
        exposure_reaction_str = """\n(reaction exposure_{grp}   (S_{grp}) (E_{grp}) (* Ki S_{grp} (/  (+ infectious_undet_All (* infectious_det_All reduced_inf_of_det_cases)) N_All )))""".format(
            grp=grp)

        return exposure_reaction_str


    def write_exposure_reaction4():
        exposure_reaction_str = """  
(reaction exposure_age0to19 (S_age0to19) (E_age0to19) (* Ki S_age0to19 (+ (* C1_1 (/ (+ infectious_undet_age0to19 (* infectious_det_age0to19 reduced_inf_of_det_cases)) N_age0to19)) (* C1_2 (/ (+ infectious_undet_age20to39 (* infectious_det_age20to39 reduced_inf_of_det_cases)) N_age20to39)) (* C1_3 (/ (+ infectious_undet_age40to59 (* infectious_det_age40to59 reduced_inf_of_det_cases)) N_age40to59)) (* C1_4 (/ (+ infectious_undet_age60to100 (* infectious_det_age60to100 reduced_inf_of_det_cases)) N_age60to100)))))
(reaction exposure_age20to39 (S_age20to39) (E_age20to39) (* Ki S_age20to39 (+ (* C2_1 (/ (+ infectious_undet_age0to19 (* infectious_det_age0to19 reduced_inf_of_det_cases)) N_age0to19)) (* C2_2 (/ (+ infectious_undet_age20to39 (* infectious_det_age20to39 reduced_inf_of_det_cases)) N_age20to39)) (* C2_3 (/ (+ infectious_undet_age40to59 (* infectious_det_age40to59 reduced_inf_of_det_cases)) N_age40to59)) (* C2_4 (/ (+ infectious_undet_age60to100 (* infectious_det_age60to100 reduced_inf_of_det_cases)) N_age60to100)))))
(reaction exposure_age40to59 (S_age40to59) (E_age40to59) (* Ki S_age40to59 (+ (* C3_1 (/ (+ infectious_undet_age0to19 (* infectious_det_age0to19 reduced_inf_of_det_cases)) N_age0to19)) (* C3_2 (/ (+ infectious_undet_age20to39 (* infectious_det_age20to39 reduced_inf_of_det_cases)) N_age20to39)) (* C3_3 (/ (+ infectious_undet_age40to59 (* infectious_det_age40to59 reduced_inf_of_det_cases)) N_age40to59)) (* C3_4 (/ (+ infectious_undet_age60to100 (* infectious_det_age60to100 reduced_inf_of_det_cases)) N_age60to100)))))
(reaction exposure_age60to100 (S_age60to100) (E_age60to100) (* Ki S_age60to100 (+ (* C4_1 (/ (+ infectious_undet_age0to19 (* infectious_det_age0to19 reduced_inf_of_det_cases)) N_age0to19)) (* C4_2 (/ (+ infectious_undet_age20to39 (* infectious_det_age20to39 reduced_inf_of_det_cases)) N_age20to39)) (* C4_3 (/ (+ infectious_undet_age40to59 (* infectious_det_age40to59 reduced_inf_of_det_cases)) N_age40to59)) (* C4_4 (/ (+ infectious_undet_age60to100 (* infectious_det_age60to100 reduced_inf_of_det_cases)) N_age60to100)))))

    """
        return exposure_reaction_str


    def write_exposure_reaction8():
        exposure_reaction_str = """  
(reaction exposure_age0to9 (S_age0to9) (E_age0to9) (* Ki S_age0to9 (+ (* C1_1 (/ (+ infectious_undet_age0to9 (* infectious_det_age0to9 reduced_inf_of_det_cases)) N_age0to9)) (* C1_2 (/ (+ infectious_undet_age10to19 (* infectious_det_age10to19 reduced_inf_of_det_cases)) N_age10to19)) (* C1_3 (/ (+ infectious_undet_age20to29 (* infectious_det_age20to29 reduced_inf_of_det_cases)) N_age20to29)) (* C1_4 (/ (+ infectious_undet_age30to39 (* infectious_det_age30to39 reduced_inf_of_det_cases)) N_age30to39)) (* C1_5 (/ (+ infectious_undet_age40to49 (* infectious_det_age40to49 reduced_inf_of_det_cases)) N_age40to49)) (* C1_6 (/ (+ infectious_undet_age50to59 (* infectious_det_age50to59 reduced_inf_of_det_cases)) N_age50to59)) (* C1_7 (/ (+ infectious_undet_age60to69 (* infectious_det_age60to69 reduced_inf_of_det_cases)) N_age60to69)) (* C1_8 (/ (+ infectious_undet_age70to100 (* infectious_det_age70to100 reduced_inf_of_det_cases)) N_age70to100)))))
(reaction exposure_age10to19 (S_age10to19) (E_age10to19) (* Ki S_age10to19 (+ (* C2_1 (/ (+ infectious_undet_age0to9 (* infectious_det_age0to9 reduced_inf_of_det_cases)) N_age0to9)) (* C2_2 (/ (+ infectious_undet_age10to19 (* infectious_det_age10to19 reduced_inf_of_det_cases)) N_age10to19)) (* C2_3 (/ (+ infectious_undet_age20to29 (* infectious_det_age20to29 reduced_inf_of_det_cases)) N_age20to29)) (* C2_4 (/ (+ infectious_undet_age30to39 (* infectious_det_age30to39 reduced_inf_of_det_cases)) N_age30to39)) (* C2_5 (/ (+ infectious_undet_age40to49 (* infectious_det_age40to49 reduced_inf_of_det_cases)) N_age40to49)) (* C2_6 (/ (+ infectious_undet_age50to59 (* infectious_det_age50to59 reduced_inf_of_det_cases)) N_age50to59)) (* C2_7 (/ (+ infectious_undet_age60to69 (* infectious_det_age60to69 reduced_inf_of_det_cases)) N_age60to69)) (* C2_8 (/ (+ infectious_undet_age70to100 (* infectious_det_age70to100 reduced_inf_of_det_cases)) N_age70to100)))))
(reaction exposure_age20to29 (S_age20to29) (E_age20to29) (* Ki S_age20to29 (+ (* C3_1 (/ (+ infectious_undet_age0to9 (* infectious_det_age0to9 reduced_inf_of_det_cases)) N_age0to9)) (* C3_2 (/ (+ infectious_undet_age10to19 (* infectious_det_age10to19 reduced_inf_of_det_cases)) N_age10to19)) (* C3_3 (/ (+ infectious_undet_age20to29 (* infectious_det_age20to29 reduced_inf_of_det_cases)) N_age20to29)) (* C3_4 (/ (+ infectious_undet_age30to39 (* infectious_det_age30to39 reduced_inf_of_det_cases)) N_age30to39)) (* C3_5 (/ (+ infectious_undet_age40to49 (* infectious_det_age40to49 reduced_inf_of_det_cases)) N_age40to49)) (* C3_6 (/ (+ infectious_undet_age50to59 (* infectious_det_age50to59 reduced_inf_of_det_cases)) N_age50to59)) (* C3_7 (/ (+ infectious_undet_age60to69 (* infectious_det_age60to69 reduced_inf_of_det_cases)) N_age60to69)) (* C3_8 (/ (+ infectious_undet_age70to100 (* infectious_det_age70to100 reduced_inf_of_det_cases)) N_age70to100)))))
(reaction exposure_age30to39 (S_age30to39) (E_age30to39) (* Ki S_age30to39 (+ (* C4_1 (/ (+ infectious_undet_age0to9 (* infectious_det_age0to9 reduced_inf_of_det_cases)) N_age0to9)) (* C4_2 (/ (+ infectious_undet_age10to19 (* infectious_det_age10to19 reduced_inf_of_det_cases)) N_age10to19)) (* C4_3 (/ (+ infectious_undet_age20to29 (* infectious_det_age20to29 reduced_inf_of_det_cases)) N_age20to29)) (* C4_4 (/ (+ infectious_undet_age30to39 (* infectious_det_age30to39 reduced_inf_of_det_cases)) N_age30to39)) (* C4_5 (/ (+ infectious_undet_age40to49 (* infectious_det_age40to49 reduced_inf_of_det_cases)) N_age40to49)) (* C4_6 (/ (+ infectious_undet_age50to59 (* infectious_det_age50to59 reduced_inf_of_det_cases)) N_age50to59)) (* C4_7 (/ (+ infectious_undet_age60to69 (* infectious_det_age60to69 reduced_inf_of_det_cases)) N_age60to69)) (* C4_8 (/ (+ infectious_undet_age70to100 (* infectious_det_age70to100 reduced_inf_of_det_cases)) N_age70to100)))))
(reaction exposure_age40to49 (S_age40to49) (E_age40to49) (* Ki S_age40to49 (+ (* C5_1 (/ (+ infectious_undet_age0to9 (* infectious_det_age0to9 reduced_inf_of_det_cases)) N_age0to9)) (* C5_2 (/ (+ infectious_undet_age10to19 (* infectious_det_age10to19 reduced_inf_of_det_cases)) N_age10to19)) (* C5_3 (/ (+ infectious_undet_age20to29 (* infectious_det_age20to29 reduced_inf_of_det_cases)) N_age20to29)) (* C5_4 (/ (+ infectious_undet_age30to39 (* infectious_det_age30to39 reduced_inf_of_det_cases)) N_age30to39)) (* C5_5 (/ (+ infectious_undet_age40to49 (* infectious_det_age40to49 reduced_inf_of_det_cases)) N_age40to49)) (* C5_6 (/ (+ infectious_undet_age50to59 (* infectious_det_age50to59 reduced_inf_of_det_cases)) N_age50to59)) (* C5_7 (/ (+ infectious_undet_age60to69 (* infectious_det_age60to69 reduced_inf_of_det_cases)) N_age60to69)) (* C5_8 (/ (+ infectious_undet_age70to100 (* infectious_det_age70to100 reduced_inf_of_det_cases)) N_age70to100)))))
(reaction exposure_age50to59 (S_age50to59) (E_age50to59) (* Ki S_age50to59 (+ (* C6_1 (/ (+ infectious_undet_age0to9 (* infectious_det_age0to9 reduced_inf_of_det_cases)) N_age0to9)) (* C6_2 (/ (+ infectious_undet_age10to19 (* infectious_det_age10to19 reduced_inf_of_det_cases)) N_age10to19)) (* C6_3 (/ (+ infectious_undet_age20to29 (* infectious_det_age20to29 reduced_inf_of_det_cases)) N_age20to29)) (* C6_4 (/ (+ infectious_undet_age30to39 (* infectious_det_age30to39 reduced_inf_of_det_cases)) N_age30to39)) (* C6_5 (/ (+ infectious_undet_age40to49 (* infectious_det_age40to49 reduced_inf_of_det_cases)) N_age40to49)) (* C6_6 (/ (+ infectious_undet_age50to59 (* infectious_det_age50to59 reduced_inf_of_det_cases)) N_age50to59)) (* C6_7 (/ (+ infectious_undet_age60to69 (* infectious_det_age60to69 reduced_inf_of_det_cases)) N_age60to69)) (* C6_8 (/ (+ infectious_undet_age70to100 (* infectious_det_age70to100 reduced_inf_of_det_cases)) N_age70to100)))))
(reaction exposure_age60to69 (S_age60to69) (E_age60to69) (* Ki S_age60to69 (+ (* C7_1 (/ (+ infectious_undet_age0to9 (* infectious_det_age0to9 reduced_inf_of_det_cases)) N_age0to9)) (* C7_2 (/ (+ infectious_undet_age10to19 (* infectious_det_age10to19 reduced_inf_of_det_cases)) N_age10to19)) (* C7_3 (/ (+ infectious_undet_age20to29 (* infectious_det_age20to29 reduced_inf_of_det_cases)) N_age20to29)) (* C7_4 (/ (+ infectious_undet_age30to39 (* infectious_det_age30to39 reduced_inf_of_det_cases)) N_age30to39)) (* C7_5 (/ (+ infectious_undet_age40to49 (* infectious_det_age40to49 reduced_inf_of_det_cases)) N_age40to49)) (* C7_6 (/ (+ infectious_undet_age50to59 (* infectious_det_age50to59 reduced_inf_of_det_cases)) N_age50to59)) (* C7_7 (/ (+ infectious_undet_age60to69 (* infectious_det_age60to69 reduced_inf_of_det_cases)) N_age60to69)) (* C7_8 (/ (+ infectious_undet_age70to100 (* infectious_det_age70to100 reduced_inf_of_det_cases)) N_age70to100)))))
(reaction exposure_age70to100 (S_age70to100) (E_age70to100) (* Ki S_age70to100 (+ (* C8_1 (/ (+ infectious_undet_age0to9 (* infectious_det_age0to9 reduced_inf_of_det_cases)) N_age0to9)) (* C8_2 (/ (+ infectious_undet_age10to19 (* infectious_det_age10to19 reduced_inf_of_det_cases)) N_age10to19)) (* C8_3 (/ (+ infectious_undet_age20to29 (* infectious_det_age20to29 reduced_inf_of_det_cases)) N_age20to29)) (* C8_4 (/ (+ infectious_undet_age30to39 (* infectious_det_age30to39 reduced_inf_of_det_cases)) N_age30to39)) (* C8_5 (/ (+ infectious_undet_age40to49 (* infectious_det_age40to49 reduced_inf_of_det_cases)) N_age40to49)) (* C8_6 (/ (+ infectious_undet_age50to59 (* infectious_det_age50to59 reduced_inf_of_det_cases)) N_age50to59)) (* C8_7 (/ (+ infectious_undet_age60to69 (* infectious_det_age60to69 reduced_inf_of_det_cases)) N_age60to69)) (* C8_8 (/ (+ infectious_undet_age70to100 (* infectious_det_age70to100 reduced_inf_of_det_cases)) N_age70to100)))))
    """
        return exposure_reaction_str


    def write_reactions(self, grp):
        grp = str(grp)

        reaction_str_III = """
(reaction recovery_H1_{grp}   (H1_{grp})   (RH1_{grp})   (* Kr_h{grp} H1_{grp}))
(reaction recovery_C2_{grp}   (C2_{grp})   (RC2_{grp})   (* Kr_c C2_{grp}))
(reaction recovery_H1_det3_{grp}   (H1_det3_{grp})   (RH1_det3_{grp})   (* Kr_h{grp} H1_det3_{grp}))
(reaction recovery_C2_det3_{grp}   (C2_det3_{grp})   (RC2_det3_{grp})   (* Kr_c C2_det3_{grp}))
        """.format(grp=grp)

        expand_base_str = """
(reaction infection_asymp_undet_{grp}  (E_{grp})   (As_{grp})   (* Kl{grp} E_{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (E_{grp})   (As_det1_{grp})   (* Kl{grp} E_{grp} d_As))
(reaction presymptomatic_{grp} (E_{grp})   (P_{grp})   (* Ks{grp} E_{grp} (- 1 d_P)))
(reaction presymptomatic_{grp} (E_{grp})   (P_det_{grp})   (* Ks{grp} E_{grp} d_P))

(reaction mild_symptomatic_undet_{grp} (P_{grp})  (Sym_{grp}) (* Ksym{grp} P_{grp} (- 1 d_Sym)))
(reaction mild_symptomatic_det_{grp} (P_{grp})  (Sym_det2_{grp}) (* Ksym{grp} P_{grp} d_Sym))
(reaction severe_symptomatic_undet_{grp} (P_{grp})  (Sys_{grp})  (* Ksys{grp} P_{grp} (- 1 d_Sys)))
(reaction severe_symptomatic_det_{grp} (P_{grp})  (Sys_det3_{grp})  (* Ksys{grp} P_{grp} d_Sys))

(reaction mild_symptomatic_det_{grp} (P_det_{grp})  (Sym_det2_{grp}) (* Ksym{grp} P_det_{grp}))
(reaction severe_symptomatic_det_{grp} (P_det_{grp})  (Sys_det3_{grp})  (* Ksys{grp} P_det_{grp} ))

(reaction hospitalization_1_{grp}   (Sys_{grp})   (H1_{grp})   (* Kh1{grp} Sys_{grp}))
(reaction hospitalization_2_{grp}   (Sys_{grp})   (H2_{grp})   (* Kh2{grp} Sys_{grp}))
(reaction hospitalization_3_{grp}   (Sys_{grp})   (H3_{grp})   (* Kh3{grp} Sys_{grp}))
(reaction critical_2_{grp}   (H2_{grp})   (C2_{grp})   (* Kc{grp} H2_{grp}))
(reaction critical_3_{grp}   (H3_{grp})   (C3_{grp})   (* Kc{grp} H3_{grp}))
(reaction death_{grp}   (C3_{grp})   (D3_{grp})   (* Km C3_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3_{grp})   (H1_det3_{grp})   (* Kh1{grp} Sys_det3_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3_{grp})   (H2_det3_{grp})   (* Kh2{grp} Sys_det3_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3_{grp})   (H3_det3_{grp})   (* Kh3{grp} Sys_det3_{grp}))
(reaction critical_2_det2_{grp}   (H2_det3_{grp})   (C2_det3_{grp})   (* Kc{grp} H2_det3_{grp}))
(reaction critical_3_det2_{grp}   (H3_det3_{grp})   (C3_det3_{grp})   (* Kc{grp} H3_det3_{grp}))
(reaction death_det3_{grp}   (C3_det3_{grp})   (D3_det3_{grp})   (* Km C3_det3_{grp}))

(reaction recovery_As_{grp}   (As_{grp})   (RAs_{grp})   (* Kr_a As_{grp}))
(reaction recovery_As_det_{grp} (As_det1_{grp})   (RAs_det1_{grp})   (* Kr_a As_det1_{grp}))

(reaction recovery_Sym_{grp}   (Sym_{grp})   (RSym_{grp})   (* Kr_m  Sym_{grp}))
(reaction recovery_Sym_det2_{grp}   (Sym_det2_{grp})   (RSym_det2_{grp})   (* Kr_m  Sym_det2_{grp}))
    """.format(grp=grp)


        expand_testDelay_SymSys_str = """
(reaction infection_asymp_undet_{grp}  (E_{grp})   (As_{grp})   (* Kl{grp} E_{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (E_{grp})   (As_det1_{grp})   (* Kl{grp} E_{grp} d_As))
(reaction presymptomatic_{grp} (E_{grp})   (P_{grp})   (* Ks{grp} E_{grp}))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{grp} (P_{grp})  (Sym_preD_{grp}) (* Ksym{grp} P_{grp}))
(reaction severe_symptomatic_{grp} (P_{grp})  (Sys_preD_{grp})  (* Ksys{grp} P_{grp}))

; never detected 
(reaction mild_symptomatic_undet_{grp} (Sym_preD_{grp})  (Sym_{grp}) (* Ksym_D Sym_preD_{grp} (- 1 d_Sym)))
(reaction severe_symptomatic_undet_{grp} (Sys_preD_{grp})  (Sys_{grp})  (* Ksys_D Sys_preD_{grp} (- 1 d_Sys)))

; new detections  - time to detection is substracted from hospital time
(reaction mild_symptomatic_det_{grp} (Sym_preD_{grp})  (Sym_det2_{grp}) (* Ksym_D Sym_preD_{grp} d_Sym))
(reaction severe_symptomatic_det_{grp} (Sys_preD_{grp})  (Sys_det3_{grp})  (* Ksys_D Sys_preD_{grp} d_Sys))

(reaction hospitalization_1_{grp}   (Sys_{grp})   (H1_{grp})   (* Kh1_D{grp} Sys_{grp}))
(reaction hospitalization_2_{grp}   (Sys_{grp})   (H2_{grp})   (* Kh2_D{grp} Sys_{grp}))
(reaction hospitalization_3_{grp}   (Sys_{grp})   (H3_{grp})   (* Kh3_D{grp} Sys_{grp}))
(reaction critical_2_{grp}   (H2_{grp})   (C2_{grp})   (* Kc{grp} H2_{grp}))
(reaction critical_3_{grp}   (H3_{grp})   (C3_{grp})   (* Kc{grp} H3_{grp}))
(reaction death_{grp}   (C3_{grp})   (D3_{grp})   (* Km C3_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3_{grp})   (H1_det3_{grp})   (* Kh1_D{grp} Sys_det3_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3_{grp})   (H2_det3_{grp})   (* Kh2_D{grp} Sys_det3_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3_{grp})   (H3_det3_{grp})   (* Kh3_D{grp} Sys_det3_{grp}))
(reaction critical_2_det2_{grp}   (H2_det3_{grp})   (C2_det3_{grp})   (* Kc{grp} H2_det3_{grp}))
(reaction critical_3_det2_{grp}   (H3_det3_{grp})   (C3_det3_{grp})   (* Kc{grp} H3_det3_{grp}))
(reaction death_det3_{grp}   (C3_det3_{grp})   (D3_det3_{grp})   (* Km C3_det3_{grp}))

(reaction recovery_As_{grp}   (As_{grp})   (RAs_{grp})   (* Kr_a As_{grp}))
(reaction recovery_As_det_{grp} (As_det1_{grp})   (RAs_det1_{grp})   (* Kr_a As_det1_{grp}))
(reaction recovery_Sym_{grp}   (Sym_{grp})   (RSym_{grp})   (* Kr_m_D  Sym_{grp}))
(reaction recovery_Sym_det2_{grp}   (Sym_det2_{grp})   (RSym_det2_{grp})   (* Kr_m_D  Sym_det2_{grp}))
    
    """.format(grp=grp)


        expand_testDelay_AsSymSys_str = """
(reaction infection_asymp_det_{grp}  (E_{grp})   (As_preD_{grp})   (* Kl{grp} E_{grp}))
(reaction infection_asymp_undet_{grp}  (As_preD_{grp})   (As_{grp})   (* Kl_D As_preD_{grp} (- 1 d_As)))
(reaction infection_asymp_det_{grp}  (As_preD_{grp})   (As_det1_{grp})   (* Kl_D As_preD_{grp} d_As))

(reaction presymptomatic_{grp} (E_{grp})   (P_{grp})   (* Ks{grp}  E_{grp} (- 1 d_P)))
(reaction presymptomatic_{grp} (E_{grp})   (P_det_{grp})   (* Ks{grp}  E_{grp} d_P))

; developing symptoms - same time to symptoms as in master emodl
(reaction mild_symptomatic_{grp} (P_{grp})  (Sym_preD_{grp}) (* Ksym{grp} P_{grp}))
(reaction severe_symptomatic_{grp} (P_{grp})  (Sys_preD_{grp})  (* Ksys{grp} P_{grp}))

; never detected 
(reaction mild_symptomatic_undet_{grp} (Sym_preD_{grp})  (Sym_{grp}) (* Ksym_D Sym_preD_{grp} (- 1 d_Sym)))
(reaction severe_symptomatic_undet_{grp} (Sys_preD_{grp})  (Sys_{grp})  (* Ksys_D Sys_preD_{grp} (- 1 d_Sys)))

; new detections  - time to detection is subtracted from hospital time
(reaction mild_symptomatic_det_{grp} (Sym_preD_{grp})  (Sym_det2a_{grp}) (* Ksym_D Sym_preD_{grp} d_Sym))
(reaction severe_symptomatic_det_{grp} (Sys_preD_{grp})  (Sys_det3a_{grp})  (* Ksys_D Sys_preD_{grp} d_Sys))

; developing symptoms - already detected, same time to symptoms as in master emodl
(reaction mild_symptomatic_det_{grp} (P_det_{grp})  (Sym_det2b_{grp}) (* Ksym{grp}  P_det_{grp}))
(reaction severe_symptomatic_det_{grp} (P_det_{grp})  (Sys_det3b_{grp})  (* Ksys{grp}  P_det_{grp} ))

(reaction hospitalization_1_{grp}  (Sys_{grp})   (H1_{grp})   (* Kh1_D{grp} Sys_{grp}))
(reaction hospitalization_2_{grp}   (Sys_{grp})   (H2_{grp})   (* Kh2_D{grp} Sys_{grp}))
(reaction hospitalization_3_{grp}   (Sys_{grp})   (H3_{grp})   (* Kh3_D{grp} Sys_{grp}))
(reaction critical_2_{grp}  (H2_{grp})   (C2_{grp})   (* Kc{grp} H2_{grp}))
(reaction critical_3_{grp}   (H3_{grp})   (C3_{grp})   (* Kc{grp} H3_{grp}))
(reaction death_{grp}   (C3_{grp})   (D3_{grp})   (* Km C3_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3a_{grp})   (H1_det3_{grp})   (* Kh1_D{grp} Sys_det3a_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3a_{grp})   (H2_det3_{grp})   (* Kh2_D{grp} Sys_det3a_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3a_{grp})   (H3_det3_{grp})   (* Kh3_D{grp} Sys_det3a_{grp}))

(reaction hospitalization_1_det_{grp}   (Sys_det3b_{grp})   (H1_det3_{grp})   (* Kh1{grp} Sys_det3b_{grp}))
(reaction hospitalization_2_det_{grp}   (Sys_det3b_{grp})   (H2_det3_{grp})   (* Kh2{grp} Sys_det3b_{grp}))
(reaction hospitalization_3_det_{grp}   (Sys_det3b_{grp})   (H3_det3_{grp})   (* Kh3{grp} Sys_det3b_{grp}))

(reaction critical_2_det2_{grp}   (H2_det3_{grp})   (C2_det3_{grp})   (* Kc{grp} H2_det3_{grp}))
(reaction critical_3_det2_{grp}   (H3_det3_{grp})   (C3_det3_{grp})   (* Kc{grp} H3_det3_{grp}))
(reaction death_det3_{grp}   (C3_det3_{grp})   (D3_det3_{grp})   (* Km C3_det3_{grp}))

(reaction recovery_As_{grp}   (As_{grp})   (RAs_{grp})   (* Kr_a_D As_{grp}))
(reaction recovery_As_det_{grp} (As_det1_{grp})   (RAs_det1_{grp})   (* Kr_a_D As_det1_{grp}))

(reaction recovery_Sym_{grp}   (Sym_{grp})   (RSym_{grp})   (* Kr_m_D  Sym_{grp}))
(reaction recovery_Sym_det2a_{grp}   (Sym_det2a_{grp})   (RSym_det2_{grp})   (* Kr_m_D  Sym_det2a_{grp}))
(reaction recovery_Sym_det2b_{grp}   (Sym_det2b_{grp})   (RSym_det2_{grp})   (* Kr_m  Sym_det2b_{grp}))
     """.format(grp=grp)

        if self.expandModel ==None :
            reaction_str =  expand_base_str + reaction_str_III
        if self.expandModel == "testDelay_SymSys" or self.expandModel == "uniformtestDelay" :
            reaction_str =  expand_testDelay_SymSys_str + reaction_str_III
        if self.expandModel == 'testDelay_AsSymSys':
            reaction_str =  expand_testDelay_AsSymSys_str + reaction_str_III

        reaction_str = reaction_str.replace("  ", " ")

        return reaction_str

    def define_change_detection_and_isolation(self,
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

                for grp in self.grpList:

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
        time_event_str = """(time-event contact_tracing_start @contact_tracing_start_1@ ( {change_param} ))""".format(change_param=change_param_str)

        contactTracing_str = observe_str + "\n" + time_event_str

        return contactTracing_str

    def write_interventions(self,total_string) :

        param_change_str = """
(time-event detection1 @detection_time_1@ ((d_Sys @d_Sys_incr1@)))
(time-event detection2 @detection_time_2@ ((d_Sys @d_Sys_incr2@)))
(time-event detection3 @detection_time_3@ ((d_Sys @d_Sys_incr3@)))
(time-event detection4 @detection_time_4@ ((d_Sys @d_Sys_incr4@)))
(time-event detection5 @detection_time_5@ ((d_Sys @d_Sys_incr5@)))
(time-event detection6 @detection_time_6@ ((d_Sys @d_Sys_incr6@)))
(time-event detection5 @detection_time_7@ ((d_Sys @d_Sys_incr7@)))
    """

    #TODO results in negative counts
    #(param cfr_change1_{grp} (* @cfr_{grp}@ (/ 2 3) ) )
    #(param cfr_change2_{grp} (* @cfr_{grp}@ (/ 1 3) ) )
    #(observe cfr_t_{grp} cfr_{grp})
    #(time-event cfr_adjust1_{grp} @cfr_time_1@ ((cfr_{grp} cfr_change1_{grp}) (fraction_dead_{grp} (/ cfr fraction_severe_{grp})) (fraction_hospitalized_{grp} (- 1 (+ fraction_critical fraction_dead_{grp}))) (Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization)) (Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization )) (Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys))) (Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) )) ))
    #(time-event cfr_adjust2_{grp} @cfr_time_2@ ((cfr_{grp} cfr_change2_{grp}) (fraction_dead_{grp} (/ cfr fraction_severe_{grp})) (fraction_hospitalized_{grp} (- 1 (+ fraction_critical fraction_dead_{grp}))) (Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization)) (Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization )) (Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys))) (Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) )) ))

        param_change_age_specific_str = ""
        for grp in self.grpList:
            temp_str =  """
(observe frac_crit_t_{grp} fraction_critical_{grp})
(observe fraction_hospitalized_t_{grp} fraction_hospitalized_{grp})
(observe fraction_dead_t_{grp} fraction_dead_{grp})

(time-event frac_crit_adjust1_{grp} @crit_time_1@ ((fraction_critical_{grp} @fraction_critical_incr1@) (fraction_hospitalized_{grp} (- 1 (+ @fraction_critical_incr1@ fraction_dead_{grp}))) (Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization)) (Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization )) (Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys))) (Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) )) ))  
(time-event frac_crit_adjust2_{grp} @crit_time_2@ ((fraction_critical_{grp} @fraction_critical_incr2@) (fraction_hospitalized_{grp} (- 1 (+ @fraction_critical_incr2@ fraction_dead_{grp}))) (Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization)) (Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization )) (Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys))) (Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) )) ))
(time-event frac_crit_adjust3_{grp} @crit_time_3@ ((fraction_critical_{grp} @fraction_critical_incr3@) (fraction_hospitalized_{grp} (- 1 (+ @fraction_critical_incr3@ fraction_dead_{grp}))) (Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization)) (Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization )) (Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys))) (Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) )) )) 

(param fraction_dead_change1_{grp} (* @fraction_dead_{grp}@ (/ 2 3) ) )
(param fraction_dead_change2_{grp} (* @fraction_dead_{grp}@ (/ 1 3) ) )
(time-event fraction_dead_adjust1_{grp} @cfr_time_1@ ((fraction_dead_{grp} fraction_dead_change1_{grp}) (fraction_hospitalized_{grp} (- 1 (+ fraction_critical_{grp} fraction_dead_{grp}))) (Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization)) (Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization )) (Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys))) (Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) )) )) 
(time-event fraction_dead_adjust2_{grp} @cfr_time_2@ ((fraction_dead_{grp} fraction_dead_change2_{grp}) (fraction_hospitalized_{grp} (- 1 (+ fraction_critical_{grp} fraction_dead_{grp}))) (Kh1{grp} (/ fraction_hospitalized_{grp} time_to_hospitalization)) (Kh2{grp} (/ fraction_critical_{grp} time_to_hospitalization )) (Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys))) (Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) )) )) 
    """.format(grp=grp)
            param_change_age_specific_str = param_change_age_specific_str + temp_str

        # TODO results in worse fitting?
        #param_change_str = param_change_str + param_change_age_specific_str

        ki_multiplier_change_str = """
(param Ki_red3a (* Ki @ki_multiplier_3a@))
(param Ki_red3b (* Ki @ki_multiplier_3b@))
(param Ki_red3c (* Ki @ki_multiplier_3c@))
(param Ki_red4 (* Ki @ki_multiplier_4@))
(param Ki_red6 (* Ki @ki_multiplier_6@))
(param Ki_red7 (* Ki @ki_multiplier_7@))
(param Ki_red8 (* Ki @ki_multiplier_8@))
(param Ki_red9 (* Ki @ki_multiplier_9@))
(param Ki_red10 (* Ki @ki_multiplier_10@))
(param Ki_red11 (* Ki @ki_multiplier_11@))
(param Ki_red12 (* Ki @ki_multiplier_12@))
(param Ki_red13 (* Ki @ki_multiplier_13@))

(param backtonormal_multiplier_1  (/ (- Ki_red6  Ki_red4 ) (- Ki Ki_red4 ) ) )  
(observe backtonormal_multiplier_1 backtonormal_multiplier_1)

(time-event ki_multiplier_change_3a @ki_multiplier_time_3a@ ((Ki Ki_red3a)))
(time-event ki_multiplier_change_3b @ki_multiplier_time_3b@ ((Ki Ki_red3b)))
(time-event ki_multiplier_change_3c @ki_multiplier_time_3c@ ((Ki Ki_red3c)))
(time-event ki_multiplier_change_4 @ki_multiplier_time_4@ ((Ki Ki_red4)))
(time-event ki_multiplier_change_6 @ki_multiplier_time_6@ ((Ki Ki_red6)))
(time-event ki_multiplier_change_7 @ki_multiplier_time_7@ ((Ki Ki_red7)))
(time-event ki_multiplier_change_8 @ki_multiplier_time_8@ ((Ki Ki_red8)))
(time-event ki_multiplier_change_9 @ki_multiplier_time_9@ ((Ki Ki_red9)))
(time-event ki_multiplier_change_10 @ki_multiplier_time_10@ ((Ki Ki_red10)))
(time-event ki_multiplier_change_11 @ki_multiplier_time_11@ ((Ki Ki_red11)))
(time-event ki_multiplier_change_12 @ki_multiplier_time_12@ ((Ki Ki_red12)))
(time-event ki_multiplier_change_13 @ki_multiplier_time_13@ ((Ki Ki_red13)))
    """

        rollback_str = """
(time-event ki_multiplier_change_rollback @socialDistance_rollback_time@ ((Ki Ki_red7)))
    """


        rollbacktriggered_str =  """
(state-event rollbacktrigger (and (> time @today@) (> {channel} (* @trigger@ @capacity_multiplier@)) ) ((Ki Ki_red7)))
    """

        rollbacktriggered_delay_str = """
(param time_of_trigger 10000)
(state-event rollbacktrigger (and (> time @today@) (> crit_det (* @trigger@ @capacity_multiplier@)) ) ((time_of_trigger time)))
(func time_since_trigger (- time time_of_trigger))
(state-event apply_rollback (> (- time_since_trigger @trigger_delay_days@) 0) ((Ki Ki_red7)))   
(observe triggertime_{grpout} time_of_trigger)
    """

        d_Sym_change_str = """
(time-event d_Sym_change1 @d_Sym_change_time_1@ ((d_Sym @d_Sym_change1@)))
(time-event d_Sym_change2 @d_Sym_change_time_2@ ((d_Sym @d_Sym_change2@)))
(time-event d_Sym_change3 @d_Sym_change_time_3@ ((d_Sym @d_Sym_change3@)))
(time-event d_Sym_change4 @d_Sym_change_time_4@ ((d_Sym @d_Sym_change4@)))
(time-event d_Sym_change5 @d_Sym_change_time_5@ ((d_Sym @d_Sym_change5@)))
    """

        interventionSTOP_str ="""
(param Ki_back (* Ki @backtonormal_multiplier@))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki Ki_back)))
     """

    # % change from lowest transmission level - immediate
    # starting point is lowest level of transmission  Ki_red4
        interventionSTOP_adj_str = """
(param Ki_back (+ Ki_red7 (* @backtonormal_multiplier@ (- Ki Ki_red7))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki Ki_back)))
    """

    # % change from current transmission level - immediate
    # starting point is current level of transmission  Ki_red6
        interventionSTOP_adj2_str = """
(param Ki_back (+ Ki_red7 (* @backtonormal_multiplier@ (- Ki Ki_red7))))
(time-event stopInterventions @socialDistanceSTOP_time@ ((Ki Ki_back)))
    """


    # gradual reopening from 'lowest' transmission level,  Ki_red6 == Ki_back1
        gradual_reopening_str = """
(param backtonormal_multiplier_1_adj  (- @backtonormal_multiplier@ backtonormal_multiplier_1 ))
(observe backtonormal_multiplier_1_adj  backtonormal_multiplier_1_adj)

(param Ki_back2 (+ Ki_red6 (* backtonormal_multiplier_1_adj 0.3333 (- Ki Ki_red4))))
(param Ki_back3 (+ Ki_red6 (* backtonormal_multiplier_1_adj 0.6666 (- Ki Ki_red4))))
(param Ki_back4 (+ Ki_red6 (* backtonormal_multiplier_1_adj 1.00 (- Ki Ki_red4))))
(time-event gradual_reopening2 @gradual_reopening_time1@ ((Ki Ki_back2)))
(time-event gradual_reopening3 @gradual_reopening_time2@ ((Ki Ki_back3)))
(time-event gradual_reopening4 @gradual_reopening_time3@ ((Ki Ki_back4)))
    """

    # gradual reopening from 'current' transmission level
        gradual_reopening2_str = """
(param Ki_back1 (+ Ki_red7 (* @reopening_multiplier_4@ 0.25 (- Ki Ki_red7))))
(param Ki_back2 (+ Ki_red7 (* @reopening_multiplier_4@ 0.50 (- Ki Ki_red7))))
(param Ki_back3 (+ Ki_red7 (* @reopening_multiplier_4@ 0.75 (- Ki Ki_red7))))
(param Ki_back4 (+ Ki_red7 (* @reopening_multiplier_4@ 1.00 (- Ki Ki_red7))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki Ki_back1)))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki Ki_back2)))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki Ki_back3)))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki Ki_back4)))
     """

    # gradual reopening from 'current' transmission level with region-specific reopening
        gradual_reopening3_str = """
(param Ki_back1 (+ Ki_red7 (* @reopening_multiplier_4@ 0.25 (- Ki Ki_red7))))
(param Ki_back2 (+ Ki_red7 (* @reopening_multiplier_4@ 0.50 (- Ki Ki_red7))))
(param Ki_back3 (+ Ki_red7 (* @reopening_multiplier_4@ 0.75 (- Ki Ki_red7))))
(param Ki_back4 (+ Ki_red7 (* @reopening_multiplier_4@ 1.00 (- Ki Ki_red7))))
(time-event gradual_reopening1 @gradual_reopening_time1@ ((Ki Ki_back1)))
(time-event gradual_reopening2 @gradual_reopening_time2@ ((Ki Ki_back2)))
(time-event gradual_reopening3 @gradual_reopening_time3@ ((Ki Ki_back3)))
(time-event gradual_reopening4 @gradual_reopening_time4@ ((Ki Ki_back4)))
    """


        improveHS_str = covidModel.define_change_detection_and_isolation(self,
                                        reduced_inf_of_det_cases = False,
                                        d_As = False,
                                        d_P = False ,
                                        d_Sym_ct = True,
                                        d_Sym_grp = False,
                                        d_Sym_grp_option = 'increase_to_common_target')


        contactTracing_str = covidModel.define_change_detection_and_isolation(self,
                                        reduced_inf_of_det_cases = True,
                                        d_As = True,
                                        d_P = True ,
                                        d_Sym_ct = False,
                                        d_Sym_grp = False,
                                        d_Sym_grp_option = None)


        contactTracing_improveHS_str = covidModel.define_change_detection_and_isolation(self,
                                        reduced_inf_of_det_cases = True,
                                        d_As = True,
                                        d_P = True,
                                        d_Sym_ct = True,
                                        d_Sym_grp = False,
                                        d_Sym_grp_option = 'increase_to_common_target')

    ##### change_uniformtestDelay_str
        temp_age_str = ""
        for grp in self.grpList:
            temp_str =  """
(Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D))) 
(Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D) ))
(Kh3_D{grp} (/ fraction_dead_{grp} (- time_to_hospitalization time_D)))
    """.format(grp=grp)
            temp_age_str = temp_age_str + temp_str

        change_uniformtestDelay_str = """
(time-event change_testDelay1 @change_testDelay_time1@ ( (time_D @change_testDelay_1@) (Ksys_D (/ 1 time_D)) (Ksym_D (/ 1 time_D))  {temp_age_str} (Kr_m_D (/ 1 (- recovery_time_mild time_D ))) ))
        """.format(temp_age_str=temp_age_str)


    ##### change_testDelay_Sym_str

        change_testDelay_Sym_str = """
(time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} ))
        """.format("(time_D_Sym @change_testDelay_Sym_1@)",
                   "(Ksym_D (/ 1 time_D_Sym))",
                   "(Kr_m_D (/ 1 (- recovery_time_mild time_D_Sym )))")

    ##### change_testDelay_Sys_str
        temp_age_str = ""
        for grp in self.grpList:
            temp_str =  """
(Kh1_D{grp} (/ fraction_hospitalized_{grp} (- time_to_hospitalization time_D_Sys))) 
(Kh2_D{grp} (/ fraction_critical_{grp} (- time_to_hospitalization time_D_Sys) ))
(Kh3_D{grp} (/ fraction_dead_{grp} (- time_to_hospitalization time_D_Sys)))
    """.format(grp=grp)
            temp_age_str = temp_age_str + temp_str

        change_testDelay_Sys_str = """
(time-event change_testDelay1 @change_testDelay_time1@ ( (time_D_Sys @change_testDelay_Sys_1@) (Ksys_D (/ 1 time_D_Sys)) {temp_age_str} ))
        """.format(temp_age_str=temp_age_str)


        change_testDelay_As_str = """
(time-event change_testDelay1 @change_testDelay_time1@ ( {} {} {} ))
        """.format("(time_D_As @change_testDelay_As_1@)",
                   "(Kl_D (/ 1 time_D_As))",
                   "(Kr_a_D (/ 1 (- recovery_time_asymp time_D_As )))")

        fittedTimeEvents_str = param_change_str + ki_multiplier_change_str + d_Sym_change_str

        if self.add_interventions == "interventionStop" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_str)
        if self.add_interventions == "interventionSTOP_adj" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj_str)
        if self.add_interventions == "interventionSTOP_adj2":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj2_str)
        if self.add_interventions == "gradual_reopening" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening_str)
        if self.add_interventions == "gradual_reopening2" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str)
        if self.add_interventions == "gradual_reopening3" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening3_str)
        if self.add_interventions == "baseline" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str)
        if self.add_interventions == "rollback" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + rollback_str)
        if self.add_interventions == "reopen_rollback":
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + interventionSTOP_adj2_str + rollback_str)
        if self.add_interventions == "reopen_contactTracing" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + contactTracing_str)
        if self.add_interventions == "reopen_contactTracing_improveHS" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + contactTracing_improveHS_str)
        if self.add_interventions == "reopen_improveHS" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + improveHS_str)
        if self.add_interventions == "contactTracing" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + contactTracing_str)
        if self.add_interventions == "contactTracing_improveHS" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + contactTracing_improveHS_str)
        if self.add_interventions == "improveHS" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + improveHS_str)
        if self.add_interventions == "rollbacktriggered" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + rollbacktriggered_str)
        if self.add_interventions == "rollbacktriggered_delay" :
            total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening3_str + rollbacktriggered_delay_str)

       # if scenarioName == "gradual_contactTracing" :
       #    total_string = total_string.replace(';[INTERVENTIONS]', fittedTimeEvents_str + gradual_reopening2_str + contactTracing_gradual_str)


        if self.change_testDelay != None :
            if self.change_testDelay == "uniform" :
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_uniformtestDelay_str)
            if self.change_testDelay == "As"  :
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str )
            if self.change_testDelay == "Sym"  :
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sym_str )
            if self.change_testDelay == "Sys"  :
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sys_str )
            if self.change_testDelay == "AsSym"  :
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_Sym_str )
            if self.change_testDelay == "SymSys" :
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)
            if self.change_testDelay == "AsSymSys" :
                total_string = total_string.replace(';[ADDITIONAL_TIMEEVENTS]', change_testDelay_As_str + '\n' + change_testDelay_Sym_str + '\n' + change_testDelay_Sys_str)


        return total_string



    ###stringing all of the functions together to make the file:
    def generate_emodl(self):
        if self.emodl_name is None:
            emodl_name = f'{self.model}_{self.add_interventions}'
            file_output = os.path.join(self.emodl_dir, f'{emodl_name}.emodl')
        else:
            file_output = os.path.join(self.emodl_dir, f'{self.emodl_name}.emodl')
        if (os.path.exists(file_output)):
            os.remove(file_output)

        model_name = "seir.emodl"
        header_str = "; simplemodel \n\n" + "(import (rnrs) (emodl cmslib)) \n\n" + '(start-model "{}") \n\n'.format(
            model_name)
        footer_str = "(end-model)"

        # building up the .emodl string
        total_string = ""
        species_string = ""
        observe_string = ""
        reaction_string = ""
        functions_string = ""
        age_specific_param_string = ""
        total_string = total_string + header_str

        for grp in self.grpList:
            species = covidModel.write_species(self, grp)
            observe = covidModel.write_observe(self, grp)
            reaction = covidModel.write_reactions(self, grp)
            functions = covidModel.write_functions(self, grp)
            species_string = species_string + species
            observe_string = observe_string + observe
            reaction_string = reaction_string + reaction
            functions_string = functions_string + functions
            age_specific_param_string = age_specific_param_string + covidModel.write_age_specific_param(self, grp)

        if (self.homogeneous == False):
            if (len(self.grpList) == 4):
                reaction_string_combined = covidModel.write_exposure_reaction4() + '\n' + reaction_string
            if (len(self.grpList) == 8):
                reaction_string_combined = covidModel.write_exposure_reaction8() + '\n' + reaction_string

        elif (self.homogeneous == True):
            reaction_string_combined = ""
            for grp in self.grpList:
                temp = covidModel.write_exposure_reaction_homogeneous(grp)
                reaction_string_combined = reaction_string_combined + temp

            reaction_string_combined = reaction_string_combined + '\n' + reaction_string

        params = covidModel.write_params(self) + age_specific_param_string + covidModel.write_N_population(self) + covidModel.write_observed_param(self) + covidModel.write_contact_matrix(len(self.grpList))
        if self.add_ageShift_2ndWave:
            params = params + covidModel.write_ageShift_2ndWave(len(self.grpList))
        functions_string = functions_string + covidModel.write_All(self)
        intervention_string = ";[INTERVENTIONS]\n;[ADDITIONAL_TIMEEVENTS]"

        total_string = total_string + '\n\n' + species_string + '\n\n' + functions_string + '\n\n' + observe_string + '\n\n' + params  + '\n\n' + intervention_string + '\n\n' + reaction_string_combined + '\n\n' + footer_str

        ### Add interventions (optional)
        if self.add_interventions != None :
            total_string =  covidModel.write_interventions(self,total_string)

        emodl = open(file_output, "w")  ## again, can make this more dynamic
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
                         'observeLevel' : ('primary','secondary','tertiary','all'),
                         'homogeneous' : ('True','False'),
                         'add_ageShift_2ndWave' : ('True','False'),
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

