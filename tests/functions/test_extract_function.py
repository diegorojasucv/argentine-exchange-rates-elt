import json
from unittest.mock import patch

import pytest
from requests.exceptions import RequestException

from dags.functions.extract_data import extract_data_from_api


@pytest.fixture
def mock_usdt_response():
    return '{"bitso": {"ask": 735.0, "totalAsk": 736.0}}'


@pytest.fixture
def mock_usd_response():
    return '{"blue": 750.0, "oficial": 365.0}'


@pytest.fixture
def mock_bcra_response():
    return '{"dolar_oficial": 365.0}'


@patch("requests.get")
def test_extract_usdt_data(mock_get, mock_usdt_response):
    """Test for USDT data extraction from CriptoYa API."""
    mock_get.return_value.json.return_value = mock_usdt_response
    mock_get.return_value.status_code = 200

    result = extract_data_from_api("usdt")
    assert json.loads(result) == mock_usdt_response
    mock_get.assert_called_once_with(
        "https://criptoya.com/api/usdt/ars/100", headers={}, verify=False
    )


@patch("requests.get")
def test_extract_usd_data(mock_get, mock_usd_response):
    """Test for USD data extraction from CriptoYa API."""
    mock_get.return_value.json.return_value = mock_usd_response
    mock_get.return_value.status_code = 200

    result = extract_data_from_api("usd")
    assert json.loads(result) == mock_usd_response
    mock_get.assert_called_once_with(
        "https://criptoya.com/api/dolar", headers={}, verify=False
    )


@patch("requests.get")
def test_extract_bcra_data(mock_get, mock_bcra_response):
    """Test for economic data extraction from BCRA API."""
    mock_get.return_value.json.return_value = mock_bcra_response
    mock_get.return_value.status_code = 200

    result = extract_data_from_api("bcra")
    assert json.loads(result) == mock_bcra_response
    mock_get.assert_called_once_with(
        "https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables",
        headers={"Accept-Language": "en-US"},
        verify=False,
    )


@patch("requests.get")
def test_invalid_api_name(mock_get):
    """Test for invalid API name."""
    with pytest.raises(ValueError):
        extract_data_from_api("invalid_api")

    mock_get.assert_not_called()


@patch("requests.get")
def test_api_request_failure(mock_get):
    """Test for API request failure handling."""
    mock_get.side_effect = RequestException

    with pytest.raises(RequestException):
        extract_data_from_api("usdt")
