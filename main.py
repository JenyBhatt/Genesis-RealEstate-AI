import pandas as pd
import json
import io
import base64
import matplotlib
matplotlib.use('Agg') # Prevents GUI errors
import matplotlib.pyplot as plt
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================

app = FastAPI(
    title="Real Estate RAG Agent",
    description="A deterministic RAG agent for real estate analysis."
)

# REPLACE THIS with your actual OpenAI API Key
client = OpenAI(api_key="YOUR-API-KEY") 

# Load the Database
# Load the Database
try:
    # 1. Try loading from the 'data' folder first (Best Practice)
    df = pd.read_csv("metadata.csv")
    print("Database loaded successfully from data/metadata.csv")

except FileNotFoundError:
    # 3. If that fails too, print the error
    print("CRITICAL ERROR: Could not find 'metadata.csv' in 'data/' or root folder.")
    print("Please check: Is the file named 'magicbricks_bangalore.csv' instead?")
    df = pd.DataFrame()
# ==========================================
# 2. DATA MODELS
# ==========================================

class UserRequest(BaseModel):
    query: str

class AgentResponse(BaseModel):
    answer: str
    chart_base64: str | None = None
    properties_found: list | None = None

class FilterRequest(BaseModel):
    locations: list[str] = []
    min_price: float = 0
    max_price: float = 1000000000
    decision_type: str = "All"

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================

def get_search_params(user_query: str):
    system_prompt = """
    Return a VALID JSON object ONLY.
    Fields: "intent" (FILTER/EXPLAIN), "location" (string/null), "max_price" (number/null).
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {}

def generate_plot(property_row):
    try:
        fig, ax = plt.subplots(figsize=(6, 4))
        costs = [property_row['final_buying_cost'], property_row['final_renting_cost']]
        labels = ['Total Buying (20Y)', 'Total Renting (20Y)']
        colors = ['#ff9999', '#66b3ff']
        
        ax.bar(labels, costs, color=colors)
        ax.set_ylabel('Total Cost (INR)')
        ax.set_title(f"Wealth Projection: {property_row['title'][:20]}...")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x/10000000:.1f}Cr'))
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_str
    except Exception:
        return None

# ==========================================
# 4. API ENDPOINTS
# ==========================================

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: UserRequest):
    # A. Agentic Search
    params = get_search_params(request.query)
    loc = params.get('location')
    
    # B. Deterministic Retrieval
    if loc:
        results = df[df['location'].str.contains(loc, case=False, na=False)]
    else:
        results = df.head(5) 

    if results.empty:
        return AgentResponse(answer=f"I couldn't find properties in '{loc}'.")

    # C. AI Generation
    top_property = results.iloc[0]
    context_text = ""
    for _, p in results.head(3).iterrows():
        context_text += f"Property: {p['title']}, Price: {p['price_raw']}, Decision: {p['decision']}\n"

    llm_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Real Estate Expert. Explain using only the data provided."},
            {"role": "user", "content": f"Context: {context_text}\n\nQuestion: {request.query}"}
        ]
    )
    
    # chat endpoint
    results_safe = results.fillna(0)
    table_data = results_safe.head(5)[['title', 'location', 'price_raw', 'monthly_emi', 'decision']].to_dict(orient='records')

    return AgentResponse(
        answer=llm_response.choices[0].message.content,
        chart_base64=generate_plot(top_property),
        properties_found=table_data
    )

@app.post("/filter")
async def filter_endpoint(req: FilterRequest):
    filtered = df.copy()
    
    # 1. Location Filter
    if req.locations:
        pattern = '|'.join(req.locations)
        filtered = filtered[filtered['location'].str.contains(pattern, case=False, na=False)]
        
    # 2. Price Filter
    filtered = filtered[(filtered['price_value'] >= req.min_price) & (filtered['price_value'] <= req.max_price)]
    
    # 3. Strategy Filter
    if req.decision_type != "All":
        filtered = filtered[filtered['decision'].str.lower() == req.decision_type.lower()]
    
    
    # Replace NaN (Not a Number) and Infinity with 0 so JSON doesn't crash
    filtered = filtered.fillna(0)
    
    return filtered.head(50).to_dict(orient='records')

# To Run: uvicorn main:app --reload
