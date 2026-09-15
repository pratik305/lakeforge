import pandas as pd
import numpy as np


def generate_sectors(n:int,seed:int):
    np.random.seed(seed)
    sector_ids = np.arange(1,n+1)
    sector_names = [f"Sector {i}" for i in range(1,n+1)]
    parent_sector_ids = np.random.choice(sector_ids,size=n,replace=True)
    return pd.DataFrame({
        "sector_id": sector_ids,
        "sector_name": sector_names,
        "parent_sector_id": parent_sector_ids
    })

def generate_accounts(n:int,seed:int):
    np.random.seed(seed)
    account_ids = np.arange(1,n+1)
    names = [f"Account {i}" for i in range(1,n+1)]
    emails = [np.random.choice(["gmail.com","yahoo.com","outlook.com"]) for _ in range(n)]
    emails = [f"user{i}@{domain}" for i, domain in enumerate(emails)]
    countries = np.random.choice(["USA","Canada","UK","Australia"],size=n)
    opened_dates = pd.to_datetime("2020-01-01") + pd.to_timedelta(np.random.randint(0, 5 * 365, size=n), unit="D")
    return pd.DataFrame({
        "account_id": account_ids,
        "name": names,
        "email": emails,
        "country": countries,
        "opened_date": opened_dates
    })

def generate_instruments(n:int,sector_ids:list,seed:int):
    np.random.seed(seed)
    instrument_ids = np.arange(1,n+1)
    sector_ids_sampled = np.random.choice(sector_ids,size=n,replace=True)
    tickers = [f"TICK{i}" for i in range(1,n+1)]
    names = [f"Instrument {i}" for i in range(1,n+1)]
    asset_classes = np.random.choice(["Equity", "ETF", "Bond", "Option", "Mutual Fund"],size=n)
    exchanges = np.random.choice(["NYSE", "NASDAQ", "LSE", "TSX", "ASX"],size=n)
    listed_dates = pd.to_datetime("2010-01-01") + pd.to_timedelta(np.random.randint(0, 15 * 365, size=n), unit="D")
    return pd.DataFrame({
        "instrument_id": instrument_ids,
        "sector_id": sector_ids_sampled,
        "ticker": tickers,
        "name": names,
        "asset_class": asset_classes,
        "exchange": exchanges,
        "listed_date": listed_dates
    })

def generate_orders(n:int,account_ids:list,seed:int):
    np.random.seed(seed)
    order_ids = np.arange(1,n+1)
    account_ids= np.random.choice(account_ids,size=n,replace=True)
    order_dates = pd.to_datetime("2023-01-01") + pd.to_timedelta(np.random.randint(0, 3 * 365, size=n), unit="D")
    sides = np.random.choice(["buy","sell"],size=n)
    status = np.random.choice(["pending","filled","partially_filled","cancelled","rejected"],size=n)
    total_amounts = np.round(np.random.uniform(100,10000,size=n),2)
    return pd.DataFrame({
        "order_id": order_ids,
        "account_id": account_ids,
        "order_date": order_dates,
        "side": sides,
        "status": status,
        "total_amount": total_amounts
    })

def generate_order_fills(orders:pd.DataFrame,instrument_ids:list,seed:int,fills_per_order_range=(1,4)):
    np.random.seed(seed)
    fill_counts = np.random.randint(fills_per_order_range[0], fills_per_order_range[1] + 1, size=len(orders))
    order_ids = np.repeat(orders["order_id"].values, fill_counts)
    total_fills = len(order_ids)
    return pd.DataFrame({
        "fill_id": np.arange(1, total_fills + 1),
        "order_id": order_ids,
        "instrument_id": np.random.choice(instrument_ids, size=total_fills),
        "quantity": np.random.randint(1, 100, size=total_fills),
        "price": np.round(np.random.uniform(10, 500, size=total_fills), 2),
    })

def generate_daily_prices(instrument_ids:list,price_dates:list,seed:int):
    np.random.seed(seed)
    price_records = []
    for instrument_id in instrument_ids:
        for price_date in price_dates:
            open_price = np.round(np.random.uniform(10, 500),2)
            high_price = np.round(open_price + np.random.uniform(0,50),2)
            low_price = np.round(open_price - np.random.uniform(0,50),2)
            close_price = np.round(np.random.uniform(low_price, high_price),2)
            volume = np.random.randint(1000, 100000)
            price_records.append({
                "price_id": len(price_records)+1,
                "instrument_id": instrument_id,
                "price_date": price_date,
                "open_price": open_price,
                "high_price": high_price,
                "low_price": low_price,
                "close_price": close_price,
                "volume": volume
            })
    df = pd.DataFrame(price_records)
    df["price_date"] = pd.to_datetime(df["price_date"])
    return df

def generate_statements(account_ids:list, seed:int,statement_per_account_type=(1,3),s3_key="statements/account_{account_id}/stmt_{i}.pdf"):
    np.random.seed(seed)
    statement_records = []
    for account_id in account_ids:
        num_statements = np.random.randint(statement_per_account_type[0], statement_per_account_type[1]+1)
        for i in range(num_statements):
            statement_records.append({
                "statement_id": len(statement_records)+1,
                "account_id": account_id,
                "statement_type": np.random.choice(["monthly", "quarterly", "annual", "tax"]),
                "s3_key": s3_key.format(account_id=account_id, i=i)
            })
    df = pd.DataFrame(statement_records)
    df["generated_at"] = pd.to_datetime("2024-01-01") + pd.to_timedelta(np.random.randint(0,3* 365, size=len(df)), unit='D')
    return df 

import argparse
from pathlib import Path


def write_single(df: pd.DataFrame, table_name: str, out_dir) -> Path:
    table_dir = Path(out_dir) / table_name
    table_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(table_dir / "part-0.parquet", index=False)
    return table_dir


def write_partitioned(df: pd.DataFrame, table_name: str, out_dir, partition_keys: pd.Series, part_id: int = 0) -> Path:
    table_dir = Path(out_dir) / table_name
    for key, group in df.groupby(partition_keys):
        part_dir = table_dir / key
        part_dir.mkdir(parents=True, exist_ok=True)
        group.to_parquet(part_dir / f"part-{part_id}.parquet", index=False)
    return table_dir


def sector_partition_keys(df: pd.DataFrame) -> pd.Series:
    return "sector_id=" + df["sector_id"].astype(str)


def year_month_partition_keys(df: pd.DataFrame, date_col: str) -> pd.Series:
    dt = df[date_col]
    return "year=" + dt.dt.year.astype(str) + "/month=" + dt.dt.month.astype(str).str.zfill(2)


def price_date_partition_keys(df: pd.DataFrame) -> pd.Series:
    return "price_date=" + df["price_date"].dt.date.astype(str)


# Calibrated from a 100k-row `orders`-table sample run (see docs/architecture.md):
# average on-disk Snappy-compressed Parquet bytes per orders row. --target-gb is an
# order-of-magnitude control knob (order_fills/daily_prices/statements add rows on top
# of this), not an exact byte target -- confirm actual size with `du -sh` after a run.
BYTES_PER_FACT_ROW = 42


def rows_for_target_gb(target_gb: float) -> int:
    target_bytes = target_gb * (1024 ** 3)
    return int(target_bytes / BYTES_PER_FACT_ROW)


def run_generate(out_dir, seed: int, rows_per_table: int | None = None,
                  target_gb: float | None = None, batch_rows: int = 5_000_000) -> Path:
    if target_gb is not None:
        total_fact_rows = rows_for_target_gb(target_gb)
    elif rows_per_table is not None:
        total_fact_rows = rows_per_table
    else:
        raise ValueError("either rows_per_table or target_gb must be provided")

    n_sectors = max(min(total_fact_rows, 50), 3)
    n_accounts = max(min(total_fact_rows, 50_000), 5)
    n_instruments = max(min(total_fact_rows, 20_000), 5)

    out_dir = Path(out_dir)
    sectors = generate_sectors(n=n_sectors, seed=seed)
    accounts = generate_accounts(n=n_accounts, seed=seed)
    instruments = generate_instruments(n=n_instruments, sector_ids=sectors["sector_id"].tolist(), seed=seed)
    write_single(sectors, "sectors", out_dir)
    write_single(accounts, "accounts", out_dir)
    write_partitioned(instruments, "instruments", out_dir, sector_partition_keys(instruments))

    statements = generate_statements(accounts["account_id"].tolist(), seed=seed)
    write_partitioned(statements, "statements", out_dir, year_month_partition_keys(statements, "generated_at"))

    account_ids = accounts["account_id"].tolist()
    instrument_ids = instruments["instrument_id"].tolist()

    remaining = total_fact_rows
    part_id = 0
    order_id_offset = 0
    fill_id_offset = 0
    while remaining > 0:
        this_batch = min(batch_rows, remaining)
        batch_seed = seed + part_id

        orders = generate_orders(n=this_batch, account_ids=account_ids, seed=batch_seed)
        orders["order_id"] += order_id_offset
        write_partitioned(orders, "orders", out_dir, year_month_partition_keys(orders, "order_date"), part_id=part_id)

        order_fills = generate_order_fills(orders, instrument_ids, seed=batch_seed)
        order_fills["fill_id"] += fill_id_offset
        order_fills = order_fills.merge(orders[["order_id", "order_date"]], on="order_id", how="left")
        write_partitioned(
            order_fills.drop(columns=["order_date"]), "order_fills", out_dir,
            year_month_partition_keys(order_fills, "order_date"), part_id=part_id,
        )

        order_id_offset += this_batch
        fill_id_offset += len(order_fills)
        remaining -= this_batch
        part_id += 1

    price_dates = ["2026-08-01", "2026-08-02"]
    daily_prices = generate_daily_prices(instrument_ids, price_dates, seed=seed)
    write_partitioned(daily_prices, "daily_prices", out_dir, price_date_partition_keys(daily_prices))

    return out_dir


def main():
    parser = argparse.ArgumentParser(description="Generate the LakeForge synthetic data lake")
    parser.add_argument("--out-dir", default="./data")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-rows", type=int, default=5_000_000)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--rows-per-table", type=int)
    group.add_argument("--target-gb", type=float)
    args = parser.parse_args()
    out_dir = run_generate(
        args.out_dir, args.seed,
        rows_per_table=args.rows_per_table, target_gb=args.target_gb, batch_rows=args.batch_rows,
    )
    print(f"wrote synthetic lake to {out_dir}")


if __name__ == "__main__":
    main()

