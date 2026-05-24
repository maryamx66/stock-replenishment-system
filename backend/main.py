from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import json
from typing import List
# Import the AI engine
from ai_engine import evaluate_inventory, review_basket_compliance
import json

class BasketItem(BaseModel):
    sku: str
    name: str
    quantity: int
    unit_price: str

class BasketRequest(BaseModel):
    basket: List[BasketItem]

app = FastAPI(title="Stock Replenishment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOG_PATH = "grocery-data/cleaned_catalog.csv"
SALES_PATH = "grocery-data/historical_sales.csv"

class StockEvaluationRequest(BaseModel):
    sku: str

@app.get("/api/inventory/low-stock")
def get_low_stock():
    df = pd.read_csv(CATALOG_PATH)
    
    if 'Sales_Volume' in df.columns:
        df = df.drop(columns=['Sales_Volume'])
        
    low_stock_df = df[df['Stock_Quantity'] < df['Reorder_Level']]
    
    items = []
    for _, row in low_stock_df.iterrows():
        items.append({
            "sku": str(row['Product_ID']),
            "name": str(row['Product_Name']),
            "category": str(row["Category"]),
            "supplier_name": str(row["Supplier_Name"]),
            "current_stock": int(row['Stock_Quantity']),
            "threshold": int(row['Reorder_Level']),
            "unit_price": str(row["Unit_Price"])
        })
        
    return {"items": items}

@app.post("/api/evaluate-stock")
def evaluate_stock(request: StockEvaluationRequest):
    catalog_df = pd.read_csv(CATALOG_PATH)
    sales_df = pd.read_csv(SALES_PATH)
    
    item_data = catalog_df[catalog_df['Product_ID'] == request.sku]
    item_sales = sales_df[sales_df['Product_ID'] == request.sku]
    
    if item_data.empty:
        return {"error": "Item not found in catalog"}
        
    item_dict = item_data.drop(columns=['Sales_Volume'], errors='ignore').to_dict('records')[0]
    sales_list = item_sales.to_dict('records')
    
    # Trigger the Multi-Agent Crew
    ai_output = evaluate_inventory(item_dict, sales_list)
    
    # Parse the LLM's JSON response (with a safety fallback)
    try:
        result_data = json.loads(str(ai_output))
        suggested_qty = result_data.get("suggested_order_quantity", 0)
        reasoning = result_data.get("reasoning_log", "No reasoning provided.")
    except json.JSONDecodeError:
        suggested_qty = 0
        reasoning = str(ai_output)
    
    return {
        "sku": request.sku,
        "suggested_order_quantity": suggested_qty,
        "reasoning_log": reasoning,
        "policy_referenced": "Base Financial Policy"
    }

@app.post("/api/evaluate-basket")
async def evaluate_basket(request: BasketRequest):
    # Convert the Pydantic model to a list of dictionaries for the AI
    basket_data = [item.model_dump() for item in request.basket] # Using model_dump() for Pydantic v2
    
    # Run the AI manager review
    result = review_basket_compliance(basket_data)
    final_result = json.loads(result.raw)
    
    """
    result = {
      updated_basket: [],
      reasoning_log: ""
    }
    """
    return {"result": final_result}

