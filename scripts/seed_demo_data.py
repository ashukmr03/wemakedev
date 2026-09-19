import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.s3_service import s3_service
from app.utils.ids import now_iso


def seed_demo_data():
    """Seed S3 (or memory fallback) with Rao Family demo data."""
    print("Seeding Rao Family demo data...")

    family_id = "demo-family"
    senior_id = "lakshmi-rao"

    # 1. Senior record
    senior_data = {
        "id": senior_id,
        "familyId": family_id,
        "name": "Lakshmi Rao",
        "age": 72,
        "preferredLanguage": "English",
        "conditionNotes": "Hypertension, mild knee osteoarthritis",
        "createdAt": now_iso()
    }
    s3_service.put_json(f"seniors/{senior_id}.json", senior_data)

    # 2. Family record
    family_data = {
        "id": family_id,
        "name": "Rao Family",
        "senior": senior_data,
        "members": [
            {"id": "meera-rao", "name": "Meera Rao", "relationship": "daughter", "role": "caregiver"},
            {"id": "arun-rao", "name": "Arun Rao", "relationship": "son", "role": "caregiver"},
            {"id": "ravi-rao", "name": "Ravi Rao", "relationship": "son", "role": "coordinator"}
        ],
        "emergencyContacts": [
            {"name": "Emergency Services", "relationship": "Emergency", "phone": "911"},
            {"name": "Dr. Sharma", "relationship": "Primary Care Doctor", "phone": "+1-555-0192"}
        ],
        "createdAt": now_iso()
    }
    s3_service.put_json(f"families/{family_id}.json", family_data)

    # 3. Tasks
    t1 = {
        "id": "task-morning-medicine",
        "familyId": family_id,
        "title": "Morning medicine",
        "description": "Take morning blood pressure medication",
        "assignedTo": "Lakshmi Rao",
        "dueAt": "8:00 AM",
        "status": "completed",
        "createdAt": now_iso(),
        "completedAt": now_iso(),
        "completedBy": "Lakshmi"
    }
    s3_service.put_json("tasks/task-morning-medicine.json", t1)

    t2 = {
        "id": "task-collect-blood-report",
        "familyId": family_id,
        "title": "Collect blood report",
        "description": "Pick up printed lab results from City Health Clinic",
        "assignedTo": "Arun Rao",
        "dueAt": "Friday",
        "status": "pending",
        "createdAt": now_iso(),
        "completedAt": None,
        "completedBy": None
    }
    s3_service.put_json("tasks/task-collect-blood-report.json", t2)

    t3 = {
        "id": "task-evening-checkin",
        "familyId": family_id,
        "title": "Evening check-in",
        "description": "Call mom to check how her knee is feeling",
        "assignedTo": "Ravi Rao",
        "dueAt": "Today 7:00 PM",
        "status": "pending",
        "createdAt": now_iso(),
        "completedAt": None,
        "completedBy": None
    }
    s3_service.put_json("tasks/task-evening-checkin.json", t3)

    # 4. Doctor Appointment
    app1 = {
        "id": "app-doctor-followup",
        "familyId": family_id,
        "title": "Doctor appointment",
        "doctorName": "Dr. Sharma",
        "location": "City Health Clinic",
        "scheduledAt": "Tomorrow at 10:00 AM",
        "status": "scheduled",
        "notes": "Routine blood pressure checkup and lab report review",
        "createdAt": now_iso()
    }
    s3_service.put_json("appointments/app-doctor-followup.json", app1)

    # 5. Care Event (Knee pain update)
    ce1 = {
        "id": "event-knee-pain",
        "familyId": family_id,
        "seniorId": senior_id,
        "type": "pain_report",
        "description": "Mom reported mild knee pain after evening walk. Applied warm compress.",
        "recordedBy": "Meera Rao",
        "needsHumanReview": True,
        "urgent": False,
        "urgentNotice": None,
        "metadata": {"location": "right knee", "severity": "mild"},
        "createdAt": now_iso()
    }
    s3_service.put_json("care-events/event-knee-pain.json", ce1)

    # 6. Initial Daily Summary
    summary = {
        "summary": "Lakshmi completed her morning medication. Knee pain update recorded by Meera. Arun has a pending task to collect blood report on Friday.",
        "generatedAt": now_iso(),
        "aiProvider": "seed"
    }
    s3_service.put_json(f"summaries/{family_id}.json", summary)

    # 7. Initial Notification
    n1 = {
        "id": "notif-knee-pain",
        "familyId": family_id,
        "title": "Knee Pain Reported",
        "message": "Meera recorded knee pain update for Lakshmi. Human review recommended.",
        "type": "alert",
        "read": False,
        "createdAt": now_iso()
    }
    s3_service.put_json("notifications/notif-knee-pain.json", n1)

    print("Demo data successfully seeded!")


if __name__ == "__main__":
    seed_demo_data()
