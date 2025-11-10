# rag.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple

# Simple embed using a deterministic bag-of-words fallback to avoid hard provider dependency.
# You can swap this with OpenAI embeddings for better quality.
def _tokenize(text: str) -> set[str]:
    return set([t.strip(".,:;()[]{}\"'").lower() for t in text.split() if t.strip()])

def _bow_vector(text: str, vocab: List[str]) -> np.ndarray:
    toks = _tokenize(text)
    return np.array([1.0 if v in toks else 0.0 for v in vocab], dtype=np.float32)

class TinyRAG:
    def __init__(self, docs: List[Tuple[str, str]]):
        """
        docs: List of (doc_id, text)
        """
        self.docs = docs
        self.vocab = sorted(list(set().union(*[_tokenize(t) for _, t in docs])))
        self.mat = np.vstack([_bow_vector(t, self.vocab) for _, t in docs])

    def retrieve(self, query: str, k: int = 4) -> List[Tuple[str, str, float]]:
        qv = _bow_vector(query, self.vocab).reshape(1, -1)
        sims = cosine_similarity(qv, self.mat)[0]
        idx = np.argsort(-sims)[:k]
        out = []
        for i in idx:
            doc_id, text = self.docs[i]
            out.append((doc_id, text, float(sims[i])))
        return out

def build_sales_docs() -> List[Tuple[str, str]]:
    text = []
    text.append(("endpoint",
    """Sales API Endpoint:
GET https://sandbox.mkonnekt.net/ch-portal/api/v1/orders/recent
No auth required. Returns recent orders.
"""))

    text.append(("key_fields",
    """Key Fields:
- total: integer cents (e.g., 906 == $9.06)
- state: "locked" (completed) or "open" (in progress) — use locked for sales
- createdTime: ISO8601 timestamp
- lineItems[].name: product name
- lineItems[].price: item price in cents
- lineItems[].itemCode: UPC
"""))

    text.append(("examples",
    """Example questions & outputs:
- "What were our best-selling items yesterday?"
- "Show me the sales trend for last week"
- "How much revenue did we make today?"
- "What’s the average order value this month?"
"""))

    text.append(("eval",
    """Evaluation:
- Accurate LLM responses
- Date/time handling
- Edge cases
- Good error messages
- Caching is a bonus
- Multi-turn is a bonus
"""))

    text.append(("money_rules",
    """Money Formatting Rules:
- Convert cents to dollars with 2 decimals.
- Summaries should show both units when useful, e.g., $12.34.
"""))

    return text
