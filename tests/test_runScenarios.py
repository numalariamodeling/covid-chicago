from datetime import datetime
from functools import partial
import yaml
import yamlordereddictloader

import pandas as pd
import pytest

from runScenarios import add_config_parameter_column
import runScenarios as rs

yaml_load = partial(yaml.load, Loader=yamlordereddictloader.Loader)


@pytest.fixture
def original_df():
    return pd.DataFrame({'sample_number': [1, 2, 3, 4, 5]})


def test_add_config_parameter_column__int(original_df):
    new_df = add_config_parameter_column(original_df, "new_column", 10)

    correct_df = pd.DataFrame({
        'sample_number': [1, 2, 3, 4, 5],
        'new_column': [10]*5})
    pd.testing.assert_frame_equal(new_df, correct_df)


def test_add_config_parameter_column__matrix(original_df):
    f = {'matrix': [[9, 8], [7, 6]]}
    new_df = add_config_parameter_column(original_df, "new_column", f)
    assert new_df.shape == (5, 5)
    correct_df = pd.DataFrame({
        'sample_number': [1, 2, 3, 4, 5],
        'new_column1_1': [9]*5,
        'new_column1_2': [8]*5,
        'new_column2_1': [7]*5,
        'new_column2_2': [6]*5,
    })
    pd.testing.assert_frame_equal(new_df, correct_df)


def test_add_config_parameter_column__random_uniform(original_df):
    f = {'np.random': 'uniform', 'function_kwargs': {'low': 5, 'high': 6}}
    new_df = add_config_parameter_column(original_df, "new_column", f)
    assert new_df.shape == (5, 2)
    assert "new_column" in new_df.columns
    assert all((new_df["new_column"] >= 5) & (new_df["new_column"] <= 6))


def test_add_config_parameter_column__datetotimestep():
    df = pd.DataFrame({'sample_number': [1, 2, 3, 4, 5],
                       'startdate': [datetime(2020, 2, 20)]*5})
    f = {'custom_function': 'DateToTimestep',
         'function_kwargs': {'dates': datetime(2020, 3, 1), 'startdate_col': 'startdate'}}
    new_df = add_config_parameter_column(df, "new_column", f)
    correct_df = pd.DataFrame({
        'sample_number': [1, 2, 3, 4, 5],
        'startdate': [datetime(2020, 2, 20)]*5,
        'new_column': [10]*5})
    pd.testing.assert_frame_equal(new_df, correct_df)


def test_add_config_parameter_column__subtract():
    df = pd.DataFrame({'sample_number': [1, 2, 3, 4, 5],
                       'col1': [2, 4, 6, 8, 10],
                       'col2': [1, 3, 5, 7, 9]})
    f = {'custom_function': 'subtract',
         'function_kwargs': {'x1': 'col1', 'x2': 'col2'}}
    new_df = add_config_parameter_column(df, "new_column", f)
    correct_df = pd.DataFrame({
        'sample_number': [1, 2, 3, 4, 5],
        'col1': [2, 4, 6, 8, 10],
        'col2': [1, 3, 5, 7, 9],
        'new_column': [1]*5})
    pd.testing.assert_frame_equal(new_df, correct_df)


def test_add_config_parameter_column__error():
    f = {'weird_function': {}}
    with pytest.raises(ValueError, match="Unknown type of parameter"):
        add_config_parameter_column(pd.DataFrame, "new_column", f)


@pytest.mark.parametrize("region, expected", [("EMS_11", 1), ("EMS_10", 2)])
def test_add_sampled_parameters_regions(region, expected):
    # Test that we correctly add sampled parameters by region, including
    # a default for regions not otherwise specified.
    config = """
    sampled_parameters:
        myparam:
          EMS_11:
            np.random: choice
            function_kwargs: {'a': [1]}  
          np.random: choice
          function_kwargs: {'a': [2]}
    """
    df_in = pd.DataFrame({'sample_num': [1, 2, 3]})
    df_exp = df_in.assign(myparam=len(df_in) * [expected])

    df_out = rs.add_sampled_parameters(df_in, yaml_load(config), region, None)

    pd.testing.assert_frame_equal(df_out, df_exp)


def test_add_sampled_parameters_expand_age():
    config = """
    sampled_parameters:
      myparam:
        expand_by_age: True
        np.random: choice
        function_kwargs:
          - {'a': [1]}
          - {'a': [2]}
    """
    df_in = pd.DataFrame({'sample_num': [1, 2]})
    df_exp = df_in.assign(myparam_42=[1, 1], myparam_113=[2, 2])

    df_out = rs.add_sampled_parameters(df_in, yaml_load(config), None, ['42', '113'])

    pd.testing.assert_frame_equal(df_out, df_exp)


def test_add_sampled_parameters_expand_age_same_value():
    # "Expand" age parameters even if everything has the same value
    config = """
    sampled_parameters:
      myparam:
        expand_by_age: True
        np.random: choice
        function_kwargs: {'a': [1]}
    """
    df_in = pd.DataFrame({'sample_num': [1, 2]})
    df_exp = df_in.assign(myparam_42=[1, 1], myparam_113=[1, 1])

    df_out = rs.add_sampled_parameters(df_in, yaml_load(config), None, ['42', '113'])

    pd.testing.assert_frame_equal(df_out, df_exp)


def test_add_sampled_parameters_expand_age_with_defaults():
    # Verify that you can provide a "default" for all ages, and set a specific
    # parameter later.
    config = """
    sampled_parameters:
      myparam:
        expand_by_age: True
        np.random: choice
        function_kwargs: {'a': [1]}
      myparam_0:
        np.random: choice
        function_kwargs: {'a': [2]}
    """
    df_in = pd.DataFrame({'sample_num': [1, 2]})
    df_exp = df_in.assign(myparam_0=[2, 2], myparam_42=[1, 1], myparam_113=[1, 1])

    df_out = rs.add_sampled_parameters(
        df_in, yaml_load(config), None, ['0', '42', '113'])

    pd.testing.assert_frame_equal(df_out, df_exp)


def test_add_sampled_parameters_expand_age_error():
    # We should get an error if the number of distributions doesn't match
    # the number of age bins.
    config = """
    sampled_parameters:
      myparam:
        expand_by_age: True
        np.random: choice
        function_kwargs:
          - {'a': [1]}
          - {'a': [2]}
    """
    df_in = pd.DataFrame({'sample_num': [1, 2]})
    with pytest.raises(ValueError, match="function_kwargs for myparam have 2 entries"):
        rs.add_sampled_parameters(df_in, yaml_load(config), None, ['0', '42', '113'])

