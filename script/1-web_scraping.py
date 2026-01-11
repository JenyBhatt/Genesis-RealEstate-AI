import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

title_csv = []
prices_csv = []
super_area_csv = []
carpet_area_csv = []
bathroom_csv = []
bedroom_csv = []
location_csv = []


for j in range (1,20):

 webpage_main = requests.get("https://www.magicbricks.com/property-for-sale/residential-real-estate?cityName=Bangalore&page={}".format(j),headers = headers).text
 soup = BeautifulSoup(webpage_main,'lxml')

 cards = soup.find_all("div", class_="mb-srp__card")

 
 for card in cards:
    
    title = card.find("h2", class_="mb-srp__card--title")
    price = card.find("div", class_="mb-srp__card__price--amount")
    
    super_block = card.find("div",attrs={"data-summary": "super-area"})
    super_area = super_block.find("div", class_="mb-srp__card__summary--value") if super_block else ""
    
    carpet_block = card.find("div",attrs={"data-summary": "carpet-area"})
    carpet_area = carpet_block.find("div", class_="mb-srp__card__summary--value") if carpet_block else ""
    
    bathroom_block = card.find("div",attrs={"data-summary": "bathroom"})
    bathroom = bathroom_block.find("div",class_="mb-srp__card__summary--value") if bathroom_block else ""
          
    bedrooms = ""
    if "BHK" in title.text:  #get the vlue directly from the title
            bedrooms = title.text.strip().split("BHK")[0].strip() 
            
    location = ""

    if title:
            if " in " in title.text:
              location = title.text.strip().split(" in ", 1)[1]


    
    title_csv.append(title.text.strip() if title else "")
    prices_csv.append(price.text.strip() if price else "")
    super_area_csv.append(super_area.text.strip() if super_area else "")
    carpet_area_csv.append(carpet_area.text.strip() if carpet_area else "")
    bathroom_csv.append(bathroom.text.strip() if bathroom else "")
    bedroom_csv.append(bedrooms) #coz default "" laready set above
    location_csv.append(location)
    
    #dataframe
    
df = pd.DataFrame({
    "Title": title_csv,
    "Location": location_csv,
    "Price": prices_csv,
    "Bedrooms(BHK)": bedroom_csv,
    "Bathrooms": bathroom_csv,
    "Super Area": super_area_csv,
    "Carpet Area": carpet_area_csv
})
    
df.to_csv("magicbricks_bangalore.csv", index=False, encoding="utf-8")
print("CSV file saved successfully")


    
#print(df.head())
#print(df.shape)
#print(df.isnull().sum())

    
    

