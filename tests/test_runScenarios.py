from datetime import datetime

import pandas as pd
import pytest

from runScenarios import add_config_parameter_column


@pytest.fixture
def original_df():
    return pd.DataFrame({'sample_number': [1, 2, 3, 4, 5]})


def test_add_config_parameter_column__int(original_df):
    new_df = add_config_parameter_column(original_df, "new_column", 10)
    assert new_df.shape == (5, 2)
    assert "new_column" in new_df.columns
    assert set(new_df["new_column"]) == set([10])


def test_add_config_parameter_column__matrix(original_df):
    f = {'matrix': [[9, 8], [7, 6]]}
    new_df = add_config_parameter_column(original_df, "new_column", f)
    assert new_df.shape == (5, 5)
    assert all(new_cols in new_df.columns
               for new_cols in ["new_column1_1", "new_column1_2", "new_column2_1", "new_column2_2"])
    assert set(new_df["new_column1_1"]) == set([9])
    assert set(new_df["new_column1_2"]) == set([8])
    assert set(new_df["new_column2_1"]) == set([7])
    assert set(new_df["new_column2_2"]) == set([6])


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
    assert new_df.shape == (5, 3)
    assert "new_column" in new_df.columns
    print(new_df)
    assert set(new_df["new_column"]) == set([10])


def test_add_config_parameter_column__subtract():
    df = pd.DataFrame({'sample_number': [1, 2, 3, 4, 5],
                       'col1': [2, 4, 6, 8, 10],
                       'col2': [1, 3, 5, 7, 9]})
    f = {'custom_function': 'subtract',
         'function_kwargs': {'x1': 'col1', 'x2': 'col2'}}
    new_df = add_config_parameter_column(df, "new_column", f)
    assert new_df.shape == (5, 4)
    assert "new_column" in new_df.columns
    assert set(new_df["new_column"]) == set([1])


def test_add_config_parameter_column__error():
    f = {'weird_function': {}}
    with pytest.raises(ValueError) as e:
        add_config_parameter_column(pd.DataFrame, "new_column", f)
    assert "Unknown type of parameter" in str(e.value)
