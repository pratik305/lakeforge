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
    opened_dates = pd.date_range(start="2020-01-01", periods=n, freq='D')
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
    listed_dates = pd.date_range(start="2010-01-01", periods=n, freq='D')
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
    order_dates  =pd.date_range(start="2021-01-01", periods=n, freq='D')
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
    fill_records = []
    order_ids = np.repeat(orders["order_id"].values, np.random.randint(fills_per_order_range[0], fills_per_order_range[1]+1, size=len(orders)))
    for order_id in order_ids:
        instrument_id = np.random.choice(instrument_ids)
        quantity = np.random.randint(1, 100)
        price = np.round(np.random.uniform(10, 500),2)
        fill_records.append({
            "fill_id": len(fill_records)+1,
            "order_id": order_id,
            "instrument_id": instrument_id,
            "quantity": quantity,
            "price": price
        })
    return pd.DataFrame(fill_records)

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
    return pd.DataFrame(price_records)

def generate_statements(account_ids:list, seed:int,statement_per_account_type=(1,3),s3_key="statements/account_{account_id}/stmt_{i}.pdf",generated_at=pd.Timestamp.now()):
    np.random.seed(seed)
    statement_records = []
    for account_id in account_ids:
        num_statements = np.random.randint(statement_per_account_type[0], statement_per_account_type[1]+1)
        for i in range(num_statements):
            statement_records.append({
                "statement_id": len(statement_records)+1,
                "account_id": account_id,
                "statement_type": np.random.choice(["monthly", "quarterly", "annual", "tax"]),
                "s3_key": s3_key.format(account_id=account_id, i=i),
                "generated_at": generated_at
            })
    return pd.DataFrame(statement_records)
