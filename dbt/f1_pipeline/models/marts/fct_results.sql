select
    r.race_id,
    ra.season,
    r.driver_id,
    r.constructor_id,
    ra.circuit_id,
    ra.race_date,
    ra.round,
    r.finish_position,
    r.points,
    r.grid_position,
    r.laps,
    r.status
from {{ ref('stg_results') }} r
left join {{ ref('stg_races') }} ra
    on r.race_id = ra.race_id