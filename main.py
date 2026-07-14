import csv
import json
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in the environment")

genai.configure(api_key=api_key)


# ---------------------------------------------------------
# AGENT TOOL / FUNCTION DEFINITION
# ---------------------------------------------------------
def calculate_order_total(item_name: str, quantity: int) -> str:
    """Calculates the total cost for a specific quantity of an inventory item."""
    try:
        # Search for the item in the loaded inventory dictionary (case-insensitive)
        for item in inventory:
            if item_name.lower() in item["product_name"].lower():
                total_cost = item["price_pln"] * quantity
                return f"The total cost for {quantity} units of '{item['product_name']}' is {total_cost} PLN."
        return f"Item not found in inventory: {item_name}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


# Define the model and equip it with the tool(s)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
model = genai.GenerativeModel(model_name=GEMINI_MODEL, tools=[calculate_order_total])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).parent / "static"
CSV_PATH = Path(__file__).parent / "inventory.csv"
inventory: list[dict] = []


class QueryRequest(BaseModel):
    question: str


def load_inventory() -> None:
    global inventory
    with CSV_PATH.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        inventory = [
            {
                "item_id": int(row["item_id"]),
                "product_name": row["product_name"],
                "category": row["category"],
                "stock_quantity": int(row["stock_quantity"]),
                "price_pln": float(row["price_pln"]),
            }
            for row in reader
        ]


def inventory_to_context() -> str:
    return json.dumps(inventory, indent=2)


@app.on_event("startup")
def startup_event() -> None:
    load_inventory()


@app.get("/")
def chat_ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api")
def welcome() -> dict[str, str]:
    return {"message": "Welcome to the Inventory API"}


@app.get("/items")
def get_items() -> list[dict]:
    return inventory


@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict:
    for item in inventory:
        if item["item_id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail=f"Item {item_id} not found")


@app.post("/ask")
def ask(request: QueryRequest) -> dict[str, str]:
    context = inventory_to_context()

    # Prompt the AI to act as a Procurement Assistant for Roche
    prompt = (
        "You are an AI Procurement Assistant for Roche. Use the following "
        "inventory data to answer the user's questions or calculate order costs.\n\n"
        f"Inventory data:\n{context}\n\n"
        f"User Question: {request.question}"
    )

    try:
        # start_chat with automatic function calling turns the LLM into an Agent
        chat = model.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(prompt)
        return {"answer": response.text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {exc}") from exc


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
