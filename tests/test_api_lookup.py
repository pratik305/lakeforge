import duckdb
import pandas as pd
from fastapi.testclient import TestClient

from api.main import app
from api.db import get_connection


def _fixture_connection(tmp_path):
    instruments = pd.DataFrame({
        "instrument_id": [1], "sector_id": [10], "ticker": ["AAA"], "name": ["Acme Corp"],
        "asset_class": ["Equity"], "exchange": ["NYSE"], "listed_date": pd.to_datetime(["2020-01-01"]),
    })
    orders = pd.DataFrame({
        "order_id": [100], "account_id": [5], "order_date": pd.to_datetime(["2026-02-01"]),
        "side": ["buy"], "status": ["filled"], "total_amount": [999.0],
    })
    db_path = tmp_path / "test_index.duckdb"
    con = duckdb.connect(str(db_path))
    con.register("instruments_df", instruments)
    con.execute("CREATE TABLE instruments AS SELECT * FROM instruments_df")
    con.register("orders_df", orders)
    con.execute("CREATE TABLE orders AS SELECT * FROM orders_df")
    return con


def _override(con):
    def _get_connection():
        yield con
    return _get_connection


def test_get_instrument_found(tmp_path):
    con = _fixture_connection(tmp_path)
    app.dependency_overrides[get_connection] = _override(con)
    client = TestClient(app)
    resp = client.get("/instruments/1")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Acme Corp"
    app.dependency_overrides.clear()


def test_get_instrument_not_found(tmp_path):
    con = _fixture_connection(tmp_path)
    app.dependency_overrides[get_connection] = _override(con)
    client = TestClient(app)
    resp = client.get("/instruments/999")
    assert resp.status_code == 404
    app.dependency_overrides.clear()


def test_get_order_found(tmp_path):
    con = _fixture_connection(tmp_path)
    app.dependency_overrides[get_connection] = _override(con)
    client = TestClient(app)
    resp = client.get("/orders/100")
    assert resp.status_code == 200
    assert resp.json()["status"] == "filled"
    app.dependency_overrides.clear()
