from datetime import date, timedelta
import numpy as np
import os, sys
import numpy as np
import subprocess
import pandas as pd

master_channel_list = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic', 'hospitalized', 'detected', 'critical', 'deaths', 'recovered']
detection_channel_list = ['detected', 'detected_cumul',  'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul',  'crit_det_cumul']
custom_channel_list = ['detected_cumul', 'symp_det_cumul', 'asymp_det_cumul', 'hosp_det_cumul', 'crit_det_cumul', 'symp_cumul',  'asymp_cumul','hosp_cumul', 'crit_cumul']
first_day = date(2020, 3, 1)



Kivalues =  np.random.uniform(3.23107e-06, 4.7126e-06 , 1)   # [9e-05, 7e-06, 8e-06, 9e-06, 9e-077]



class model:
    def __init__(self, param_dic):#, groups):
        #self.modeltype= modeltype
        self.param_dic= param_dic
        
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
        scendf = pd.read_csv("scenarios.csv", index_col=0)
        #del scendf['Unnamed: 0']

        df_list = []
        for scen_i in range(1, Nscenarios):
            input_name = "trajectories_scen" + str(scen_i) + ".csv"
#             print(os.path.exists(input_name)) ##qc
#             try:
            df_i = self.reprocess(git_dir, input_fname=input_name, output_fname=None)
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
        
    def plot_origional(self, adf):
        """Manuela's origional plotting function in extended_model_postprocessing"""
        fig = plt.figure(figsize=(12,6))

        plotchannels = ['susceptible', 'exposed', 'asymptomatic', 'symptomatic',
                        'detected', 'hospitalized', 'critical', 'deaths', 'recovered',
                        'new_detected', 'new_hospitalized', 'new_deaths']
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
    
    def __init__(self, modeltype='spatial'):
        self.modeltype='spatial'
    
    def generate_emodl(self, county_dic, param_dic, emodl_output, verbose=False ):
        from locale_emodl_generator import generate_locale_emodl, generate_locale_cfg
        generate_locale_emodl(county_dic, param_dic,emodl_output, verbose=False)
        print('emodl generated')
        
        
    def runExp(self,Kivalues, sub_samples, exe_dir, git_dir):
        import subprocess
        lst = []
        scen_num = 0
        for sample in range(sub_samples):
            for i in Kivalues:
                scen_num += 1
                print(i)

                lst.append([sample, scen_num, i]) 
                #define_and_replaceParameters(Ki_i=i) ### this will need to be changed at some point if we want to test multiple Ki values. 

                # adjust simplemodel.cfg
                fin = open("simplemodel.cfg", "rt")
                data_cfg = fin.read()
                data_cfg = data_cfg.replace('trajectories', 'trajectories_scen' + str(scen_num))
                fin.close()
                fin = open("simplemodel_i.cfg", "wt")
                fin.write(data_cfg)
                fin.close()

                file = open('runModel_i.bat', 'w')
                file.write('\n"' + os.path.join(exe_dir, "compartments.exe") + '"' + ' -c ' + '"' + os.path.join(git_dir,
                                                                                                                 "simplemodel_i.cfg") +
                           '"' + ' -m ' + '"' + os.path.join(git_dir, "extendedmodel_covid_i.emodl", ) + '"')
                file.close()

                subprocess.call([r'runModel_i.bat'])

        df = pd.DataFrame(lst, columns=['sample_num', 'scen_num', 'Ki'])
        df.to_csv("spatial_model//scenarios.csv")
        return (scen_num)
        
    
        
    
# class extended_model(model):
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