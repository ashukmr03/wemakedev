import logging
from typing import Any, Dict
from app.services.bedrock_service import bedrock_service
from app.services.care_service import care_service
from app.services.s3_service import s3_service
from app.services.task_service import task_service
from app.utils.ids import now_iso

logger = logging.getLogger("carecircle.dashboard_service")


class DashboardService:
    """Aggregates all dashboard data into a single, efficient payload."""

    def get_dashboard_data(self, family_id: str = "demo-family") -> Dict[str, Any]:
        """Fetch and aggregate complete dashboard state."""
        # 1. Fetch Senior & Family info
        senior = s3_service.get_json(f"seniors/lakshmi-rao.json") or {
            "id": "lakshmi-rao",
            "familyId": family_id,
            "name": "Lakshmi Rao",
            "age": 72,
            "preferredLanguage": "English",
            "conditionNotes": "Hypertension, mild knee osteoarthritis",
            "createdAt": now_iso()
        }

        family = s3_service.get_json(f"families/{family_id}.json") or {
            "id": family_id,
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

        # 2. Fetch Tasks
        all_tasks = task_service.get_tasks(family_id)
        pending_tasks = [t for t in all_tasks if t.get("status") != "completed"]
        completed_tasks = [t for t in all_tasks if t.get("status") == "completed"]

        total_tasks_count = len(all_tasks)
        completed_tasks_count = len(completed_tasks)
        percentage = int((completed_tasks_count / total_tasks_count * 100)) if total_tasks_count > 0 else 100

        today_progress = {
            "completedTasks": completed_tasks_count,
            "totalTasks": total_tasks_count,
            "percentage": percentage
        }

        # 3. Fetch Appointments
        raw_appointments = s3_service.list_json("appointments/")
        upcoming_appointments = [
            a for a in raw_appointments
            if isinstance(a, dict) and (a.get("familyId") == family_id or a.get("family_id") == family_id)
        ]
        upcoming_appointments.sort(key=lambda x: x.get("scheduledAt") or x.get("scheduled_at") or "")

        # 4. Medication Reminders (from tasks or dedicated records)
        medication_reminders = [
            t for t in all_tasks
            if "medicine" in (t.get("title") or "").lower() or "med" in (t.get("title") or "").lower()
        ]
        if not medication_reminders:
            medication_reminders = [
                {
                    "id": "med-morning",
                    "title": "Morning Medicine",
                    "dueAt": "8:00 AM",
                    "status": "completed",
                    "completedBy": "Lakshmi"
                },
                {
                    "id": "med-evening",
                    "title": "Evening Medicine",
                    "dueAt": "8:00 PM",
                    "status": "pending",
                    "completedBy": None
                }
            ]

        # 5. Fetch Recent Care Events
        recent_care_events = care_service.get_timeline(family_id)

        # 6. Fetch Notifications
        raw_notifications = s3_service.list_json("notifications/")
        notifications = [
            n for n in raw_notifications
            if isinstance(n, dict) and (n.get("familyId") == family_id or n.get("family_id") == family_id)
        ]
        notifications.sort(key=lambda x: x.get("createdAt") or x.get("created_at") or "", reverse=True)

        # 7. Daily Summary (stored or generated)
        summary_record = s3_service.get_json(f"summaries/{family_id}.json")
        if summary_record and isinstance(summary_record, dict):
            daily_summary = summary_record
        else:
            context = {
                "recentCareEvents": recent_care_events[:3],
                "pendingTasks": pending_tasks[:3],
                "upcomingAppointments": upcoming_appointments[:3]
            }
            summary_text = bedrock_service.generate_daily_summary(context)
            daily_summary = {
                "summary": summary_text,
                "generatedAt": now_iso(),
                "aiProvider": bedrock_service.check_status()
            }

        return {
            "senior": senior,
            "family": family,
            "todayProgress": today_progress,
            "pendingTasks": pending_tasks,
            "upcomingAppointments": upcoming_appointments,
            "medicationReminders": medication_reminders,
            "recentCareEvents": recent_care_events,
            "notifications": notifications,
            "dailySummary": daily_summary
        }


dashboard_service = DashboardService()
