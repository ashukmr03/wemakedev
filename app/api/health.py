from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Simple health check endpoint for uptime and Render health monitoring."""
    return {
        "status": "ok",
        "service": "carecircle-api"
    }
