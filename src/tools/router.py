from schemas.ticket import Ticket, TicketEnriched, Category, Team, Priority

# Tabella di routing basata sulla categoria
CATEGORY_TO_TEAM: dict[Category, Team] = {
    "IT": "team_tecnico",
    "BILLING": "amministrazione",
    "SALES": "commerciale",
    "SECURITY": "sicurezza",
}

def route_ticket(ticket: Ticket) -> TicketEnriched:
    """
    Prende un Ticket e lo arricchisce con l'assegnazione al team 
    e la logica di priorità riassegnata.
    """

    # 1. Identificazione del Team
    # Usiamo .get() per sicurezza, anche se la categoria è validata da Pydantic
    target_team = CATEGORY_TO_TEAM.get(ticket.categoria, "team_tecnico")

    # 2. Logica per priorità_riassegnata
    # Per ora la manteniamo identica a quella dell'LLM (o inserisci qui la tua logica)
    new_priority = ticket.priorita

    # 3. Creazione dell'oggetto arricchito
    # Spacchettiamo il ticket esistente e aggiungiamo i nuovi campi
    enriched_data = {
        **ticket.model_dump(),
        "team": target_team,
        "priorita_riassegnata": new_priority
    }

    return TicketEnriched(**enriched_data)