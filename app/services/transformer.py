import threading
from pathlib import Path
import json
import numpy as np
import unicodedata
import re
from FlagEmbedding import BGEM3FlagModel
from app.config import CORPUS_PATH

_lock = threading.Lock()
_MODEL = None
_CORPUS: list[dict] = []
_CORPUS_EMBS: np.ndarray | None = None

def strip_accents(s: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

def normalize(text: str) -> str:
    return strip_accents(text.lower())

# helper to normalize tokens: strip accents, lowercase, and drop non‐letters
def normalize_token(tok: str) -> str:
    tok = strip_accents(tok.lower())
    return re.sub(r'[^a-zA-Z]', '', tok)

def load_transformer_corpus():
    """Load the BM25 corpus JSONL, extract texts, and embed them."""
    global _MODEL, _CORPUS, _CORPUS_EMBS
    with _lock:
        # Initialize model once
        if _MODEL is None:
            _MODEL = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

        # Load documents
        _CORPUS.clear()
        jsonl_file = Path(CORPUS_PATH) / "corpus.jsonl"
        with jsonl_file.open(encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
                doc_id = obj['id']
                title  = obj.get('title','')
                text   = obj.get('text','')
                full   = f"{title} {text}".strip()
                # normalize accents
                full_norm = normalize(full)

                _CORPUS.append({
                    "id": doc_id,
                    "title": title,
                    "text_norm": full_norm,
                    "text": full
                })                

        # Compute embeddings in batch
        texts = [doc["text_norm"] for doc in _CORPUS]
        res = _MODEL.encode(texts, batch_size=8, max_length=1024)
        _CORPUS_EMBS = np.vstack(res['dense_vecs']).astype('float32')

def transformer_search(query: str, top_k: int = 30) -> list[dict]:
    """Return top_k by dot-product similarity between query and corpus embeddings."""
    if _MODEL is None or _CORPUS_EMBS is None:
        load_transformer_corpus()

    q_norm = normalize(query)
    q_emb = _MODEL.encode([q_norm])['dense_vecs'][0]  # single embedding
    # compute similarity
    sims = _CORPUS_EMBS @ q_emb
    # sort by similarity, keep only top_k
    idxs = np.argsort(-sims)
    idxs = [i for i in idxs if sims[i] > 0][:top_k]

    results = []
    tokenized_query = [normalize_token(tok) for tok in q_norm.split()]
    for i in idxs:
        doc = _CORPUS[i]
        text = doc['text']

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
            "score": float(sims[i]),
            "snippet": snippet,
            "download_url": file_url,
        })

    return results

# eager load at import
# load_transformer_corpus()
