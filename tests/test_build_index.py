import duckdb
import pandas as pd
from moto import mock_aws

from storage.s3_client import get_s3_client, ensure_bucket
from index.build_index import rebuild_index_from_bucket


@mock_aws
def test_rebuild_index_from_bucket_enables_point_lookup(tmp_path, monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.delenv("AWS_ENDPOINT_URL", raising=False)

    client = get_s3_client()
    ensure_bucket(client, "lakeforge-test")

    instruments = pd.DataFrame({
        "instrument_id": [1, 2, 3],
        "sector_id": [10, 10, 10],
        "ticker": ["AAA", "BBB", "CCC"],
        "name": ["x", "y", "z"],
        "asset_class": ["Equity", "Equity", "ETF"],
        "exchange": ["NYSE", "NASDAQ", "NYSE"],
        "listed_date": pd.to_datetime(["2020-01-01"] * 3),
    })
    local_file = tmp_path / "part-0.parquet"
    instruments.to_parquet(local_file)
    client.upload_file(str(local_file), "lakeforge-test", "instruments/sector_id=10/part-0.parquet")

    index_path = tmp_path / "lake_index.duckdb"
    rebuild_index_from_bucket(client, "lakeforge-test", index_path)

    con = duckdb.connect(str(index_path))
    row = con.execute("SELECT name FROM instruments WHERE instrument_id = 1").fetchone()
    assert row == ("x",)

    indexes = con.execute(
        "SELECT index_name FROM duckdb_indexes() WHERE table_name = 'instruments'"
    ).fetchall()
    assert ("idx_instruments_instrument_id",) in indexes
    con.close()
