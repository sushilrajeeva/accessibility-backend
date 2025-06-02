# app/routes/ai_tagger.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from app.services.extractor import extract_regions, extract_metadata
from app.services.classifier import classify_regions
from app.models.schema import TagResponse, PDFMetadata

router = APIRouter()

@router.get(
    "/ping",
    summary="Health check endpoint",
    tags=["Health"],
)
async def ping():
    """
    Simple health check to verify the API is up.
    """
    return {"pong": "true"}

@router.post(
    "/ai-tag",
    response_model=TagResponse,
    summary="Upload a PDF and get back AI-suggested accessibility tags + metadata",
)
async def ai_tag(file: UploadFile = File(...)):
    # 1) Validate input
    if file.content_type != "application/pdf":
        raise HTTPException(
            HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted."
        )
    print("pdf recieved ....")
    # 2) Read PDF bytes
    pdf_bytes = await file.read()

    # 3) Extract regions (text blocks & images)
    regions = extract_regions(pdf_bytes)

    # 4) Classify each region with AI
    tagged = await classify_regions(regions)

    # 5) Extract PDF metadata
    raw_meta = extract_metadata(pdf_bytes)
    meta_obj = PDFMetadata(**raw_meta)

    # 6) Return combined JSON
    return JSONResponse(content={
        "structure": tagged,
        "metadata": meta_obj.model_dump()
    })
