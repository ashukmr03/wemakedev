from typing import List, Optional
from app.models.family import CamelModel


class ExtractionInput(CamelModel):
    text: str
    family_id: str = "demo-family"


class MedicationInstruction(CamelModel):
    instruction: str
    source: str = "user_reported"


class CareEventExtract(CamelModel):
    type: str
    description: str


class TaskExtract(CamelModel):
    title: str
    assigned_to: Optional[str] = None
    due_text: Optional[str] = None
    status: str = "pending"


class AppointmentExtract(CamelModel):
    title: str
    doctor_name: Optional[str] = None
    scheduled_text: Optional[str] = None


class ExtractionResult(CamelModel):
    summary: str
    care_events: List[CareEventExtract] = []
    tasks: List[TaskExtract] = []
    medication_instructions: List[MedicationInstruction] = []
    appointments: List[AppointmentExtract] = []
    concerns: List[str] = []
    needs_human_review: bool = True
    urgent: bool = False
    urgent_notice: Optional[str] = None
    ai_provider: str = "fallback"


class DailySummaryRequest(CamelModel):
    family_id: str = "demo-family"


class DailySummaryResponse(CamelModel):
    summary: str
    generated_at: str
    ai_provider: str = "fallback"
