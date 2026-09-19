import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import (
    ai,
    appointments,
    care,
    dashboard,
    family,
    health,
    notifications,
    system,
    tasks,
)
from app.config import settings
from app.services.s3_service import s3_service
from app.utils.ids import generate_uuid
from app.utils.responses import make_error_response
from scripts.seed_demo_data import seed_demo_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s (%(threadName)s): %(message)s"
)
logger = logging.getLogger("carecircle.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to automatically seed demo data on startup if storage is empty."""
    logger.info("Initializing CareCircle API...")
    try:
        # Check if demo family exists, if not run seed
        existing_family = s3_service.get_json("families/demo-family.json")
        if not existing_family:
            logger.info("No existing demo data found. Seeding initial Rao Family data...")
            seed_demo_data()
        else:
            logger.info("Demo family data already present.")
    except Exception as e:
        logger.error(f"Error during startup data check: {e}")
    yield
    logger.info("Shutting down CareCircle API...")


app = FastAPI(
    title="CareCircle API",
    description="Mobile-first eldercare coordination API backend for families.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS Configuration
origins = ["http://localhost:3000"]
if settings.FRONTEND_URL and settings.FRONTEND_URL not in origins:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_and_id_middleware(request: Request, call_next):
    """Attach unique request ID and log request metrics securely."""
    req_id = request.headers.get("X-Request-ID", generate_uuid())
    request.state.request_id = req_id

    logger.info(f"[{req_id}] {request.method} {request.url.path}")

    response = await call_next(request)
    response.headers["X-Request-ID"] = req_id

    logger.info(f"[{req_id}] {request.method} {request.url.path} -> Status {response.status_code}")
    return response


# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    req_id = getattr(request.state, "request_id", generate_uuid())
    logger.error(f"[{req_id}] HTTP Exception {exc.status_code}: {exc.detail}")
    return make_error_response(
        message=str(exc.detail),
        code=f"HTTP_{exc.status_code}",
        request_id=req_id,
        status_code=exc.status_code
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "request_id", generate_uuid())
    logger.error(f"[{req_id}] Validation error: {exc.errors()}")
    return make_error_response(
        message="Invalid request payload or query parameters.",
        code="VALIDATION_ERROR",
        request_id=req_id,
        status_code=422
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", generate_uuid())
    logger.error(f"[{req_id}] Unhandled exception: {exc}", exc_info=False)
    return make_error_response(
        message="An unexpected server error occurred.",
        code="INTERNAL_SERVER_ERROR",
        request_id=req_id,
        status_code=500
    )


# Register API Routers
app.include_router(health.router)
app.include_router(system.router)
app.include_router(dashboard.router)
app.include_router(ai.router)
app.include_router(care.router)
app.include_router(tasks.router)
app.include_router(appointments.router)
app.include_router(notifications.router)
app.include_router(family.router)
