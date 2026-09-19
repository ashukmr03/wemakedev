from typing import Optional
from app.models.family import CamelModel


class Appointment(CamelModel):
    id: str
    family_id: str
    title: str
    doctor_name: Optional[str] = None
    location: Optional[str] = None
    scheduled_at: str
    status: str = "scheduled"  # scheduled, completed, cancelled
    notes: Optional[str] = None
    created_at: str


class AppointmentCreate(CamelModel):
    family_id: str = "demo-family"
    title: str
    doctor_name: Optional[str] = None
    location: Optional[str] = None
    scheduled_at: str
    notes: Optional[str] = None
    status: str = "scheduled"
