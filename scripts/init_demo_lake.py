import os
from pathlib import Path

from data_generator.generate import run_generate
from index.build_index import rebuild_index_from_bucket
from storage.s3_client import ensure_bucket, get_s3_client
from storage.upload import upload_directory


def main():
    bucket = os.environ["LAKEFORGE_BUCKET"]
    out_dir = Path("/tmp/lake-data")
    run_generate(out_dir, seed=42, rows_per_table=2000)

    client = get_s3_client()
    ensure_bucket(client, bucket)
    upload_directory(client, out_dir, bucket)

    index_path = Path("/app/index-data/lake_index.duckdb")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    rebuild_index_from_bucket(client, bucket, index_path)
    print(f"demo lake ready: bucket={bucket}, index={index_path}")


if __name__ == "__main__":
    main()
