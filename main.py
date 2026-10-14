from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from shopping_tools import load_catalogue
from workflow import run_shopping_assistant

app = FastAPI(title="Agentic AI E-Commerce Shopping Assistant", version="1.0.0")
cart: list[dict[str, Any]] = []


class ShoppingRequest(BaseModel):
    query: str = Field(..., examples=["Suggest a laptop under ₹60,000 with 16 GB RAM"])
    budget: int | None = Field(default=None, ge=1)
    min_ram: int | None = Field(default=None, ge=1)


class CartRequest(BaseModel):
    product_id: str


@app.get("/", tags=["Health"])
def home():
    return {"message": "Shopping assistant is running. Visit /docs to try the API."}


@app.get("/products", tags=["Products"])
def products():
    return load_catalogue()


@app.post("/shop", tags=["Shopping"])
def shop(request: ShoppingRequest):
    """Search, filter, compare, check stock, and recommend via LangGraph."""
    return run_shopping_assistant(request.query, request.budget, request.min_ram)


@app.post("/cart", tags=["Cart"])
def add_to_cart(request: CartRequest):
    product = next((item for item in load_catalogue() if item["id"] == request.product_id.upper()), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product["availability"] != "In stock":
        raise HTTPException(status_code=409, detail="Product is currently out of stock")
    if not any(item["id"] == product["id"] for item in cart):
        cart.append(product)
    return {"message": f"{product['name']} added to cart", "cart": cart}


@app.get("/cart", tags=["Cart"])
def view_cart():
    return {"items": cart, "total_inr": sum(item["price_inr"] for item in cart)}
