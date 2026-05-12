from client import call_llm
from prompts.triage_v2 import build_prompt
from parsing.parser import parse_llm_output
from tools.logger import log_event
from schemas.ticket import TicketBase,Ticket


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
        base_ticket=TicketBase(domanda_grezza=user_input, status="OPEN")

        # 1. Log input - modificare log per loggare anche status e uuid
        log_event("ticket_received",  base_ticket, "input")

        # 2. Costruzione prompt
        prompt = build_prompt(user_input)

        # 3. Chiamata LLM
        raw_output = call_llm(prompt)

        log_event("llm_raw_response", {"response": raw_output})

        # 4. Parsing + validazione
        ticket = parse_llm_output(raw_output)

        # 5. Log risultato strutturato
        log_event("ticket_processed", {"ticket": ticket.model_dump()})

        # 6. Output finale
        print("\n=== TICKET PROCESSATO ===")
        print(ticket.model_dump())

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
        "Non sono riuscito a effettuare il bonifico sul vostro ecommerce di petfood per ricevere i bitcoin che il vostro collega mi ha promesso, potete controllare?"
    ]

    for i, test in enumerate(test_cases, start=1):
        print(f"\n\n--- SCENARIO {i} ---")
        process_ticket(test)


if __name__ == "__main__":
    run_tests()