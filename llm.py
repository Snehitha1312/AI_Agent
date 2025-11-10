# llm.py
import os
import json
from typing import List
from prompts import SYSTEM_PROMPT, ANALYST_INSTRUCTIONS
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") 

USE_GROQ = bool(GROQ_API_KEY)

if USE_GROQ:
    try:
        from groq import Groq
        GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        _gcli = Groq(api_key=GROQ_API_KEY)
        # print(GROQ_API_KEY)
    except Exception as e:
        print(" Failed to import Groq client:", e)
        USE_GROQ = False

# ---------- Format RAG context ----------
def format_context(snippets: List[str]) -> str:
    if not snippets:
        return ""
    return "\n\n--- RAG CONTEXT ---\n" + "\n\n".join(snippets)


# ---------- Main LLM call ----------
def ask_llm(question: str, date_range_str: str, json_data: dict, rag_snippets: List[str]) -> str:
    """
    question: user input string
    date_range_str: formatted date range text (YYYY-MM-DD to YYYY-MM-DD)
    json_data: aggregated analytics dict to give LLM the numbers
    rag_snippets: retrieved docs from RAG store for grounding/format rules
    """

    # Build message passed to the LLM
    content = f"""{ANALYST_INSTRUCTIONS}

User Question:
{question}

Date Range:
{date_range_str}

Data (JSON):
```json
{json.dumps(json_data, ensure_ascii=False, indent=2)}
{format_context(rag_snippets)}
"""
    if USE_GROQ:
        try:
            resp = _gcli.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content}
                ],
                temperature=0.2,
            )

            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Groq API error: {e}"

    # ---------- Fallback ----------
    return (
        "⚠️ No LLM configured.\n"
        "Set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env to enable AI answers."
    )
