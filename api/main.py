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


@app.get("/orders/{order_id}")
def get_order(order_id: int, con=Depends(get_connection)):
    row = con.execute(
        f"SELECT {', '.join(ORDER_COLUMNS)} FROM orders WHERE order_id = ?", [order_id]
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="order not found")
    return dict(zip(ORDER_COLUMNS, row))
