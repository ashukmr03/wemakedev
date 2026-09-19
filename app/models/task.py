from typing import Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from app.models.family import CamelModel


class Task(CamelModel):
    id: str
    family_id: str
    title: str
    description: Optional[str] = ""
    assigned_to: Optional[str] = None
    due_at: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, overdue
    created_at: str
    completed_at: Optional[str] = None
    completed_by: Optional[str] = None


class TaskCreate(CamelModel):
    family_id: str = "demo-family"
    title: str
    description: Optional[str] = ""
    assigned_to: Optional[str] = None
    due_at: Optional[str] = None
    status: str = "pending"


class TaskUpdate(CamelModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_at: Optional[str] = None
    status: Optional[str] = None
    completed_by: Optional[str] = None
