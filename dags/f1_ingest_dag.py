import sys
from datetime import datetime

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.python import get_current_context

sys.path.append("/opt/airflow/include")
from extract.jolpica import fetch_all_pages         # noqa: E402
from warehouse import ensure_raw_table, load_pages  # noqa: E402

ENDPOINTS = ["races", "drivers", "constructors", "circuits", "results"]
DBT = "/opt/dbt-venv/bin/dbt"
DBT_ARGS = "--project-dir /opt/airflow/dbt/f1_pipeline --profiles-dir /opt/airflow/dbt"


@dag(
    dag_id="f1_ingest",
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2025, 1, 1),
    schedule="@yearly",
    catchup=False,
    max_active_runs=1,
    tags=["f1", "phase-6"],
)
def f1_ingest():

    @task
    def ingest(endpoint: str) -> dict:
        season = get_current_context()["data_interval_start"].year
        ensure_raw_table(endpoint)
        pages = fetch_all_pages(season, endpoint)
        load_pages(season, endpoint, pages)
        return {"season": season, "endpoint": endpoint, "pages": len(pages)}

    ingested = ingest.expand(endpoint=ENDPOINTS)

    # Gate: staging must build AND pass every test before marts are allowed to rebuild.
    dbt_build_staging = BashOperator(
        task_id="dbt_build_staging",
        bash_command=f"{DBT} build --select staging {DBT_ARGS}",
    )

    # Marts rebuild only if the gate passed — bad data never reaches the dashboards.
    dbt_build_marts = BashOperator(
        task_id="dbt_build_marts",
        bash_command=f"{DBT} build --select marts {DBT_ARGS}",
    )

    ingested >> dbt_build_staging >> dbt_build_marts


f1_ingest()