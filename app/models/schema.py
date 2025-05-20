# app/models/schema.py

from pydantic import BaseModel
from typing import List

class Region(BaseModel):
    page: int
    type: str            # "text" or "image"
    content: str         # text content, or e.g. "<image data>" / base64 string
    bbox: List[float]    # [x0, y0, x1, y1]
    tag: str             # "title", "h1", "paragraph", "image", etc.

class TagResponse(BaseModel):
    structure: List[Region]
