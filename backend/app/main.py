from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base
from .routers import auth, doctor, nurse, patient, admin

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Centralized Hospital Platform with AI-based Patient Monitoring",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(doctor.router, prefix=settings.API_V1_PREFIX)
app.include_router(nurse.router, prefix=settings.API_V1_PREFIX)
app.include_router(patient.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "message": "Med-Chatbot Hospital Platform API is running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }
