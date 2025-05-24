# api/ai_tag.py
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.services.extractor   import extract_regions
from app.services.classifier  import classify_regions

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"pong": "true"}

@app.post("/ai-tag")
async def ai_tag(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are accepted.")
    pdf_bytes = await file.read()
    regions   = extract_regions(pdf_bytes)
    tagged    = await classify_regions(regions)
    return JSONResponse({"structure": tagged})

# this is the entrypoint for Vercel
handler = Mangum(app)
