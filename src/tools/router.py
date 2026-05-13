from schemas.ticket import Ticket, TicketEnriched, Category, Team, Priority
from priority_tables.table_v1 import PRIORITY_RULES

"""Le regole di priorità PRIORITY_RULES sono salvate in un file versionato a parte
    per consentire rielaborazioni future concordate col cliente
"""
# Tabella di routing basata sulla categoria
CATEGORY_TO_TEAM: dict[Category, Team] = {
    "IT": "team_tecnico",
    "BILLING": "amministrazione",
    "SALES": "commerciale",
    "SECURITY": "sicurezza",
}

def _calculate_reassigned_priority(text: str, current_priority: Priority) -> Priority:
    """
    Logica deterministica per ricalcolare la priorità basata su parole chiave.
    """
    text_lower = text.lower()
    
    # Ordiniamo le priorità per gestire la logica "MINIMUM"
    priority_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    new_priority = current_priority

    for rule in PRIORITY_RULES:
        if any(kw in text_lower for kw in rule["keywords"]):
            target = rule["target"]
            
            if rule["type"] == "SET":
                # Sovrascrive sempre (es. "urgente" -> HIGH)
                new_priority = target
            elif rule["type"] == "MINIMUM":
                # Se la priorità attuale è più bassa della target, la alza. 
                # Altrimenti lascia quella dell'LLM (es. se era già HIGH, resta HIGH)
                if priority_order[current_priority] < priority_order[target]:
                    new_priority = target
            
            # Se troviamo una parola chiave forte (tipo CRITICAL), possiamo fermarci
            if new_priority == "CRITICAL":
                break
                
    return new_priority

def assign_to_team(ticket: Ticket) -> TicketEnriched:
    """
    Prende un Ticket e lo arricchisce con l'assegnazione al team 
    e la logica di priorità riassegnata.
    """

    # 1. Identificazione del Team
    # Usiamo .get() per sicurezza, anche se la categoria è validata da Pydantic
    target_team = CATEGORY_TO_TEAM.get(ticket.categoria, "team_tecnico")

    # 2. Logica per priorità_riassegnata
    # Applichiamo la logica della riassegnazione sulla domanda grezza
    reassigned = _calculate_reassigned_priority(ticket.domanda_grezza, ticket.priorita)

    # 3. Creazione dell'oggetto arricchito
    # Spacchettiamo il ticket esistente e aggiungiamo i nuovi campi
    enriched_data = {
        **ticket.model_dump(),
        "team": target_team,
        "priorita_riassegnata": reassigned
    }

    return TicketEnriched(**enriched_data)