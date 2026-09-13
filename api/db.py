import os
import duckdb

def get_connection():
    path = os.environ.get("LAKE_INDEX_PATH", "lake_index.duckdb")
    con = duckdb.connect(path, read_only=True)
    try:
        yield con
    finally:
        con.close()
