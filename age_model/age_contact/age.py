import pandas as pd
import numpy as np


def normalize_matrix(base_name='C', proportions=[0.25, 0.25, 0.25, 0.25], matrix_file='sample_contact_matrix.csv',
                     return_flat=True):
    # For N age groups...
    # this function takes a list of what proportion of the population
    # each age group takes up (alternatively, a list of population
    # counts by each age group) and an initial contact matrix in
    # .csv format and outputs a normalized matrix, either as a N by N
    # dataframe or a 1 by N^2 dataframe. By default, it returns the latter
    # 'flat' Dataframe. The base name of your parameter of interest
    # is specified in base_name (default = 'C' for Contact).

    matrix_df = pd.read_csv(matrix_file, index_col=0)
    num_groups = len(proportions)

    if (num_groups != len(matrix_df)) or (num_groups != len(matrix_df.columns)):
        raise ValueError("Inconsistent number of age groups in matrix and proportions list.")

    proportions = np.array(proportions) / np.sum(proportions)  # Normalizing proportions

    norm_factor = np.sum(np.array(matrix_df.sum(axis=1)) * proportions)  # Calculating normilization factor

    norm_matrix_df = matrix_df.div(norm_factor)  # Applying normalization factor

    # Flattening matrix
    flat_norm = pd.DataFrame(index=[0])
    for col in range(1, num_groups + 1):
        for row in range(1, num_groups + 1):
            flat_norm[base_name + str(row) + '_' + str(col)] = norm_matrix_df[str(col)].at[row]

    if return_flat:
        return flat_norm
    else:
        return norm_matrix_df






mnorm = normalize_matrix(matrix_file=os.path.join("C:/Users/mrung/Downloads", 'sample_contact_matrix.csv'  ))