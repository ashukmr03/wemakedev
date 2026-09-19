from fastapi import APIRouter
from app.config import settings
from app.services.bedrock_service import bedrock_service
from app.services.s3_service import s3_service
from app.utils.responses import make_success_response

router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/status")
def system_status():
    """Return backend operational status including S3, Bedrock, and Lambda status."""
    lambda_status = "configured" if settings.USE_LAMBDA_AI and settings.CARE_AI_LAMBDA_NAME else "disabled"
    status_data = {
        "api": "healthy",
        "s3": s3_service.check_status(),
        "bedrock": bedrock_service.check_status(),
        "lambda": lambda_status
    }
    return make_success_response(status_data)
