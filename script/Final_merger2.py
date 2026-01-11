import pandas as pd
from sqlalchemy import create_engine

# Load final CSV
df = pd.read_csv("magicbricks_bangalore_final_with_rent.csv")

# Rename columns to match database
df = df.rename(columns={
    "title": "name",
    "location": "address",
    "bhk": "bedrooms",
    "price_value": "price",
    "rent_real": "rent",
    "super_area_sqft": "area",          # rename correctly
    "initial_monthly_rent": "initial_monthly_rent",
    "monthly_emi": "monthly_emi",
    "effective_rent": "effective_rent",
    "total_tax_buy": "total_tax_buy",
    "total_tax_rent": "total_tax_rent",
    "final_buying_cost": "final_buying_cost",
    "final_renting_cost": "final_renting_cost",
    "decision": "decision"
})

# Create missing columns if they don't exist
for col in ["property_price", "interest_rate", "down_payment_percent", "down_payment", "loan_amount", "chosen_tax", "final_property_cost"]:
    if col not in df.columns:
        df[col] = 0  # default placeholder

df["interest_rate"] = df.get("interest_rate", 8.5)
df["property_price"] = df.get("property_price", df["price"])

df["chosen_tax"] = df.get("chosen_tax", "DYNAMIC")
df["final_property_cost"] = df.get("final_property_cost", df["property_price"])

# Reorder columns to match database table
df = df[[
    "name", "address", "bedrooms", "price", "rent", "area",
    "property_price", "interest_rate", "initial_monthly_rent",
    "down_payment_percent", "down_payment", "loan_amount",
    "monthly_emi", "effective_rent",
    "chosen_tax", "total_tax_buy", "total_tax_rent",
    "final_property_cost", "final_buying_cost", "final_renting_cost",
    "decision"
]]

# Connect to PostgreSQL
engine = create_engine(
    "postgresql+psycopg2://postgres:D5chj4yxii%40@localhost:5432/real_estate_ai"
)

# Insert into database table
df.to_sql("properties", engine, if_exists="replace", index=False)  # append if needed

print("✅ CSV successfully converted and loaded into database!")
