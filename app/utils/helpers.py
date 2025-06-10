# app/utils/helpers.py

import base64
from typing import List, Tuple, Dict, Any
from decimal import Decimal
from borb.pdf.canvas.color.color import HexColor

def float_rgb_to_hex(rgb_floats: List[float]) -> HexColor:
    """
    JSON stores colors as floats 0-1 → convert to HexColor for borb.
    """
    r, g, b = [int(c * 255) for c in rgb_floats]
    return HexColor("#{0:02x}{1:02x}{2:02x}".format(r, g, b))

# Helper to turn PyMuPDF’s color‐int into [r,g,b] floats
def int_to_rgb(color_int: int) -> List[float]:
    # PDF colors in PyMuPDF come as 0xRRGGBB integers
    r = (color_int >> 16) & 0xFF
    g = (color_int >> 8)  & 0xFF
    b = (color_int >> 0)  & 0xFF
    # normalize to 0.0–1.0
    return [r / 255.0, g / 255.0, b / 255.0]

ROLE_MAP = {
    "title": "Title",
    "subtitle": "H1",          # or "Subtitle" – PDF/UA doesn’t define it
    "h1": "H1",
    "h2": "H2",
    "h3": "H3",
    "h4": "H4",
    "h5": "H5",
    "h6": "H6",
    "paragraph": "P",
    "image": "Figure",
    "image_caption": "Caption",
    "form_label": "Lbl",
    "checkbox": "Form"
}

def map_tag_to_role(tag: str) -> str:
    """
    Map our JSON tags to PDF/UA structure element roles.
    Defaults to Paragraph (P) if unknown.
    """
    return ROLE_MAP.get(tag.lower(), "P")

# def convert_bbox_top_to_bottom(
#     bbox: List[float], page_height: float
# ) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
#     """
#     MuPDF and borb both use a top-left origin for layout, so we can keep
#     the coordinates unchanged: (x0, y0, width, height).
#     """
#     x0, y0, x1, y1 = bbox
#     width  = x1 - x0
#     height = y1 - y0
#     return (Decimal(x0), Decimal(y0), Decimal(width), Decimal(height))

def convert_bbox_top_to_bottom(
    bbox: List[float], page_height: float
) -> Tuple[Decimal, Decimal, Decimal, Decimal]:
    """
    Convert MuPDF bbox (x0, y0, x1, y1) where y0 is from top-edge downward,
    into borb rectangle (x, y, w, h) where y is from bottom-edge upward.
    """
    x0, y0, x1, y1 = bbox
    width  = x1 - x0
    height = y1 - y0                 # same in both systems
    # y coordinate in borb = distance from bottom of page to *bottom* of bbox
    y_borb = page_height - y1        # page_height minus bbox‐bottom
    return (Decimal(x0), Decimal(y_borb), Decimal(width), Decimal(height))


def _assign_role(layout_obj, role_str: str) -> None:
    """
    Call whichever role-setter the installed borb version provides.
    Silently no-ops if none found (worst-case: PDF is untagged but still renders).
    """
    if hasattr(layout_obj, "set_role"):
        layout_obj.set_role(role_str)
    elif hasattr(layout_obj, "set_semantic_role"):
        layout_obj.set_semantic_role(role_str)
    elif hasattr(layout_obj, "set_pdf_role"):
        layout_obj.set_pdf_role(role_str)

def _ensure_rect_height(para, w: Decimal, h: Decimal) -> Decimal:
    """
    Ask borb how high the paragraph really is.  If the installed borb
    doesn’t expose `.get_size`, skip the check and keep original height.
    """
    if hasattr(para, "get_size"):
        try:
            _, h_needed = para.get_size((int(w), 2 ** 31))
            if h_needed > h:
                print("ok here!!!")
                return Decimal(h_needed)
        except Exception:
            pass
    return h


def sort_regions(regions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort regions in natural reading order:
      1) page number (ascending)
      2) y-coordinate (ascending -- top first)
      3) x-coordinate (ascending -- left-to-right)
    """
    return sorted(
        regions,
        key=lambda r: (
            r["page"],
            r["bbox"][1],   # y0 ascending  (top first)
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
