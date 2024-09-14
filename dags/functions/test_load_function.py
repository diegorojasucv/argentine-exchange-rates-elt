import ast
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.engine import Engine
from functions.load_data import connect_to_redshift_engine, load_data_to_redshift


@pytest.fixture
def mock_variable_get():
    with patch("airflow.models.Variable.get") as mock_get:
        mock_get.return_value = "mock_password"
        yield mock_get


@pytest.fixture
def mock_create_engine():
    with patch("sqlalchemy.create_engine") as mock_engine:
        mock_engine.return_value = MagicMock(spec=Engine)
        yield mock_engine


@pytest.fixture
def sample_json_data():
    return '{"col1": [1, 2, 3], "col2": ["a", "b", "c"]}'


def test_connect_to_redshift_engine(mock_variable_get, mock_create_engine):
    """
    Test connect_to_redshift_engine function to ensure it creates an engine.
    """

    engine = connect_to_redshift_engine()
    mock_create_engine.assert_called_once()

    assert isinstance(engine, Engine)


def test_load_data_to_redshift(mock_create_engine, sample_json_data):
    """
    Test load_data_to_redshift function to ensure it loads the data correctly.
    """

    mock_engine = mock_create_engine.return_value
    load_data_to_redshift(sample_json_data, "mock_table")

    df_dict = ast.literal_eval(sample_json_data)
    expected_df = pd.DataFrame.from_dict(df_dict)

    mock_engine.connect().to_sql.assert_called_once_with(
        "mock_table",
        mock_engine,
        schema="2024_diego_rojas_schema",
        if_exists="append",
        index=False,
    )

    pd.testing.assert_frame_equal(
        mock_engine.connect().to_sql.call_args[0][0], expected_df
    )
