"""
Author: Garrett Eickelberg
04/08/2020
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append("C:\\Users\\garrett\\Documents\\GitHub\\covid-chicago") #added for the loadpaths

from load_paths import load_box_paths
import parameters as param

#mpl.rcParams['pdf.fonttype'] = 42

##directories
user_path = os.path.expanduser('~')
datapath, projectpath, wdir, exe_dir, git_dir = load_box_paths()
temp_dir = os.path.join(git_dir, '_temp')

sim_output_path = os.path.join(wdir, 'sample_trajectories')
plot_path = os.path.join(wdir, 'sample_plots')
age_matrix_path=os.path.join(projectpath,"..","emod_sim",'age_contact_matrices')


sys.path.append("C:\\Users\\garrett\\Documents\\GitHub\\covid-chicago")
sys.path.append(git_dir)
sys.path.append(os.path.join(git_dir, 'spatial_model/'))

import model_classes as mc


#### grabbing all files in the age_matrix_path that matches the regex and puts them into a list
import glob
age_contact_matrices_files= glob.glob(os.path.join(str(age_matrix_path),'*_2.xlsx'))


### functions

def plot_heatmap(adjusted_age_matrix3):
    """
    simple heatmap plotter function
    """
    import seaborn as sns
    fig = plt.figure(figsize=(10,7))
    ax = sns.heatmap(adjusted_age_matrix3)
    ax.invert_yaxis()
    plt.show()

def create_filename(age_contact_matrices_file, grp):
    "generates the filename in a nice way by parsing the names of the contact matrix"

    name_split= age_contact_matrices_file.split('\\')[-1].split('_')[-2]
    if name_split=='locations':
        name_split= age_contact_matrices_file.split('\\')[-1].split('_')[-2]+"_"+ age_contact_matrices_file.split('\\')[-1].split('_')[-3]  

    filename=os.path.join(projectpath,'inputs','contact_matrix_{}_grp{}.csv'.format(name_split, grp))
    return(filename)

def age_contact_xls_reader(age_contact_matrices_file, age_labels):
    """
    reads a file in the glob age_contact_matrices_files and turns the USA tab into a dataframe with row and col indicies = to age_labels
    """
    age_matrix=pd.read_excel(age_contact_matrices_file, sheet_name='United States of America', header=None)#index_col=0)  
    
    #setting the index for row and col
    age_matrix.columns=age_labels
    age_matrix['row_age_group']=age_labels
    age_matrix.set_index('row_age_group', inplace=True)
    
    return(age_matrix)

def adjust_age_groups(age_labels):
    """
    for each pair of cols to aggregate, takes the first number of the first element, and the last number for the last element
    for instance: ["0-4",'5-10'] -> ['0-10']
    """
    i=0
    new_age_labels=[]
    label=""
    for element in age_labels:
        if i%2==0:
            label+=element.split('-')[0]
            i+=1
        elif i%2==1:
            label=label+'-'+element.split('-')[-1]
            new_age_labels.append(label)
            label=""
            i+=1
    #making the last agegroup based on the first number +
    new_age_labels[-1]= new_age_labels[-1].split("-")[0]+"+"
    return(new_age_labels)

def row_col_aggregator(age_matrix, age_labels, age_file, save=False, plot=True):
    """
    input:takes in the age_matrix dataframe and the age_labels (ie row and col agegroups) associated with it
    age_file is the age_contact_matrix file, needed to create the filename for saving the dataframe. 
    
    output: dataframe that aggregates every two columns and rows together (ie 4 cells ->1) via a 2step col mean and row mean. also adjusts the age labels to reflect this.
    the output will have 1/2 the number of columns
    
    """ 
    
    #making the last agegroup based on the first number +
    new_age_labels=adjust_age_groups(age_labels)

    ### aggregating the columns  then by rows via two step aggregation:
    adjusted_age_matrix= pd.DataFrame()
    adjusted_age_matrix2= pd.DataFrame(columns= new_age_labels)#, rows=new_age_labels)
    adjusted_age_matrix2.columns=new_age_labels
    adjusted_age_matrix2['row_age_group']=new_age_labels
    adjusted_age_matrix2.set_index('row_age_group', inplace=True)

    ## column aggregation (step 1)
    i=0
    for element in new_age_labels:
        adjusted_age_matrix[element]= np.mean([age_matrix.iloc[:,i],age_matrix.iloc[:,i+1]],axis=0)
        i+=2

    ## row aggregation on output of column aggregation (step 2)
    i=0
    j=0
    for element in new_age_labels:
        adjusted_age_matrix2.loc[element,:]=np.mean([adjusted_age_matrix.iloc[i,:],adjusted_age_matrix.iloc[i+1,:]],axis=0)
        i+=2
        j+=1
    
    #ensuring values remain as floats instead of objects
    adjusted_age_matrix2=adjusted_age_matrix2.astype(float)
    
    #run the filename function to get a nice automated filename
    filename= create_filename(age_file, grp=len(adjusted_age_matrix2))
    
    ## plotting and saving functionality
    if save==True:
        adjusted_age_matrix2.to_csv(os.path.join(projectpath,'inputs','{}.csv'.format(filename)))
        
    if plot==True:
            plot_heatmap(adjusted_age_matrix2)
    return(adjusted_age_matrix2,new_age_labels )




#### running code for all files in the age_contact_matrices_files:

for element in age_contact_matrices_files:
    age_labels = ["0-4","5-9","10-14","15-19","20-24","25-29","30-34","35-39","40-44","45-49","50-54","55-59","60-64","65-69","70-74","75+"]
    age_matrix= age_contact_xls_reader(element, age_labels)
    adjusted_age_matrix2, new_age_labels= row_col_aggregator(age_matrix, age_labels, age_file=element, save=True, plot=True)
    adjusted_age_matrix3, new_age_labels2= row_col_aggregator(age_matrix, new_age_labels, age_file=element, save=True, plot=True)