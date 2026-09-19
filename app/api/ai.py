from fastapi import APIRouter
from app.models.ai import DailySummaryRequest, ExtractionInput
from app.services.bedrock_service import bedrock_service
from app.services.care_service import care_service
from app.services.s3_service import s3_service
from app.services.task_service import task_service
from app.utils.ids import now_iso
from app.utils.responses import make_success_response

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/extract")
def extract_care_info(payload: ExtractionInput):
    """Extract structured eldercare information from transcript or text using Bedrock/Fallback AI."""
    result = bedrock_service.extract_care_update(payload.text, payload.family_id)
    return make_success_response(result.model_dump(by_alias=True))


@router.post("/summary")
def generate_summary(payload: DailySummaryRequest = DailySummaryRequest()):
    """Generate an AI daily care summary based on recent care records."""
    family_id = payload.family_id
    recent_events = care_service.get_timeline(family_id)[:5]
    all_tasks = task_service.get_tasks(family_id)
    pending_tasks = [t for t in all_tasks if t.get("status") != "completed"]

    raw_appointments = s3_service.list_json("appointments/")
    upcoming_appointments = [
        a for a in raw_appointments
        if isinstance(a, dict) and (a.get("familyId") == family_id or a.get("family_id") == family_id)
    ]

    context = {
        "recentCareEvents": recent_events,
        "pendingTasks": pending_tasks,
        "upcomingAppointments": upcoming_appointments
    }

    summary_text = bedrock_service.generate_daily_summary(context)
    summary_record = {
        "summary": summary_text,
        "generatedAt": now_iso(),
        "aiProvider": bedrock_service.check_status()
    }

    # Persist summary record to S3
    s3_service.put_json(f"summaries/{family_id}.json", summary_record)

    return make_success_response(summary_record)
