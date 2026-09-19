from fastapi import APIRouter
from app.models.appointment import Appointment, AppointmentCreate
from app.services.s3_service import s3_service
from app.utils.ids import generate_uuid, now_iso
from app.utils.responses import make_success_response

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


@router.get("")
def list_appointments(familyId: str = "demo-family"):
    """List appointments for a family."""
    raw = s3_service.list_json("appointments/")
    apps = [a for a in raw if isinstance(a, dict) and (a.get("familyId") == familyId or a.get("family_id") == familyId)]
    apps.sort(key=lambda x: x.get("scheduledAt") or x.get("scheduled_at") or "")
    return make_success_response(apps)


@router.post("")
def create_appointment(payload: AppointmentCreate):
    """Create a new medical appointment."""
    app_id = generate_uuid()
    appointment = Appointment(
        id=app_id,
        family_id=payload.family_id,
        title=payload.title,
        doctor_name=payload.doctor_name,
        location=payload.location,
        scheduled_at=payload.scheduled_at,
        status=payload.status or "scheduled",
        notes=payload.notes,
        created_at=now_iso()
    )
    app_dict = appointment.model_dump(by_alias=True)
    s3_service.put_json(f"appointments/{app_id}.json", app_dict)
    return make_success_response(app_dict)
