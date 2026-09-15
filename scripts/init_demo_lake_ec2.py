import os
from pathlib import Path

from data_generator.generate import run_generate
from index.build_index import rebuild_index_from_bucket
from storage.s3_client import get_s3_client
from storage.upload import upload_directory


def main():
    bucket = os.environ["LAKEFORGE_BUCKET"]
    target_gb = float(os.environ.get("LAKEFORGE_TARGET_GB", "5"))
    out_dir = Path("/data/lake-data")
    run_generate(out_dir, seed=42, target_gb=target_gb)

    # The EC2 instance role is deliberately scoped to this one bucket only (no
    # s3:ListAllMyBuckets / s3:CreateBucket) -- the bucket must already exist,
    # created ahead of time with broader (admin) credentials.
    client = get_s3_client()
    upload_directory(client, out_dir, bucket)

    index_path = Path("/app/index-data/lake_index.duckdb")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    rebuild_index_from_bucket(client, bucket, index_path)
    print(f"EC2 demo lake ready: bucket={bucket}, target_gb={target_gb}, index={index_path}")


if __name__ == "__main__":
    main()
