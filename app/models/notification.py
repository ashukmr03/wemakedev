from typing import Optional
from app.models.family import CamelModel


class Notification(CamelModel):
    id: str
    family_id: str
    title: str
    message: str
    type: str = "info"  # info, alert, task, care_update
    read: bool = False
    created_at: str


class NotificationCreate(CamelModel):
    family_id: str = "demo-family"
    title: str
    message: str
    type: str = "info"
