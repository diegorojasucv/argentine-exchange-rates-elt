with source as (

    select * from {{ source('redshift_source', 'raw_usdt_ars_prices') }}

),

base as (

    select

        exchange_name,
        coalesce(ask_price, 0) as ask_price,
        coalesce(total_ask_price, 0) as total_ask_price,
        coalesce(bid_price, 0) as bid_price,
        coalesce(total_bid_price, 0) as total_bid_price,
        cast(updated_at as timestamp) as updated_at,
        cast(extracted_at as timestamp) as extracted_at

    from source

),

stage as (

    select

        {{ map_values_from_seed('exchange_name','exchange_names_mapping') }} as exchange_name,
        'Cripto Exchange Rate (USDT / ARS)' as indicator_description,
        'Criptoya - Cripto' as source_reference,
        ask_price,
        total_ask_price,
        bid_price,
        total_bid_price,
        avg(total_bid_price) over () as avg_total_bid_price,
        avg(total_ask_price) over () as avg_total_ask_price,

        convert_timezone('UTC', 'America/Argentina/Buenos_Aires', updated_at)
            as updated_ars_at,
        convert_timezone('UTC', 'America/Argentina/Buenos_Aires', extracted_at)
            as extracted_ars_at

    from base

)

select * from stage
