from __future__ import annotations

from client import get_default_model, get_openai_client


def call_llm(prompt: str) -> str:
    """
    Invia un prompt al modello e restituisce l'output testuale.
    
    Requisiti:
    - output deterministico
    - nessun parsing qui (solo testo)
    """
    resolved_model = get_default_model() or "gpt-4.1-mini"
    client = get_openai_client()

    resolved_messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

    response = client.chat.completions.create(
        model=resolved_model,
        temperature=0,
        messages=resolved_messages,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Risposta vuota dal modello")

    return content.strip()
