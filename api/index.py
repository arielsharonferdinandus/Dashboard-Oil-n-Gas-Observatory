from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.db import query

app = FastAPI()

# CORS for frontend JS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok"}

# -----------------------------
# PRICE DATA
# -----------------------------
@app.get("/api/price")
def price_data():
    df = query("""
        SELECT
            period,
            benchmark,
            value
        FROM price
        WHERE benchmark IN ('Brent', 'WTI', 'Henry Hub')
        ORDER BY period
    """)

    if df.empty:
        return [
            {"period": "2020", "benchmark": "Brent", "value": 50},
            {"period": "2020", "benchmark": "WTI", "value": 45},
            {"period": "2020", "benchmark": "Henry Hub", "value": 3},
        ]

    return df.to_dict(orient="records")

# -----------------------------
# PRODUCTION vs CONSUMPTION
# -----------------------------
@app.get("/api/prod-cons")
def prod_cons():
    oil = query("""
        SELECT
            p.Year,
            p.Production,
            c.Consumtion,
            'Oil' AS Energy
        FROM oil_prod p
        LEFT JOIN oil_cons c ON p.Year = c.Year
        ORDER BY p.Year
    """)

    gas = query("""
        SELECT
            p.Year,
            p.Production,
            c.Consumtion,
            'Gas' AS Energy
        FROM gas_prod p
        LEFT JOIN gas_cons c ON p.Year = c.Year
        ORDER BY p.Year
    """)

    return {
        "oil": oil.fillna(0).to_dict(orient="records"),
        "gas": gas.fillna(0).to_dict(orient="records"),
    }
