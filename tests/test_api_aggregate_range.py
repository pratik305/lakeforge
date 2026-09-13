import duckdb
import pandas as pd
from fastapi.testclient import TestClient

from api.main import app
from api.db import get_connection


def _fixture_connection(tmp_path):
    instruments = pd.DataFrame({
        "instrument_id": [1, 2], "sector_id": [10, 20], "ticker": ["AAA", "BBB"], "name": ["Acme Corp", "Globex"],
        "asset_class": ["Equity", "Equity"], "exchange": ["NYSE", "NASDAQ"],
        "listed_date": pd.to_datetime(["2020-01-01", "2020-01-02"]),
    })
    orders = pd.DataFrame({
        "order_id": [100, 101, 102],
        "account_id": [5, 6, 7],
        "order_date": pd.to_datetime(["2026-02-01", "2026-03-01", "2026-04-01"]),
        "side": ["buy", "buy", "sell"],
        "status": ["filled", "filled", "filled"],
        "total_amount": [999.0, 1999.0, 500.0],
    })
    order_fills = pd.DataFrame({
        "fill_id": [1, 2, 3],
        "order_id": [100, 101, 102],
        "instrument_id": [1, 2, 1],
        "quantity": [1, 1, 1],
        "price": [999.0, 1999.0, 500.0],
    })
    db_path = tmp_path / "test_index.duckdb"
    con = duckdb.connect(str(db_path))
    for name, df in [("instruments", instruments), ("orders", orders), ("order_fills", order_fills)]:
        con.register(f"{name}_df", df)
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM {name}_df")
    return con


def _override(con):
    def _get_connection():
        yield con
    return _get_connection


def test_aggregate_by_sector(tmp_path):
    con = _fixture_connection(tmp_path)
    app.dependency_overrides[get_connection] = _override(con)
    client = TestClient(app)
    resp = client.get("/aggregate/sector")
    assert resp.status_code == 200
    body = {row["sector_id"]: row["total_value"] for row in resp.json()}
    assert body[10] == 999.0 + 500.0
    assert body[20] == 1999.0
    app.dependency_overrides.clear()


def test_orders_in_range(tmp_path):
    con = _fixture_connection(tmp_path)
    app.dependency_overrides[get_connection] = _override(con)
    client = TestClient(app)
    resp = client.get("/orders/range", params={"start": "2026-02-15", "end": "2026-03-15"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["order_id"] == 101
    app.dependency_overrides.clear()


def test_orders_in_range_respects_limit_cap(tmp_path):
    con = _fixture_connection(tmp_path)
    app.dependency_overrides[get_connection] = _override(con)
    client = TestClient(app)
    resp = client.get("/orders/range", params={"start": "2026-01-01", "end": "2026-12-31", "limit": 5000})
    assert resp.status_code == 200
    assert len(resp.json()) == 3
    app.dependency_overrides.clear()
