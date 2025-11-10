# web_server.py
from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from app import handle_query

app = FastAPI()

class QRequest(BaseModel):
    q: str
    cache: bool = True
    top: int = 3

@app.post("/query")
async def query_endpoint(req: QRequest):
    # This re-uses the CLI handler but returns a string
    # For simplicity we will call the LLM directly here, but production code
    # should refactor common logic into a shared module that returns strings.
    # To keep this example concise, we run handle_query which prints to stdout;
    # a refactor is recommended for real web usage.
    await handle_query(req.q, req.cache, req.top)
    return {"status": "ok"}
