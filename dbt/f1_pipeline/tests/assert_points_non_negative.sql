-- Business rule: points can never be negative.
-- A dbt test "passes" when this query returns zero rows.
select
    race_id,
    driver_id,
    points
from {{ ref('stg_results') }}
where points < 0