# AskPDF-AI: PDF Intelligence & Accessibility Platform

## Main Repository: [Click here for AskPDF Backend Codebase](https://github.com/sushilrajeeva/AskPDF-AI_Backend)

AskPDF-AI is a comprehensive Generative AI-powered platform that combines intelligent PDF interaction with accessibility conversion capabilities. This advanced application allows users to not only ask questions about PDF content using Retrieval-Augmented Generation (RAG) but also transform PDFs into accessible formats that comply with accessibility standards.
The platform is built using FastAPI backend architecture with React frontend, containerized using Docker, and deployed using AWS Fargate with a fully automated CI/CD pipeline.

## Current Repository: 
This repository converts PDFs into accessible PDFs. For the RAG and AI PDF chatbot, please click on the [main repository](https://github.com/sushilrajeeva/AskPDF-AI_Backend)

## **How It Works**

![AskPDF-AI](https://github.com/sushilrajeeva/AskPDF-AI_Backend/blob/main/docs/PDF-LangChain.jpg)

## Background & Overview

**AskPDF AI - Core Intelligence Engine**
The primary functionality of AskPDF-AI is a RAG (Retrieval-Augmented Generation) application that processes PDF documents and provides accurate answers to questions based on the content within the PDFs. Users can upload multiple PDFs, and the AI system creates a knowledge base that can be queried through natural language questions.

**PDF Accessibility Converter** Building on the core functionality, this platform now includes PDF accessibility conversion. It is a subset of the work I did at `U.S. Digital Response`, where I built an AI solution for the `Maryland State Department of Education (MSDE)` to convert PDFs into accessible formats using LLMs. The goal is to make digital content more accessible. The accessibility module accepts PDF uploads, extracts `text` and `image` regions via `PyMuPDF`, invokes an `LLM` (through `LangChain`/`OpenAI`) to assign accessibility tags (e.g., `title`, `h1`, `paragraph`, `image`), and returns a structured JSON representation of the tagged document along with basic PDF metadata (author, creation date, etc.). Users can then review the AI-generated tags and generate an accessible PDF.  

**Note:** I am merging both projects into one cohesive platform as it creates a more natural user experience. The accessibility feature represents a subset of the larger project I developed during my time at `U.S. Digital Response`. The current implementation supports limited PDF formats, primarily those with standard formatting structures.

This backend is intended to be paired with a frontend (I have used `React` + `Vite`) and the [AskPDF backend](https://github.com/sushilrajeeva/AskPDF-AI_Backend) that uploads a PDF, displays a loading indicator while the AI processes, and then renders the returned JSON structure to the user.  

---

## AskPDF Intelligence Engine Features
The LangChain-based backend follows these steps to provide responses to your questions:

- **PDF Loading:** The app reads multiple PDF documents and extracts their text content.
- **Text Chunking:** The extracted text is divided into smaller, manageable chunks.
- **Vector Embeddings:** The application generates vector representations (embeddings) for the text chunks.
- **Similarity Matching:** When you ask a question, the app compares it with the text chunks and identifies the most semantically similar ones.
- **Response Generation:** The relevant text chunks are passed to a language model to generate an accurate response.

## Accessibility Features

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

## Tech Stack
**Backend Technologies**
 - FastAPI → Modern, high-performance web framework for Python
 - LangChain → Framework for building LLM-powered applications
 - OpenAI API → Used for embeddings, language modeling, and accessibility tagging
 - FAISS → Vector database for efficient similarity searches
 - PyMuPDF → PDF parsing and region extraction
 - PostgreSQL → Database for storing user and document data
 - Redis → Caching system to optimize performance

**Frontend Technologies**
 - React.js → Modern JavaScript library for building user interfaces
 - Vite → Fast build tool and development server
 - Modern UI Components → Responsive design with file upload and chat interfaces

**Infrastructure & DevOps**
 - Docker → Containerization for consistent deployment
 - AWS Fargate → Serverless container deployment
 - GitHub Actions → Automated CI/CD pipeline
 - Terraform → Infrastructure as code

---

## Installation & Setup

For AskPDF AI backend installation and setup, follow the installation link [link](https://github.com/sushilrajeeva/AskPDF-AI_Backend?tab=readme-ov-file#-installation-and-setup)

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

---

## **🔧 Usage Examples**

### **AskPDF Intelligence**
1. Upload your PDF documents
2. Wait for processing and vector embedding generation
3. Ask questions like:
   - "What are the main conclusions in this research paper?"
   - "Summarize the financial results from Q3"
   - "What methodology was used in this study?"

### **PDF Accessibility Conversion**
1. Upload a PDF file to the `/api/ai-tag` endpoint
2. Receive structured JSON with:
   - Semantic tags for all content regions
   - Proper heading hierarchy
   - Image descriptions and captions
   - Document metadata

---

## **🚀 CI/CD Pipeline**

### **Continuous Integration**
- Automated builds on every push to main branch
- Docker images built and pushed to DockerHub
- Automated testing and code quality checks

### **Continuous Deployment**
- Zero-downtime deployments using AWS Fargate
- Automatic scaling based on demand
- Health checks and rollback capabilities

---

## **🎯 Use Cases**

- **Educational Institutions**: Make course materials accessible while enabling AI-powered study assistance
- **Corporate Training**: Convert training documents and provide intelligent Q&A capabilities
- **Legal & Compliance**: Ensure document accessibility while enabling quick information retrieval
- **Research & Academia**: Process research papers for both accessibility and intelligent analysis
- **Government Agencies**: Transform public documents for accessibility compliance
- **Healthcare**: Make medical documents accessible and searchable

---

## **Frontend Repositories**

For the complete frontend setup and deployment instructions, visit:

👉 **[1. AskPDF-AI Frontend Repository](https://github.com/sushilrajeeva/askpdf-frontend)**

👉 **[1. Accessibility-UI Frontend Repository](https://github.com/sushilrajeeva/accessible-pdf-ui)**

---

## **🤝 Contributing**

I welcome contributions to improve both the intelligence and accessibility features of this platform. Please feel free to submit issues and pull requests.

---

## **📜 License**

The Accessibility and AskPDF platform is released under the [MIT License](https://opensource.org/licenses/MIT).

---
