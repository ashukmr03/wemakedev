import logging
from typing import Any, Dict, List, Optional
from app.models.task import Task, TaskCreate, TaskUpdate
from app.services.s3_service import s3_service
from app.utils.ids import generate_uuid, now_iso

logger = logging.getLogger("carecircle.task_service")


class TaskService:
    """Task CRUD & completion service."""

    def get_tasks(self, family_id: str = "demo-family") -> List[Dict[str, Any]]:
        """List tasks for a family."""
        raw_tasks = s3_service.list_json("tasks/")
        tasks = [t for t in raw_tasks if isinstance(t, dict) and (t.get("familyId") == family_id or t.get("family_id") == family_id)]
        tasks.sort(key=lambda x: x.get("createdAt") or x.get("created_at") or "", reverse=True)
        return tasks

    def create_task(self, payload: TaskCreate) -> Dict[str, Any]:
        """Create a new task."""
        task_id = generate_uuid()
        task = Task(
            id=task_id,
            family_id=payload.family_id,
            title=payload.title,
            description=payload.description or "",
            assigned_to=payload.assigned_to,
            due_at=payload.due_at,
            status=payload.status or "pending",
            created_at=now_iso(),
            completed_at=None,
            completed_by=None
        )
        task_dict = task.model_dump(by_alias=True)
        s3_service.put_json(f"tasks/{task_id}.json", task_dict)
        logger.info(f"Created task {task_id}: {task.title}")
        return task_dict

    def update_task(self, task_id: str, payload: TaskUpdate) -> Optional[Dict[str, Any]]:
        """Update an existing task."""
        key = f"tasks/{task_id}.json"
        existing = s3_service.get_json(key)
        if not existing or not isinstance(existing, dict):
            logger.warning(f"Task not found for update: {task_id}")
            return None

        fields_to_update = payload.model_dump(exclude_unset=True, by_alias=True)
        for k, v in fields_to_update.items():
            if v is not None:
                existing[k] = v

        if fields_to_update.get("status") == "completed" and not existing.get("completedAt"):
            existing["completedAt"] = now_iso()

        s3_service.put_json(key, existing)
        return existing

    def complete_task(self, task_id: str, completed_by: str = "Lakshmi") -> Optional[Dict[str, Any]]:
        """Mark task completed and persist."""
        key = f"tasks/{task_id}.json"
        existing = s3_service.get_json(key)
        if not existing or not isinstance(existing, dict):
            logger.warning(f"Task not found for completion: {task_id}")
            return None

        existing["status"] = "completed"
        existing["completedAt"] = now_iso()
        existing["completedBy"] = completed_by
        s3_service.put_json(key, existing)
        logger.info(f"Task completed: {task_id} by {completed_by}")
        return existing


task_service = TaskService()
