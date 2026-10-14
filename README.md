# Agentic AI E-Commerce Shopping Assistant

A small FastAPI application that uses Python tools and a lightweight LangGraph workflow to search a local laptop catalogue, filter products, compare options, verify availability, recommend the best value, and manage a simulated cart.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs` to use the interactive API documentation.

## Example request

`POST /shop`

```json
{
  "query": "Suggest a laptop under ₹60,000 with 16 GB RAM"
}
```

The response compares matching in-stock laptops and recommends Laptop A because it meets the criteria at the lowest price.

## Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/products` | View the local laptop catalogue |
| POST | `/shop` | Run the LangGraph shopping workflow |
| POST | `/cart` | Add an in-stock product by `product_id` |
| GET | `/cart` | View the simulated cart and total |

To add a recommended product:

```json
POST /cart
{ "product_id": "LAP001" }
```
To run the project
1. pip install -r requirements.txt
2. uvicorn main:app --reload
3. eg:- Open http://127.0.0.1:8000/docs
        Open POST /shop
        Click Try it out
        Use:{
              "query": "Suggest a laptop under ₹60,000 with 16 GB RAM"
            }
