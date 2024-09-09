with source as (

    select *
    from {{ source('postgres_source', 'mep_ars_prices') }}

),

stage as (

    select

        mep_name as exchange_name,

        'The MEP dollar arises from the buying and
			selling of bonds and stocks that are traded in the local and
			foreign markets.' as indicator_description,

        'Criptoya - MEP' as source_reference,
        coalesce(price, 0) as total_bid_price,
        avg(coalesce(price, 0)) over() as avg_total_bid_price,

        updated_at at time zone 'America/Argentina/Buenos_Aires'
            as updated_ars_at,
        extracted_at at time zone 'America/Argentina/Buenos_Aires'
            as extracted_ars_at

    from source

)

select * from stage
