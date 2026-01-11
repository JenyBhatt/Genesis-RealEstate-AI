import os
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from google import genai
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import re


# 1. CONFIGURATION
GOOGLE_API_KEY = "Your-API-key"

client = genai.Client(api_key=GOOGLE_API_KEY)
# model used to generate responses
MODEL_NAME = 'gemini-3-flash-preview'

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. DATA LOADING 
try:
    df = pd.read_csv("metadata.csv")
    
    # Check if the clean column exists
    if 'price_value' in df.columns:
        # to numeric
        df['price_value'] = pd.to_numeric(df['price_value'], errors='coerce').fillna(0)
        print(" Database loaded successfully.")
        print(f"   Sample Data: {df[['location', 'price_value']].iloc[0].to_dict()}")
    else:
        print(" ERROR: 'price_value' column missing.")
        df['price_value'] = 0

except Exception as e:
    print(f"CSV Error: {e}")
    df = pd.DataFrame()

# 3. ENDPOINTS
class FilterRequest(BaseModel):
    locations: List[str]
    min_price: float
    max_price: float
    decision_type: str 

class ChatRequest(BaseModel):
    query: str

@app.post("/filter")
def filter_properties(req: FilterRequest):
    if df.empty: return []
    
    print(f"🔍 Filter: {req.locations} | ₹{req.min_price} - ₹{req.max_price}")
    
    temp_df = df.copy()
    
    # 1. Location Filter
    if req.locations:
        pattern = '|'.join([re.escape(loc) for loc in req.locations])
        temp_df = temp_df[temp_df['location'].astype(str).str.contains(pattern, case=False, na=False)]
    
    # 2. Price Filter (Direct Comparison)
    temp_df = temp_df[
        (temp_df['price_value'] >= req.min_price) & 
        (temp_df['price_value'] <= req.max_price)
    ]
        
    # 3. Decision Filter
    if req.decision_type != "All" and 'decision' in temp_df.columns:
        temp_df = temp_df[temp_df['decision'].str.upper() == req.decision_type.upper()]

    print(f"   ✅ Found {len(temp_df)} properties.")
    # Return specific columns for the UI
    return temp_df[['title', 'location', 'price_raw', 'monthly_emi', 'decision']].head(50).fillna("").to_dict(orient="records")


from difflib import get_close_matches

@app.post("/chat")
def chat_agent(req: ChatRequest):
    try:
        user_query = req.query.lower()
        
        # SMART SEARCH LOGIC
        relevant_info = "No specific property data found in the database."
        
        if not df.empty and 'location' in df.columns:
            # 1. Clean the database locations for searching
            # Create a list of all locations from the CSV
            all_locations = df['location'].astype(str).tolist()
            
            # 2. Try to find the best match for words in the user's query
            # We check if any significant part of the query matches a location
            best_match = None
            
            # Simple keyword scan: Check if any CSV location substring is in the query
            # OR if the query substring is in the CSV location
            for loc in all_locations:
                clean_loc = loc.lower()
                # Check intersection of words
                if clean_loc in user_query or user_query in clean_loc:
                    best_match = loc
                    break
                
                # If still no match, try checking specific property names if they exist
                if 'title' in df.columns:
                     for title in df['title'].astype(str):
                         if title.lower() in user_query:
                             best_match = loc
                             break
            
            # 3. If a match is found, retrieve data
            if best_match:
                # Get the row corresponding to the matched location
                row = df[df['location'] == best_match].iloc[0]
                
                price = row.get('price_raw', row.get('price', 'N/A'))
                emi = row.get('monthly_emi', 'N/A')
                decision = row.get('decision', 'N/A')
                location_name = row.get('location', 'this area')
                
                relevant_info = (
                    f"DATA FOUND: The property at {location_name} is listed at {price}. "
                    f"Estimated Monthly EMI: ₹{emi}. "
                    f"AI Investment Verdict: {decision}."
                )

        # Construct the Prompt
        prompt = f"""
        You are 'Genesis', an expert Real Estate Investment Advisor.
        
        USER QUESTION: "{req.query}"
        
        DATABASE FACTS:
        {relevant_info}
        
        INSTRUCTIONS:
        1. If 'DATA FOUND' is above, you MUST use those exact numbers in your answer. 
        2. Explain *why* the verdict ({decision} if available) makes sense.
        3. If no data is found, give general market advice for Bangalore.
        4. Keep it professional and concise.
        """
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        
        return {
            "answer": response.text,
            "properties_found": [],
            "chart_base64": None
        }

    except Exception as e:
        print(f" AI Error: {e}")
        return {
            "answer": "My database connection flickered. Please try asking about 'Whitefield' or 'Hebbal' directly.",
            "properties_found": [],
            "chart_base64": None
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
