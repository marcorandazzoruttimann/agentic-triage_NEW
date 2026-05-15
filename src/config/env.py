"""Utilities for loading configuration from `.env`.

This project treats `.env` as a required part of runtime configuration.
"""

from __future__ import annotations

from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


_ENV_LOADED = False


def require_dotenv(dotenv_path: str | Path = ".env") -> Path:
    """Load `.env` exactly once, failing if missing.

    Args:
        dotenv_path: path to the `.env` file (default: `.env` in current working directory).

    Returns:
        Resolved `Path` to the `.env` file that was loaded.

    Raises:
        RuntimeError: if `python-dotenv` is not installed or the `.env` file is missing.
    """

    global _ENV_LOADED
    if _ENV_LOADED:
        return Path(dotenv_path).expanduser().resolve()

    if load_dotenv is None:  # pragma: no cover
        raise RuntimeError(
            "Dipendenza 'python-dotenv' non disponibile. Installa il progetto con le dipendenze."
        )

    p = Path(dotenv_path).expanduser()
    if not p.exists():
        raise RuntimeError(
            f"File .env mancante ({p}). Crealo (es. `cp .env.example .env`) prima di eseguire."
        )

    load_dotenv(dotenv_path=p, override=False)
    _ENV_LOADED = True
    return p.resolve()


def _reset_env_for_tests() -> None:
    """Reset internal `.env` loaded flag (tests only)."""

    global _ENV_LOADED
    _ENV_LOADED = False
