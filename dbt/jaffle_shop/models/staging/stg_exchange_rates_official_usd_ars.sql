with source as (

    select * from {{ source('postgres_source', 'bcra_indicators') }}

),

filter_exchange_rates as (

    select

        case
            when indicator_id = 4 then 'Official Retailer Dollar'
            when indicator_id = 5 then 'Official Wholesale Dollar'
        end as exchange_name,

        indicator_description,
        'BCRA' as source_reference,
        coalesce(valor, 0) as total_bid_price,
        avg(coalesce(valor, 0)) over () as avg_total_bid_price,
        updated_at at time zone 'America/Argentina/Buenos_Aires'
            as updated_ars_at,
        extracted_at at time zone 'America/Argentina/Buenos_Aires'
            as extracted_ars_at

    from source
    where indicator_id in (4, 5)

)

select * from filter_exchange_rates
