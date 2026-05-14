import json
import os
from datetime import datetime
from typing import Dict, Any, Union, List
from schemas.ticket import Ticket, TicketBase, TicketEnriched
from config.config import STORAGE_FILE_PATH

def save_ticket(ticket: Union[Ticket, TicketBase, TicketEnriched, Dict[str, Any]], label: str = "update") -> None:
    """
    Gestisce il salvataggio dei ticket:
    - OPEN: Aggiunge una nuova riga (append).
    - TRIAGED: Cerca il ticket_id e sovrascrive la riga esistente.
    """
    # 1. Preparazione dati (JSON-ready)
    data = ticket.model_dump(mode="json") if hasattr(ticket, "model_dump") else ticket
    ticket_id = str(data.get("ticket_id"))
    current_status = data.get("status")

    entry = {
        "storage_timestamp": datetime.now().isoformat(),
        "workflow_step": label,
        "ticket_data": data
    }

    try:
        if current_status == "TRIAGED" and STORAGE_FILE_PATH.exists():
            # LOGICA DI SOVRASCRITTURA
            updated_lines = []
            found = False
            
            with STORAGE_FILE_PATH.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        line_data = json.loads(line)
                        # Se l'ID coincide, carichiamo la nuova entry invece della vecchia
                        if str(line_data.get("ticket_data", {}).get("ticket_id")) == ticket_id:
                            updated_lines.append(json.dumps(entry, ensure_ascii=False))
                            found = True
                        else:
                            updated_lines.append(line.strip())
                    except json.JSONDecodeError:
                        continue

            # Se per qualche motivo il ticket_id non esisteva, lo aggiungiamo in coda
            if not found:
                updated_lines.append(json.dumps(entry, ensure_ascii=False))

            # Riscrittura integrale del file
            with STORAGE_FILE_PATH.open("w", encoding="utf-8") as f:
                f.write("\n".join(updated_lines) + "\n")
        
        else:
            # LOGICA APPEND (Status OPEN o file inesistente)
            with STORAGE_FILE_PATH.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    except Exception as e:
        print(f"Errore critico durante il salvataggio su file: {e}")