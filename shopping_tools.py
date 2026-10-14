"""Small, reusable catalogue tools used by the LangGraph workflow."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

CATALOGUE_PATH = Path(__file__).parent / "data" / "products.csv"


def load_catalogue() -> list[dict[str, Any]]:
    """Load and type-convert the local product catalogue."""
    with CATALOGUE_PATH.open(encoding="utf-8", newline="") as file:
        products = list(csv.DictReader(file))
    for product in products:
        for field in ("price_inr", "ram_gb", "battery_hours", "storage_gb"):
            product[field] = int(product[field])
    return products


def search_laptops(products: list[dict[str, Any]], query: str = "") -> list[dict[str, Any]]:
    """Search names, brands, processors, and storage in the in-memory catalogue."""
    words = [word.lower() for word in query.split() if word.lower() not in {"laptop", "laptops"}]
    if not words:
        return products
    return [
        product
        for product in products
        if any(word in " ".join(map(str, product.values())).lower() for word in words)
    ]


def filter_by_requirements(
    products: list[dict[str, Any]], budget: int | None, min_ram: int | None
) -> list[dict[str, Any]]:
    """Keep products within budget and with at least the requested RAM."""
    return [
        product
        for product in products
        if (budget is None or product["price_inr"] <= budget)
        and (min_ram is None or product["ram_gb"] >= min_ram)
    ]


def check_availability(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only products available for purchase."""
    return [product for product in products if product["availability"].lower() == "in stock"]


def recommend_best(products: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Choose best value: lowest price, then more RAM and battery life."""
    if not products:
        return None
    return min(products, key=lambda item: (item["price_inr"], -item["ram_gb"], -item["battery_hours"]))


def comparison_rows(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create a compact comparison for the customer-facing response."""
    return [
        {
            "id": product["id"],
            "laptop": product["name"],
            "price": f"₹{product['price_inr']:,}",
            "ram": f"{product['ram_gb']} GB",
            "battery_life": f"{product['battery_hours']} hours",
            "availability": product["availability"],
        }
        for product in products
    ]
