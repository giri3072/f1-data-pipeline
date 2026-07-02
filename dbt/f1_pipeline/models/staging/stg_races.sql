with source as (

    select payload
    from {{ source('f1_raw', 'races') }}

),

flattened as (

    select jsonb_array_elements(
        payload -> 'MRData' -> 'RaceTable' -> 'Races'
    ) as race
    from source

)

select
    (race ->> 'season') || '-' || (race ->> 'round')  as race_id,
    (race ->> 'season')::int                          as season,
    (race ->> 'round')::int                           as round,
    race ->> 'raceName'                               as race_name,
    race -> 'Circuit' ->> 'circuitId'                 as circuit_id,
    (race ->> 'date')::date                           as race_date
from flattened