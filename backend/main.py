import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.database import engine, Base
from backend.api import (
    routes_health,
    routes_models,
    routes_conversations,
    routes_chat,
    routes_documents,
    routes_search,
    routes_audio,
    routes_settings
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("chatbot")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure directories and DB tables
    logger.info("Initializing Multimodal AI Chatbot backend...")
    settings.ensure_directories()
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schemas verified and initialized.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    yield
    logger.info("Shutting down backend...")

app = FastAPI(
    title="Multimodal AI Chatbot API",
    description="High-performance backend API supporting multimodal chat (text, vision, documents RAG, voice, and web search).",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"  # Permissive for local development ease
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(routes_health.router)
app.include_router(routes_models.router)
app.include_router(routes_conversations.router)
app.include_router(routes_chat.router)
app.include_router(routes_documents.router)
app.include_router(routes_search.router)
app.include_router(routes_audio.router)
app.include_router(routes_settings.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please check server logs."}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.APP_DEBUG
    )

