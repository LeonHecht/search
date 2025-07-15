# Legal Search App

This repository contains a small search system for legal documents built with **FastAPI** and a **React** front‑end. It indexes a corpus of 5,000 Paraguayan Supreme Court cases and lets users search either by BM25 keyword matching or by semantic transformer embeddings.

## Features

- **Exact (BM25) and Semantic search** over a corpus in `data/static_corpus`.
- **FastAPI** backend exposing `/search`, `/feedback`, `/upload` and `/ping` endpoints.
- **React** + **Tailwind CSS** front‑end under `frontend/`.
- Search queries and feedback are stored in `queries.db` (SQLite).
- Optional upload of new JSONL/TXT corpora when running in public mode.

## Requirements

- Python 3.10+
- Node 18+ for the front‑end
- See `requirements.txt` for Python dependencies.

## Configuration

The application uses two environment variables:

- `MODE` – `thesis` (default corpus with transformer search) or `public` (uploads only, transformer disabled).
- `ENV` – `dev` (local GeoIP databases) or `prod` (system path GeoIP databases).

Example `.env` file:

```env
MODE=thesis
ENV=dev
```

## Running

1. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```bash
   python run.py
   ```
3. In another terminal run the front‑end:
   ```bash
   cd frontend
   npm install
   npm start
   ```
   The web interface will be available on <http://localhost:5173> by default.

## Corpus format

Documents are stored in JSON Lines format with fields `id`, `title` and `text`. An example line from `data/static_corpus/corpus.jsonl`:
```json
{"id":"38949","title":"RECURSO EXTRAORDINARIO DE CASACIÓN INTERPUESTO POR EL SR. HANS FRIEDICH SCHUCHARDT..."}
```

Uploaded files are kept in `data/uploads/` and will trigger a BM25 index rebuild.

## License

This project is licensed under the Apache 2.0 License. See `LICENSE.txt` for details.
