import pandas as pd
import numpy as np

# Sale data
df_sales = pd.read_csv("magicbricks_bangalore_final2.csv")

# Rent data (~270 rows)
df_rent = pd.read_csv("magicbricks_bangalore_rent.csv")

print(df_sales.columns)

# Preview
print(df_sales.head())
print(df_rent.head())

# Strip whitespaces
df_sales['location'] = df_sales['location'].str.strip()
df_rent['location'] = df_rent['location'].str.strip()

# Ensure BHK numeric
df_sales['bhk'] = pd.to_numeric(df_sales['bhk'], errors='coerce')
df_rent['bhk'] = pd.to_numeric(df_rent['bhk'], errors='coerce')

# Optional: lowercase all locations
df_sales['location'] = df_sales['location'].str.lower()
df_rent['location'] = df_rent['location'].str.lower()

def match_rent(row, rent_df):
    # Filter by location and BHK
    matches = rent_df[
        (rent_df['location'] == row['location']) &
        (rent_df['bhk'] == row['bhk'])
    ]
    
    # Optional: filter by area if available in rent_df
    if 'area' in rent_df.columns and not np.isnan(row['area']):
        matches = matches[
            (matches['area'] >= row['area'] * 0.85) &
            (matches['area'] <= row['area'] * 1.15)
        ]
    
    if len(matches) > 0:
        return matches['rent'].median()  # use median to avoid outliers
    else:
        return np.nan

# Apply to sale dataset
df_sales['rent_real'] = df_sales.apply(lambda row: match_rent(row, df_rent), axis=1)

# Check how many were matched
print(df_sales['rent_real'].isna().sum(), "properties without matched rent")

# Fill NaNs with fallback
fallback_rent = df_rent.groupby('bhk')['rent'].median().to_dict()
df_sales['rent_real'] = df_sales.apply(
    lambda x: fallback_rent.get(x['bhk'], x['rent_real']),
    axis=1
)

# Recalculate initial rent
df_sales['initial_monthly_rent'] = df_sales['rent_real']

# Financial assumptions
df_sales['property_price'] = df_sales['price_value']
df_sales['interest_rate'] = 8.5
df_sales['down_payment_percent'] = 0.25
df_sales['down_payment'] = df_sales['price_value'] * df_sales['down_payment_percent']
df_sales['loan_amount'] = df_sales['price_value'] - df_sales['down_payment']

r = 8.5 / 100 / 12
n = 20 * 12

df_sales['monthly_emi'] = (
    df_sales['loan_amount'] * r * (1 + r)**n / ((1 + r)**n - 1)
).round(0)

df_sales['effective_rent'] = df_sales['monthly_emi']

# Taxes
df_sales['total_tax_buy'] = df_sales['price_value'] * 0.15
df_sales['total_tax_rent'] = df_sales['rent_real'] * 12 * 5

# Final cost
df_sales['final_buying_cost'] = df_sales['price_value'] + df_sales['total_tax_buy']
df_sales['final_renting_cost'] = df_sales['rent_real'] * 12 * 20 + df_sales['total_tax_rent']

# Decision
df_sales['decision'] = np.where(
    df_sales['final_buying_cost'] < df_sales['final_renting_cost'],
    'BUY',
    'RENT'
)

df_sales.to_csv("magicbricks_bangalore_final_with_rent.csv", index=False, encoding="utf-8")

