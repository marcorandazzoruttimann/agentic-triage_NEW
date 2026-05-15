import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Caricamento ambiente
load_dotenv()

# 2. Riferimento alla radice del progetto
# __file__ è config.py, .parent è la cartella dove risiede
BASE_DIR = Path(__file__).resolve().parents[2]

# 3. Definizione Percorsi Assoluti
# Usiamo BASE_DIR / "percorso" per ancorare tutto alla root
LOG_FILE_PATH = BASE_DIR / os.getenv("LOG_FILE_PATH", "logs/agentic.log")
STORAGE_FILE_PATH = BASE_DIR / os.getenv("STORAGE_FILE_PATH", "data/tickets.jsonl")

def bootstrap():
    """Prepara l'ambiente fisico ovunque tu sia nel terminale."""
    for path in [LOG_FILE_PATH, STORAGE_FILE_PATH]:
        path.parent.mkdir(parents=True, exist_ok=True)

# Esecuzione al caricamento
bootstrap()