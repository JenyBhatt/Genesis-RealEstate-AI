import pandas as pd

#Data Cleaning for all the columns not showing bedrooms or prices or anything (except super carpet area)
df = pd.read_csv("magicbricks_bangalore.csv")
print(df.isnull().sum()) #Check which columns have null values, so we do selective deletions
df = df.dropna(subset=["Bedrooms(BHK)"])

    
print(df["Bedrooms(BHK)"].isna().sum()) 
print(df.shape)
 #modified dataframe to csv
df.to_csv("magicbricks_bangalore_final.csv", index=False, encoding="utf-8")
print("CSV file saved successfully")

print(df.isnull().sum())

