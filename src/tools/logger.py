import json
import os
from datetime import datetime
from typing import Any, Dict
from schemas.ticket import TicketBase,Ticket


LOG_FILE_PATH = os.path.join("logs", "activity.jsonl")


def _ensure_log_dir():
    """
    Assicura che la cartella logs/ esista.
    """
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)


def _redact_sensitive_data(text: str) -> str:
    """
    Oscura informazioni sensibili nel testo.
    Esempi:
    - API keys (pattern base)
    - token lunghi
    """

    if not isinstance(text, str):
        return text

    # Redazione semplice per API key OpenAI (sk-...)
    text = text.replace("sk-", "sk-***")

    # Redazione generica per stringhe lunghe (token-like)
    # Es: abcdefghijklmnopqrstuvwxyz123456 → abc***456
    if len(text) > 20:
        text = text[:3] + "***" + text[-3:]

    return text


def _sanitize_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applica redaction a tutti i campi stringa del payload.
    """

    sanitized = {}

    for key, value in payload.items():
        if isinstance(value, str):#controlla se il valore è una stringa semplice
            sanitized[key] = _redact_sensitive_data(value)#se lo è la controlla con redact
        else:
            sanitized[key] = value #se è un altro genere di valore lo copia

    return sanitized


def log_event(
    event_type: str, 
    payload: Dict[str, Any] | TicketBase, 
    label: str = None
) -> None:

    _ensure_log_dir()

    """
    Rendo il log in grado di trattare anche Dict per resilienza con assegnazione data_to_log :
    """

    if isinstance(payload, TicketBase):
        # Se passo una label (es. "ticket"), creiamo {"ticket": {dati...}}
        if label:
            data_to_log = {label: payload.model_dump()}
        else:
            data_to_log = payload.model_dump()
    else:
        # Se è già un dict, lo usiamo così com'è
        data_to_log = payload

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "status": data_to_log.get("status", "UNKNOWN"),
        "payload": _sanitize_payload(data_to_log),
    }

    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False, default=str) + "\n")