import json
from pathlib import Path
from rank_bm25 import BM25Okapi
from app.config import CORPUS_PATH
from threading import Lock
import unicodedata
import re

"""
Load a JSONL corpus file and initialize BM25 index.
Expected JSONL format: one JSON object per line with keys 'id', 'title', and 'text'.
"""

_lock = Lock()
_CORPUS = []
_TOKENIZED = []
_BM25 = None


# helper to strip accents
def strip_accents(s: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


# helper to normalize tokens: strip accents, lowercase, and drop non‐letters
def normalize_token(tok: str) -> str:
    tok = strip_accents(tok.lower())
    return re.sub(r'[^a-zA-Z]', '', tok)


def load_corpus():
    """Load documents from CORPUS_PATH into BM25 index."""
    print("Loading corpus and initializing BM25 index...")
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
                    tokens_norm = [normalize_token(w) for w in content.split()]

                    _CORPUS.append({"id": doc_id, "title": title, "text": content})
                    _TOKENIZED.append(tokens_norm)
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
        print("Done loading corpus and initializing BM25 index.")


def bm25_search(query: str, top_k: int = 30) -> list[dict]:
    """
    Perform BM25 search over the loaded corpus.

    Parameters
    ----------
    query : str
        The search query string.
    top_k : int
        Number of top results to return.

    Returns top_k results as list of dicts with:
      - id: document ID
      - score: BM25 score
      - snippet: first 100 words of the text
      - download_url: path under /files to fetch the original doc
    """
    if _BM25 is None:
        return []
    
    tokenized_query = [normalize_token(t) for t in query.split() if t]
    if not tokenized_query:
        print("Empty query after normalization, returning empty results.")
        return []
    print(f"Searching for query: {tokenized_query}")
    scores = _BM25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    top_indices = [i for i in top_indices if scores[i] > 0][:top_k]
    
    results = []
    for i in top_indices:
        doc = _CORPUS[i]
        text = doc["text"]

        # find first exact match of any query term and take 50-word window
        snippet = ""
        doc_tokens = text.split()
        for idx, orig_tok in enumerate(doc_tokens):
            if normalize_token(orig_tok) in tokenized_query:
                start = max(idx - 25, 0)
                snippet_tokens = doc_tokens[start : start + 50]
                snippet = " ".join(snippet_tokens)
                break
        
        if snippet == "":
            print(f"Warning: No snippet found for document ID {doc['id']}")
            
        # detect the actual file extension (pdf, html, docx, etc.)
        file_url = None
        for ext in (".pdf", ".PDF", ".htm", ".html", ".HTML", ".docx", ".doc", ".txt"):
            candidate = Path(CORPUS_PATH) / "files" / f"{doc['id']}{ext}"
            if candidate.exists():
                file_url = f"/files/{candidate.name}"
                break
        if file_url is None:
            print(f"Warning: No file found for document ID {doc['id']}")

        results.append({
            "id": doc["id"],
            "title": doc["title"],
            "score": float(scores[i]),
            "snippet": snippet,
            "download_url": file_url,
        })
    return results

# Initial load at module import
load_corpus()