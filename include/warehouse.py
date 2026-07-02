import json
import psycopg2

WAREHOUSE = dict(host="postgres", port=5432, dbname="f1",
                 user="f1_user", password="f1_pass")


def get_conn():
    return psycopg2.connect(**WAREHOUSE)


def ensure_raw_table(endpoint: str) -> None:
    """Create the landing table if it doesn't exist yet."""
    ddl = f"""
        CREATE TABLE IF NOT EXISTS raw.{endpoint} (
            id           bigserial PRIMARY KEY,
            season       integer     NOT NULL,
            endpoint     text        NOT NULL,
            page_offset  integer     NOT NULL,
            payload      jsonb       NOT NULL,
            extracted_at timestamptz NOT NULL DEFAULT now()
        );
    """
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(ddl)
        conn.commit()
    finally:
        conn.close()


def load_pages(season: int, endpoint: str, pages: list) -> None:
    """Idempotent load: wipe this season's rows, then insert the fresh pages."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"DELETE FROM raw.{endpoint} WHERE season = %s AND endpoint = %s;",
                (season, endpoint),
            )
            for i, page in enumerate(pages):
                cur.execute(
                    f"""INSERT INTO raw.{endpoint} (season, endpoint, page_offset, payload)
                        VALUES (%s, %s, %s, %s);""",
                    (season, endpoint, i * PAGE_LIMIT if (PAGE_LIMIT := 100) else 0, json.dumps(page)),
                )
        conn.commit()
    finally:
        conn.close()