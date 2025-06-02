# Accessibility-Backend

## Overview

**Accessibility-Backend** is a FastAPI service that powers an AI-driven PDF accessibility tagging prototype. It accepts PDF uploads, extracts text/image regions via PyMuPDF, invokes an LLM (through LangChain/OpenAI) to assign accessibility tags (e.g., `title`, `h1`, `paragraph`, `image`, etc.), and returns a structured JSON representation of the tagged document along with basic PDF metadata (author, creation date, etc.).  

This backend is intended to be paired with a frontend (e.g., React/Vite) that uploads a PDF, displays a loading indicator while the AI processes, and then renders the returned JSON structure to the user.  

---

## Features

- **PDF Parsing & Region Extraction**  
  - Uses [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`) to parse each page into “regions” (text blocks and embedded images).  
  - Normalizes bounding boxes (`bbox`) and sorts regions in reading order (top→bottom, left→right).  
  - Encodes images as Base64 data URIs for JSON transport.

- **AI-Powered Tagging**  
  - Leverages [LangChain](https://python.langchain.com/) and `ChatOpenAI` (OpenAI) to classify each region as one of:  
    ```text
    title, subtitle, h1, h2, h3, h4, h5, h6, paragraph, image_caption, image, header, footer, form_label, checkbox
    ```
  - Runs classification asynchronously for all regions in parallel.

- **PDF Metadata Extraction**  
  - Extracts standard PDF metadata (e.g., `author`, `creation_date`, `mod_date`, `creator`, etc.) and includes it alongside the tagged structure in the JSON response.

- **Structured Logging & Configuration**  
  - Uses Pydantic-Settings (`pydantic_settings.BaseSettings`) to drive configuration from a `.env` file.  
  - Initializes timestamped INFO-level logging to stdout via a custom `init_logging()` function.

- **CORS Support**  
  - Configured to allow cross-origin requests from a frontend dev server (e.g., `http://localhost:5173`) or any specified origin.

---

## Minimum Requirements

- **Python 3.11+**  
- **pip** (Python package installer)  
- **git** (for cloning the repository)  

---

## Installation & Setup

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/<your-org>/accessibility-backend.git
   cd accessibility-backend
   ```

2. **Create & Activate a Virtual Environment**
```bash
python3.11 -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows PowerShell
```
3. **Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
4. **Create a .env File at Project Root**
Copy the sample below into a file named .env:
```bash
OPENAI_API_KEY=sk-your_openai_api_key_here
LLM_MODEL_NAME=gpt-4o-mini
LLM_TEMPERATURE=0.0
PROJECT_NAME="PDF AI Tagger"
VERSION="0.1.0"
PROJECT_DESCRIPTION="FastAPI service for AI-based PDF tagging"
```
- OPENAI_API_KEY must be set to your OpenAI API key.

- LLM_MODEL_NAME can be any model name supported by langchain_openai.ChatOpenAI.

- LLM_TEMPERATURE controls inference randomness (0.0 for deterministic).
6. **Verify Configuration**
  Make sure your .env is located at the repository root and contains the correct values. The backend will load these automatically on startup.

**Running Locally**

1. **Without Docker**
- Start Uvicorn (Dev Mode)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
* --reload watches for file changes and restarts automatically.

* By default, CORS is enabled for http://localhost:5173, so make sure your frontend runs on that origin during development.

- Health Check

Visit:

GET http://127.0.0.1:8000/ →

```json
{ "status": "ok", "message": "PDF AI Tagger is running" }
```

GET http://127.0.0.1:8000/api/ping →
```json
{ "pong": "true" }
```

Tag a PDF
Use curl, Postman, or your frontend to POST a file to:

```
POST http://127.0.0.1:8000/api/ai-tag
Content-Type: multipart/form-data
Form field: file (PDF)
```

Response body (Simplified): 

```json
{
  "structure": [
    {
      "page": 1,
      "type": "text",
      "bbox": [72.0, 345.0, 495.0, 360.0],
      "content": "This is a paragraph…",
      "tag": "paragraph"
    },
    // …more regions…
  ],
  "metadata": {
    "title": "My Document",
    "author": "Jane Doe",
    "subject": "",
    "keywords": "",
    "creator": "Microsoft Word",
    "producer": "PDF Producer",
    "creation_date": "D:20250519045555-07'00'",
    "mod_date": "D:20250519045555-07'00'"
  }
}
```

2. **With Docker**
Build the Docker Image
```bash
docker build -t accessibility-backend:latest .
```
3. **Run the Container Locally**
```bash
docker run --rm -it \
  -p 8000:8000 \
  --env-file .env \
  accessibility-backend:latest
```
Exposes port 8000 and injects environment variables from your local .env.

3. **Test Endpoints**

GET http://localhost:8000/ → health check

GET http://localhost:8000/api/ping → “pong”

POST http://localhost:8000/api/ai-tag with a PDF file → JSON structure + metadata

4. **Project Structure**
```
accessibility-backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic-Settings for ENV-driven config
│   │   └── logging.py          # Structured logging setup
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schema.py           # Pydantic models: Region, TagResponse
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── ai_tagger.py        # `/api/ping` & `/api/ai-tag` endpoints
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── classifier.py       # LangChain/OpenAI tagging logic
│   │   └── extractor.py        # PyMuPDF region & metadata extraction
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py          # bbox normalization, sorting, base64 encoding
│   │
│   ├── __init__.py
│   └── main.py                 # FastAPI app + CORS setup + router mounting
│
├── .env                        # Environment variables (not checked into VCS)
├── .gitignore
├── README.md                   # ← This file
├── requirements.txt            # Python dependencies
└── Dockerfile                  # Multi-stage build for production
```
5. 

6. 
