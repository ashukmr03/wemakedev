from fastapi import APIRouter
from app.models.care import CareEventCreate, CareUpdateConfirmRequest
from app.services.care_service import care_service
from app.utils.responses import make_success_response

router = APIRouter(prefix="/api/care", tags=["Care Events"])


@router.post("/confirm")
def confirm_care_update(payload: CareUpdateConfirmRequest):
    """Confirm human-reviewed AI extraction, persisting care event, tasks, and notifications."""
    res = care_service.confirm_care_update(payload)
    return make_success_response(res.model_dump(by_alias=True))


@router.get("/timeline")
def get_care_timeline(familyId: str = "demo-family"):
    """Fetch care timeline events sorted newest first."""
    events = care_service.get_timeline(familyId)
    return make_success_response(events)


@router.post("")
def create_manual_care_event(payload: CareEventCreate):
    """Manually record a care event."""
    event = care_service.create_care_event(
        family_id=payload.family_id,
        senior_id=payload.senior_id,
        event_type=payload.type,
        description=payload.description,
        recorded_by=payload.recorded_by,
        needs_human_review=payload.needs_human_review,
        urgent=payload.urgent
    )
    return make_success_response(event.model_dump(by_alias=True))
