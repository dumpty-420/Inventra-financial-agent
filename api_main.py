"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.assistant import router as assistant_router
from config.settings import get_settings
from config.logger import get_logger

logger = get_logger(__name__)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Inventra AI API",
        description="API for Intelligent Inventory and Financial Management Assistant",
        version="1.0.0"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(assistant_router, prefix="/api/v1/assistant", tags=["assistant"])

    @app.get("/")
    async def root():
        return {
            "message": "Welcome to Inventra AI API",
            "docs": "/docs",
            "version": "1.0.0"
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_main:app", host="0.0.0.0", port=8000, reload=True)
