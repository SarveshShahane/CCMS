from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis

from app.config.db import get_db
from app.config.redis_conf import get_redis
from app.routes.file import router as file_router
from app.routes.chat import router as chat_router
from app.routes.complaint import router as complaint_router

app = FastAPI(
    title="CCMS API",
    description="Customer Complaint Management System - API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(file_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(complaint_router, prefix="/api/v1")




@app.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    cache: redis.Redis = Depends(get_redis),
):
    health_status = {
        "status": "healthy",
        "services": {
            "postgres": "unknown",
            "redis": "unknown",
        },
    }

# pgsql healthcheck
    try:
        await db.execute(text("SELECT 1"))
        health_status["services"]["postgres"] = "healthy"
    except Exception as e:
        health_status["services"]["postgres"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

#  Redis healthcheck
    try:
        ping_result = await cache.ping()
        if ping_result:
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "unhealthy"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    if health_status["status"] != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status,
        )

    return health_status
