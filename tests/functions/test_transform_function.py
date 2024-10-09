import textwrap
from datetime import datetime
from io import StringIO

import pandas as pd
import pytest

from dags.functions.transform_data import (
    
    transform_bcra_from_api, 
    transform_mep_usd_from_criptoya_api,
    transform_other_usd_from_criptoya_api, 
    transform_usdt_from_criptoya_api,
)


@pytest.fixture
def sample_usdt_data():
    """Fixture providing sample USDT data as a string."""
    return textwrap.dedent(
        """{
        "binance": {
            "ask": 1000.5,
            "totalAsk": 2000.5,
            "bid": 995.3,
            "totalBid": 1995.3,
            "time": 1633024800
        }
    }"""
    )


@pytest.fixture
def sample_usd_data():
    """Fixture providing sample MEP USD data as a string."""
    return textwrap.dedent(
        """
    {
        "mayorista": {"price": 961.75, "variation": 0.22, "timestamp": 1726239600},
        "oficial": {"price": 980.5, "variation": 0.2, "timestamp": 1726340062},
        "ahorro": {
            "ask": 1568.8,
            "bid": 940.5,
            "variation": 0.2,
            "timestamp": 1726340062
        },
        "tarjeta": {"price": 1568.8, "variation": 0.2, "timestamp": 1726340062},
        "blue": {
            "ask": 1265,
            "bid": 1235,
            "variation": -1.17,
            "timestamp": 1726340047
        },
        "cripto": {
            "ccb": {
                "ask": 1259.663,
                "bid": 1249.665,
                "variation": 0.43,
                "timestamp": 1726340507
            },
            "usdt": {
                "ask": 1258.46,
                "bid": 1254,
                "variation": 0.28,
                "timestamp": 1726340507
            },
            "usdc": {
                "ask": 1258.086,
                "bid": 1256.984,
                "variation": 0.25,
                "timestamp": 1726340507
            }
        },
        "mep": {
            "al30": {
                "24hs": {"price": 1226.69, "variation": -1.07, "timestamp": 1726257379},
                "ci": {"price": 1219.59, "variation": -1.19, "timestamp": 1726255803}
            },
            "gd30": {
                "24hs": {"price": 1223.37, "variation": -1.2, "timestamp": 1726257379},
                "ci": {"price": 1220.77, "variation": -0.81, "timestamp": 1726255809}
            },
            "letras": {
                "name": "S30S4",
                "24hs": {"price": 1228.36, "variation": 0, "timestamp": 1726084547},
                "ci": {"price": 1241.65, "variation": 0, "timestamp": 1726168741}
            },
            "bpo27": {
                "24hs": {"price": 1221.48, "variation": -1.28, "timestamp": 1726257141},
                "ci": {"price": 1217.15, "variation": -1.65, "timestamp": 1726254083}
            }
        },
        "ccl": {
            "al30": {
                "24hs": {"price": 1250.72, "variation": -0.49, "timestamp": 1726257352},
                "ci": {"price": 1244.19, "variation": -0.49, "timestamp": 1726255801}
            },
            "gd30": {
                "24hs": {"price": 1249.08, "variation": -0.86, "timestamp": 1726256458},
                "ci": {"price": 1240.85, "variation": -0.83, "timestamp": 1726255430}
            },
            "letras": {
                "name": "S30S4",
                "24hs": {"price": 1314.59, "variation": 0, "timestamp": 1725293303},
                "ci": {"price": 1255.44, "variation": 0, "timestamp": 1726168739}
            },
            "bpo27": {
                "24hs": {"price": 1247.58, "variation": -0.64, "timestamp": 1726255245},
                "ci": {"price": 1250.08, "variation": 0, "timestamp": 1726077783}
            }
        }
    }
    """
    )


@pytest.fixture
def sample_bcra_data():
    """Fixture providing sample BCRA data as a string."""
    return textwrap.dedent(
        """
    {
        "results": [
            {
                "idVariable": 1,
                "cdSerie": "serie1",
                "descripcion": "USD Official",
                "valor": 95.0,
                "fecha": "2021-09-30"
            }
        ]
    }
    """
    )


def test_transform_usdt_from_criptoya_api(sample_usdt_data):
    """Test for the transform_usdt_from_criptoya_api function."""
    transformed_json = transform_usdt_from_criptoya_api(sample_usdt_data)

    assert isinstance(transformed_json, str)
    df = pd.read_json(StringIO(transformed_json))

    expected_columns = [
        "exchange_name",
        "ask_price",
        "total_ask_price",
        "bid_price",
        "total_bid_price",
        "updated_at",
        "extracted_at",
    ]
    assert list(df.columns) == expected_columns

    assert df["exchange_name"][0] == "binance"
    assert df["ask_price"][0] == 1000.5
    assert df["total_ask_price"][0] == 2000.5
    assert df["bid_price"][0] == 995.3
    assert df["total_bid_price"][0] == 1995.3

    updated_at = datetime.strptime(str(df["updated_at"][0]), "%Y-%m-%d %H:%M:%S")
    extracted_at = datetime.strptime(str(df["extracted_at"][0]), "%Y-%m-%d %H:%M:%S")

    assert isinstance(updated_at, datetime)
    assert isinstance(extracted_at, datetime)


def test_transform_mep_usd_from_criptoya_api(sample_usd_data):
    """Test for the transform_mep_usd_from_criptoya_api function."""
    transformed_json = transform_mep_usd_from_criptoya_api(sample_usd_data)

    assert isinstance(transformed_json, str)
    df = pd.read_json(StringIO(transformed_json))

    expected_columns = ["mep_name", "total_bid_price", "updated_at", "extracted_at"]
    assert list(df.columns) == expected_columns

    assert df["mep_name"][0] == "mep al30 ci"
    assert df["mep_name"][1] == "mep gd30 ci"
    assert df["mep_name"][2] == "mep al30 24 hs"
    assert df["mep_name"][3] == "mep gd30 24 hs"
    assert df["total_bid_price"][0] == 1219.59
    assert df["total_bid_price"][1] == 1220.77
    assert df["total_bid_price"][2] == 1226.69
    assert df["total_bid_price"][3] == 1223.37

    updated_at = datetime.strptime(str(df["updated_at"][0]), "%Y-%m-%d %H:%M:%S")
    extracted_at = datetime.strptime(str(df["extracted_at"][0]), "%Y-%m-%d %H:%M:%S")

    assert isinstance(updated_at, datetime)
    assert isinstance(extracted_at, datetime)


def test_transform_other_usd_from_criptoya_api(sample_usd_data):
    """Test for the transform_other_usd_from_criptoya_api function."""
    transformed_json = transform_other_usd_from_criptoya_api(sample_usd_data)

    assert isinstance(transformed_json, str)
    df = pd.read_json(StringIO(transformed_json))

    expected_columns = [
        "exchange_name",
        "total_ask_price",
        "total_bid_price",
        "updated_at",
        "extracted_at",
    ]
    assert list(df.columns) == expected_columns

    assert df["exchange_name"][0] == "ahorro"
    assert df["exchange_name"][1] == "tarjeta"
    assert df["exchange_name"][2] == "blue"
    assert df["total_ask_price"][0] == 1568.8
    assert df["total_ask_price"][1] == 1568.8
    assert df["total_ask_price"][2] == 1265.0
    assert df["total_bid_price"][0] == 940.5
    assert df["total_bid_price"][1] == 1568.8
    assert df["total_bid_price"][2] == 1235.0

    updated_at = datetime.strptime(str(df["updated_at"][0]), "%Y-%m-%d %H:%M:%S")
    extracted_at = datetime.strptime(str(df["extracted_at"][0]), "%Y-%m-%d %H:%M:%S")

    assert isinstance(updated_at, datetime)
    assert isinstance(extracted_at, datetime)


def test_transform_bcra_from_api(sample_bcra_data):
    """Test for the transform_bcra_from_api function."""
    transformed_json = transform_bcra_from_api(sample_bcra_data)

    assert isinstance(transformed_json, str)
    df = pd.read_json(StringIO(transformed_json))

    expected_columns = [
        "indicator_id",
        "cd_serie",
        "indicator_description",
        "total_bid_price",
        "updated_at",
        "extracted_at",
    ]
    assert list(df.columns) == expected_columns

    assert df["indicator_id"][0] == 1
    assert df["cd_serie"][0] == "serie1"
    assert df["indicator_description"][0] == "USD Official"
    assert df["total_bid_price"][0] == 95.0

    updated_at = datetime.strptime(str(df["updated_at"][0]), "%Y-%m-%d %H:%M:%S")
    extracted_at = datetime.strptime(str(df["extracted_at"][0]), "%Y-%m-%d %H:%M:%S")

    assert isinstance(updated_at, datetime)
    assert isinstance(extracted_at, datetime)
