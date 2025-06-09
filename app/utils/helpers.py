# app/utils/helpers.py

import base64
from typing import List, Dict, Any

# Helper to turn PyMuPDF’s color‐int into [r,g,b] floats
def int_to_rgb(color_int: int) -> List[float]:
    # PDF colors in PyMuPDF come as 0xRRGGBB integers
    r = (color_int >> 16) & 0xFF
    g = (color_int >> 8)  & 0xFF
    b = (color_int >> 0)  & 0xFF
    # normalize to 0.0–1.0
    return [r / 255.0, g / 255.0, b / 255.0]


def sort_regions(regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort regions in “reading order”:
      1) page number (ascending)
      2) y-coordinate (descending, so top of page first)
      3) x-coordinate (ascending, so left-to-right)
    """
    return sorted(
        regions,
        key=lambda r: (
            r["page"],
            -r["bbox"][1],  # y0 descending
            r["bbox"][0],   # x0 ascending
        )
    )

def encode_pixmap_to_base64(pixmap) -> str:
    """
    Given a PyMuPDF Pixmap, convert to PNG bytes then Base64.
    Returns a data URI string you can stick into JSON.
    """
    png_bytes = pixmap.tobytes("png")
    b64 = base64.b64encode(png_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def normalize_bbox(block: Any) -> List[float]:
    """
    Given a fitz block tuple or an image metadata tuple, extract
    and return the bbox as [x0, y0, x1, y1].
    """
    # block[:4] works for text-blocks (x0,y0,x1,y1, ...)
    # image metadata is often (xref, x0, y0, x1, y1, ...), so skip index 0
    coords = block[:4] if hasattr(block, "__len__") and len(block) >= 4 else block[1:5]
    return [float(c) for c in coords]
