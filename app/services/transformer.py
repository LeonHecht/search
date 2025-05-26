# app/services/transformer.py

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
_CORPUS_TEXTS = []
_CORPUS_IDS = []
_CORPUS_EMBS = None

def strip_accents(s: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

def normalize(text: str) -> str:
    return strip_accents(text.lower())

def load_transformer_corpus():
    """Load the BM25 corpus JSONL, extract texts, and embed them."""
    global _MODEL, _CORPUS_TEXTS, _CORPUS_IDS, _CORPUS_EMBS
    with _lock:
        # Initialize model once
        if _MODEL is None:
            _MODEL = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True)

        # Load documents
        _CORPUS_TEXTS.clear()
        _CORPUS_IDS.clear()
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
                _CORPUS_TEXTS.append(full_norm)
                _CORPUS_IDS.append(doc_id)

        # Compute embeddings in batch
        res = _MODEL.encode(_CORPUS_TEXTS, batch_size=8, max_length=1024)
        _CORPUS_EMBS = res['dense_vecs']

def transformer_search(query: str, top_k: int = 10) -> list[dict]:
    """Return top_k by dot-product similarity between query and corpus embeddings."""
    if _MODEL is None or _CORPUS_EMBS is None:
        load_transformer_corpus()

    q_norm = normalize(query)
    q_emb = _MODEL.encode([q_norm])['dense_vecs'][0]  # single embedding
    # compute similarity
    sims = np.dot(_CORPUS_EMBS, q_emb)
    # pick top_k indices
    idxs = np.argsort(-sims)[:top_k]
    return [
        {"id": _CORPUS_IDS[i], "score": float(sims[i])}
        for i in idxs
    ]

# eager load at import
load_transformer_corpus()
