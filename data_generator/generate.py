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