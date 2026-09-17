import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from backend.api.routes import router as api_router

load_dotenv()

app = FastAPI(
    title="Nova PPT Gen API",
    description="Stateless Agentic AI PowerPoint generator backend powered by LangGraph, ChatGroq, and python-pptx.",
    version="1.0.0",
)

# Configure CORS for local development and future Next.js/React frontend
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://*.vercel.app",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("ENVIRONMENT") == "development" else allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router)

# Serve index.html at the project root
_ROOT = Path(__file__).parent.parent  # project root (one level above backend/)
_INDEX = _ROOT / "index.html"


@app.get("/")
def root():
    """Serve the frontend index.html if it exists, otherwise return API info."""
    if _INDEX.exists():
        return FileResponse(str(_INDEX), media_type="text/html")
    return {
        "service": "Nova PPT Gen API",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Silence browser default favicon 404."""
    return Response(status_code=204)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
