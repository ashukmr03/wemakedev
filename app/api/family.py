from fastapi import APIRouter
from app.services.s3_service import s3_service
from app.utils.ids import now_iso
from app.utils.responses import make_success_response

router = APIRouter(prefix="/api/family", tags=["Family"])


@router.get("/{familyId}")
def get_family_details(familyId: str):
    """Get family structure, senior info, and emergency contacts."""
    senior = s3_service.get_json("seniors/lakshmi-rao.json") or {
        "id": "lakshmi-rao",
        "familyId": familyId,
        "name": "Lakshmi Rao",
        "age": 72,
        "preferredLanguage": "English",
        "conditionNotes": "Hypertension, mild knee osteoarthritis",
        "createdAt": now_iso()
    }

    family = s3_service.get_json(f"families/{familyId}.json") or {
        "id": familyId,
        "name": "Rao Family",
        "senior": senior,
        "members": [
            {"id": "meera-rao", "name": "Meera Rao", "relationship": "daughter", "role": "caregiver"},
            {"id": "arun-rao", "name": "Arun Rao", "relationship": "son", "role": "caregiver"},
            {"id": "ravi-rao", "name": "Ravi Rao", "relationship": "son", "role": "coordinator"}
        ],
        "emergencyContacts": [
            {"name": "Emergency Services", "relationship": "Emergency", "phone": "911"}
        ],
        "createdAt": now_iso()
    }

    return make_success_response(family)
