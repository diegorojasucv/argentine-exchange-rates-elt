{%- macro map_values_from_seed(column_to_map, seed_name, value_not_in_seed_then_null=False) -%}

    {%- set seed_query -%}
        select *
        from {{ ref(seed_name) }}
    {%- endset -%}

    {%- set values_to_map_from_seed = run_query(seed_query) -%}

    {% if execute %}

        case
        {% for value_from in values_to_map_from_seed.columns[0].values() -%}
            {%- set value_to = values_to_map_from_seed.columns[1].values()[loop.index0] -%}
            {%- if value_to not in ['null', 'none', None] -%}
                when lower({{ column_to_map }}) = '{{ value_from }}' then '{{ value_to }}'
            {% else %}
                when lower({{ column_to_map }}) = '{{ value_from }}' then null
            {% endif -%}
        {%- endfor %}

            {%- if not value_not_in_seed_then_null -%}
                else {{ column_to_map }}
            {% endif -%}
        end

    {% endif %}

{% endmacro %}
