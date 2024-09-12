import requests


def extract_data_from_api(api_name, **kwargs):
    """
    Extracts data from different APIs based on the provided API name.

    Args:
        api_name (str): The name of the API to extract data from.
            Valid options are 'usdt', 'usd', or 'bcra'.
        **kwargs: Additional arguments that can be passed if necessary.

    Returns:
        dict or None: The response data from the API in JSON format if the request
        was successful, otherwise None.
    """
    api_urls = {
        "usdt": "https://criptoya.com/api/usdt/ars/100",
        "usd": "https://criptoya.com/api/dolar",
        "bcra": "https://api.bcra.gob.ar/estadisticas/v2.0/principalesvariables",
    }

    api_url = api_urls.get(api_name)

    if not api_url:
        raise ValueError(
            f"Invalid API name: {api_name}. Valid options are 'usdt', 'usd', or 'bcra'."
        )

    headers = {"Accept-Language": "en-US"} if api_name == "bcra" else {}

    try:
        response = requests.get(api_url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException:
        return None
