with source as (

    select *
    from {{ source('postgres_source', 'usdt_ars_prices') }}

)

select * from source