with source as (

    select payload
    from {{ source('f1_raw', 'results') }}

),

races as (

    -- first explode: one row per race
    select jsonb_array_elements(
        payload -> 'MRData' -> 'RaceTable' -> 'Races'
    ) as race
    from source

),

results as (

    -- second explode: one row per result inside each race,
    -- carrying the race_id down with it
    select
        (race ->> 'season') || '-' || (race ->> 'round')  as race_id,
        jsonb_array_elements(race -> 'Results')           as result
    from races

)

select
    race_id,
    result -> 'Driver'      ->> 'driverId'       as driver_id,
    result -> 'Constructor' ->> 'constructorId'  as constructor_id,
    (result ->> 'position')::int                 as finish_position,
    (result ->> 'points')::numeric               as points,
    (result ->> 'grid')::int                     as grid_position,
    (result ->> 'laps')::int                     as laps,
    result ->> 'status'                          as status
from results