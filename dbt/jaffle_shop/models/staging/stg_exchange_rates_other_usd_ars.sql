{% set dollars_descriptions = {

    'ahorro': ['Saving Dollar', 'Exchange rate at which Argentine citizens can buy a limited amount of US dollars for personal savings.'],
    'tarjeta': ['Tourist Dollar', 'Exchange rate used for credit card purchases in foreign currency.'],
    'blue': ['Black Market Dollar', 'Parallel market for buying and selling US dollars in Argentina, also known as the "informal dollar" or "black market dollar".']

} %}


with source as (

	select *
	from {{ source('postgres_source', 'other_ars_prices') }}
),

stage as (

    select

        case
            {% for spanish_name, english_name in dollars_descriptions.items() %}
                when other_name = '{{ spanish_name }}' then '{{ english_name[0] }}'
            {% endfor %}
            else other_name
        end as other_name,

        case
            {% for other_name, exchange_rate_description in dollars_descriptions.items() %}
                when other_name = '{{ other_name }}' then '{{ exchange_rate_description[1] }}'
            {% endfor %}
            else other_name
        end as indicator_description,

        'Criptoya - USD' as source_reference,
        coalesce(bid_price, price, 0) as total_bid_price,
        coalesce(ask_price, price, 0) as total_ask_price,

        updated_at at time zone 'America/Argentina/Buenos_Aires'
            as updated_ars_at,
        extracted_at at time zone 'America/Argentina/Buenos_Aires'
            as extracted_ars_at

    from source

)

select * from stage
