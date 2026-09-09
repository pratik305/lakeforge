import pandas as pd
from moto import mock_aws

from storage.s3_client import get_s3_client, ensure_bucket
from storage.upload import upload_directory

@mock_aws
def test_upload_directory_preserves_key_layout(tmp_path, monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.delenv("AWS_ENDPOINT_URL", raising=False)

    local_dir = tmp_path / "lake"
    (local_dir / "instruments" / "sector_id=1").mkdir(parents=True)
    (local_dir / "orders" / "year=2026" / "month=08").mkdir(parents=True)
    pd.DataFrame({"a": [1]}).to_parquet(local_dir / "instruments" / "sector_id=1" / "part-0.parquet")
    pd.DataFrame({"a": [1]}).to_parquet(local_dir / "orders" / "year=2026" / "month=08" / "part-0.parquet")

    client = get_s3_client()
    ensure_bucket(client, "lakeforge-test")
    keys = upload_directory(client, local_dir, "lakeforge-test")

    assert sorted(keys) == [
        "instruments/sector_id=1/part-0.parquet",
        "orders/year=2026/month=08/part-0.parquet",
    ]
    remote_keys = {obj["Key"] for obj in client.list_objects_v2(Bucket="lakeforge-test")["Contents"]}
    assert remote_keys == set(keys)
