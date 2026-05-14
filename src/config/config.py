import os
from pathlib import Path
from dotenv import load_dotenv

# 1. Caricamento ambiente
load_dotenv()

# 2. Gestione Percorsi (con Fallback e conversione in Path)
# Usiamo Path di pathlib perché è più moderno e robusto di os.path
BASE_DIR = Path(__file__).resolve().parent

# Se la variabile non esiste nel .env, usiamo i default
LOG_FILE_PATH = Path(os.getenv("LOG_FILE_PATH", "logs/activity.jsonl"))
STORAGE_FILE_PATH = Path(os.getenv("STORAGE_FILE_PATH", "data/tickets.jsonl"))

def bootstrap():
    """
    Si occupa della preparazione fisica del sistema.
    """
    # Lista delle directory da creare basata sui file necessari
    required_dirs = [
        LOG_FILE_PATH.parent,
        STORAGE_FILE_PATH.parent
    ]

    for directory in required_dirs:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"[BOOTSTRAP] Creata directory: {directory}")

# Esecuzione immediata al primo import
bootstrap()

