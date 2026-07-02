select
    circuit_id,
    circuit_name,
    locality,
    country,
    latitude,
    longitude
from {{ ref('stg_circuits') }}