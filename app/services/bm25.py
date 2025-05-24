import json
from pathlib import Path
from rank_bm25 import BM25Okapi
from app.config import CORPUS_PATH
from threading import Lock

"""
Load a JSONL corpus file and initialize BM25 index.
Expected JSONL format: one JSON object per line with keys 'id', 'title', and 'text'.
"""

_lock = Lock()
_CORPUS = []
_TOKENIZED = []
_BM25 = None


def load_corpus():
    """Load documents from CORPUS_PATH into BM25 index."""
    global _CORPUS, _TOKENIZED, _BM25
    with _lock:
        _CORPUS.clear()
        _TOKENIZED.clear()
        jsonl_file = Path(CORPUS_PATH) / "corpus.jsonl"
        if jsonl_file.exists():
            # Load JSONL format
            with jsonl_file.open(encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    doc_id = obj.get("id")
                    title = obj.get("title", "")
                    text = obj.get("text", "")
                    content = f"{title} {text}".strip()
                    tokens = content.split()
                    _CORPUS.append({"id": doc_id, "text": content})
                    _TOKENIZED.append(tokens)
        else:
            # Load .txt files in directory
            dir_path = Path(CORPUS_PATH)
            for file in dir_path.glob("**/*.txt"):
                text = file.read_text(encoding="utf-8")
                tokens = text.split()
                _CORPUS.append({"id": file.stem, "text": text})
                _TOKENIZED.append(tokens)
        # Build BM25
        if _TOKENIZED:
            _BM25 = BM25Okapi(_TOKENIZED)
        else:
            _BM25 = None


def bm25_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Perform BM25 search over the loaded corpus.

    Parameters
    ----------
    query : str
        The search query string.
    top_k : int
        Number of top results to return.

    Returns
    -------
    List of {'id': str, 'score': float} ordered by descending score.
    """
    if _BM25 is None:
        return []
    tokenized_query = query.split()
    scores = _BM25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [
        {"id": _CORPUS[i]["id"], "score": float(scores[i])}
        for i in top_indices
    ]

# Initial load at module import
load_corpus()