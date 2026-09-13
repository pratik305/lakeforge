from fastapi import Depends, FastAPI, HTTPException

from api.db import get_connection

app = FastAPI(title="LakeForge Query API")

INSTRUMENT_COLUMNS = ["instrument_id", "sector_id", "ticker", "name", "asset_class", "exchange", "listed_date"]
ORDER_COLUMNS = ["order_id", "account_id", "order_date", "side", "status", "total_amount"]


@app.get("/instruments/{instrument_id}")
def get_instrument(instrument_id: int, con=Depends(get_connection)):
    row = con.execute(
        f"SELECT {', '.join(INSTRUMENT_COLUMNS)} FROM instruments WHERE instrument_id = ?", [instrument_id]
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="instrument not found")
    return dict(zip(INSTRUMENT_COLUMNS, row))


@app.get("/orders/range")
def orders_in_range(start: str, end: str, limit: int = 100, offset: int = 0, con=Depends(get_connection)):
    limit = min(limit, 1000)
    rows = con.execute(
        f"SELECT {', '.join(ORDER_COLUMNS)} FROM orders "
        "WHERE order_date >= ? AND order_date <= ? ORDER BY order_date LIMIT ? OFFSET ?",
        [start, end, limit, offset],
    ).fetchall()
    return [dict(zip(ORDER_COLUMNS, r)) for r in rows]

@app.get("/orders/{order_id}")
def get_order(order_id: int, con=Depends(get_connection)):
    row = con.execute(
        f"SELECT {', '.join(ORDER_COLUMNS)} FROM orders WHERE order_id = ?", [order_id]
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="order not found")
    return dict(zip(ORDER_COLUMNS, row))

@app.get("/aggregate/sector")
def aggregate_by_sector(con=Depends(get_connection)):
    rows = con.execute(
        "SELECT i.sector_id, SUM(f.quantity * f.price) AS total_value "
        "FROM order_fills f JOIN instruments i ON f.instrument_id = i.instrument_id "
        "GROUP BY i.sector_id ORDER BY i.sector_id"
    ).fetchall()
    return [{"sector_id": r[0], "total_value": r[1]} for r in rows]



