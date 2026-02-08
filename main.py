from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.endpoints import games, rules, auth
from db.init_db import init_database
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc.errors()}")
    # logger.error(f"Body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

@app.on_event("startup")
async def startup_event():
    """Application startup logic."""
    logger.info("Starting application...")
    # NOTE: init_database() is disabled here because it causes timeouts on Vercel cold starts.
    # Use /api/v1/init-db for manual initialization if needed.
    logger.info("Application started successfully")

@app.get("/health")
def health_check():
    return {"status": "ok", "supabase_url": "configured" if settings.SUPABASE_URL else "missing"}

@app.post(f"{settings.API_V1_STR}/init-db", tags=["management"])
def manual_init_db():
    """Manually trigger database initialization."""
    try:
        init_database()
        return {"status": "success", "message": "Database initialization triggered"}
    except Exception as e:
        logger.error(f"Manual DB init failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(games.router, prefix=f"{settings.API_V1_STR}/games", tags=["games"])
app.include_router(rules.router, prefix=f"{settings.API_V1_STR}/rules", tags=["rules"])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
