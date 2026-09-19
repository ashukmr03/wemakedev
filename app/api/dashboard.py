from fastapi import APIRouter
from app.services.dashboard_service import dashboard_service
from app.utils.responses import make_success_response

router = APIRouter(prefix="/api", tags=["Dashboard"])


@router.get("/dashboard")
def get_dashboard(familyId: str = "demo-family"):
    """Fetch complete dashboard state for a family in one single request."""
    data = dashboard_service.get_dashboard_data(familyId)
    return make_success_response(data)
