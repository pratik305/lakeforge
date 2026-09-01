from data_generator.generate import generate_sectors, generate_accounts, generate_instruments


def test_generate_sectors_row_count_and_columns():
    df = generate_sectors(n=10, seed=42)
    assert len(df) == 10
    assert list(df.columns) == ["sector_id", "sector_name", "parent_sector_id"]
    assert df["sector_id"].is_unique


def test_generate_accounts_row_count_and_columns():
    df = generate_accounts(n=25, seed=42)
    assert len(df) == 25
    assert list(df.columns) == ["account_id", "name", "email", "country", "opened_date"]
    assert df["account_id"].is_unique
    assert df["email"].str.contains("@").all()


def test_generate_instruments_references_valid_sectors():
    sectors = generate_sectors(n=5, seed=1)
    df = generate_instruments(n=50, sector_ids=sectors["sector_id"].tolist(), seed=1)
    assert len(df) == 50
    assert list(df.columns) == [
        "instrument_id", "sector_id", "ticker", "name",
        "asset_class", "exchange", "listed_date",
    ]
    assert set(df["sector_id"]).issubset(set(sectors["sector_id"]))
    assert df["instrument_id"].is_unique
    assert df["asset_class"].isin(["Equity", "ETF", "Bond", "Option", "Mutual Fund"]).all()
