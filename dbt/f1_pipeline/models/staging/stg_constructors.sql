with source as (
    select payload from {{ source('f1_raw', 'constructors') }}
),
flattened as (
    select jsonb_array_elements(payload -> 'MRData' -> 'ConstructorTable' -> 'Constructors') as constructor
    from source
),
renamed as (
    select
        constructor ->> 'constructorId'  as constructor_id,
        constructor ->> 'name'           as constructor_name,
        constructor ->> 'nationality'    as nationality
    from flattened
)
select distinct on (constructor_id) *
from renamed
order by constructor_id