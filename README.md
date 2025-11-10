# Sales Insight Agent

A minimal Sales Insight Agent that accepts natural language sales questions, fetches order data from the sample Sales API, analyzes it, and answers using an LLM (OpenAI by default). Includes a CLI and optional FastAPI web endpoint.

## Features

- CLI for natural-language queries (Typer)
- Sales API integration with caching (SQLite)
- Date parsing for relative phrases: "yesterday", "last week", "this month"
- Local aggregations: best-selling items, sales trend by day
- LLM fallback for freeform questions (OpenAI example)
- Basic tests (pytest)

## Requirements

- Python 3.10+
- pip install -r requirements.txt

## Setup

1. Clone repo.
2. Copy `.env.example` to `.env` and fill `OPENAI_API_KEY`.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
## Setup

1. To run the application
   ```bash
   python app.py "Your Query"
   ```

## Screenshots

<img width="1220" height="330" alt="image" src="https://github.com/user-attachments/assets/b5cf4e7c-350e-4b46-b65b-dc57becb6c77" />


