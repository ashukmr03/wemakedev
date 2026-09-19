from typing import Any, Dict, Optional
from fastapi.responses import JSONResponse
from app.utils.ids import generate_uuid


def make_success_response(data: Any, request_id: Optional[str] = None, status_code: int = 200) -> Dict[str, Any]:
    """Format a successful API response matching contract."""
    req_id = request_id or generate_uuid()
    return {
        "success": True,
        "data": data,
        "meta": {
            "requestId": req_id
        }
    }


def make_error_response(
    message: str,
    code: str = "INTERNAL_ERROR",
    request_id: Optional[str] = None,
    status_code: int = 400
) -> JSONResponse:
    """Format an error API response matching contract."""
    req_id = request_id or generate_uuid()
    content = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "requestId": req_id
        }
    }
    return JSONResponse(status_code=status_code, content=content)
