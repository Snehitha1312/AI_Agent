# app.py
import os, asyncio, json, typer
from date_utils import parse_natural_date_range
from sales_api import fetch_recent_orders, filter_orders_by_range, cents_to_dollars
from rag import TinyRAG, build_sales_docs
from llm import ask_llm

app = typer.Typer(help="Sales Insight Agent")

@app.command()
def query(question: str):
    """
    Ask: python app.py "What were our best selling items yesterday?"
    No -t needed. Time is extracted from sentence.
    """

    # detect time phrase from the question
    # If none found → default last 7 days
    start_dt, end_dt = parse_natural_date_range(question)
    date_range_str = f"{start_dt.date().isoformat()} to {end_dt.date().isoformat()}"

    orders = asyncio.run(fetch_recent_orders())
    scoped = filter_orders_by_range(orders, start_dt, end_dt)

    # aggregate
    from collections import defaultdict
    revenue_total = 0
    orders_count = 0
    item_counts = defaultdict(int)
    item_revenue = defaultdict(int)
    daily = defaultdict(lambda: {"revenue":0, "orders":0})

    for o in scoped:
        revenue_total += (o.total or 0)
        orders_count += 1
        day = o.createdTime.date().isoformat()
        daily[day]["revenue"] += (o.total or 0)
        daily[day]["orders"] += 1
        for li in o.lineItems:
            if li.name:
                item_counts[li.name] += 1
                item_revenue[li.name] += (li.price or 0)

    # prepare data for LLM
    aov = int(revenue_total / orders_count) if orders_count else 0
    payload = {
        "date_range": date_range_str,
        "order_count": orders_count,
        "revenue_total_cents": revenue_total,
        "revenue_total_dollars": cents_to_dollars(revenue_total),
        "average_order_value_cents": aov,
        "average_order_value_dollars": cents_to_dollars(aov),
        "top_items_by_units": sorted(item_counts.items(), key=lambda x: -x[1])[:10],
        "top_items_by_revenue_cents": sorted(item_revenue.items(), key=lambda x: -x[1])[:10],
        "daily": daily
    }

    # RAG context
    rag = TinyRAG(build_sales_docs())
    rag_snippets = [text for _, text, _ in rag.retrieve(question, k=4)]

    answer = ask_llm(question, date_range_str, payload, rag_snippets)
    typer.echo(answer)


if __name__ == "__main__":
    app()
