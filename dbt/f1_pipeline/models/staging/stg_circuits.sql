with source as (
    select payload from {{ source('f1_raw', 'circuits') }}
),
flattened as (
    select jsonb_array_elements(payload -> 'MRData' -> 'CircuitTable' -> 'Circuits') as circuit
    from source
),
renamed as (
    select
        circuit ->> 'circuitId'                      as circuit_id,
        circuit ->> 'circuitName'                    as circuit_name,
        circuit -> 'Location' ->> 'locality'         as locality,
        circuit -> 'Location' ->> 'country'          as country,
        (circuit -> 'Location' ->> 'lat')::numeric   as latitude,
        (circuit -> 'Location' ->> 'long')::numeric  as longitude
    from flattened
)
select distinct on (circuit_id) *
from renamed
order by circuit_id