import requests
import json


def extract_usdt_from_criptoya_api(**kwargs):
    api_url = "https://criptoya.com/api/usdt/ars/100"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return None


def extract_usd_from_criptoya_api(**kwargs):
    api_url = "https://criptoya.com/api/dolar"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return None


def extract_bcra_from_api(**kwargs):
    api_url = "https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables"
    headers = {"Accept-Language": "en-US"}
    try:
        response = requests.get(api_url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return None
