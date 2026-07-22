"""
MotoMod AI — FastAPI Application Entrypoint
Integrates CORS, global middlewares, routing, and database lifecycles.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings
from app.core.logger import setup_logging, get_logger
from app.core.database import check_database_connection, dispose_engine
from app.core.redis import close_redis_client, check_redis_connection
from app.core.storage import storage_client
from app.api.v1.routes import auth, bikes, modifications, predictions, builds, collector, images

# Initialize structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for external connections."""
    logger.info("app_startup_sequence_initiated")
    
    # 1. Check Database connection
    db_ok = await check_database_connection()
    if not db_ok:
        logger.error("database_connection_failed_during_startup")
    else:
        logger.info("database_connection_successful")

    # 2. Check Redis connection
    redis_ok = await check_redis_connection()
    if not redis_ok:
        logger.warning("redis_connection_failed_during_startup")
    else:
        logger.info("redis_connection_successful")

    # 3. Check and initialize MinIO buckets
    try:
        await storage_client.initialize_buckets()
    except Exception as e:
        logger.error("storage_bucket_initialization_failed", error=str(e))

    yield

    # Shutdown sequence
    logger.info("app_shutdown_sequence_initiated")
    await close_redis_client()
    await dispose_engine()
    logger.info("app_shutdown_sequence_completed")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=settings.effective_docs_url,
    redoc_url=settings.effective_redoc_url,
    lifespan=lifespan,
)

# CORS Middleware config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint validating database and cache status."""
    db_status = await check_database_connection()
    redis_status = await check_redis_connection()
    
    overall_status = "healthy" if db_status and redis_status else "degraded"
    
    return JSONResponse(
        status_code=status.HTTP_200_OK if overall_status == "healthy" else status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": overall_status,
            "database": "connected" if db_status else "disconnected",
            "redis": "connected" if redis_status else "disconnected"
        }
    )


# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(bikes.router, prefix=settings.API_V1_PREFIX)
app.include_router(modifications.router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions.router, prefix=settings.API_V1_PREFIX)
app.include_router(builds.router, prefix=settings.API_V1_PREFIX)
app.include_router(collector.router, prefix=settings.API_V1_PREFIX)
app.include_router(images.router, prefix=settings.API_V1_PREFIX)


from fastapi.staticfiles import StaticFiles

# Serve root SPA frontend and static assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(static_dir, "index.html"))

