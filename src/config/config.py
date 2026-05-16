import os
from pathlib import Path

# --- 1. LOGICA DI CARICAMENTO AMBIENTE (Ex env.py) ---
try:
    from dotenv import load_dotenv
except ImportError:
    raise RuntimeError(
        "Dipendenza 'python-dotenv' non disponibile. Installa il progetto con le dipendenze."
    )

_ENV_LOADED = False

def require_dotenv(dotenv_path: Path) -> None:
    """Carica il file .env esattamente una volta, fallendo se manca."""
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    if not dotenv_path.exists():
        raise RuntimeError(
            f"File .env mancante in ({dotenv_path}). Crealo (es. `cp .env.example .env`) prima di eseguire."
        )

    load_dotenv(dotenv_path=dotenv_path, override=False)
    _ENV_LOADED = True

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