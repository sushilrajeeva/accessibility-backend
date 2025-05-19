import io
import logging
import fitz  # PyMuPDF
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PDF Extraction API",
    version="0.3.0",
    description="Upload a PDF and log text with manual tags"
)

@app.post("/upload", summary="Upload PDF and extract tagged lines")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(HTTP_400_BAD_REQUEST, "Only PDF files are accepted.")

    # 1. Read bytes & open with PyMuPDF
    data = await file.read()
    doc = fitz.open(stream=data, filetype="pdf")

    # 2. Gather all font sizes
    all_sizes = []
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    all_sizes.append(span["size"])

    unique_sizes = sorted(set(all_sizes), reverse=True)
    logger.info(f"Found font sizes: {unique_sizes}")

    # 3. Manual mapping—replace these with the real values you observe
    FONT_TAG_MAP = {
         26.0: "title",
         20.0: "h1",
         16.0: "h2",
         15.0: "subtitle",
         14.0: "h3",
         12.0: "h4",
         11.0: "p"
     }
    
    DEFAULT_TAG = "h5"

    def infer_tag(font_size: float) -> str:
        # exact match
        if font_size in FONT_TAG_MAP:
            return FONT_TAG_MAP[font_size]
        # find closest if within tolerance
        if FONT_TAG_MAP:
            closest = min(FONT_TAG_MAP.keys(), key=lambda s: abs(s - font_size))
            if abs(closest - font_size) < 1.0:  # tweak tolerance as needed
                return FONT_TAG_MAP[closest]
        return DEFAULT_TAG

    # 4. Second pass: extract, tag, and log
    for page_no, page in enumerate(doc, start=1):
        logger.info(f"\n=== Page {page_no} ===")
        for block in page.get_text("dict")["blocks"]:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                text = "".join(span["text"] for span in line["spans"]).strip()
                if not text:
                    continue
                font_size = line["spans"][0]["size"]
                tag = infer_tag(font_size)
                logger.info(f"<{tag}> <size={font_size}> {text}")

    return JSONResponse({
        "status": "success",
        "message": "PDF processed. Check logs for tagged output."
    })
