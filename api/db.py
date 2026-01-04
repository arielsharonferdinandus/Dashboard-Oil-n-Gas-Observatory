import duckdb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "energy.duckdb"

def query(sql: str, params=None):
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DuckDB not found at {DB_PATH}")

    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        if params:
            return con.execute(sql, params).df()
        return con.execute(sql).df()
    finally:
        con.close()
