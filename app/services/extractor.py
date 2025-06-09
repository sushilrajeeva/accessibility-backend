# app/services/extractor.py

import fitz  # PyMuPDF
from typing import List, Dict
import base64
from app.utils.helpers import sort_regions, encode_pixmap_to_base64, normalize_bbox, int_to_rgb

def extract_page_info(pdf_bytes: bytes) -> List[Dict]:
    """Get each page’s width & height."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for i, page in enumerate(doc, start=1):
        rect = page.rect
        pages.append({
            "page": i,
            "width": rect.width,
            "height": rect.height,
        })

    doc.close()
    return pages

def extract_regions(pdf_bytes: bytes) -> List[Dict]:
    """
    Parse the PDF into “regions” (text blocks and images),
    each with page number, bbox, type, and content.
    Uses helpers to normalize bbox and encode images.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    regions: List[Dict] = []

    for page_no, page in enumerate(doc, start=1):
        # Text blocks with font & size spans
        page_dict = page.get_text("dict")
        for block in page_dict["blocks"]:
            if block.get("type") != 0:
                continue
            bbox = block.get("bbox", [])
            # rebuild text from block.text or spans
            raw_text = block.get("text") or "".join(
                span["text"]
                for line in block.get("lines", [])
                for span in line.get("spans", [])
            )
            text = raw_text.strip()
            if not text:
                continue
            # Heuristic for label vs normal text
            region_type = ("form_label" if text.endswith(":") and len(text.split()) <= 3 else "text")

            # Capture spans (font, size, individual bbox) and also captures color
            spans = []

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    # raw color integer
                    color_int = span.get("color", 0)
                    # convert to [r, g, b]
                    rgb = int_to_rgb(color_int)
                    spans.append({
                        "text": span["text"],
                        "font": span["font"],
                        "size": span["size"],
                        "bbox": span["bbox"],
                        "color": rgb,     # e.g. [0,0,0] for black
                    })



            regions.append({
                "page": page_no,
                "type": region_type,
                "bbox": bbox,
                "content": text,
                "spans": spans,
            })

        # # Image regions (with normalize_bbox, preview & raw PNG) (check for small square boxes as potential checkboxes)
        for img_meta in page.get_images(full=True):
            xref = img_meta[0]
            bbox = normalize_bbox(img_meta)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]

            pix = fitz.Pixmap(doc, xref)

            # 1) Preview URI (small, PNG)
            data_uri = encode_pixmap_to_base64(pix)

            # 2) Raw PNG bytes (full quality) for future regeneration
            png_bytes = pix.tobytes("png")
            raw_b64 = base64.b64encode(png_bytes).decode("utf-8")

            # 3) Pixel dimensions of the image
            img_w, img_h = pix.width, pix.height

            pix = None  # free memory 

            

            # Heuristic: small square = checkbox
            region_type = (
                "checkbox" if abs(width - height) < 3 and width < 25 and height < 25 else "image"
            )

            regions.append({
                "page": page_no,
                "type": region_type,
                "bbox": bbox,
                "content": data_uri,
                "xref": xref,
                "raw_png": raw_b64,
                "image_width": img_w,
                "image_height": img_h,
            })


    # close the document to release resources
    doc.close()

    # Sort in reading order
    return sort_regions(regions)

def extract_metadata(pdf_bytes: bytes, filename: str) -> Dict[str, str]:
    """
    helper function: open the same PDF, read doc.metadata, normalize its keys to snake_case,
    and return that dict. PyMuPDF’s doc.metadata may include:
      'title', 'author', 'subject', 'keywords', 'creator', 'producer',
      'creationDate', 'modDate', etc.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    # meta = doc.metadata or {}
    # doc.close()

    # normalized: Dict[str, str] = {}
    # for k, v in meta.items():
    #     if k == "creationDate":
    #         normalized["creation_date"] = v
    #     elif k == "modDate":
    #         normalized["mod_date"] = v
    #     else:
    #         normalized[k.lower()] = v  # e.g. "title","author","subject","keywords","creator","producer"
    # return normalized
    raw_meta = doc.metadata  # e.g. {'title': '...', 'author': '...', 'creationDate': 'D:20250519045555-07\'00\'', …}
    doc.close()

    # Normalize key names to snake_case that match our Metadata model
    return {
        "filename":       filename,
        "title":          raw_meta.get("title", ""),
        "author":         raw_meta.get("author", ""),
        "subject":        raw_meta.get("subject", ""),
        "keywords":       raw_meta.get("keywords", ""),
        "creator":        raw_meta.get("creator", ""),
        "producer":       raw_meta.get("producer", ""),
        "creation_date":  raw_meta.get("creationDate", ""),
        "mod_date":       raw_meta.get("modDate", ""),
    }
