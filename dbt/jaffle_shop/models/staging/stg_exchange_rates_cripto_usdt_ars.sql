with source as (

    select *
    from {{ source('postgres_source', 'usdt_ars_prices') }}

),

stage as (

    select

        {{ map_values_from_seed('exchange_name','exchange_names_mapping') }} as exchange_name,
        'Cripto Exchange Rate (USDT / ARS)'  as indicator_description,
        'Criptoya - Cripto' as source_reference,
        ask_price,
        total_ask_price,
        bid_price,
        total_bid_price,
        avg(total_bid_price) over () as avg_total_bid_price,
        avg(total_ask_price) over () as avg_total_ask_price,
        updated_at at time zone 'America/Argentina/Buenos_Aires'
            as updated_ars_at,
        extracted_at at time zone 'America/Argentina/Buenos_Aires'
            as extracted_ars_at

    from source

)


select * from stage
