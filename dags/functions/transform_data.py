import pandas as pd
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
    df_json = df.to_json()
    return df_json


def transform_other_usd_from_criptoya_api(data, **kwargs):

    data_dict = ast.literal_eval(data)
    df = pd.DataFrame.from_dict(data_dict)
    df = df[["ahorro", "tarjeta", "blue"]]
    df = df[df.index.isin(["price", "timestamp", "ask", "bid"])]
    df = df.T.reset_index()
    df["updated_at"] = pd.to_datetime(df["timestamp"], unit="s").astype(str)
    df["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df.fillna(0)
    df = df[["index", "price", "ask", "bid", "updated_at", "extracted_at"]]
    df_json = df.to_json()
    return df_json


def transform_bcra_from_api(data, **kwargs):

    data_dict = ast.literal_eval(data)
    df = pd.DataFrame.from_dict(data_dict)
    df["updated_at"] = pd.to_datetime(df["fecha"]).astype(str)
    df["extracted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df[
        ["idVariable", "cdSerie", "descripcion", "valor", "updated_at", "extracted_at"]
    ]
    df_json = df.to_json()
    return df_json
