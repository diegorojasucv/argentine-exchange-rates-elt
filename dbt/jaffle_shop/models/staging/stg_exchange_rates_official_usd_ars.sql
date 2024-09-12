with source as (

    select * from {{ source('redshift_source', 'raw_bcra_indicators') }}

),

base as (

    select

        indicator_id,
        cd_serie,
        indicator_description,
        coalesce(total_bid_price, 0) as total_bid_price,
        cast(updated_at as timestamp) as updated_at,
        cast(extracted_at as timestamp) as extracted_at

    from source

),

stage as (

    select

        case
            when indicator_id = 4 then 'Official Retailer Dollar'
            when indicator_id = 5 then 'Official Wholesale Dollar'
        end as exchange_name,

        indicator_description,
        cast('BCRA' as varchar) as source_reference,
        coalesce(total_bid_price, 0) as total_bid_price,
        avg(coalesce(total_bid_price, 0)) over () as avg_total_bid_price,

        convert_timezone('UTC', 'America/Argentina/Buenos_Aires', updated_at)
            as updated_ars_at,
        convert_timezone('UTC', 'America/Argentina/Buenos_Aires', extracted_at)
            as extracted_ars_at

    from base
    where indicator_id in (4, 5)

)

select * from stage
