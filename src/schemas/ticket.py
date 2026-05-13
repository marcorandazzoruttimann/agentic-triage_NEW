import uuid
from pydantic import BaseModel, Field, field_validator
from typing import Literal

# Tipi definiti con Literal (vincoli forti e leggibili)
Category = Literal["IT", "BILLING", "SALES", "SECURITY"]
Priority = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
TicketStatus = Literal["OPEN", "TRIAGED", "CLOSED"]
Team = Literal["team_tecnico", "amministrazione", "commerciale", "sicurezza"]

class TicketBase(BaseModel):
    """Dati iniziali del sistema."""
    domanda_grezza: str = Field(..., description="Il testo originale inserito dall'utente")
    status: TicketStatus = Field(default="OPEN", description="Stato iniziale del ticket")

class Ticket(TicketBase):
    """Modello finale arricchito dall'AI e dal sistema dopo il triage."""
    # Campi generati dall'AI (mantenendo la tua sintassi Field)
    categoria: Category = Field(
        ..., 
        description="Categoria del ticket (IT, BILLING, SALES, SECURITY)"
    )
    priorita: Priority = Field(
        ..., 
        description="Livello di priorità del ticket"
    )
    riassunto_breve: str = Field(
        ..., 
        description="Riassunto sintetico (max 15 parole)"
    )
    messaggio_originale: str = Field(
        ..., 
        description="Testo originale del ticket utente"
    )

    # Campo assegnato dal sistema DOPO l'LLM (come da consegna)
    ticket_id: str = Field(
        default=None, 
        description="UUID assegnato post-triage"
    )
        

    @field_validator("riassunto_breve")
    @classmethod
    def validate_riassunto_length(cls, value: str) -> str:
        word_count = len(value.strip().split())
        if word_count > 15:
            raise ValueError(f"Il riassunto supera il limite di 15 parole ({word_count})")
        return value
    
    @field_validator("messaggio_originale")
    @classmethod
    def validate_messaggio_not_empty(cls, value: str) -> str:
        """
        Evita messaggi vuoti o non validi.
        """
        if not value or not value.strip():
            raise ValueError("Il messaggio originale non può essere vuoto")
        return value
    
class TicketEnriched(Ticket):
        team: Team = Field(
        ..., 
        description="Team di assegnazione"
    )
        priorita_riassegnata: Priority = Field(
        ..., 
        description="Priorita riassegnata deterministicamente"
    )
        