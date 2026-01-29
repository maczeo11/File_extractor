```markdown
# 🚀 Universal Text Extractor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![OCR](https://img.shields.io/badge/OCR-Tesseract-green)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-orange)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

A full-stack document text extraction system that intelligently extracts text from PDFs, Images, Word files, Excel/CSV tables,
and HTML using OCR and format-aware extraction strategies, and returns a standardized structured JSON output.

</div>

---

## 📌 Overview

Universal Text Extractor is designed to handle real-world documents that may contain native text, scanned pages, embedded images, and tables.  
The system automatically detects the file type, applies the appropriate extraction strategy, falls back to OCR when required, and produces a consistent JSON output schema for all supported formats.

The project consists of a FastAPI backend and a modern drag-and-drop frontend.

---

## ✨ Features

- Supports **PDF, DOCX, XLSX, CSV, TXT, PNG, JPG, HTML**
- OCR using **Tesseract** with OpenCV preprocessing
- Strategy Design Pattern for modular extractors
- MIME-based file type detection with extension fallback
- Page-wise, row-wise, and sheet-wise extraction
- OCR for embedded images in PDFs and Word documents
- FastAPI REST API
- Modern drag-and-drop frontend UI
- Frontend supports File selection
- Docker-ready backend

---

## 🏗️ System Architecture

```

Web Frontend (HTML / CSS / JavaScript)
│
│  File selected
│  
▼
FastAPI Backend
│
│  MIME Detection (libmagic)
▼
Extractor Router (Strategy Pattern)
│
├── PDFExtractor
│     ├── Native text extraction
│     ├── Embedded image OCR
│     └── Full-page OCR fallback
│
├── WordExtractor
│     ├── Paragraph text
│     ├── Table rows
│     └── Inline image OCR
│
├── ImageExtractor (OCR)
├── TableExtractor (Excel / CSV)
└── HTMLExtractor
│
▼
Standardized JSON Output

```

---

## 🛠️ Tech Stack

### Backend
- Python 3.9+
- FastAPI
- Tesseract OCR
- OpenCV
- PDFPlumber
- python-docx
- Pandas
- BeautifulSoup
- libmagic

### Frontend
- HTML5, CSS3, JavaScript
- Drag-and-drop file upload
- Sequential processing queue for multiple files

### DevOps
- Docker
- requirements.txt
- MIT License

---

## 📁 Project Structure

```

FILE_EXTRACTOR/
│
├── app/
│   ├── extractors/
│   │   ├── base.py        # Abstract extractor interface
│   │   ├── documents.py  # PDF & Word extraction logic
│   │   ├── images.py     # OCR image extractor
│   │   ├── tables.py     # Excel / CSV extractor
│   │   └── web.py        # HTML extractor
│   │
│   ├── schemas.py        # Standardized response models
│   ├── utils.py          # OCR preprocessing utilities
│   └── main.py           # FastAPI application
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── test_files/
│   └── Experiment-1.pdf
│
├── Dockerfile
├── requirements.txt
├── LICENSE
└── README.md

````

---

## ⚙️ How It Works

1. User select file in the frontend
2. Frontend send file to the backend
3. Backend detects the file type using MIME detection
4. The appropriate extractor is selected
5. OCR is applied when native text is unavailable
6. Extracted data is normalized into a common schema
7. Structured JSON is returned and rendered in the UI

---

## 🔌 API Reference

### POST `/api/extract`

Extract text from a single uploaded file.

**Request**
- `multipart/form-data`
- Field name: `file`

**Supported Formats**
- PDF
- DOCX
- XLSX
- CSV
- TXT
- PNG / JPG
- HTML

**Response**
```json
{
  "filename": "sample.pdf",
  "file_type": "pdf",
  "processing_time_ms": 124.83,
  "content": [
    {
      "text": "Extracted text",
      "source": "page_1",
      "location": {
        "type": "page",
        "number": 1
      }
    }
  ]
}
````

---

## 📦 Output Schema

* **DocumentResponse** – One processed document
* **ExtractedUnit** – Atomic unit of extracted text
* **Location** – Context-aware metadata (`page`, `row`, `pixel_box`)

---

## 🚀 Running the Server

### Prerequisites

* Python 3.9+
* Tesseract OCR installed
* Dependencies installed via `requirements.txt`

### Start the FastAPI Server

From the project root directory:

```bash
python -m uvicorn app.main:app --reload
```

### Access

* API Base URL: `http://localhost:8000`
* Health Check: `http://localhost:8000/`
* Swagger Docs: `http://localhost:8000/docs`

---

## 🐳 Docker Support

```bash
docker build -t universal-text-extractor .
docker run -p 8000:8000 universal-text-extractor
```

---

## 📌 Use Cases

* Academic document digitization
* OCR for scanned lab records
* Resume and report parsing
* Backend document-processing pipelines
* Automation and data extraction systems

---

## ⚠️ Current Limitations

* Backend processes one file per API request
* Multiple files are handled sequentially by the frontend
* Bounding box visualization is not exposed in the UI

---

## 🚧 Future Enhancements

* Native multi-file backend API
* Language detection
* Bounding box visualization
* Export results as JSON / TXT
* Cloud-native scaling

---

## 📄 License

This project is licensed under the MIT License.

---

