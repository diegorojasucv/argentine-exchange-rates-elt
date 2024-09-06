import pandas as pd
import logging
import json
import ast
from datetime import datetime


def transform_usdt_from_criptoya_api(data, **kwargs):

    data_dict = ast.literal_eval(data)
    df = pd.DataFrame.from_dict(data_dict)
    df = df.T.reset_index()
    df["updated_at"] = pd.to_datetime(df["time"], unit="s").astype(str)
    df["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df[
        ["index", "ask", "totalAsk", "bid", "totalBid", "updated_at", "extracted_at"]
    ]
    df_json = df.to_json()
    return df_json


def transform_mep_usd_from_criptoya_api(data, **kwargs):

    data_dict = ast.literal_eval(data)

    mep_al30_ci = data_dict["mep"]["al30"]["ci"]
    mep_gd30_ci = data_dict["mep"]["gd30"]["ci"]
    mep_lede_ci = data_dict["mep"]["lede"]["ci"]

    mep_al30_48hs = data_dict["mep"]["al30"]["24hs"]
    mep_gd30_48hs = data_dict["mep"]["gd30"]["24hs"]
    mep_lede_48hs = data_dict["mep"]["lede"]["24hs"]

    data = {
        "MEP al30 CI": mep_al30_ci,
        "MEP gd30 CI": mep_gd30_ci,
        "MEP lede CI": mep_lede_ci,
        "MEP al30 24 hs": mep_al30_48hs,
        "MEP gd30 24 hs": mep_gd30_48hs,
        "MEP lede 24 hs": mep_lede_48hs,
    }

    df = pd.DataFrame.from_dict(data_dict)
    df = df.T.reset_index()
    df["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_json = df.to_json()
    return df_json


def transform_other_usd_from_criptoya_api(data, **kwargs):

    data_dict = ast.literal_eval(data)
    df = pd.DataFrame.from_dict(data_dict)
    df = df[["ahorro", "tarjeta", "blue"]]
    df = df.T.reset_index()
    df_json = df.to_json()
    return df_json


def transform_bcra_from_api(data, **kwargs):

    data_dict = ast.literal_eval(data)
    df = pd.DataFrame.from_dict(data_dict)
    df["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_json = df.to_json()
    return df_json
