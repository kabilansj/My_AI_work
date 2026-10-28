"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .models import Document, Extraction, DbMedication, DbDiagnosis, DbInvestigation, DbAllergy, AuditLog
from .routers import documents, extractions, review


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(documents.router)
app.include_router(extractions.router)
app.include_router(review.router)


@app.get("/api/health")
def health_check():
    """Service health verification."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version,
        "database": settings.database_url.split("://")[0],
        "default_engine": settings.default_engine,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
