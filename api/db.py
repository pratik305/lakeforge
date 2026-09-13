import duckdb

def get_connection(db_path="index.duckdb"):
    con = duckdb.connect(db_path,read_only=True)
    try:
        yield con
    finally:
        con.close()