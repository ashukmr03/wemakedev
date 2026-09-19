import logging
from typing import Any, Dict, List, Optional
from app.models.care import CareEvent, CareUpdateConfirmRequest, CareUpdateConfirmResponse
from app.models.notification import Notification
from app.models.task import Task
from app.services.s3_service import s3_service
from app.utils.ids import generate_uuid, now_iso

logger = logging.getLogger("carecircle.care_service")


class CareService:
    """Service for Care Events and AI Extraction Human Confirmation."""

    def create_care_event(
        self,
        family_id: str,
        senior_id: str,
        event_type: str,
        description: str,
        recorded_by: str,
        needs_human_review: bool = True,
        urgent: bool = False,
        urgent_notice: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CareEvent:
        """Create and persist a manual or confirmed CareEvent."""
        event_id = generate_uuid()
        care_event = CareEvent(
            id=event_id,
            family_id=family_id,
            senior_id=senior_id,
            type=event_type,
            description=description,
            recorded_by=recorded_by,
            needs_human_review=needs_human_review,
            urgent=urgent,
            urgent_notice=urgent_notice,
            metadata=metadata or {},
            created_at=now_iso()
        )
        # S3 key: care-events/{uuid}.json
        key = f"care-events/{event_id}.json"
        s3_service.put_json(key, care_event.model_dump(by_alias=True))
        logger.info(f"Saved CareEvent {event_id} to S3 key {key}")
        return care_event

    def confirm_care_update(self, payload: CareUpdateConfirmRequest) -> CareUpdateConfirmResponse:
        """Process human-reviewed extraction confirmation and persist all generated records."""
        family_id = payload.family_id
        senior_id = payload.senior_id
        confirmed_by = payload.confirmed_by
        extraction = payload.extraction

        # 1. Primary Care Event creation
        events_extracted = extraction.get("careEvents", []) or extraction.get("care_events", [])
        primary_type = events_extracted[0].get("type", "doctor_visit") if events_extracted else "general_update"
        summary_desc = extraction.get("summary") or payload.original_text

        care_event = self.create_care_event(
            family_id=family_id,
            senior_id=senior_id,
            event_type=primary_type,
            description=summary_desc,
            recorded_by=confirmed_by,
            needs_human_review=extraction.get("needsHumanReview", extraction.get("needs_human_review", True)),
            urgent=extraction.get("urgent", False),
            urgent_notice=extraction.get("urgentNotice", extraction.get("urgent_notice")),
            metadata={
                "originalText": payload.original_text,
                "extraction": extraction
            }
        )

        created_tasks: List[Dict[str, Any]] = []
        created_appointments: List[Dict[str, Any]] = []
        notifications: List[Dict[str, Any]] = []

        # 2. Persist Tasks extracted
        tasks_extracted = extraction.get("tasks", [])
        for t_item in tasks_extracted:
            task_id = generate_uuid()
            task_obj = Task(
                id=task_id,
                family_id=family_id,
                title=t_item.get("title", "Follow-up Task"),
                description=f"Generated from care update: {payload.original_text[:80]}",
                assigned_to=t_item.get("assignedTo") or t_item.get("assigned_to") or "Arun Rao",
                due_at=t_item.get("dueText") or t_item.get("due_text") or "Friday",
                status="pending",
                created_at=now_iso(),
                completed_at=None,
                completed_by=None
            )
            task_dict = task_obj.model_dump(by_alias=True)
            s3_service.put_json(f"tasks/{task_id}.json", task_dict)
            created_tasks.append(task_dict)

            # Create notification for assigned task
            notif_id = generate_uuid()
            notif_obj = Notification(
                id=notif_id,
                family_id=family_id,
                title="New Task Assigned",
                message=f"Task '{task_obj.title}' assigned to {task_obj.assigned_to}",
                type="task",
                read=False,
                created_at=now_iso()
            )
            notif_dict = notif_obj.model_dump(by_alias=True)
            s3_service.put_json(f"notifications/{notif_id}.json", notif_dict)
            notifications.append(notif_dict)

        # 3. Create Notification for Care Event
        event_notif_id = generate_uuid()
        event_notif = Notification(
            id=event_notif_id,
            family_id=family_id,
            title="Care Update Confirmed",
            message=f"{confirmed_by} confirmed: {summary_desc}",
            type="care_update",
            read=False,
            created_at=now_iso()
        )
        event_notif_dict = event_notif.model_dump(by_alias=True)
        s3_service.put_json(f"notifications/{event_notif_id}.json", event_notif_dict)
        notifications.append(event_notif_dict)

        return CareUpdateConfirmResponse(
            care_event=care_event.model_dump(by_alias=True),
            created_tasks=created_tasks,
            created_appointments=created_appointments,
            notifications=notifications
        )

    def get_timeline(self, family_id: str = "demo-family") -> List[Dict[str, Any]]:
        """Get care events list sorted newest first."""
        raw_events = s3_service.list_json("care-events/")
        events = [e for e in raw_events if isinstance(e, dict) and e.get("familyId") == family_id or e.get("family_id") == family_id]

        # Sort newest-first by createdAt ISO string
        events.sort(key=lambda x: x.get("createdAt") or x.get("created_at") or "", reverse=True)
        return events


care_service = CareService()
