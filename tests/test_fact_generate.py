from data_generator.generate import (
    generate_sectors, generate_accounts, generate_instruments,
    generate_orders, generate_order_fills, generate_daily_prices, generate_statements,
)


def test_generate_orders_reference_valid_accounts():
    accounts = generate_accounts(n=10, seed=2)
    orders = generate_orders(n=100, account_ids=accounts["account_id"].tolist(), seed=2)
    assert len(orders) == 100
    assert list(orders.columns) == ["order_id", "account_id", "order_date", "side", "status", "total_amount"]
    assert set(orders["account_id"]).issubset(set(accounts["account_id"]))
    assert orders["order_id"].is_unique
    assert orders["side"].isin(["buy", "sell"]).all()


def test_generate_order_fills_reference_valid_orders_and_instruments():
    sectors = generate_sectors(n=3, seed=3)
    instruments = generate_instruments(n=20, sector_ids=sectors["sector_id"].tolist(), seed=3)
    accounts = generate_accounts(n=10, seed=3)
    orders = generate_orders(n=30, account_ids=accounts["account_id"].tolist(), seed=3)
    fills = generate_order_fills(orders, instruments["instrument_id"].tolist(), seed=3)
    assert list(fills.columns) == ["fill_id", "order_id", "instrument_id", "quantity", "price"]
    assert set(fills["order_id"]).issubset(set(orders["order_id"]))
    assert set(fills["instrument_id"]).issubset(set(instruments["instrument_id"]))
    assert (fills["quantity"] > 0).all()


def test_generate_daily_prices_one_row_per_instrument_per_date_with_valid_ohlc():
    sectors = generate_sectors(n=2, seed=4)
    instruments = generate_instruments(n=10, sector_ids=sectors["sector_id"].tolist(), seed=4)
    prices = generate_daily_prices(
        instruments["instrument_id"].tolist(),
        price_dates=["2026-08-01", "2026-08-02"],
        seed=4,
    )
    assert len(prices) == 10 * 2
    assert list(prices.columns) == [
        "price_id", "instrument_id", "price_date",
        "open_price", "high_price", "low_price", "close_price", "volume",
    ]
    assert set(prices["instrument_id"]) == set(instruments["instrument_id"])
    assert (prices["high_price"] >= prices["open_price"]).all()
    assert (prices["high_price"] >= prices["close_price"]).all()
    assert (prices["low_price"] <= prices["open_price"]).all()
    assert (prices["low_price"] <= prices["close_price"]).all()


def test_generate_statements_within_expected_range_per_account():
    accounts = generate_accounts(n=5, seed=5)
    statements = generate_statements(accounts["account_id"].tolist(), seed=5)
    assert list(statements.columns) == ["statement_id", "account_id", "statement_type", "s3_key", "generated_at"]
    counts = statements.groupby("account_id").size()
    assert counts.between(1, 3).all()