from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from app.models.family import CamelModel


class CareEvent(CamelModel):
    id: str
    family_id: str
    senior_id: str
    type: str  # e.g., doctor_visit, medication_check, general_update, pain_report
    description: str
    recorded_by: str
    needs_human_review: bool = True
    urgent: bool = False
    urgent_notice: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: str


class CareEventCreate(CamelModel):
    family_id: str = "demo-family"
    senior_id: str = "lakshmi-rao"
    type: str = "general_update"
    description: str
    recorded_by: str = "meera-rao"
    needs_human_review: bool = True
    urgent: bool = False


class CareUpdateConfirmRequest(CamelModel):
    family_id: str = "demo-family"
    senior_id: str = "lakshmi-rao"
    original_text: str
    confirmed_by: str = "meera-rao"
    extraction: Dict[str, Any]


class CareUpdateConfirmResponse(CamelModel):
    care_event: Dict[str, Any]
    created_tasks: List[Dict[str, Any]] = []
    created_appointments: List[Dict[str, Any]] = []
    notifications: List[Dict[str, Any]] = []
