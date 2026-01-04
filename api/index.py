from fastapi import FastAPI
import duckdb
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "db", "energy.duckdb")

def get_conn():
    return duckdb.connect(DB_PATH, read_only=True)

# -----------------------------
# PRICE DATA
# -----------------------------
@app.get("/api/price")
def price_data():
    con = get_conn()
    df = con.execute("""
        SELECT
            period,
            benchmark,
            value,
            units,
            "product-name"
        FROM price
        WHERE benchmark IN ('Brent', 'WTI', 'Henry Hub')
        ORDER BY period
    """).fetchdf()
    con.close()
    return df.to_dict(orient="records")

# -----------------------------
# GLOBAL PROD vs CONS
# -----------------------------
@app.get("/api/prod-cons")
def prod_cons():
    con = get_conn()

    oil = con.execute("""
        SELECT
            Year,
            SUM(Production) AS Production,
            'Oil' AS Energy
        FROM oil_prod
        GROUP BY Year
    """).fetchdf()

    oil_cons = con.execute("""
        SELECT
            Year,
            SUM(Consumtion) AS Consumtion
        FROM oil_cons
        GROUP BY Year
    """).fetchdf()

    oil = oil.merge(oil_cons, on="Year", how="left")

    gas = con.execute("""
        SELECT
            Year,
            SUM(Production) AS Production,
            'Gas' AS Energy
        FROM gas_prod
        GROUP BY Year
    """).fetchdf()

    gas_cons = con.execute("""
        SELECT
            Year,
            SUM(Consumtion) AS Consumtion
        FROM gas_cons
        GROUP BY Year
    """).fetchdf()

    gas = gas.merge(gas_cons, on="Year", how="left")

    con.close()

    return {
        "oil": oil.fillna(0).to_dict(orient="records"),
        "gas": gas.fillna(0).to_dict(orient="records")
    }
