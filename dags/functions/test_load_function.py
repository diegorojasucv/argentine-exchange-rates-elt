import pytest
from unittest.mock import patch, MagicMock
from functions.load_data import connect_to_redshift_engine, load_data_to_redshift


@pytest.fixture
def mock_create_engine():
    with patch("functions.load_data.create_engine") as mock:
        yield mock


@pytest.fixture
def sample_json_data():
    return '{"col1": [1, 2, 3], "col2": ["a", "b", "c"]}'


def test_connect_to_redshift_engine(mock_create_engine):
    """
    Test connect_to_redshift_engine function to ensure it creates an engine.
    """
    # Call the function under test
    engine = connect_to_redshift_engine()

    # Check that create_engine was called exactly once
    mock_create_engine.assert_called_once()

    # Verify that the connection string is used correctly
    args, kwargs = mock_create_engine.call_args
    assert args[0] == "redshift+psycopg2://user:password@host:port/db"


def test_load_data_to_redshift(mock_create_engine, sample_json_data):
    """
    Test load_data_to_redshift function to ensure it loads the data correctly.
    """
    mock_engine = mock_create_engine.return_value

    # Patch the to_sql method on the mock engine
    with patch("functions.load_data.pd.DataFrame.to_sql") as mock_to_sql:
        load_data_to_redshift(sample_json_data, "mock_table")

        # Check that to_sql was called with the correct arguments
        mock_to_sql.assert_called_once_with(
            "mock_table", mock_engine, if_exists="append", index=False
        )
