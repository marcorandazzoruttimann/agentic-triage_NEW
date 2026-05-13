import json
import os
from datetime import datetime
from typing import Dict, Any, Union
from schemas.ticket import Ticket, TicketBase , TicketEnriched

# Percorso di default per i log
STORAGE_FILE_PATH = "data/tickets.jsonl"

def _ensure_dir():
    """Assicura che la cartella per i dati esista."""
    os.makedirs(os.path.dirname(STORAGE_FILE_PATH), exist_ok=True)

def save_ticket(ticket: Union[Ticket, TicketBase, TicketEnriched, Dict[str, Any]], label: str = "update") -> None:
    """
    Salva un'istantanea del ticket nel file JSONL.
    
    Ogni chiamata crea una nuova riga nel file, permettendo di tracciare 
    l'evoluzione del ticket nel workflow.
    """
    _ensure_dir()

    # 1. Conversione in dizionario puro
    if hasattr(ticket, "model_dump"):
        # Se è un oggetto Pydantic (Ticket o TicketBase)
        data = ticket.model_dump()
    else:
        # Se è un dizionario (per resilienza)
        data = ticket

    # 2. Arricchimento con metadati di scrittura
    # Usiamo datetime.now().isoformat() per tracciare QUANDO è avvenuto il salvataggio
    entry = {
        "storage_timestamp": datetime.now().isoformat(),
        "workflow_step": label,
        "ticket_data": data
    }

    # 3. Scrittura in modalità 'append' (a)
    try:
        with open(STORAGE_FILE_PATH, "a", encoding="utf-8") as f:
            # ensure_ascii=False serve per gestire correttamente accenti e caratteri speciali
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except Exception as e:
        print(f"Errore critico durante il salvataggio su file: {e}")