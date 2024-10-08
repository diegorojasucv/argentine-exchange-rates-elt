"""Extract functions"""

import json
from typing import Any, Dict, Optional

import requests


def extract_data_from_api(api_name: str, **kwargs: Any) -> Optional[Dict]:
    """
    Extracts data from different APIs based on the provided API name.

    Args:
        api_name (str): The name of the API to extract data from.
            Valid options are 'usdt', 'usd', or 'bcra'.
        **kwargs: Additional arguments that can be passed if necessary.

    Returns:
        Optional[Dict]: The response data from the API in JSON format if the request
        is successful.

    Raises:
        ValueError: If an invalid API name is provided.
        requests.exceptions.RequestException: If there is an issue with the API request.
    """
    api_urls = {
        "usdt": "https://criptoya.com/api/usdt/ars/100",
        "usd": "https://criptoya.com/api/dolar",
        "bcra": "https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables",
    }

    api_url: Optional[str] = api_urls.get(api_name)

    if not api_url:
        raise ValueError(
            f"Invalid API name: {api_name}. Valid options are 'usdt', 'usd', or 'bcra'."
        )

    headers: Dict[str, str] = {"Accept-Language": "en-US"} if api_name == "bcra" else {}

    response = requests.get(api_url, headers=headers, verify=False)
    response.raise_for_status()
    data: Dict = json.dumps(response.json())
    return data
