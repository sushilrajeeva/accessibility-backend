# app/services/generator.py
"""
Generate an accessible (tagged) PDF from the verified JSON structure
using the borb library.
"""
from __future__ import annotations

import base64
import io
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Any

from borb.pdf import Document, Page, PDF
from borb.pdf.canvas.geometry.rectangle import Rectangle
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.canvas.layout.text.chunk_of_text import ChunkOfText
from borb.pdf.canvas.layout.image.image import Image
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.text.heterogeneous_paragraph import (HeterogeneousParagraph)


from app.utils.helpers import (
    float_rgb_to_hex,
    map_tag_to_role,
    convert_bbox_top_to_bottom,
    _assign_role,
)

# ---------------------------------------------------------------------------
# Optionally cache custom fonts so we don't reload on every span
# ---------------------------------------------------------------------------
_FONT_CACHE: Dict[str, Any] = {}


def _resolve_font(font_name: str) -> str | TrueTypeFont:
    """
    Return a font usable by borb:
    - If it's one of the 14 standard PDF fonts, just return the name.
    - Otherwise try to load/ cache a .ttf from ./fonts/<font_name>.ttf
      (you can adapt the lookup path).
    Fallback to Helvetica if not found.
    """
    std_fonts = {
        "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
        "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
        "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
        "Symbol", "ZapfDingbats"
    }
    if font_name in std_fonts:
        return font_name

    if font_name in _FONT_CACHE:
        return _FONT_CACHE[font_name]

    # expect font files as ./fonts/<font_name>.ttf  (case-sensitive)
    font_path = Path(__file__).resolve().parent.parent / "fonts" / f"{font_name}.ttf"
    if font_path.exists():
        _FONT_CACHE[font_name] = TrueTypeFont.open(font_path)
        return _FONT_CACHE[font_name]

    # Fallback
    return "Helvetica"


def _build_text_element(span_list: List[Dict[str, Any]]) -> Paragraph:
    """
    Build a Paragraph (plain or multi-styled) from JSON spans.
    """
    # For single-span
    if len(span_list) == 1:
        s = span_list[0]
        font_obj = _resolve_font(s["font"])
        color = float_rgb_to_hex(s["color"])
        return Paragraph(
            s["text"],
            font=font_obj,
            font_size=Decimal(s["size"]),
            font_color=color,
        )


    # For multi-span (mixed style)
    chunks = []
    for s in span_list:
        font_obj = _resolve_font(s["font"])
        color = float_rgb_to_hex(s["color"])
        chunks.append(
            ChunkOfText(
                s["text"],
                font=font_obj,
                font_size=Decimal(s["size"]),
                font_color=color,
            )
        )

    # Paragraph now accepts the list *positional* (no kw arg)
    return _multi_span_paragraph(chunks)


def _add_image_to_page(
    page: Page, region: Dict[str, Any], page_height: float
) -> None:
    """
    Decode the base64 PNG and add it as an InlineImage with correct bbox.
    """
    x, y, w, h = convert_bbox_top_to_bottom(region["bbox"], page_height)
    img_bytes = base64.b64decode(region["raw_png"])
    img_stream = io.BytesIO(img_bytes)
    image = Image(
        img_stream,  # file-like object or path
        width = w,
        height = h,
    )
    _assign_role(image, map_tag_to_role(region.get("tag", "image")))
    image.paint(page, Rectangle(x, y, w, h))


def generate_pdf_from_json(data: Dict[str, Any]) -> bytes:
    """
    Main entry: pass the verified JSON, return PDF bytes.
    """
    # 1. Create document and set metadata
    doc = Document()
    info = doc.get_document_info()
    meta = data.get("metadata", {})
    info.title = meta.get("title", "")
    info.author = meta.get("author", "")
    info.subject = meta.get("subject", "")
    info.keywords = meta.get("keywords", "")
    # Set language if you have it:  info.language = "en-US"

    # Group regions by page for easier processing
    regions_by_page: Dict[int, List[Dict[str, Any]]] = {}
    for r in data["structure"]:
        regions_by_page.setdefault(r["page"], []).append(r)

    # 2. Iterate pages
    for page_def in data["pages"]:
        page_w = Decimal(page_def["width"])
        page_h = Decimal(page_def["height"])
        page = Page(width=page_w, height=page_h)
        doc.add_page(page)

        # Render every region on this page
        for region in regions_by_page.get(page_def["page"], []):
            tag = region.get("tag", "paragraph").lower()

            if region["type"] == "image" or tag == "image":
                # Handle image (or checkbox if you want separate logic)
                _add_image_to_page(page, region, float(page_h))
                continue

            # Build paragraph(s) from spans
            para = _build_text_element(region["spans"])
            _assign_role(para, map_tag_to_role(tag))

            # Placement rectangle
            x, y, w, h = convert_bbox_top_to_bottom(region["bbox"], float(page_h))

            # add small safety margin so text always fits
            h += Decimal(4)          # 4 pt ≈ 1.4 mm
            # # guarantee enough height
            # h = max(h, page_h - y)     # stretch down to bottom if needed

            
            para.paint(page, Rectangle(x, y, w, h))

    # 3. Serialize to bytes
    pdf_bytes = io.BytesIO()
    PDF.dumps(pdf_bytes, doc)
    return pdf_bytes.getvalue()

def _multi_span_paragraph(chunks: List[ChunkOfText]) -> HeterogeneousParagraph:
    return HeterogeneousParagraph(chunks=chunks)


