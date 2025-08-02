# Event Networking AI System - Main Application
"""
FastAPI application entry point for the Event Networking AI System.
Provides AI-powered networking recommendations and clustering analysis.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from api.routes import router
from database.connection import init_database
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting Event Networking AI System")
    try:
        init_database()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Event Networking AI System")

# Create FastAPI application
app = FastAPI(
    title="Event Networking AI System",
    description="""
    An intelligent AI-powered event networking and recommendation system that helps 
    attendees find meaningful connections at events through advanced machine learning 
    algorithms and network analysis.
    
    ## Features
    
    * ** AI-Powered Recommendations**: TF-IDF vectorization and cosine similarity
    * **🕸Network Clustering**: Community detection for attendee grouping
    * ** Analytics**: Comprehensive event and user analytics
    * ** Visualization**: Data export for visualization tools
    
    ## Core Algorithms
    
    - **Text Processing**: TF-IDF vectorization of user profiles
    - **Similarity Calculation**: Cosine similarity for user matching
    - **Community Detection**: Louvain, Girvan-Newman algorithms
    - **Recommendation Scoring**: Multi-factor similarity scoring
    """,
    version="1.0.0",
    contact={
        "name": "PopIn Development Team",
        "email": "dev@letspopin.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=f"/api/{settings.api_version}")

@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - System information and health check
    """
    return {
        "message": "Event Networking AI System",
        "version": app.version,
        "status": "running",
        "description": "AI-powered event networking and recommendation service",
        "endpoints": {
            "health": "/health",
            "api_docs": "/docs",
            "api_spec": "/openapi.json",
            "api_base": f"/api/{settings.api_version}"
        }
    }

@app.get("/health", tags=["System"])
async def health_check():
    """
    System health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Event Networking AI",
        "version": app.version,
        "timestamp": "2025-07-31T20:00:00Z"
    }

@app.get("/info", tags=["System"])
async def system_info():
    """
    Detailed system information
    """
    return {
        "system": "Event Networking AI",
        "version": app.version,
        "description": "AI-powered event networking recommendations",
        "features": [
            "TF-IDF text vectorization",
            "Cosine similarity matching",
            "Network clustering analysis",
            "Real-time recommendations",
            "Comprehensive analytics"
        ],
        "algorithms": {
            "recommendation": "TF-IDF + Cosine Similarity",
            "clustering": ["Louvain", "Girvan-Newman", "Label Propagation"],
            "features": ["bio", "interests", "goals", "job_title", "company", "industry"]
        },
        "api": {
            "base_url": f"/api/{settings.api_version}",
            "documentation": "/docs",
            "openapi_spec": "/openapi.json"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return HTTPException(
        status_code=500,
        detail="An internal server error occurred. Please try again later."
    )

if __name__ == "__main__":
    logger.info(" Starting Event Networking AI Server...")
    logger.info(f" Server will be available at: http://localhost:8000")
    logger.info(f" API Documentation: http://localhost:8000/docs")
    logger.info(f" Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )