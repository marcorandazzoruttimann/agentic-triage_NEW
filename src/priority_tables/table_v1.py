

"""
Visto che questa tabella ssarà soggetta a fine tuning progressivo col cliente,
la gestisco come versioni salvate e facilmente intercambiabili

"""


# Configurazione Regole di Priorità
PRIORITY_RULES = [
    {"keywords": ["urgente", "bloccato", "sicurezza", "hacker"], "target": "HIGH", "type": "SET"},
    {"keywords": ["subito", "non funziona", "errore"], "target": "MEDIUM", "type": "MINIMUM"},
    {"keywords": ["down", "offline", "interruzione", "bitcoin"], "target": "CRITICAL", "type": "SET"},
    {"keywords": ["informazione", "curiosità", "domanda"], "target": "LOW", "type": "SET"},
]
