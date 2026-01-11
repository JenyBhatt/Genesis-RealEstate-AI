import pandas as pd
from sqlalchemy import create_engine
import re

# 1. Load CSV
df = pd.read_csv("magicbricks_bangalore_final.csv")

# 2. Price conversion function
def price_to_number(price):
    if pd.isna(price):
        return None

    price = str(price).lower().replace("₹", "").replace(",", "").strip()

    if "cr" in price:
        return int(float(price.replace("cr", "").strip()) * 10_000_000)
    if "lac" in price or "lakh" in price:
        return int(float(price.replace("lac", "").replace("lakh", "").strip()) * 100_000)

    return None

# 3. Create numeric price column
df["price_value"] = df["Price"].apply(price_to_number)

# 4. Rename columns to match DB
df = df.rename(columns={
    "Title": "title",
    "Location": "location",
    "Price": "price_raw",
    "Bedrooms(BHK)": "bhk",
    "Bathrooms": "bathrooms",
    "Super Area": "super_area_sqft",
    "Carpet Area": "carpet_area_sqft"
})

df = df[[
    "title", "location", "price_raw", "price_value",
    "bhk", "bathrooms", "super_area_sqft", "carpet_area_sqft"
]]

# Remove ' sqft' and convert to integer
df['super_area_sqft'] = df['super_area_sqft'].str.replace(' sqft', '', regex=False)
df['super_area_sqft'] = pd.to_numeric(df['super_area_sqft'], errors='coerce')  # invalid values become NaN

df['carpet_area_sqft'] = df['carpet_area_sqft'].str.replace(' sqft', '', regex=False)
df['carpet_area_sqft'] = pd.to_numeric(df['carpet_area_sqft'], errors='coerce')

# Bathrooms
df['bathrooms'] = pd.to_numeric(df['bathrooms'].str.extract('(\d+)')[0], errors='coerce')

# Bedrooms
df['bhk'] = pd.to_numeric(df['bhk'].str.extract('(\d+)')[0], errors='coerce')

df.to_csv("data/magicbricks_bangalore_final2.csv", index=False, encoding="utf-8")


# 5. Connect to PostgreSQL
engine = create_engine(
    "postgresql+psycopg2://postgres:D5chj4yxii%40@localhost:5432/real_estate_ai",
    connect_args={"host": "127.0.0.1"}
)



# 6. Insert into table
df.to_sql("properties", engine, if_exists="append", index=False)

print("Data loaded successfully!")
