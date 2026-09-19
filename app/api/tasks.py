from fastapi import APIRouter, Header, HTTPException
from app.models.task import TaskCreate, TaskUpdate
from app.services.task_service import task_service
from app.utils.responses import make_error_response, make_success_response

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("")
def list_tasks(familyId: str = "demo-family"):
    """List all tasks for a family."""
    tasks = task_service.get_tasks(familyId)
    return make_success_response(tasks)


@router.post("")
def create_task(payload: TaskCreate):
    """Create a new task."""
    task = task_service.create_task(payload)
    return make_success_response(task)


@router.patch("/{taskId}/complete")
def complete_task(taskId: str, x_demo_user: str = Header(default="meera-rao", alias="X-Demo-User")):
    """Mark a task as completed."""
    updated = task_service.complete_task(taskId, completed_by=x_demo_user)
    if not updated:
        return make_error_response("Task not found", code="TASK_NOT_FOUND", status_code=404)
    return make_success_response(updated)


@router.patch("/{taskId}")
def update_task(taskId: str, payload: TaskUpdate):
    """Update task fields."""
    updated = task_service.update_task(taskId, payload)
    if not updated:
        return make_error_response("Task not found", code="TASK_NOT_FOUND", status_code=404)
    return make_success_response(updated)
