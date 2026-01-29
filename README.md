
```markdown
# 🚀 Universal Text Extractor

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![OCR](https://img.shields.io/badge/OCR-Tesseract-green)
![OpenCV](https://img.shields.io/badge/OpenCV-Image%20Processing-orange)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A high-performance, full-stack document extraction engine.**

Intelligently parse PDFs, Images, Word documents, and Tables into standardized JSON using OCR and format-aware extraction strategies.

</div>

---

## 📌 Overview

**Universal Text Extractor** is a robust solution for digitizing unstructured documents. Whether dealing with a "searchable" PDF, a scanned JPG, or a complex Excel spreadsheet, this system abstracts the complexity behind a single API endpoint.

By utilizing a **Strategy Design Pattern**, the backend dynamically selects the most efficient extraction method based on the file's MIME type, falling back to Tesseract OCR only when native text extraction is unavailable.

---

## ✨ Features

* **Multi-Format Support:** PDF, DOCX, XLSX, CSV, TXT, PNG, JPG, HTML.
* **Intelligent OCR:** Powered by **Tesseract** with **OpenCV** grayscale and thresholding preprocessing.
* **Hybrid Extraction:** Extracts native text from PDFs/Word but switches to OCR for embedded images within those documents.
* **Structured Output:** Every file type returns a uniform JSON schema for easy downstream integration.
* **Modern UI:** Drag-and-drop frontend with a real-time processing queue.
* **Containerized:** Fully Dockerized for seamless deployment.

---

## 🏗️ System Architecture



```text
  [ Web Frontend ] ----( Multipart Form Data )----> [ FastAPI Backend ]
                                                           │
                                                   [ MIME Type Detector ]
                                                           │
                                               [ Extractor Router (Strategy) ]
                                                           │
                ┌──────────────────┬───────────────────────┼───────────────────┐
                │                  │                       │                   │
        [PDF Extractor]    [Word Extractor]        [Image Extractor]    [Table Extractor]
        (Native + OCR)      (XML + OCR)             (OpenCV + OCR)       (Pandas/CSV)
                │                  │                       │                   │
                └──────────────────┴───────────┬───────────┴───────────────────┘
                                               │
                                    [ Standardized JSON Response ]

```

---

## 📁 Project Structure

```text
FILE_EXTRACTOR/
├── app/
│   ├── extractors/
│   │   ├── base.py         # Abstract Base Class (ABC) for Strategy Pattern
│   │   ├── documents.py    # Logic for PDF (pdfplumber) and Word (python-docx)
│   │   ├── images.py       # Tesseract OCR & OpenCV processing
│   │   ├── tables.py       # Pandas-based Excel/CSV parsing
│   │   └── web.py          # HTML parsing (BeautifulSoup)
│   ├── main.py             # FastAPI entry point & Routing
│   ├── schemas.py          # Pydantic models for request/response
│   └── utils.py            # Image processing & helper functions
├── frontend/
│   ├── index.html          # Modern UI
│   ├── style.css           # Custom styling for drag-and-drop
│   └── script.js           # API interaction & Queue management
├── test_files/             # Sample documents for validation
├── Dockerfile              # Multi-stage build for Python & Tesseract
├── requirements.txt        # Backend dependencies
└── README.md               # Project documentation

```

---

## 🛠️ Tech Stack

### Backend

* **Core:** Python 3.9+, FastAPI, Uvicorn
* **Extraction:** Tesseract OCR, OpenCV (cv2)
* **Parsing:** PDFPlumber, python-docx, Pandas, BeautifulSoup4

### Frontend

* **Languages:** HTML5, CSS3, JavaScript 
* **Features:** Drag-and-drop API, Fetch API for asynchronous uploads

---

## 🔌 API Reference

### Extract Text

`POST /api/extract`

**Request:**

* **Body:** `multipart/form-data`
* **Key:** `file` (The document file)

**Sample Response:**

```json
{
  "filename": "invoice_01.pdf",
  "file_type": "pdf",
  "processing_time_ms": 145.2,
  "content": [
    {
      "text": "INVOICE #12345",
      "source": "page_1",
      "location": {
        "type": "page",
        "number": 1
      }
    }
  ]
}

```

---

## 🚀 Getting Started

### Prerequisites

1. **Python 3.9+**
2. **Tesseract OCR Engine:**
* **Ubuntu:** `sudo apt install tesseract-ocr`
* **macOS:** `brew install tesseract`



### Local Installation

1. **Clone the repository:**
```bash
git clone [https://github.com/your-username/universal-text-extractor.git](https://github.com/your-username/universal-text-extractor.git)
cd universal-text-extractor

```


2. **Install Dependencies:**
```bash
pip install -r requirements.txt

```


3. **Run the Server:**
```bash
python -m uvicorn app.main:app --reload

```


4. **Open the Frontend:**
Open `frontend/index.html` in your preferred browser.

### Using Docker

```bash
docker build -t text-extractor .
docker run -p 8000:8000 text-extractor

```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

