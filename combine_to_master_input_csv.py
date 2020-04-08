import numpy as np
import pandas as pd
import itertools

def gen_combos(csv_base_list=['sampled_parameters', 'scenarios'], output_base='master_input'):

    #Function takes list of csv bases, generates a master
    #csv file with all combinations of parameters contained therein.
    #Ensure that all parameters have unique names in input files
    #and that multiple input files are supplied.

    dfs_list = ['']*(len(csv_base_list)) #Initialize list to store DataFrames

    #Importing data...
    base_index = 0
    for base in csv_base_list:
        fullname = './' + base + '.csv'
        csv_df = pd.read_csv(fullname, header=0).dropna(axis='columns') #Import csv
        dfs_list[base_index] = csv_df.copy()
        base_index += 1

    #Restructuring data in lists with all possible combinations...
    cool_list = np.array(list(itertools.product(dfs_list[0].to_numpy(),dfs_list[1].to_numpy())))
    cool_list = np.array(list(np.concatenate(x) for x in cool_list))
    for i in range(2,len(dfs_list)):
        cool_list = np.array(list(itertools.product(cool_list,dfs_list[i].to_numpy())))
        cool_list = np.array(list(np.concatenate(x) for x in cool_list))

    #Creating a list of columns for use in the final DataFrame...
    master_columns = []
    for df in dfs_list:
        master_columns.extend(np.array(df.columns))

    #Isolating index columns...
    index_columns = []
    for col in master_columns:
        if 'index' in col:
            index_columns.append(col)

    #Writing all data to master DataFrame...
    master_df = pd.DataFrame(data=cool_list, columns=master_columns)

    #Restructuring master DataFrame to bring index columns to front...
    master_df = master_df[[c for c in master_df if c in index_columns]+[c for c in master_df if c not in index_columns]]

    #Writing master dataframe to output csv.
    master_df.to_csv(output_base+'.csv')
