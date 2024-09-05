import pandas as pd
import logging
import json
import ast
from datetime import datetime

def transform_data(data, **kwargs):

    data_dict = ast.literal_eval(data)
    df = pd.DataFrame.from_dict(data_dict)
    df = df.T.reset_index()
    df["updated_at"] = pd.to_datetime(df['time'], unit='s').astype(str)
    df['extracted_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = df[["index", "ask", "totalAsk", "bid", "totalBid", "updated_at", "extracted_at"]]
    df_json = df.to_json() 
    return df_json