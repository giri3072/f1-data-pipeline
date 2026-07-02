with source as (
    select payload from {{ source('f1_raw', 'drivers') }}
),
flattened as (
    select jsonb_array_elements(payload -> 'MRData' -> 'DriverTable' -> 'Drivers') as driver
    from source
),
renamed as (
    select
        driver ->> 'driverId'                as driver_id,
        driver ->> 'code'                    as driver_code,
        (driver ->> 'permanentNumber')::int  as permanent_number,
        driver ->> 'givenName'               as first_name,
        driver ->> 'familyName'              as last_name,
        (driver ->> 'dateOfBirth')::date     as date_of_birth,
        driver ->> 'nationality'             as nationality
    from flattened
)
select distinct on (driver_id) *
from renamed
order by driver_id