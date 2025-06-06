# app/services/extractor.py

import fitz  # PyMuPDF
from typing import List, Dict
from app.utils.helpers import sort_regions, encode_pixmap_to_base64, normalize_bbox

def extract_regions(pdf_bytes: bytes) -> List[Dict]:
    """
    Parse the PDF into “regions” (text blocks and images),
    each with page number, bbox, type, and content.
    Uses helpers to normalize bbox and encode images.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    regions: List[Dict] = []

    for page_no, page in enumerate(doc, start=1):
        # Text blocks
        for block in page.get_text("blocks"):
            bbox = normalize_bbox(block)
            text = block[4].strip()
            if not text:
                continue
            # Heuristic: common label format (e.g., "Email:", "Name:")
            region_type = "form_label" if text.endswith(":") and len(text.split()) <= 3 else "text"

            regions.append({
                "page": page_no,
                "type": region_type,
                "bbox": bbox,
                "content": text,
            })

        # Images
                # Images (check for small square boxes as potential checkboxes)
        for img_meta in page.get_images(full=True):
            xref = img_meta[0]
            bbox = normalize_bbox(img_meta)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]

            pix = fitz.Pixmap(doc, xref)
            data_uri = encode_pixmap_to_base64(pix)
            pix = None  # free memory

            # Heuristic: small square (e.g., < 20x20 px) = checkbox
            if abs(width - height) < 3 and width < 25 and height < 25:
                region_type = "checkbox"
            else:
                region_type = "image"

            regions.append({
                "page": page_no,
                "type": region_type,
                "bbox": bbox,
                "content": data_uri,
            })


    # close the document to release resources
    doc.close()

    # Sort in reading order
    return sort_regions(regions)

def extract_metadata(pdf_bytes: bytes) -> Dict[str, str]:
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
        "title":          raw_meta.get("title", ""),
        "author":         raw_meta.get("author", ""),
        "subject":        raw_meta.get("subject", ""),
        "keywords":       raw_meta.get("keywords", ""),
        "creator":        raw_meta.get("creator", ""),
        "producer":       raw_meta.get("producer", ""),
        "creation_date":  raw_meta.get("creationDate", ""),
        "mod_date":       raw_meta.get("modDate", ""),
    }
