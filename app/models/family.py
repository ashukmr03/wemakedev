from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
    )


class Senior(CamelModel):
    id: str
    family_id: str
    name: str
    age: int
    preferred_language: str = "English"
    condition_notes: Optional[str] = None
    created_at: str


class FamilyMember(CamelModel):
    id: str
    name: str
    relationship: str
    role: str
    email: Optional[str] = None
    phone: Optional[str] = None


class EmergencyContact(CamelModel):
    name: str
    relationship: str
    phone: str


class Family(CamelModel):
    id: str
    name: str
    senior: Optional[Senior] = None
    members: List[FamilyMember] = []
    emergency_contacts: List[EmergencyContact] = []
    created_at: str
