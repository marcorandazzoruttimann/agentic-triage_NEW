"""Logging degli eventi dell'agente in formato JSON Lines (JSONL).

Ogni evento viene salvato come una riga JSON su file. Questo formato è comodo
perché:
- si può appendere velocemente
- si può leggere con strumenti standard (anche a mano)
- è semplice da analizzare con script
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    """Ritorna un timestamp leggibile in stile ISO (senza librerie esterne)."""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def _log_path() -> Path:
    """Decide dove salvare il file di log.

    Returns:
        Un `Path` calcolato così:
        - se `AGENTIC_LOG_PATH` è impostata, usa quel percorso
        - altrimenti usa `./logs/agentic.log` relativo alla cartella di esecuzione
    """
    raw = os.environ.get("AGENTIC_LOG_PATH", "").strip()
    if raw:
        return Path(raw)
    return Path("logs") / "agentic.log"


def _jsonable(value: Any) -> Any:
    """Converte un valore in qualcosa serializzabile in JSON.

    Se un oggetto non è serializzabile (es. una classe custom), lo trasformiamo
    in `repr(value)` così il logging non fallisce.
    """
    try:
        json.dumps(value)
        return value
    except TypeError:
        return repr(value)


_REDACTED = "***REDACTED***"


def _looks_sensitive_key(key: str) -> bool:
    """Ritorna True se una chiave sembra contenere un secret.

    La funzione usa euristiche semplici su substringhe (case-insensitive) per
    determinare se un campo dovrebbe essere redatto nei log.

    Args:
        key: nome del campo.

    Returns:
        True se la chiave è considerata sensibile, altrimenti False.
    """
    k = (key or "").lower()
    return any(part in k for part in ("api_key", "apikey", "token", "secret", "password"))


def _redact(value: Any) -> Any:
    """Redige ricorsivamente valori potenzialmente sensibili.

    - Se `value` è un dict, redige i campi le cui chiavi risultano sensibili.
    - Se è una lista/tupla, redige ricorsivamente gli elementi.
    - Altrimenti ritorna il valore così com'è.

    Args:
        value: valore arbitrario (tipicamente campi di log).

    Returns:
        Una copia redatta/trasformata, preservando la struttura del dato.
    """
    if isinstance(value, dict):
        out: dict[Any, Any] = {}
        for k, v in value.items():
            if isinstance(k, str) and _looks_sensitive_key(k):
                out[k] = _REDACTED
            else:
                out[k] = _redact(v)
        return out
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, tuple):
        return [_redact(v) for v in value]
    return value


def log_event(event: str, **fields: Any) -> None:
    """Scrive un evento su file in formato JSONL.

    Args:
        event: nome breve dell'evento (es. "tool_start", "tool_ok", ...).
        **fields: campi aggiuntivi da salvare (verranno resi JSON-compatibili e redatti).
    """
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {"ts": _now_iso(), "event": event}
    for k, v in fields.items():
        if _looks_sensitive_key(k):
            payload[k] = _REDACTED
        else:
            payload[k] = _jsonable(_redact(v))

    # JSONL: una riga per evento
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
