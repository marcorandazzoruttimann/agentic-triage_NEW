from __future__ import annotations
import json
import os
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Union
from schemas.ticket import TicketBase, Ticket, TicketEnriched
from config.config import LOG_FILE_PATH

def _is_uuid(text: str) -> bool:
    """Controlla se una stringa è un UUID valido per evitarne l'oscuramento."""
    try:
        uuid.UUID(text)
        return True
    except ValueError:
        return False

def _redact_sensitive_data(value: Any) -> Any:
    """
    Logica di oscuramento specifica con esclusione inizio frase.
    """
    if not isinstance(value, str):
        return value

    if _is_uuid(value):
        return value

    # 1. API Keys e IBAN (logica precedente invariata)
    value = value.replace("sk-", "sk-***")
    iban_pattern = r'([A-Z]{2}[0-9]{2})[A-Z0-9]{10,26}([A-Z0-9]{2})'
    value = re.sub(iban_pattern, r'\1***********\2', value, flags=re.IGNORECASE)

    # 2. Riconoscimento Nomi Propri con esclusione inizio frase/punteggiatura
    # SPIEGAZIONE REGEX:
    # (?<!^): Non all'inizio della riga
    # (?<![.!?]\s): Non preceduto da . ! ? seguiti da uno spazio
    # \b[A-Z][a-z]{2,9}\b: Parola con Maiuscola lunga 3-15 caratteri
    
    name_pattern = r'(?<!^)(?<![.!?]\s)\b[A-Z][a-z]{2,14}\b'

    def replace_name(match):
        name = match.group(0)
        return f"{name[0]}***{name[-1]}"
    
    value = re.sub(name_pattern, replace_name, value)

    return value

def _sanitize_payload(payload: Any) -> Any:
    """
    Applica la sanificazione in modo RICORSIVO.
    Funziona con dizionari nidificati, liste e stringhe.
    """
    if isinstance(payload, dict):
        return {k: _sanitize_payload(v) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [_sanitize_payload(i) for i in payload]
    elif isinstance(payload, str):
        return _redact_sensitive_data(payload)
    else:
        return payload

def log_event(
    event_type: str, 
    payload: Union[Dict[str, Any], TicketBase, Ticket, TicketEnriched],
    label: str = None
) -> None:
   

    # Conversione in dict (gestendo Pydantic o dict puri)
    if hasattr(payload, "model_dump"):
        data_to_log = payload.model_dump(mode="json")
    else:
        data_to_log = payload

    # Se c'è una label, inscatoliamo il payload
    if label:
        data_to_log = {label: data_to_log}

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "payload": _sanitize_payload(data_to_log),
    }

    with LOG_FILE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + "\n")