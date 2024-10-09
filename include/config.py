from dags.functions.transform_data import (
    transform_bcra_from_api, transform_mep_usd_from_criptoya_api,
    transform_other_usd_from_criptoya_api, transform_usdt_from_criptoya_api)

TRANSFORM_FUNCTIONS = {
    "mep": {
        "transform_func": transform_mep_usd_from_criptoya_api,
        "api_name": "usd",
        "table_name": "raw_mep_ars_prices_test",
    },
    "usdt": {
        "transform_func": transform_usdt_from_criptoya_api,
        "api_name": "usdt",
        "table_name": "raw_usdt_prices_test",
    },
    "bcra": {
        "transform_func": transform_bcra_from_api,
        "api_name": "bcra",
        "table_name": "raw_bcra_indicators_test",
    },
    "other": {
        "transform_func": transform_other_usd_from_criptoya_api,
        "api_name": "usd",
        "table_name": "raw_other_usd_prices_test",
    },
}
