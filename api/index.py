from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import os

# =============================
# APP INIT
# =============================
app = FastAPI(
    title="Global Energy API",
    description="Energy Price, Production & Consumption API (DuckDB)",
    version="1.0.0"
)

# =============================
# CORS (IMPORTANT for frontend JS)
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# DATABASE CONFIG
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "energy.duckdb")

def get_conn():
    return duckdb.connect(DB_PATH, read_only=True)

# =============================
# ROOT (HEALTH CHECK)
# =============================
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Global Energy API is running",
        "endpoints": [
            "/api/price",
            "/api/prod-cons",
            "/api/tables"
        ]
    }

# =============================
# LIST TABLES (DEBUG / INFO)
# =============================
@app.get("/api/tables")
def list_tables():
    con = get_conn()
    df = con.execute("""
        SELECT
            table_catalog,
            table_schema,
            table_name,
            table_type
        FROM information_schema.tables
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY table_name
    """).fetchdf()
    con.close()

    return df.to_dict(orient="records")

# =============================
# PRICE DATA
# =============================
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
        FROM energy.main.price
        WHERE benchmark IN ('Brent', 'WTI', 'Henry Hub')
        ORDER BY period
    """).fetchdf()
    con.close()

    return df.to_dict(orient="records")

# =============================
# GLOBAL PRODUCTION vs CONSUMPTION
# =============================
@app.get("/api/prod-cons")
def prod_cons():
    con = get_conn()

    # -------- OIL --------
    oil_prod = con.execute("""
        SELECT
            Year,
            SUM(Production) AS Production
        FROM energy.main.oil_prod
        GROUP BY Year
        ORDER BY Year
    """).fetchdf()

    oil_cons = con.execute("""
        SELECT
            Year,
            SUM(Consumtion) AS Consumtion
        FROM energy.main.oil_cons
        GROUP BY Year
        ORDER BY Year
    """).fetchdf()

    oil = oil_prod.merge(oil_cons, on="Year", how="left")
    oil["Energy"] = "Oil"

    # -------- GAS --------
    gas_prod = con.execute("""
        SELECT
            Year,
            SUM(Production) AS Production
        FROM energy.main.gas_prod
        GROUP BY Year
        ORDER BY Year
    """).fetchdf()

    gas_cons = con.execute("""
        SELECT
            Year,
            SUM(Consumtion) AS Consumtion
        FROM energy.main.gas_cons
        GROUP BY Year
        ORDER BY Year
    """).fetchdf()

    gas = gas_prod.merge(gas_cons, on="Year", how="left")
    gas["Energy"] = "Gas"

    con.close()

    return {
        "oil": oil.fillna(0).to_dict(orient="records"),
        "gas": gas.fillna(0).to_dict(orient="records")
    }

# =============================
# DUMMY: SUBSIDY vs GDP
# =============================
@app.get("/api/subsidy-gdp")
def subsidy_vs_gdp():
    return [
        {
            "Country": "Indonesia",
            "Fuel Subsidy (% GDP)": 2.1,
            "GDP (Trillion USD)": 1.4
        },
        {
            "Country": "India",
            "Fuel Subsidy (% GDP)": 1.8,
            "GDP (Trillion USD)": 3.4
        },
        {
            "Country": "China",
            "Fuel Subsidy (% GDP)": 0.9,
            "GDP (Trillion USD)": 17.7
        },
        {
            "Country": "United States",
            "Fuel Subsidy (% GDP)": 0.4,
            "GDP (Trillion USD)": 26.9
        },
        {
            "Country": "Saudi Arabia",
            "Fuel Subsidy (% GDP)": 3.2,
            "GDP (Trillion USD)": 1.1
        }
    ]

# =============================
# DUMMY: NEWS
# =============================
@app.get("/api/news")
def energy_news():
    return [
        {
            "title": "OPEC+ Considers Production Cut",
            "source": "Reuters",
            "summary": "OPEC+ members are discussing potential production cuts amid weakening global demand."
        },
        {
            "title": "Middle East Tensions Push Oil Prices Higher",
            "source": "Bloomberg",
            "summary": "Geopolitical risks in the Middle East increase oil price volatility."
        },
        {
            "title": "Energy Transition Impacts Oil Demand",
            "source": "IEA",
            "summary": "Renewables growth reshapes long-term oil demand outlook."
        }
    ]
