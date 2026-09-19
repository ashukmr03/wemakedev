from fastapi import APIRouter
from app.services.s3_service import s3_service
from app.utils.responses import make_error_response, make_success_response

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("")
def list_notifications(familyId: str = "demo-family"):
    """List notifications for a family."""
    raw = s3_service.list_json("notifications/")
    notifs = [n for n in raw if isinstance(n, dict) and (n.get("familyId") == familyId or n.get("family_id") == familyId)]
    notifs.sort(key=lambda x: x.get("createdAt") or x.get("created_at") or "", reverse=True)
    return make_success_response(notifs)


@router.patch("/{notificationId}/read")
def mark_notification_read(notificationId: str):
    """Mark a notification as read."""
    key = f"notifications/{notificationId}.json"
    notif = s3_service.get_json(key)
    if not notif or not isinstance(notif, dict):
        return make_error_response("Notification not found", code="NOTIFICATION_NOT_FOUND", status_code=404)

    notif["read"] = True
    s3_service.put_json(key, notif)
    return make_success_response(notif)
