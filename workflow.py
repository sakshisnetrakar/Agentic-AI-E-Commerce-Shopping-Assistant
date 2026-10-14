"""A lightweight LangGraph workflow coordinating shopping tools."""

from __future__ import annotations

import re
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from shopping_tools import (
    check_availability,
    comparison_rows,
    filter_by_requirements,
    load_catalogue,
    recommend_best,
    search_laptops,
)


class ShoppingState(TypedDict, total=False):
    query: str
    budget: int | None
    min_ram: int | None
    catalogue: list[dict[str, Any]]
    candidates: list[dict[str, Any]]
    available: list[dict[str, Any]]
    recommendation: dict[str, Any] | None


def parse_requirements(state: ShoppingState) -> ShoppingState:
    """Extract a rupee budget and minimum RAM from natural language when omitted."""
    query = state["query"]
    budget = state.get("budget")
    min_ram = state.get("min_ram")
    if budget is None:
        budget_match = re.search(r"(?:under|below|within|less than)\s*(?:₹|rs\.?|inr)?\s*([\d,]+)", query, re.I)
        if budget_match:
            budget = int(budget_match.group(1).replace(",", ""))
    if min_ram is None:
        ram_match = re.search(r"(\d+)\s*(?:gb)?\s*ram", query, re.I)
        if ram_match:
            min_ram = int(ram_match.group(1))
    return {"budget": budget, "min_ram": min_ram}


def find_products(state: ShoppingState) -> ShoppingState:
    catalogue = load_catalogue()
    return {"catalogue": catalogue, "candidates": search_laptops(catalogue, state["query"])}


def apply_filters(state: ShoppingState) -> ShoppingState:
    return {"candidates": filter_by_requirements(state["candidates"], state.get("budget"), state.get("min_ram"))}


def verify_stock(state: ShoppingState) -> ShoppingState:
    return {"available": check_availability(state["candidates"])}


def choose_recommendation(state: ShoppingState) -> ShoppingState:
    return {"recommendation": recommend_best(state["available"])}


def build_workflow():
    graph = StateGraph(ShoppingState)
    graph.add_node("parse_requirements", parse_requirements)
    graph.add_node("search_catalogue", find_products)
    graph.add_node("filter_products", apply_filters)
    graph.add_node("check_availability", verify_stock)
    graph.add_node("recommend_product", choose_recommendation)
    graph.add_edge(START, "parse_requirements")
    graph.add_edge("parse_requirements", "search_catalogue")
    graph.add_edge("search_catalogue", "filter_products")
    graph.add_edge("filter_products", "check_availability")
    graph.add_edge("check_availability", "recommend_product")
    graph.add_edge("recommend_product", END)
    return graph.compile()


shopping_workflow = build_workflow()


def run_shopping_assistant(query: str, budget: int | None = None, min_ram: int | None = None) -> dict[str, Any]:
    """Execute the graph and format its result for the API."""
    result = shopping_workflow.invoke({"query": query, "budget": budget, "min_ram": min_ram})
    recommended = result.get("recommendation")
    explanation = "No in-stock laptop matches those requirements. Try increasing your budget or reducing the RAM requirement."
    if recommended:
        explanation = (
            f"{recommended['name']} is recommended because it meets your requirements, is in stock, "
            f"and costs the least among matching products."
        )
    return {
        "query": query,
        "parsed_requirements": {"budget_inr": result.get("budget"), "minimum_ram_gb": result.get("min_ram")},
        "products": comparison_rows(result.get("available", [])),
        "recommendation": recommended,
        "reason": explanation,
    }
