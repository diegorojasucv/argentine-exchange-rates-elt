{% set dollars_descriptions = {

    'ahorro': ['Saving Dollar', 'Exchange rate at which Argentine citizens can buy a limited amount of US dollars for personal savings.'],
    'tarjeta': ['Tourist Dollar', 'Exchange rate used for credit card purchases in foreign currency.'],
    'blue': ['Black Market Dollar', 'Parallel market for buying and selling US dollars in Argentina, also known as the "informal dollar" or "black market dollar".']

} %}


with source as (

	select * from {{ source('redshift_source', 'raw_other_ars_prices') }}

),

base as (

    select

        exchange_name,
        coalesce(total_ask_price, 0) as total_ask_price,
        coalesce(total_bid_price, 0) as total_bid_price,
        cast(updated_at as timestamp) as updated_at,
        cast(extracted_at as timestamp) as extracted_at

    from source

),

stage as (

    select

        case
            {% for spanish_name, english_name in dollars_descriptions.items() %}
                when exchange_name = '{{ spanish_name }}' then '{{ english_name[0] }}'
            {% endfor %}
            else exchange_name
        end as exchange_name,

        case
            {% for exchange_name, exchange_rate_description in dollars_descriptions.items() %}
                when exchange_name = '{{ exchange_name }}' then '{{ exchange_rate_description[1] }}'
            {% endfor %}
            else exchange_name
        end as indicator_description,

        cast('Criptoya - USD' as varchar) as source_reference,
        total_bid_price,
        total_ask_price,
        avg(total_bid_price) over () as avg_total_bid_price,
        avg(total_ask_price) over () as avg_total_ask_price,

        convert_timezone('UTC', 'America/Argentina/Buenos_Aires', updated_at)
            as updated_ars_at,
        convert_timezone('UTC', 'America/Argentina/Buenos_Aires', extracted_at)
            as extracted_ars_at

    from base

)

select * from stage
