import os
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("MODE", "thesis")  # thesis or public

if MODE == "thesis":
    CORPUS_PATH = "data/static_corpus"
    ENABLE_TRANSFORMERS = True
else:
    CORPUS_PATH = "data/uploads"
    ENABLE_TRANSFORMERS = False