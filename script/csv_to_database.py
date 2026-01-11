import pandas as pd
from sqlalchemy import create_engine
import numpy as np

# Load cleaned CSV
df = pd.read_csv("magicbricks_bangalore_final2.csv")

# -------------------------
# 1. Rename columns
# -------------------------
df = df.rename(columns={
    "title": "name",
    "location": "address",
    "bhk": "bedrooms",
    "price_value": "price",
    "super_area_sqft": "area"
})

# -------------------------
# 2. Fill missing base fields
# -------------------------
df["furnishing"] = "Unfurnished"

df["rent"] = (df["price"] * 0.004 / 12).round(0)

# -------------------------
# 3. Financial assumptions
# -------------------------
df["property_price"] = df["price"]
df["interest_rate"] = 8.5
df["initial_monthly_rent"] = df["rent"]

df["down_payment_percent"] = 0.25
df["down_payment"] = df["price"] * df["down_payment_percent"]
df["loan_amount"] = df["price"] - df["down_payment"]

# EMI formula
r = 8.5 / 100 / 12
n = 20 * 12

df["monthly_emi"] = (
    df["loan_amount"] * r * (1 + r) ** n /
    ((1 + r) ** n - 1)
).round(0)

df["effective_rent"] = df["monthly_emi"]

# -------------------------
# 4. Taxes (simple version)
# -------------------------
df["chosen_tax"] = "DYNAMIC"
df["total_tax_buy"] = df["price"] * 0.15
df["total_tax_rent"] = df["rent"] * 12 * 5

# -------------------------
# 5. Final cost comparison
# -------------------------
df["final_property_cost"] = df["price"] + df["total_tax_buy"]
df["final_buying_cost"] = df["final_property_cost"] 
df["final_renting_cost"] = df["rent"] * 12 * 20 + df["total_tax_rent"]

# Decision
df["buy_score"] = (
    df["monthly_emi"] * 12 * 20 +
    df["total_tax_buy"]
)

df["rent_score"] = (
    df["rent"] * 12 * 20 +
    df["total_tax_rent"]
)

df["user_horizon_years"] = np.random.choice([3, 5, 10, 20], size=len(df))

df["decision"] = np.where(
    df["monthly_emi"] * 12 * df["user_horizon_years"]
    <
    df["rent"] * 12 * df["user_horizon_years"],
    "BUY",
    "RENT"
)




# -------------------------
# 6. Select EXACT DB columns
# -------------------------
df = df[[
    "name", "address", "bedrooms", "price", "rent", "area", "furnishing",
    "property_price", "interest_rate", "initial_monthly_rent",
    "down_payment_percent", "down_payment", "loan_amount",
    "monthly_emi", "effective_rent",
    "chosen_tax", "total_tax_buy", "total_tax_rent",
    "final_property_cost", "final_buying_cost", "final_renting_cost",
    "decision"
]]

# -------------------------
# 7. Insert into PostgreSQL
# -------------------------
engine = create_engine(
    "postgresql+psycopg2://postgres:D5chj4yxii%40@localhost:5432/real_estate_ai"
)

df.to_sql("properties", engine, if_exists="append", index=False)

print("✅ Data successfully converted & loaded into database")
