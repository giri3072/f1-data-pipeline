select
    driver_id,
    driver_code,
    first_name,
    last_name,
    first_name || ' ' || last_name as full_name,
    nationality,
    date_of_birth
from {{ ref('stg_drivers') }}