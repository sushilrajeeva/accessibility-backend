# app/models/schema.py

from pydantic import BaseModel
from typing import List, Optional, Dict

class Region(BaseModel):
    page: int
    type: str            # "text" or "image"
    content: str         # text content, or e.g. "<image data>" / base64 string
    bbox: List[float]    # [x0, y0, x1, y1]
    tag: str             # "title", "h1", "paragraph", "image", etc.

# represent standard PDF metadata fields
class PDFMetadata(BaseModel):
    title: Optional[str]
    author: Optional[str]
    subject: Optional[str]
    keywords: Optional[str]
    creator: Optional[str]
    producer: Optional[str]
    creation_date: Optional[str]
    mod_date: Optional[str]

class TagResponse(BaseModel):
    structure: List[Region]
    metadata: PDFMetadata
