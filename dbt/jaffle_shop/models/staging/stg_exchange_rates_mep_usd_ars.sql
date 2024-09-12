with source as (

    select * from {{ source('redshift_source', 'raw_mep_ars_prices') }}

),

base as (

    select

        mep_name as exchange_name,
        coalesce(total_bid_price, 0) as total_bid_price,
        cast(updated_at as timestamp) as updated_at,
        cast(extracted_at as timestamp) as extracted_at

    from source

),

stage as (

    select

        exchange_name,

        cast('The MEP dollar arises from the buying and
			selling of bonds and stocks that are traded in the local and
			foreign markets.' as varchar) as indicator_description,

        cast('Criptoya - MEP' as varchar) as source_reference,
        total_bid_price,
        avg(total_bid_price) over () as avg_total_bid_price,

        convert_timezone('UTC', 'America/Argentina/Buenos_Aires', updated_at)
            as updated_ars_at,
        convert_timezone('UTC', 'America/Argentina/Buenos_Aires', extracted_at)
            as extracted_ars_at

    from base

)

select * from stage
