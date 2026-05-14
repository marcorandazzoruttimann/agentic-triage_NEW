from __future__ import annotations
import os
from openai import OpenAI
from typing import TYPE_CHECKING
from config.env import require_dotenv

if TYPE_CHECKING:  # pragma: no cover
    from openai import OpenAI


_CLIENT: "OpenAI | None" = None
_OPENAI_CLS: type | None = None


def _load_env() -> None:
    """Carica `.env` tramite loader centralizzato (richiesto)."""

    require_dotenv()


def get_default_model() -> str:
    """Ritorna il modello di default da usare per le chiamate OpenAI.

    Returns:
        Il valore di `OPENAI_MODEL` se presente, altrimenti un fallback sicuro.
    """
    _load_env()
    return os.getenv("OPENAI_MODEL") or "gpt-4o-mini"


def _get_openai_cls() -> type:
    """Importa e memoizza la classe `OpenAI` dalla libreria `openai`.

    Serve per:
    - ritardare l'import finché non serve (lazy import)
    - rendere facile "mockare" la classe nei test

    Returns:
        La classe `OpenAI` (o un sostituto impostato nei test).
    """
    global _OPENAI_CLS
    if _OPENAI_CLS is not None:
        return _OPENAI_CLS

    try:
        from openai import OpenAI  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Dipendenza 'openai' non disponibile. Installa il progetto con le dipendenze."
        ) from e

    _OPENAI_CLS = OpenAI
    return _OPENAI_CLS


def get_openai_client() -> "OpenAI":
    """
    Costruisce e memoizza un client OpenAI per processo.

    Richiede `OPENAI_API_KEY` nell'ambiente (caricato da `.env` o già presente).
    """
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT

    _load_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY mancante: imposta la variabile d'ambiente o un file .env."
        )

    openai_cls = _get_openai_cls()
    _CLIENT = openai_cls(api_key=api_key)
    return _CLIENT


def _reset_client_for_tests() -> None:
    """Resetta lo stato globale del client (solo per test).

    Nei test è utile ripartire da una situazione pulita così ogni caso è
    indipendente e ripetibile.
    """
    global _CLIENT, _OPENAI_CLS
    _CLIENT = None
    _OPENAI_CLS = None



#######################--------------------------- sotto cè l'originale di questo progetto


# Inizializzazione client OpenAI
def get_client() -> OpenAI:
    """
    Crea e restituisce un client OpenAI utilizzando la API key da variabile d'ambiente.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("API key non trovata. Assicurati di aver configurato .env")

    return OpenAI(api_key=api_key)


def call_llm(prompt: str) -> str:
    """
    Invia un prompt al modello e restituisce l'output testuale.
    
    Requisiti:
    - output deterministico
    - nessun parsing qui (solo testo)
    """

    client = get_client()

    response = client.chat.completions.create(
        model="gpt-4.1-mini",  # modello leggero e stabile
        temperature=0,         # determinismo massimo
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Risposta vuota dal modello")

    return content.strip()