with source as (

    select *
    from {{ source('postgres_source', 'mep_ars_prices') }}

),

stage as (

    select

        mep_name,

        'The MEP dollar arises from the buying and
			selling of bonds and stocks that are traded in the local and
			foreign markets.' as indicator_description,

        'Criptoya - MEP' as source_reference,
        coalesce(price, 0) as total_bid_price,

        avg(total_bid_price) over() as avg_total_bid_price,

        convert_timezone(
            'America/Argentina/Buenos_Aires',
            to_timestamp(updated_at)
        ) as updated_ars_at,

        convert_timezone(
            'America/Argentina/Buenos_Aires',
            to_timestamp(extracted_at)
        ) as extracted_at

    from source

)

select * from stage
