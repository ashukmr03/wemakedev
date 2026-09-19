import uuid
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Generate a unique UUID v4 string."""
    return str(uuid.uuid4())


def now_iso() -> str:
    """Get current UTC timestamp formatted as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()
