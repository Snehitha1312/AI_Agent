# utils.py
from datetime import datetime, timedelta, timezone
import dateparser
from typing import Tuple, List, Dict, Any
import math

def parse_natural_date_range(text: str, reference: datetime=None) -> Tuple[datetime, datetime]:
    """
    Return (start, end) as naive UTC datetimes for a parsed natural-language range.
    Example: "yesterday", "last week", "this month", "2025-11-03".
    """
    ref = reference or datetime.now(timezone.utc)
    t = text.strip().lower()
    if t in ("yesterday",):
        day = (ref - timedelta(days=1)).date()
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        return start, end
    if t in ("today",):
        day = ref.date()
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)
        return start, end
    if t == "last week":
        # ISO week ranges: last full Monday-Sunday
        # find previous week's Monday
        ref_date = (ref - timedelta(days=7)).date()
        monday = ref_date - timedelta(days=ref_date.weekday())
        start = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)
        end = start + timedelta(days=7)
        return start, end
    if t == "this month":
        first = datetime(ref.year, ref.month, 1, tzinfo=timezone.utc)
        # next month:
        if ref.month == 12:
            nm = datetime(ref.year+1, 1, 1, tzinfo=timezone.utc)
        else:
            nm = datetime(ref.year, ref.month+1, 1, tzinfo=timezone.utc)
        return first, nm

    # fallback to dateparser for single date or range
    parsed = dateparser.parse(text, settings={"RETURN_AS_TIMEZONE_AWARE": True})
    if parsed:
        # return single-day span if it's a single date
        start = parsed.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return start, end

    raise ValueError(f"Could not parse date expression: {text}")

def iso_to_datetime(s: str):
    # handle ISO with/without timezone
    return dateparser.parse(s).astimezone(timezone.utc)

def filter_orders_by_range(orders: List[Dict[str,Any]], start: datetime, end: datetime):
    out = []
    for o in orders:
        try:
            ct = iso_to_datetime(o.get("createdTime"))
            if ct >= start and ct < end and o.get("state") == "locked":
                out.append(o)
        except Exception:
            continue
    return out

def cents_to_dollars(cents: int) -> float:
    return round(cents / 100.0, 2)

def aggregate_best_selling_items(orders: List[Dict[str,Any]], top_n: int=5):
    counts = {}
    revenue = {}
    for o in orders:
        for li in o.get("lineItems", []):
            name = li.get("name") or "Unknown"
            qty = li.get("unitQty") or 1
            price = li.get("price", 0)
            counts[name] = counts.get(name, 0) + (qty if isinstance(qty, int) else 1)
            revenue[name] = revenue.get(name, 0) + price * (qty if isinstance(qty, int) else 1)
    sorted_items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    results = []
    for name, cnt in sorted_items[:top_n]:
        results.append({
            "name": name,
            "sold": int(cnt),
            "revenue_cents": int(revenue.get(name, 0)),
            "revenue_dollars": cents_to_dollars(int(revenue.get(name,0)))
        })
    return results

def sales_trend_by_day(orders: List[Dict[str,Any]]):
    # group by date (UTC date)
    daily = {}
    for o in orders:
        dt = iso_to_datetime(o.get("createdTime"))
        key = dt.date().isoformat()
        daily.setdefault(key, {"revenue_cents": 0, "orders": 0})
        daily[key]["revenue_cents"] += int(o.get("total", 0))
        daily[key]["orders"] += 1
    # return ordered by date
    keys = sorted(daily.keys())
    return [{"date": k, "revenue_dollars": cents_to_dollars(daily[k]["revenue_cents"]), "orders": daily[k]["orders"]} for k in keys]
