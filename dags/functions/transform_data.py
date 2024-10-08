"""Transform functions"""

import json
from datetime import datetime
from typing import Any, Dict

import pandas as pd

COLUMNS_TO_RENAME_USDT: Dict[str, str] = {
    "index": "exchange_name",
    "ask": "ask_price",
    "totalAsk": "total_ask_price",
    "bid": "bid_price",
    "totalBid": "total_bid_price",
}

COLUMNS_TO_RENAME_MEP: Dict[str, str] = {
    "index": "mep_name",
    "price": "total_bid_price",
}

COLUMNS_TO_RENAME_OTHER: Dict[str, str] = {
    "index": "exchange_name",
    "ask": "total_ask_price",
    "bid": "total_bid_price",
}

COLUMNS_TO_RENAME_BCRA: Dict[str, str] = {
    "idVariable": "indicator_id",
    "cdSerie": "cd_serie",
    "descripcion": "indicator_description",
    "valor": "total_bid_price",
}


def transform_usdt_from_criptoya_api(data: str, **kwargs: Any) -> str:
    """
    Transforms USDT data from CriptoYa API to a JSON format.

    Args:
        data (str): A string containing the raw data from CriptoYa API.
        **kwargs: Additional keyword arguments.

    Returns:
        str: JSON string of the transformed data.
    """
    data_dict = json.loads(data)
    df = pd.DataFrame.from_dict(data_dict)
    df = df.T.reset_index()
    df["updated_at"] = pd.to_datetime(df["time"], unit="s").astype(str)
    df["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df[
        [
            "index",
            "ask",
            "totalAsk",
            "bid",
            "totalBid",
            "updated_at",
            "extracted_at",
        ]
    ]
    df.rename(columns=COLUMNS_TO_RENAME_USDT, inplace=True)
    df_json = df.to_json()
    return df_json


def transform_mep_usd_from_criptoya_api(data: str, **kwargs: Any) -> str:
    """
    Transforms MEP USD data from CriptoYa API to a JSON format.

    Args:
        data (str): A string containing the raw data from CriptoYa API.
        **kwargs: Additional keyword arguments.

    Returns:
        str: JSON string of the transformed MEP data.
    """
    data_dict: Dict[str, Any] = json.loads(data)
    mep_al30_ci = data_dict["mep"]["al30"]["ci"]
    mep_gd30_ci = data_dict["mep"]["gd30"]["ci"]
    mep_al30_48hs = data_dict["mep"]["al30"]["24hs"]
    mep_gd30_48hs = data_dict["mep"]["gd30"]["24hs"]

    data = {
        "mep al30 ci": mep_al30_ci,
        "mep gd30 ci": mep_gd30_ci,
        "mep al30 24 hs": mep_al30_48hs,
        "mep gd30 24 hs": mep_gd30_48hs,
    }

    df = pd.DataFrame.from_dict(data)
    df = df.T.reset_index()
    df["updated_at"] = pd.to_datetime(df["timestamp"], unit="s").astype(str)
    df["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df[["index", "price", "updated_at", "extracted_at"]]
    df.rename(columns=COLUMNS_TO_RENAME_MEP, inplace=True)
    df_json = df.to_json()
    return df_json


def transform_other_usd_from_criptoya_api(data: str, **kwargs: Any) -> str:
    """
    Transforms other USD data (ahorro, tarjeta, blue) from CriptoYa API to a JSON format.

    Args:
        data (str): A string containing the raw data from CriptoYa API.
        **kwargs: Additional keyword arguments.

    Returns:
        str: JSON string of the transformed data.
    """

    data_dict: Dict[str, Any] = json.loads(data)
    df = pd.DataFrame.from_dict(data_dict)
    df = df[["ahorro", "tarjeta", "blue"]]
    df = df[df.index.isin(["price", "timestamp", "ask", "bid"])]
    df = df.T.reset_index()
    df["ask"] = df["ask"].fillna(df["price"]).fillna(0)
    df["bid"] = df["bid"].fillna(df["price"]).fillna(0)
    df["updated_at"] = pd.to_datetime(df["timestamp"], unit="s").astype(str)
    df["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df[["index", "ask", "bid", "updated_at", "extracted_at"]]
    df.rename(columns=COLUMNS_TO_RENAME_OTHER, inplace=True)
    df_json = df.to_json()
    return df_json


def transform_bcra_from_api(data: str, **kwargs: Any) -> str:
    """
    Transforms BCRA data to a JSON format.

    Args:
        data (str): A string containing the raw data from the BCRA API.
        **kwargs: Additional keyword arguments.

    Returns:
        str: JSON string of the transformed BCRA data.
    """
    data_dict: Dict[str, Any] = json.loads(data)
    df = pd.DataFrame.from_dict(data_dict["results"])
    df["updated_at"] = pd.to_datetime(df["fecha"]).astype(str)
    df["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df[
        [
            "idVariable",
            "cdSerie",
            "descripcion",
            "valor",
            "updated_at",
            "extracted_at",
        ]
    ]
    df.rename(columns=COLUMNS_TO_RENAME_BCRA, inplace=True)
    df_json = df.to_json()
    return df_json
