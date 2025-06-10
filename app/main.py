# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.ai_tagger import router as ai_router
from app.routes.pdf_generator import router as pdf_router
from app.core.logging import init_logging
from app.core.config import settings

# 1) Initialize structured logging
init_logging()

# 2) Create the FastAPI app with your project metadata
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=getattr(settings, "PROJECT_DESCRIPTION", None),
)

# 2.1) Enable CORS so the frontend at localhost:5173 can talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # your Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3) Mount the AI-Tagger routes under /api
app.include_router(
    ai_router,
    prefix="/api",
    tags=["AI Tagger"]
)

# 4) Mount PDF-generator routes
app.include_router(pdf_router, prefix="/api", tags=["PDF Generator"])

# (Optional) You could add a root health check here as well:
@app.get("/", summary="Root health check")
async def root():
    return {"status": "ok", "message": "PDF AI Tagger is running"}
