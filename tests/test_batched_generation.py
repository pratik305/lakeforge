import pandas as pd

from data_generator.generate import run_generate


def test_run_generate_batches_fact_tables_without_id_collisions(tmp_path):
    out_dir = run_generate(tmp_path, seed=11, rows_per_table=25, batch_rows=10)

    order_files = sorted((out_dir / "orders").rglob("*.parquet"))
    assert len(order_files) >= 3  # 25 rows / batch_rows=10 -> 3 batches -> at least 3 part files somewhere

    all_orders = pd.concat([pd.read_parquet(f) for f in order_files], ignore_index=True)
    assert len(all_orders) == 25
    assert all_orders["order_id"].is_unique

    order_fill_files = sorted((out_dir / "order_fills").rglob("*.parquet"))
    all_order_fills = pd.concat([pd.read_parquet(f) for f in order_fill_files], ignore_index=True)
    assert all_order_fills["fill_id"].is_unique
    assert set(all_order_fills["order_id"]).issubset(set(all_orders["order_id"]))
