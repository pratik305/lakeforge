

import pathlib
import pandas as pd
import duckdb
import tempfile

TABLES = ["sectors", "accounts", "instruments", "orders", "order_fills", "daily_prices", "statements"]

POINT_LOOKUP_COLUMNS = {
    "instruments": "instrument_id",
    "orders": "order_id",
    "accounts": "account_id",
}


def download_bucket(client,bucket_name,dest_dir) -> pathlib.Path:

    dest_dir = pathlib.Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket_name):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            dest_path = dest_dir / key
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            client.download_file(bucket_name,key,str(dest_path))

    return dest_dir

def build_index(local_dir, index_path) -> None:
    local_dir = pathlib.Path(local_dir)
    con = duckdb.connect(str(index_path))
    try:
        for table in TABLES:
            table_dir = local_dir / table
            if not table_dir.exists():
                continue
            glob_pattern = str(table_dir / "**" / "*.parquet")
            con.execute(
                f"CREATE OR REPLACE TABLE {table} AS "
                f"SELECT * FROM read_parquet('{glob_pattern}', hive_partitioning=true)"
            )
        for table, column in POINT_LOOKUP_COLUMNS.items():
            if (local_dir / table).exists():
                con.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_{column} ON {table}({column})")
    finally:
        con.close()


def rebuild_index_from_bucket(client, bucket_name: str, index_path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        download_bucket(client, bucket_name, tmp)
        build_index(tmp, index_path)





