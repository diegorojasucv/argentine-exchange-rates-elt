import requests
import json


def fetch_data_from_api(**kwargs):
    api_url = "https://criptoya.com/api/usdt/ars/100"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return None
