from datetime import date, timedelta
import numpy as np
import os, sys
import numpy as np
import subprocess
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import matplotlib.dates as mdates

master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
detection_channel_list = ['detected', 'detected_cumul',  'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul',  'crit_det_cumul']
custom_channel_list = ['detected_cumul', 'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul', 'crit_det_cumul', 'symp_cumul',  'asymp_cumul','hosp_cumul', 'crit_cumul']
first_day = date(2020, 3, 1)



Kivalues =  np.random.uniform(3.23107e-06, 4.7126e-06 , 1)   # [9e-05, 7e-06, 8e-06, 9e-06, 9e-077]

def CI_5(x) :
    return np.percentile(x, 5)

def CI_95(x) :
    return np.percentile(x, 95)

def CI_25(x) :
    return np.percentile(x, 25)

def CI_75(x) :
    return np.percentile(x, 75)


class model:
    def __init__(self, modeltype, modelname):#, param_dic):#, groups):
        self.modeltype= modeltype
        self.modelname= modelname
        #self.param_dic= param_dic
        
    def read_group_dictionary(self, filepath, grpname, testMode, ngroups=2):
        import csv
        grp_dic = {}
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                grp_dic[row[grpname]] = [int(x) for x in row['val_list'].strip('][').split(', ')]

        if testMode == True:
            grp_dic = {k: grp_dic[k] for k in sorted(grp_dic.keys())[:ngroups]}

        return grp_dic

    ### data management. these are SAME for any emodl
    def reprocess(self, git_dir, input_fname='trajectories.csv', output_fname=None):
        """
        this function combines trajectories, since individual traj files are not useful on their own. 
        """

        fname = os.path.join(git_dir, input_fname)
        row_df = pd.read_csv(fname, skiprows=1)
        #print(row_df.head())
        df = row_df.set_index('sampletimes').transpose()
        num_channels = len([x for x in df.columns.values if '{0}' in x])
        num_samples = int((len(row_df) - 1) / num_channels)

        df = df.reset_index(drop=False)
        df = df.rename(columns={'index': 'time'})
        df['time'] = df['time'].astype(float)

        adf = pd.DataFrame()
        for sample_num in range(num_samples):
            channels = [x for x in df.columns.values if '{%d}' % sample_num in x]
            sdf = df[['time'] + channels]
            sdf = sdf.rename(columns={
                x: x.split('{')[0] for x in channels
            })
            sdf['sample_num'] = sample_num
            adf = pd.concat([adf, sdf])

        adf = adf.reset_index()
        del adf['index']
        if output_fname:
            adf.to_csv(os.path.join(sim_output_path,output_fname))
        return adf


    def combineTrajectories(self, Nscenarios, sim_output_path, git_dir, deleteFiles=False):
        print(os.path.join(git_dir, self.modeltype,"scenarios.csv"))
        scendf = pd.read_csv(os.path.join(git_dir, self.modeltype,"scenarios.csv"), index_col=0)
        #del scendf['Unnamed: 0']

        df_list = []
        for scen_i in range(1, Nscenarios):
            input_name = "trajectories_scen" + str(scen_i) + ".csv"
#             print(os.path.exists(input_name)) ##qc
#             try:
            print("inputname:",input_name )
            df_i = self.reprocess(git_dir, input_fname=input_name, output_fname=None) ### this is what is erroring
#             print(df_i) ##qc
            df_i['scen_num'] = scen_i
            df_i = df_i.merge(scendf, on=['scen_num','sample_num'])
            df_list.append(df_i)
#             print('try')
#             except:
#                 continue

            if deleteFiles == True: os.remove(os.path.join(git_dir, input_name))

        dfc = pd.concat(df_list)
        dfc.to_csv( os.path.join(sim_output_path, "trajectoriesDat.csv"))

        return dfc
    

    
    def melter(self, df):
        """
        overview: melts columns of the grouped 
        it woulda been fairly straight forward, but i wanted to automate the finding of columns we want to keep so we dont need ot specify which columns have the prefex and suffix, and which we want to keep. 
        it should be all automatic now base_names splits a string into a list based on the "_" delimiter, and takes the first entry, but only if the entry list is longer than 1 and i do that for all column names

        suffix_list does same thing but takes the last entry and excludes a few suffixes (sample_num and scen_num). 
        so it does a pretty good job at finding the "channels" (base_names) and the channel groups (suffix_names).   
        i then make a list of booleans that loops over all column names and makes it true if any of the suffix_names match the col name. 
        so the final result is a bool list of all columns we want to pivot.

        """
        # generating a list of base names in cols we might want to keep:
        base_names=set([x.split('_')[0] for x in list(df) if len(x.split('_'))>1 and x not in ['scen','sample']])
        # generating a list of suffix names in cols we might want to keep:
        suffix_names= list(set([x.split('_')[-1] for x in list(df) if len(x.split('_'))>1 and x not in['sample_num', 'scen_num']]))
        #### automated wrangling columns wanted for melt
        col_bools= []
        for element in list(df):
            col_bools.append(any(substring in element for substring in suffix_names))
        ### melting from wide to long
        df_melted=pd.melt(df, id_vars=[x for x in list(df) if x not in list(df.loc[:,col_bools])], value_vars=list(df.loc[:,col_bools]), var_name='channels')
        df_melted['base_channel']= df_melted['channels'].apply(lambda x: "_".join(str(x).split('_')[:-1]))
        df_melted['base_group']= df_melted['channels'].apply(lambda x: str(x).split('_')[-1])

        return(df_melted)
    
    
    ##plotting functions
    
    #def detection_plot(self, df,first_day, allchannels='detected_cumul', chicago=True, chicago_filepath=os.path.join(wdir,'chicago/chicago_cases.csv'), save=False, plotname="detected_plot" ):
    def detection_plot(self, df,first_day, allchannels, chicago, chicago_filepath, save, plotname, git_dir):
        #sys.path.append(os.path.join(git_dir,'spatial_model'))
        from detection_plot import detection_plot
        detection_plot(df,first_day, allchannels, chicago, chicago_filepath, save, plotname )
        
    def plot_origional(self, adf, plotchannels, plot_path):
        """Manuela's origional plotting function in extended_model_postprocessing"""
        fig = plt.figure(figsize=(12,6))

#         plotchannels = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic',
#                         'detected', 'hospitalized', 'critical', 'deaths', 'recovered',
#                         'new_detected', 'new_hospitalized', 'new_deaths']
        palette = sns.color_palette('muted', len(plotchannels))
        axes = [fig.add_subplot(3,4,x+1) for x in range(len(plotchannels))]
        fig.subplots_adjust(bottom=0.05, hspace=0.25, right=0.95, left=0.1)
        for c, channel in enumerate(plotchannels) :

            mdf = adf.groupby('time')[channel].agg([np.mean, CI_5, CI_95, CI_25, CI_75]).reset_index()
            ax = axes[c]
            dates = [first_day + timedelta(days=int(x)) for x in mdf['time']]
            ax.plot(dates, mdf['mean'], label=channel, color=palette[c])
            ax.fill_between(dates, mdf['CI_5'], mdf['CI_95'],
                            color=palette[c], linewidth=0, alpha=0.2)
            ax.fill_between(dates, mdf['CI_25'], mdf['CI_75'],
                            color=palette[c], linewidth=0, alpha=0.4)

            ax.set_title(channel, y=0.8)

            formatter = mdates.DateFormatter("%m-%d")
            ax.xaxis.set_major_formatter(formatter)
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.set_xlim(first_day, )

        plt.savefig(os.path.join(plot_path, 'sample_plot_withIncidence.png'))

        plt.show()

        
class spatial_model(model):
    
    def __init__(self,modelname, modeltype='spatial_model'):
        self.modeltype='spatial_model'
        self.modelname=modelname
    
    def generate_emodl(self, county_dic, emodl_output, verbose=False ):
        from locale_emodl_generator import generate_locale_emodl, generate_locale_cfg
        generate_locale_emodl(county_dic, emodl_output, verbose=False)
        self.emodl_output= emodl_output
        print('emodl generated')
        
    def generate_extended_emodl(self, grp_dic, file_output, verbose=False):
        from emodl_generator_extended import generate_extended_emodl
        #grp_dic, file_output, verbose=False
        generate_extended_emodl(grp_dic,
                                file_output,
                                verbose)
        

        
#     def replaceParameters_extended(df, Ki_i, sample_nr, emodlname) :
        
        
#         fin = open(os.path.join(emodl_dir,emodlname), "rt")
#         data = fin.read()
#         data = data.replace('@speciesS@', str(df.speciesS[sample_nr]))
#         data = data.replace('@initialAs@', str(df.initialAs[sample_nr]))
#         data = data.replace('@incubation_pd@', str(df.incubation_pd[sample_nr]))
#         data = data.replace('@time_to_hospitalization@', str(df.time_to_hospitalization[sample_nr]))
#         data = data.replace('@time_to_critical@', str(df.time_to_critical[sample_nr]))
#         data = data.replace('@time_to_death@', str(df.time_to_death[sample_nr]))
#         data = data.replace('@fraction_hospitalized@', str(df.fraction_hospitalized[sample_nr]))
#         data = data.replace('@fraction_symptomatic@', str(df.fraction_symptomatic[sample_nr]))
#         data = data.replace('@fraction_critical@', str(df.fraction_critical[sample_nr]))
#         data = data.replace('@reduced_inf_of_det_cases@', str(df.reduced_inf_of_det_cases[sample_nr]))
#         data = data.replace('@cfr@', str(df.cfr[sample_nr]))
#         data = data.replace('@d_As@', str(df.d_As[sample_nr]))
#         data = data.replace('@d_Sy@', str(df.d_Sy[sample_nr]))
#         data = data.replace('@d_H@', str(df.d_H[sample_nr]))
#         data = data.replace('@recovery_rate@', str(df.recovery_rate[sample_nr]))
#         data = data.replace('@Ki@', str(Ki_i))
#         # data = data.replace('@Ki@', str(df.Ki[sub_sample]))
#         fin.close()
#         fin = open(os.path.join(temp_dir, "simulation_i.emodl"), "wt")
#         fin.write(data)
#         fin.close()
        

    def param_sample(self):
        speciesS = 360980
        initialAs = np.random.uniform(1, 5)
        incubation_pd = np.random.uniform(4.2, 6.63)
        time_to_hospitalization = np.random.normal(5.9, 2)
        time_to_critical = np.random.normal(5.9, 2)
        time_to_death = np.random.uniform(1, 3)
        recovery_rate = np.random.uniform(6, 16)
        fraction_hospitalized = np.random.uniform(0.1, 5)
        fraction_symptomatic = np.random.uniform(0.5, 0.8)
        fraction_critical = np.random.uniform(0.1, 5)
        reduced_inf_of_det_cases = np.random.uniform(0,1)
        cfr = np.random.uniform(0.008, 0.022)
        d_Sy = np.random.uniform(0.2, 0.3)
        d_H = 1
        d_As = 0
        Ki = np.random.uniform(1e-6, 9e-5)
        incubation_pd= 6.63
        recovery_rate=16
        waning=180
        return({'speciesS':speciesS,
                'initialAs':initialAs,
                'incubation_pd':incubation_pd,
                'time_to_hospitalization':time_to_hospitalization,
                'time_to_critical':time_to_critical,
                'time_to_death':time_to_death,
                'recovery_rate':recovery_rate,
                'fraction_hospitalized':fraction_hospitalized,
                'fraction_symptomatic':fraction_symptomatic,
                'fraction_critical':fraction_critical,
                'reduced_inf_of_det_cases':reduced_inf_of_det_cases,
                'cfr':cfr,
                'd_Sy':d_Sy,
                'd_H':d_H,
                'd_As':d_As,
                'Ki':Ki,
               'incubation_pd':incubation_pd,
               'recovery_rate':recovery_rate,
               'waning':waning})
    

    def replaceParameters(self, param_df, Ki_i, sample_nr, emodl_output) :
        fin = open(emodl_output, "rt")
        data = fin.read()
        data = data.replace('@Ki@', str(Ki_i))
        data = data.replace('@incubation_pd@', str(param_df.incubation_pd[sample_nr]))
        data = data.replace('@recovery_rate@', str(param_df.recovery_rate[sample_nr]))
        data = data.replace('@waning@', str(param_df.waning[sample_nr]))
        fin.close()
        fin = open(os.path.join(self.temp_dir, "{}_i.emodl".format(self.modelname)), "wt")
        fin.write(data)
        fin.close()
        
    def runExp(self, sub_samples, exe_dir, git_dir, ):
        import subprocess
        self.git_dir= git_dir
        self.temp_dir=os.path.join(self.git_dir, '_temp')
        lst = []
        scen_num = 0
        
        #construct a dataframe off the sampled values
        param_df=pd.DataFrame(self.param_sample(), index=[0])
        for sample in range(1,sub_samples):
            param_df= param_df.append(self.param_sample(), ignore_index=True)
        param_df.to_csv(os.path.join(git_dir,"{}".format(self.modeltype),"param_df.csv"))
        self.param_df=param_df
        self.sub_samples=sub_samples
        
        for sample in range(sub_samples):
            for i in range(param_df['Ki'].nunique()):
                scen_num += 1
                lst.append([sample, scen_num, param_df['Ki'].unique()[i]]) 
                ################define_and_replaceParameters(Ki_i=i) ### this will need to be changed at some point if we want to test multiple Ki values. 
                self.replaceParameters(param_df, param_df['Ki'].unique()[i], sample, self.emodl_output)#, self.temp_dir)
                # adjust simplemodel.cfg
                fin = open(os.path.join(git_dir, 'cfg',"model.cfg"), "rt")

                data_cfg = fin.read()
                data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))

                fin.close()
                fin = open("simplemodel_i.cfg", "wt")
                fin.write(data_cfg)
                fin.close()

                file = open('runModel_i.bat', 'w')
                file.write('\n"' +
                           os.path.join(exe_dir, "compartments.exe") +'"' + ' -c ' + '"' +
                           os.path.join(git_dir,"simplemodel_i.cfg") +'"' + ' -m ' + '"' +
                           os.path.join(self.temp_dir, "{}_i.emodl".format(self.modelname)) + '"'
                          )
                file.close()

                subprocess.call([r'runModel_i.bat'])
                print("scen_{} run".format(scen_num))
            print("sample_{} run".format(sample))

        df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki'])
        df.to_csv("spatial_model//scenarios.csv")
        return (scen_num)
        
    
#     def replaceParameters(df, Ki_i, sample_nr, emodlname) :
#         fin = open(os.path.join(emodl_dir,emodlname), "rt")
#         data = fin.read()
#         data = data.replace('@speciesS@', str(df.speciesS[sample_nr]))
#         data = data.replace('@initialAs@', str(df.initialAs[sample_nr]))
#         data = data.replace('@incubation_pd@', str(df.incubation_pd[sample_nr]))
#         data = data.replace('@time_to_hospitalization@', str(df.time_to_hospitalization[sample_nr]))
#         data = data.replace('@time_to_critical@', str(df.time_to_critical[sample_nr]))
#         data = data.replace('@time_to_death@', str(df.time_to_death[sample_nr]))
#         data = data.replace('@fraction_hospitalized@', str(df.fraction_hospitalized[sample_nr]))
#         data = data.replace('@fraction_symptomatic@', str(df.fraction_symptomatic[sample_nr]))
#         data = data.replace('@fraction_critical@', str(df.fraction_critical[sample_nr]))
#         data = data.replace('@reduced_inf_of_det_cases@', str(df.reduced_inf_of_det_cases[sample_nr]))
#         data = data.replace('@cfr@', str(df.cfr[sample_nr]))
#         data = data.replace('@d_As@', str(df.d_As[sample_nr]))
#         data = data.replace('@d_Sy@', str(df.d_Sy[sample_nr]))
#         data = data.replace('@d_H@', str(df.d_H[sample_nr]))
#         data = data.replace('@recovery_rate@', str(df.recovery_rate[sample_nr]))
#         data = data.replace('@Ki@', str(Ki_i))
#         # data = data.replace('@Ki@', str(df.Ki[sub_sample]))
#         fin.close()
#         fin = open(os.path.join(temp_dir, "simulation_i.emodl"), "wt")
#         fin.write(data)
#         fin.close()
    
    
#     def runExp_fullFactorial() :

#     lst = []
#     scen_num = 0

#     # Requires exactly that order!
#     for i in itertools.product(initial_infect, Ki, incubation_pd, recovery_rate) :
#         scen_num += 1
#        # print(i)

#         lst.append([scen_num ,i, "initial_infect, Ki, incubation_pd, recovery_rate"])

#         fin = open(os.path.join(git_dir, "simple_model","simplemodel_covid.emodl"), "rt")
#         data = fin.read()
#         data = data.replace('(species I 10)', '(species I ' + str(i[0]) +')')
#         data = data.replace('(param Ki 0.319)', '(param Ki '  + str(i[1]) +')')
#         data = data.replace('(param incubation_pd 6.63)', '(param incubation_pd ' + str(i[2]) +')')
#         data = data.replace('(param recovery_rate 16)', '(param recovery_rate '  + str(i[3]) +')')
#         fin.close()

#         fin = open(os.path.join(git_dir, "simple_model","simplemodel_covid_i.emodl"), "wt")
#         fin.write(data)
#         fin.close()

#         # adjust simplemodel.cfg file as well
#         fin = open(os.path.join(git_dir, "simple_model","simplemodel.cfg"), "rt")
#         data_cfg = fin.read()
#         data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num) )
#         fin.close()
#         fin = open(os.path.join(git_dir, "simple_model","simplemodel_i.cfg"), "wt")
#         fin.write(data_cfg)
#         fin.close()

#         file = open('runModel_i.bat', 'w')
#         file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(git_dir, "simple_model","simplemodel_i.cfg") +
#                    '"' + ' -m ' + '"' + os.path.join( git_dir, 'simple_model', "simplemodel_covid_i.emodl", ) + '"')
#         file.close()

#         subprocess.call([r'runModel_i.bat'])

#     df = pd.DataFrame(lst, columns=['scen_num', 'params', 'order'])
#     df.to_csv(os.path.join(git_dir, 'simple_model', "scenarios.csv"))
#     return(scen_num)
    
    
    
class age_model(model):
    
    def __init__(self, modeltype='age_model'):
        self.modeltype='age_model'
        
    def generate_emodl(self, grp_dic, file_output, verbose=False):
        from emodl_generator_extended import generate_extended_emodl
        #grp_dic, file_output, verbose=False
        generate_extended_emodl(grp_dic,
                                file_output,
                                verbose)
        #print('emodl generated')


    def sample_paramters():
        
        ...
    
    
    
    
    
    def define_and_replaceParameters(inputfile , outputfile):
        fin = open(inputfile, "rt")
        data = fin.read()
        data = data.replace('@speciesS@', str(speciesS))
        data = data.replace('@initialAs@', str(initialAs))
        data = data.replace('@incubation_pd@', str(incubation_pd))
        data = data.replace('@time_to_hospitalization@', str(time_to_hospitalization))
        data = data.replace('@time_to_critical@', str(time_to_critical))
        data = data.replace('@time_to_death@', str(time_to_death))
        data = data.replace('@fraction_hospitalized@', str(fraction_hospitalized))
        data = data.replace('@fraction_symptomatic@', str(fraction_symptomatic))
        data = data.replace('@fraction_critical@', str(fraction_critical))
        data = data.replace('@reduced_inf_of_det_cases@', str(reduced_inf_of_det_cases))
        data = data.replace('@cfr@', str(cfr))
        data = data.replace('@d_As@', str(d_As))
        data = data.replace('@d_Sy@', str(d_Sy))
        data = data.replace('@d_H@', str(d_H))
        data = data.replace('@recovery_rate@', str(recovery_rate))
        data = data.replace('@Ki@', str(Ki))
        data = data.replace('@incubation_pd@', str(incubation_pd))
        data = data.replace('@recovery_rate@', str(recovery_rate))
        data = data.replace('@waning@', str(waning))
        fin.close()

        fin = open(outputfile, "wt")
        fin.write(data)
        fin.close()
        
        
#     def param_sample():
#         speciesS = 360980
#         initialAs = np.random.uniform(1, 5)
#         incubation_pd = np.random.uniform(4.2, 6.63)
#         time_to_hospitalization = np.random.normal(5.9, 2)
#         time_to_critical = np.random.normal(5.9, 2)
#         time_to_death = np.random.uniform(1, 3)
#         recovery_rate = np.random.uniform(6, 16)
#         fraction_hospitalized = np.random.uniform(0.1, 5)
#         fraction_symptomatic = np.random.uniform(0.5, 0.8)
#         fraction_critical = np.random.uniform(0.1, 5)
#         reduced_inf_of_det_cases = np.random.uniform(0,1)
#         cfr = np.random.uniform(0.008, 0.022)
#         d_Sy = np.random.uniform(0.2, 0.3)
#         d_H = 1
#         d_As = 0
#         Ki = np.random.uniform(1e-6, 9e-5)
#         incubation_pd= 6.63
#         recovery_rate=16
#         waning=180
#         return({'speciesS':speciesS,
#                 'initialAs':initialAs,
#                 'incubation_pd':incubation_pd,
#                 'time_to_hospitalization':time_to_hospitalization,
#                 'time_to_critical':time_to_critical,
#                 'time_to_death':time_to_death,
#                 'recovery_rate':recovery_rate,
#                 'fraction_hospitalized':fraction_hospitalized,
#                 'fraction_symptomatic':fraction_symptomatic,
#                 'fraction_critical':fraction_critical,
#                 'reduced_inf_of_det_cases':reduced_inf_of_det_cases,
#                 'cfr':cfr,
#                 'd_Sy':d_Sy,
#                 'd_H':d_H,
#                 'd_As':d_As,
#                 'Ki':Ki,
#                'incubation_pd':incubation_pd,
#                'recovery_rate':recovery_rate,
#                'waning':waning})


#             sub_samples= 10
#             #construct a dataframe off the sampled values
#             param_df=pd.DataFrame(param_sample(), index=[0])
#             for i in range(1,sub_samples):
#                 param_df= param_df.append(param_sample(), ignore_index=True)
        
    
class extended_model(model):
    
    def __init__(self, modeltype='extended'):
        self.modeltype='extended_model'
    
    def generate_emodl(self, grp_dic, file_output, verbose=False):
        from emodl_generator_extended import generate_extended_emodl
        #grp_dic, file_output, verbose=False
        generate_extended_emodl(grp_dic,
                                file_output,
                                verbose=False)

    def sample_paramters():
        
        ...
    
    
    def define_and_replaceParameters(inputfile , outputfile):
        speciesS = 360980
        initialAs = np.random.uniform(1, 5)
        incubation_pd = np.random.uniform(4.2, 6.63)
        time_to_hospitalization = np.random.normal(5.9, 2)
        time_to_critical = np.random.normal(5.9, 2)
        time_to_death = np.random.uniform(1, 3)
        recovery_rate = np.random.uniform(6, 16)
        fraction_hospitalized = np.random.uniform(0.1, 5)
        fraction_symptomatic = np.random.uniform(0.5, 0.8)
        fraction_critical = np.random.uniform(0.1, 5)
        reduced_inf_of_det_cases = np.random.uniform(0,1)
        cfr = np.random.uniform(0.008, 0.022)
        d_Sy = np.random.uniform(0.2, 0.3)
        d_H = 1
        d_As = 0
        Ki = np.random.uniform(1e-6, 9e-5)

        fin = open(inputfile, "rt")
        data = fin.read()
        data = data.replace('@speciesS@', str(speciesS))
        data = data.replace('@initialAs@', str(initialAs))
        data = data.replace('@incubation_pd@', str(incubation_pd))
        data = data.replace('@time_to_hospitalization@', str(time_to_hospitalization))
        data = data.replace('@time_to_critical@', str(time_to_critical))
        data = data.replace('@time_to_death@', str(time_to_death))
        data = data.replace('@fraction_hospitalized@', str(fraction_hospitalized))
        data = data.replace('@fraction_symptomatic@', str(fraction_symptomatic))
        data = data.replace('@fraction_critical@', str(fraction_critical))
        data = data.replace('@reduced_inf_of_det_cases@', str(reduced_inf_of_det_cases))
        data = data.replace('@cfr@', str(cfr))
        data = data.replace('@d_As@', str(d_As))
        data = data.replace('@d_Sy@', str(d_Sy))
        data = data.replace('@d_H@', str(d_H))
        data = data.replace('@recovery_rate@', str(recovery_rate))
        data = data.replace('@Ki@', str(Ki))
        fin.close()

        fin = open(outputfile, "wt")
        fin.write(data)
        fin.close()
    
#     def runExp(self,Kivalues, sub_samples, exe_dir, git_dir):
#         import subprocess
#         lst = []
#         scen_num = 0
#         for sample in range(sub_samples):
#             for i in Kivalues:
#                 scen_num += 1
#                 print(i)

#                 lst.append([sample, scen_num, i]) 
#                 #define_and_replaceParameters(Ki_i=i) ### this will need to be changed at some point if we want to test multiple Ki values. 

#                 # adjust simplemodel.cfg
#                 fin = open("simplemodel.cfg", "rt")
#                 data_cfg = fin.read()
#                 data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
#                 fin.close()
#                 fin = open("simplemodel_i.cfg", "wt")
#                 fin.write(data_cfg)
#                 fin.close()

#                 file = open('runModel_i.bat', 'w')
#                 file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(git_dir,
#                                                                                                                  "simplemodel_i.cfg") +
#                            '"' + ' -m ' + '"' + os.path.join(git_dir, "extendedmodel_covid_i.emodl", ) + '"')
#                 file.close()

#                 subprocess.call([r'runModel_i.bat'])
        
        
        
        
#     def runExp(Kivalues, sub_samples):
#     """
#     tests through two different for loops:  different subsamples and different Ki values. scen_num will represent the iteration # over the subsamples\
    
#     this will likely need to be adjusted for each model?
#     """
#     lst = []
#     scen_num = 0
#     for sample in range(sub_samples):
#         for i in Kivalues:
#             scen_num += 1
#             print(i)

#             lst.append([sample, scen_num, i])
#             define_and_replaceParameters(Ki_i=i)

#             # adjust simplemodel.cfg
#             fin = open("simplemodel.cfg", "rt")
#             data_cfg = fin.read()
#             data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
#             fin.close()
#             fin = open("simplemodel_i.cfg", "wt")
#             fin.write(data_cfg)
#             fin.close()

#             file = open('runModel_i.bat', 'w')
#             file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(git_dir,
#                                                                                                              "simplemodel_i.cfg") +
#                        '"' + ' -m ' + '"' + os.path.join(git_dir, "extendedmodel_covid_i.emodl", ) + '"')
#             file.close()

#             subprocess.call([r'runModel_i.bat'])

#     df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki'])
#     df.to_csv("scenarios.csv")
#     return (scen_num)


# class simple_model(model):


# class age_model(model)
#     def generate_emodl(self, ):