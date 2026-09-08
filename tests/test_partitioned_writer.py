import pandas as pd

from data_generator.generate import (
    generate_sectors, generate_accounts, generate_instruments, generate_orders,
    write_single, write_partitioned, sector_partition_keys, year_month_partition_keys,
)


def test_write_single_creates_one_file(tmp_path):
    sectors = generate_sectors(n=3, seed=6)
    out_dir = write_single(sectors, "sectors", tmp_path)
    files = list(out_dir.glob("*.parquet"))
    assert len(files) == 1
    assert pd.read_parquet(files[0])["sector_id"].tolist() == sectors["sector_id"].tolist()


def test_write_partitioned_instruments_creates_sector_subdirs(tmp_path):
    sectors = generate_sectors(n=3, seed=6)
    instruments = generate_instruments(n=30, sector_ids=sectors["sector_id"].tolist(), seed=6)
    write_partitioned(instruments, "instruments", tmp_path, sector_partition_keys(instruments))
    out_dirs = sorted(p.name for p in (tmp_path / "instruments").iterdir())
    expected = sorted(f"sector_id={sid}" for sid in instruments["sector_id"].unique())
    assert out_dirs == expected


def test_write_partitioned_orders_creates_year_month_subdirs(tmp_path):
    accounts = generate_accounts(n=5, seed=7)
    orders = generate_orders(n=50, account_ids=accounts["account_id"].tolist(), seed=7)
    write_partitioned(orders, "orders", tmp_path, year_month_partition_keys(orders, "order_date"))
    written_files = list((tmp_path / "orders").rglob("*.parquet"))
    assert len(written_files) > 0
    for f in written_files:
        assert f.parent.parent.name.startswith("year=")
        assert f.parent.name.startswith("month=")


def test_write_partitioned_second_batch_adds_part_file_without_overwriting(tmp_path):
    sectors = generate_sectors(n=1, seed=8)
    batch_one = generate_instruments(n=5, sector_ids=sectors["sector_id"].tolist(), seed=8)
    batch_two = generate_instruments(n=5, sector_ids=sectors["sector_id"].tolist(), seed=9)
    write_partitioned(batch_one, "instruments", tmp_path, sector_partition_keys(batch_one), part_id=0)
    write_partitioned(batch_two, "instruments", tmp_path, sector_partition_keys(batch_two), part_id=1)
    part_dir = tmp_path / "instruments" / f"sector_id={sectors['sector_id'].iloc[0]}"
    files = sorted(p.name for p in part_dir.glob("*.parquet"))
    assert files == ["part-0.parquet", "part-1.parquet"]
