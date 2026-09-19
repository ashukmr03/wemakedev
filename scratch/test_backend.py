import json
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.seed_demo_data import seed_demo_data
from fastapi.testclient import TestClient
from app.main import app

# Ensure demo data is seeded for test
seed_demo_data()

client = TestClient(app)

def run_tests():
    print("=== STARTING CARECIRCLE BACKEND INTEGRATION TESTS ===")

    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[OK] GET /health:", res.json())

    # 2. System status
    res = client.get("/api/system/status")
    assert res.status_code == 200, f"System status failed: {res.text}"
    print("[OK] GET /api/system/status:", res.json())

    # 3. Initial Dashboard
    res = client.get("/api/dashboard")
    assert res.status_code == 200, f"Dashboard failed: {res.text}"
    dashboard = res.json()
    assert dashboard["success"] == True
    print("[OK] GET /api/dashboard: Senior =", dashboard["data"]["senior"]["name"], "| Family =", dashboard["data"]["family"]["name"])

    # 4. AI Extract with demo sentence
    demo_sentence = "I took Dad to the doctor today. The doctor said to continue the current medicine for five days, and Arun should collect the blood report on Friday."
    res = client.post("/api/ai/extract", json={"text": demo_sentence, "familyId": "demo-family"})
    assert res.status_code == 200, f"AI extract failed: {res.text}"
    extracted_data = res.json()["data"]
    assert "careEvents" in extracted_data or "care_events" in extracted_data
    assert "tasks" in extracted_data
    print("[OK] POST /api/ai/extract (Provider:", extracted_data.get("aiProvider"), "):", extracted_data["summary"])

    # 5. Care Confirm
    confirm_payload = {
        "familyId": "demo-family",
        "seniorId": "lakshmi-rao",
        "originalText": demo_sentence,
        "confirmedBy": "meera-rao",
        "extraction": extracted_data
    }
    res = client.post("/api/care/confirm", json=confirm_payload)
    assert res.status_code == 200, f"Care confirm failed: {res.text}"
    confirmed_res = res.json()["data"]
    created_tasks = confirmed_res["createdTasks"]
    assert len(created_tasks) > 0, "No tasks were created during confirmation!"
    new_task = created_tasks[0]
    task_id = new_task["id"]
    print("[OK] POST /api/care/confirm: Care event created & Task created with ID:", task_id)

    # 6. Care Timeline
    res = client.get("/api/care/timeline?familyId=demo-family")
    assert res.status_code == 200, f"Timeline failed: {res.text}"
    timeline = res.json()["data"]
    assert len(timeline) >= 2, f"Expected timeline items, got {len(timeline)}"
    print(f"[OK] GET /api/care/timeline: {len(timeline)} care events found.")

    # 7. List Tasks
    res = client.get("/api/tasks?familyId=demo-family")
    assert res.status_code == 200, f"List tasks failed: {res.text}"
    tasks = res.json()["data"]
    print(f"[OK] GET /api/tasks: {len(tasks)} tasks found.")

    # 8. Complete Task
    res = client.patch(f"/api/tasks/{task_id}/complete", headers={"X-Demo-User": "arun-rao"})
    assert res.status_code == 200, f"Task complete failed: {res.text}"
    completed_task = res.json()["data"]
    assert completed_task["status"] == "completed"
    print(f"[OK] PATCH /api/tasks/{task_id}/complete: Task status =", completed_task["status"])

    # 9. Dashboard verification after task completion
    res = client.get("/api/dashboard")
    assert res.status_code == 200, f"Dashboard post-complete failed: {res.text}"
    updated_dashboard = res.json()["data"]
    progress = updated_dashboard["todayProgress"]
    print("[OK] GET /api/dashboard post-completion: Today Progress =", progress)

    # 10. AI Summary
    res = client.post("/api/ai/summary", json={"familyId": "demo-family"})
    assert res.status_code == 200, f"AI summary failed: {res.text}"
    summary_data = res.json()["data"]
    print("[OK] POST /api/ai/summary:", summary_data["summary"])

    print("\n==================================================")
    print("ALL 10 ENDPOINT VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
