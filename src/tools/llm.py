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



#########-----------------------------------------------------------------------




def ask_llm(
    prompt: str | None = None,
    system: str | None = None,
    messages: list[dict[str, str]] | None = None,
    model: str | None = None,
    temperature: float = 0,
) -> str:
    """Chiama un LLM via OpenAI (chat completion) e restituisce solo testo.

    Puoi passare:
    - `messages` (lista di messaggi chat): ha priorità su `prompt/system`
    - oppure `prompt` (+ opzionale `system`)

    Args:
        prompt: prompt utente (alternativa a `messages`).
        system: prompt di sistema opzionale.
        messages: lista di messaggi con chiavi `role`/`content`.
        model: modello OpenAI; se None usa `OPENAI_MODEL` o fallback.
        temperature: creatività (0 = più deterministico).

    Returns:
        Contenuto testuale della risposta (stringa; mai None).

    Raises:
        ValueError: se non viene fornito né `prompt` né `messages`.
        RuntimeError: se manca `OPENAI_API_KEY` o le dipendenze non sono disponibili.
    """

    resolved_model = model or get_default_model()
    client = get_openai_client()
    resolved_messages: list[dict[str, str]] = []
    if messages is not None:
        resolved_messages = messages
    else:
        if prompt is None:
            raise ValueError("Devi passare `prompt` oppure `messages`.")
        if system:
            resolved_messages.append({"role": "system", "content": system})
        resolved_messages.append({"role": "user", "content": prompt})

    resp = client.chat.completions.create(
        model=resolved_model,
        messages=resolved_messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""
