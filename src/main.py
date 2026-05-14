from __future__ import annotations
import config
import uuid
from tools.llm import call_llm
from prompts.triage_v2 import build_prompt
from parsing.parser import parse_llm_output
from tools.logger import log_event
from schemas.ticket import TicketBase, Ticket, TicketEnriched
from storage.store import save_ticket
from tools.router import assign_to_team



def process_ticket(user_input: str):
    """
    Pipeline completa di gestione ticket (Parte 1):

    1. Log input
    2. Costruzione prompt
    3. Chiamata LLM
    4. Parsing output
    5. Validazione schema (Pydantic)
    6. Log risultato
    """

    try:

        #a - creare oggetto ticket con user input e status
        base_ticket=TicketBase(domanda_grezza=user_input, status="OPEN",ticket_id=uuid.uuid4())

        #b - salvataggio domanda in data
        save_ticket(base_ticket, "arrivo richiesta")

        # 1. Log input - modificare log per loggare anche status e uuid
        log_event("ticket_received",  base_ticket, "input")

        # 2. Costruzione prompt
        prompt = build_prompt(user_input)

        # 3. Chiamata LLM
        raw_output = call_llm(prompt)

        log_event("llm_raw_response", {"response": raw_output})

        # 4. Parsing + validazione
        ticket = parse_llm_output(raw_output, base_ticket)

        # 5. Log risultato strutturato
        log_event("ticket_processed", {"ticket": ticket.model_dump()})

        #d - logica di routing ed enrichment -----------------------------
        enriched_ticket = assign_to_team(ticket)

        #d - salvataggio ulteriore in data 
        save_ticket(enriched_ticket,"chiusura")

        # 6. Output finale
        print("\n=== TICKET PROCESSATO ===")
        print(enriched_ticket.model_dump())

        #e - log di chiusura
        log_event("ticket_closed",  enriched_ticket, "output")

    except Exception as e:
        log_event("error", {"message": str(e), "input": user_input})
        print("\n[ERRORE]", str(e))


def run_tests():
    """
    Esegue i 4 scenari obbligatori del progetto.
    """

    test_cases = [
        # Scenario A — IT (Urgente)
        #"Non riesco ad accedere alla mia email, è bloccata",

        # Scenario B — Business
        #"Ho effettuato un bonifico, potete confermare?",

        # Scenario C — Security
        #"Guadagna 5000 euro al mese con Bitcoin!!!",

        # Scenario D — Ambiguo
        #"Vorrei comprare il corso ma il sito non carica la pagina di pagamento",

        # Scenario E — Ambiguo 2
        #"Sto cercando l'opzione di rateizzazione del corso ma il menù a tendina non appare. E' un problema del mio browser?",

        # Scenario F — Ambiguo 3
        #"Non sono riuscito a effettuare il bonifico sul vostro ecommerce di petfood per ricevere i bitcoin che il vostro collega mi ha promesso, potete controllare?",

        # Scenario G — Oscuramento GDPR
        "Fallisce il bonifico su iban IT60X0542811101000000123456 a nome di Luca Gambardella. E' urgente!"
    ]

    for i, test in enumerate(test_cases, start=1):
        print(f"\n\n--- SCENARIO {i} ---")
        process_ticket(test)


if __name__ == "__main__":
    run_tests()