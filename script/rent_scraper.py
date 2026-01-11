import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

base_url = "https://www.magicbricks.com/property-for-rent/residential-real-estate?bedroom=&proptype=Multistorey-Apartment,Builder-Floor-Apartment,Penthouse,Studio-Apartment,Service-Apartment&cityName=Bangalore"

headers = {
    "User-Agent": "Mozilla/5.0"
}

rent_listings = []

def clean_rent(text):
    if not text:
        return None
#
    text = str(text).lower().replace("₹", "").replace(",", "").strip()

    if "cr" in text:
        return int(float(text.replace("cr", "").strip()) * 10_000_000)
    if "lac" in text or "lakh" in text:
        return int(float(text.replace("lac", "").replace("lakh", "").strip()) * 100_000)
#

    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else None

for page in range(1, 10):
    print(f"[+] Scraping page {page}")

    response = requests.get(base_url, headers=headers, params={"page": page})
    soup = BeautifulSoup(response.text, "html.parser")

   

    cards = soup.find_all("div", class_="mb-srp__card")  #list_container

    for card in cards:
        try:
            # RENT
            rent_tag = card.find("div", class_="mb-srp__card__price--amount")
            rent = clean_rent(rent_tag.text if rent_tag else " ,")

            # TITLE
            title_tag = card.find("h2", class_="mb-srp__card--title")
            title_text = title_tag.text.strip() if title_tag else " ,"

            # BHK
            bhk = None
            bhk_match = re.search(r"(\d+)\s*BHK", title_text)
            if bhk_match:
                bhk = int(bhk_match.group(1))

            # LOCATION
            location = None
            if " in " in title_text:
                location = title_text.split(" in ", 1)[1]

            rent_listings.append({
                "rent": rent,
                "bhk": bhk,
                "location": location,
                "decision": "rent"
            })

        except Exception as e:
            print("Error:", e)

    time.sleep(1)

df_rent = pd.DataFrame(rent_listings)
df_rent.to_csv("magicbricks_bangalore_rent.csv", index=False)
print("✔ Rent CSV saved")
