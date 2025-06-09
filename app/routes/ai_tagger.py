# app/routes/ai_tagger.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from app.services.extractor import extract_regions, extract_metadata, extract_page_info
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
    filename  = file.filename   
    # 2) Read PDF bytes
    pdf_bytes = await file.read()

    # 3) Extract page dimensions
    pages = extract_page_info(pdf_bytes)

    # 4) Extract regions (text blocks & images) with spans
    regions = extract_regions(pdf_bytes)

    # 5) Classify each region with AI
    tagged = await classify_regions(regions)

    # 6) Extract PDF metadata
    raw_meta = extract_metadata(pdf_bytes, filename)
    meta_obj = PDFMetadata(**raw_meta)

    # 7) Return combined JSON
    return JSONResponse(content={
        "pages": pages,
        "structure": tagged,
        "metadata": meta_obj.model_dump()
    })
