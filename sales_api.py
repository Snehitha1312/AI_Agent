from datetime import timezone
import os, json, hashlib
from datetime import datetime
from typing import List
import httpx
from schemas import Order
from dateutil import parser as dtparser

CACHE_DIR = os.getenv("CACHE_DIR", ".cache")
API_URL   = os.getenv("SALES_API_URL", "https://sandbox.mkonnekt.net/ch-portal/api/v1/orders/recent")

def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_path(key: str) -> str:
    _ensure_cache_dir()
    digest = hashlib.sha256(key.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{digest}.json")

# sales_api.py
async def fetch_recent_orders(force_refresh: bool = False):
    key = f"{API_URL}"
    path = _cache_path(key)

    if not force_refresh and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(API_URL)
            resp.raise_for_status()
            data = resp.json()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    # ✅ extract list
    orders_raw = data.get("orders", [])

    orders = []
    for row in orders_raw:
        row["createdTime"] = dtparser.isoparse(row["createdTime"])
        if row.get("modifiedTime"):
            row["modifiedTime"] = dtparser.isoparse(row["modifiedTime"])

        for li in row.get("lineItems", []):
            if li.get("createdTime"):
                li["createdTime"] = dtparser.isoparse(li["createdTime"])

        orders.append(Order(**row))

    return orders


def filter_orders_by_range(orders: List[Order], start_dt, end_dt):
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)

    results = []
    for o in orders:
        ct = o.createdTime

        # ✅ normalize order timestamp too
        if ct.tzinfo is None:
            ct = ct.replace(tzinfo=timezone.utc)

        if start_dt <= ct <= end_dt:
            results.append(o)

    return results


def cents_to_dollars(cents: int | None) -> float:
    return round((cents or 0) / 100.0, 2)
