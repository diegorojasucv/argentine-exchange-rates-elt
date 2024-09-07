with source as (

    select *
    from {{ source('postgres_source', 'usdt_ars_prices') }}

),

stage as (

    select

        exchange_name,
        ask_price,
        total_ask_price,
        bid_price,
        total_bid_price,
        updated_at at time zone 'America/Argentina/Buenos_Aires'
            as updated_ars_at,
        extracted_at at time zone 'America/Argentina/Buenos_Aires'
            as extracted_ars_at

    from source

)


select * from stage
