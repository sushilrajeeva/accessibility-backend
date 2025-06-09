# app/models/schema.py

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PageInfo(BaseModel):
    page: int
    width: float
    height: float

class Span(BaseModel):
    text: str
    font: str
    size: float
    bbox: List[float]
    color: List[float]

class Region(BaseModel):
    page: int
    type: str            # "text" or "image"
    content: str         # text content, or e.g. "<image data>" / base64 string
    bbox: List[float]    # [x0, y0, x1, y1]
    tag: str             # "title", "h1", "paragraph", "image", etc.
    spans: Optional[List[Span]] = None
    # image-specific fields
    xref: Optional[int] = None
    raw_png: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None


# represent standard PDF metadata fields
class PDFMetadata(BaseModel):
    filename: str
    title: Optional[str]
    author: Optional[str]
    subject: Optional[str]
    keywords: Optional[str]
    creator: Optional[str]
    producer: Optional[str]
    creation_date: Optional[str]
    mod_date: Optional[str]

class TagResponse(BaseModel):
    pages: List[PageInfo]
    structure: List[Region]
    metadata: PDFMetadata
