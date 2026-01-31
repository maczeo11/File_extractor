Universal Text Extractor (A SMALL PROJECT :)
    Our goal was to make a usable tool that any one can use without the knowledge of technical know-how's. 

📖 System Overview

The Universal Text Extractor solves the "Dark Data" problem by normalizing content from PDF, Word, Excel, Images, and HTML into a standardized JSON format. Unlike simple wrappers, this system implements a Hybrid Extraction Engine that switches strategies based on file content (not just extension) and uses advanced pre-processing to improve OCR accuracy on noisy documents.

It is deployed via a Serverless Architecture (Railway/Render) with a smart frontend that manages request concurrency to respect free-tier resource quotas.
🏗️ Technical Architecture & Engineering Decisions

We made several key architectural decisions to ensure scalability, reliability, and cost-efficiency.
1. The Strategy Pattern (Backend)

Decision: We implemented the Strategy Design Pattern for the extraction logic.

    Why? To strictly follow the Open/Closed Principle (SOLID). The main.py router acts as the Context, while PDFExtractor, ImageExtractor, etc., are isolated strategies.

    Benefit: We can add support for new formats (e.g., .epub or .pptx) by simply creating a new class in app/extractors/ without modifying the core API logic.

2. Hybrid OCR Pipeline (Computer Vision)

Decision: We do not simply pass images to Tesseract. We apply a Computer Vision pre-processing pipeline in app/utils.py.

    Why? Tesseract struggles with shadows, noise, and low contrast.

    The Pipeline:

        Memory Decoding: Converts raw bytes to NumPy arrays (cv2.imdecode).

        Grayscale Conversion: Reduces dimensionality (cv2.cvtColor).

        Otsu's Binarization: Applies dynamic thresholding (cv2.THRESH_BINARY + cv2.THRESH_OTSU) to separate text from background noise automatically.

        Configuration: Runs Tesseract with --oem 1 (LSTM Neural Net) and --psm 3 (Auto Page Segmentation) for maximum accuracy.

3. Client-Side "Smart Queue" (Resource Management)

Decision: The frontend implements a Sequential Promise Queue instead of parallel uploads.

    Why? The application runs on Free Tier Cloud Instances (512MB RAM). Running 5 parallel OCR processes would cause an Out of Memory (OOM) crash.

    Solution: The JavaScript loop waits for the previous await fetch() to complete before sending the next file. This creates a "Batch Experience" for the user while strictly enforcing "Serial Processing" for the server.

4. Robust MIME-Type Detection

Decision: We use python-magic (libmagic) to inspect file headers (Magic Numbers) rather than trusting file extensions.

    Why? Users often rename files incorrectly (e.g., naming a PNG image .pdf). Trusting extensions leads to crashes; trusting headers guarantees stability.

📂 Project Structure
Bash

Universal-Text-Extractor/
├── app/
│   ├── extractors/          # Strategy Pattern Implementation
│   │   ├── base.py          # Abstract Base Class (ABC)
│   │   ├── documents.py     # Complex PDF & Word Logic (Hybrid OCR)
│   │   ├── images.py        # Tesseract Wrapper
│   │   ├── tables.py        # Pandas Logic (Excel/CSV)
│   │   └── web.py           # BeautifulSoup Logic (HTML)
│   ├── utils.py             # OpenCV Pre-processing (Otsu/Grayscale)
│   ├── main.py              # FastAPI Router & Middleware
│   └── schemas.py           # Pydantic Response Models
├── frontend/
│   ├── index.html           # UI Structure
│   ├── script.js            # Batch Queue & Server Auto-Detect Logic
│   └── style.css            # Modern Dark UI
├── requirements.txt         # Python Dependencies
├── Dockerfile               # Production Container Config
└── README.md                # Documentation

⚡ Key Features
📄 PDF (Hybrid Extraction)

    Text Layer: First attempts to extract native text using pdfplumber.

    Embedded Images: Iterates through PDF objects to find raster images (charts, diagrams). If found, they are extracted, converted to PNG in memory, and passed through the OCR pipeline.

    Fallback: If a page is scanned (has <10 characters of text), it renders the full page at 300 DPI and performs full-page OCR.

📝 Word (DOCX)

    XML Parsing: Uses python-docx to traverse the document tree.

    Deep Extraction: Scans XML blip (Binary Large Image Package) tags to find and extract embedded images hidden inside paragraphs or tables.

📊 Excel & CSV

    Structure Preservation: Uses pandas to read sheets and serializes rows into pipe-separated strings (|) to maintain tabular structure in plain text.

🚀 Setup & Installation
1. Prerequisites

    Python 3.9+

    Tesseract OCR installed on your system.

        Windows: Download Installer (Add to PATH).

        Linux: sudo apt-get install tesseract-ocr libmagic1

2. Run Locally
Bash

# Clone the repo
git clone https://github.com/yourusername/universal-text-extractor.git
cd universal-text-extractor

# Install dependencies
pip install -r requirements.txt

# Start Backend
uvicorn app.main:app --reload

3. Run Frontend

Simply open frontend/index.html in your browser. The smart script will automatically detect that your local server is running at http://localhost:8000.
🌐 API Reference
POST /api/extract

Uploads a file and returns structured text.

Request: multipart/form-data

    file: The document (PDF, JPG, PNG, DOCX, XLSX, etc.)

Response Model:
JSON

{
  "filename": "invoice.png",
  "file_type": "png",
  "processing_time_ms": 1250.5,
  "content": [
    {
      "text": "Total Amount: $500.00",
      "source": "ocr_engine",
      "location": { "type": "pixel_box", "number": 1 }
    }
  ]
}

📜 License

MIT License. Copyright (c) 2026.
