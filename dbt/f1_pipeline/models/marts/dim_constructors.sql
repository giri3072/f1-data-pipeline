select
    constructor_id,
    constructor_name,
    nationality
from {{ ref('stg_constructors') }}