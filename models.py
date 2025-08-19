from pydantic import BaseModel
from typing import Optional, Literal

class AccountLookupIn(BaseModel):
    action: Literal["get", "update"]
    phone: Optional[str] = None
    updates: Optional[dict] = None

class KnowledgeBaseIn(BaseModel):
    question: str
    context: Optional[str] = None
    plan: Optional[str] = None
    pest: Optional[str] = None

class ScheduleCheckIn(BaseModel):
    action: Literal["check", "book"]
    address: Optional[str] = None
    service_type: Optional[Literal["re-service"]] = None
    slot: Optional[str] = None
    notes: Optional[str] = None
