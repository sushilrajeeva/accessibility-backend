# app/routes/pdf_generator.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io

from app.services.generator import generate_pdf_from_json

router = APIRouter()

@router.post("/generate_pdf", summary="Generate accessible PDF from JSON")
async def generate_pdf(json_payload: dict):
    """
    Accept the verified JSON (pages / structure / metadata) and
    return a remediated, tagged PDF.
    """
    print("I work inside generate pdf....")
    try:
        pdf_bytes = generate_pdf_from_json(json_payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"PDF generation failed: {exc}")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="remediated.pdf"'},
    )
