{% set gap_over_mep_threshold = 0.03 %}
{% set gap_over_official_threshold = 0.45 %}
{% set arbitrage_threshold = 0.01 %}

{% set top_cripto_exchanges =

    'Buenbit',
    'Ripio',
    'Satoshitango',
    'Decrypto',
    'Letsbit',
    'Binance',
    'Fiwind',
    'Lemon Cash',
    'Belo',
    'Tiendacrypto',
    'Cocos Crypto'

%}


with int_unioned_model as (

    select * from {{ ref('int_exchange_rates_unioned') }}

),

gaps_metrics as (

    select

        *,

        exchange_name in {{ top_cripto_exchanges }} as is_top_cripto_exchanges,

        exchange_name like '%P2P%' as is_p2p_exchange,

        {{ dbt_utils.safe_divide(
            'total_ask_price',
            'total_bid_price'
        ) }} - 1 as spread,

        {{ dbt_utils.safe_divide(
            'total_bid_price',
            'official_retailer_dollar'
        ) }} - 1 as gap_over_official_retailer_exchange_rate,

        {{ dbt_utils.safe_divide('
            total_bid_price',
            'official_wholesale_dollar'
        ) }} - 1 as gap_over_official_wholesale_exchange_rate,

        {{ dbt_utils.safe_divide(
            'total_bid_price', 'avg_mep_dollar'
        ) }} - 1 as gap_over_mep_exchange_rate,

        max(
            case
                when
                    source_reference = 'Criptoya - Cripto'
                    and exchange_name in {{ top_cripto_exchanges }}
                    then total_bid_price
                end

        ) over (
            partition by processed_ars_at
        ) as max_total_bid_price,

        min(
            case
                when
                    source_reference = 'Criptoya - Cripto'
                    and exchange_name in {{ top_cripto_exchanges }}
                    then total_ask_price
                end

        ) over (
            partition by processed_ars_at
        ) as min_total_ask_price

    from int_unioned_model
    where source_reference not in ('BCRA')

),

arbitrage_metrics as (

    select

        *,

        {{ dbt_utils.safe_divide(
            'max_total_bid_price', 'min_total_ask_price'
        ) }} - 1 as arbitrage_ratio,

        arbitrage_ratio > {{ arbitrage_threshold }} as is_arbitrage_opportunity,

        gap_over_official_wholesale_exchange_rate > {{ gap_over_official_threshold }}
            as is_high_official_gap,
        gap_over_mep_exchange_rate > {{ gap_over_mep_threshold }}
            as is_high_mep_gap

    from gaps_metrics

),

final as (

    select

        exchange_rate_token,
        exchange_name,
        indicator_description,
        source_reference,
        bid_price,
        ask_price,
        total_bid_price,
        total_ask_price,
        avg_total_bid_price,
        avg_total_ask_price,
        max_total_bid_price,
        min_total_ask_price,
        official_retailer_dollar,
        official_wholesale_dollar,
        avg_mep_dollar,
        gap_over_official_retailer_exchange_rate,
        gap_over_official_wholesale_exchange_rate,
        gap_over_mep_exchange_rate,
        spread,
        arbitrage_ratio,
        is_p2p_exchange,
        is_top_cripto_exchanges,
        is_high_mep_gap,
        is_arbitrage_opportunity,
        is_high_official_gap,
        updated_ars_at,
        extracted_ars_at,
        processed_ars_at

    from arbitrage_metrics

)

select * from final
