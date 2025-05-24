from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from app.config import CORPUS_PATH, ENABLE_TRANSFORMERS
from app.services.bm25 import load_corpus

router = APIRouter()

@router.post("/upload")
def upload_files(files: list[UploadFile] = File(...)):
    """
    Upload a JSONL corpus or multiple TXT files. Only allowed in public mode.
    After upload, rebuild BM25 index.
    """
    if ENABLE_TRANSFORMERS:
        raise HTTPException(status_code=403, detail="Upload not allowed in thesis mode")

    upload_dir = Path(CORPUS_PATH)
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    for file in files:
        filename = file.filename
        dest = upload_dir / filename
        with open(dest, "wb") as f:
            f.write(file.file.read())
        saved.append(filename)

    # Reload BM25 with updated corpus
    load_corpus()
    return {"uploaded_files": saved, "detail": "Corpus updated and BM25 indexed."}