import magic
import sys
import time
import pytesseract
import os
from typing import List

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import DocumentResponse
from app.extractors.documents import PDFExtractor, WordExtractor
from app.extractors.tables import TableExtractor
from app.extractors.images import ImageExtractor
from app.extractors.html import HTMLExtractor

# ------------------------------------------------------------------
# 🛠️ TESSERACT CONFIGURATION (WINDOWS FIX)
# ------------------------------------------------------------------
if sys.platform.startswith('win'):
    tesseract_base_path = r'C:\Program Files\Tesseract-OCR'
    executable_path = os.path.join(tesseract_base_path, 'tesseract.exe')
    tessdata_path = os.path.join(tesseract_base_path, 'tessdata')

    if os.path.exists(executable_path):
        pytesseract.pytesseract.tesseract_cmd = executable_path
        os.environ['TESSDATA_PREFIX'] = tessdata_path

        print("✅ DEBUG: Windows Tesseract configured")
        print(f"   - Exe: {executable_path}")
        print(f"   - Data: {tessdata_path}")
    else:
        print("⚠️ WARNING: Tesseract.exe not found")

else:
    print("✅ DEBUG: Using system Tesseract")

# ------------------------------------------------------------------
# 🚀 FASTAPI APP
# ------------------------------------------------------------------
app = FastAPI(title="Universal Text Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# 🧠 STRATEGY MAP (MIME → EXTRACTOR)
# ------------------------------------------------------------------
EXTRACTOR_MAP = {
    "application/pdf": PDFExtractor,

    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": WordExtractor,

    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": TableExtractor,
    "application/vnd.ms-excel": TableExtractor,

    "text/csv": lambda f, n: TableExtractor(f, n, is_csv=True),
    "text/plain": lambda f, n: TableExtractor(f, n, is_csv=True),

    "image/png": ImageExtractor,
    "image/jpeg": ImageExtractor,
    "image/tiff": ImageExtractor,

    "text/html": HTMLExtractor
}

# ------------------------------------------------------------------
# ✅ HEALTH CHECK
# ------------------------------------------------------------------
@app.get("/")
def health_check():
    return {"status": "active", "service": "text-extractor-v1"}

# ------------------------------------------------------------------
# 🔥 MULTI-FILE EXTRACTION ENDPOINT (MAX 5 FILES)
# ------------------------------------------------------------------
@app.post("/api/extract")
def extract_files(files: List[UploadFile]):
    """
    Accepts up to 5 files, detects type using magic numbers,
    routes to appropriate extractor, and returns results per file.
    """

    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 files allowed at a time"
        )

    responses = []

    for file in files:
        start_time = time.time()

        # 1️⃣ Read file bytes
        try:
            file_bytes = file.file.read()
        except Exception:
            raise HTTPException(status_code=400, detail=f"Unreadable file: {file.filename}")

        # 2️⃣ Detect MIME type using magic
        try:
            mime_type = magic.from_buffer(file_bytes, mime=True)
        except Exception:
            mime_type = "application/octet-stream"

        print(f"DEBUG: {file.filename} → MIME: {mime_type}")

        # 3️⃣ Strategy selection
        extractor_class = EXTRACTOR_MAP.get(mime_type)

        # 🔁 Fallback to extension (Windows-safe)
        if not extractor_class or mime_type == "application/octet-stream":
            name = file.filename.lower()

            if name.endswith(".pdf"):
                extractor_class = PDFExtractor
                mime_type = "application/pdf"

            elif name.endswith(".docx"):
                extractor_class = WordExtractor
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            elif name.endswith(".xlsx"):
                extractor_class = TableExtractor
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

            elif name.endswith(".csv"):
                extractor_class = lambda f, n: TableExtractor(f, n, is_csv=True)
                mime_type = "text/csv"

            elif name.endswith(".txt"):
                extractor_class = lambda f, n: TableExtractor(f, n, is_csv=True)
                mime_type = "text/plain"

            elif name.endswith((".png", ".jpg", ".jpeg")):
                extractor_class = ImageExtractor
                mime_type = "image/png"

            elif name.endswith((".html", ".htm")):
                extractor_class = HTMLExtractor
                mime_type = "text/html"

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}"
                )

        # 4️⃣ Extract content
        try:
            extractor = extractor_class(file_bytes, file.filename)
            content = extractor.extract()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Extraction failed for {file.filename}: {str(e)}"
            )

        # 5️⃣ Simplified file type
        type_map = {
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
            "text/csv": "csv",
            "text/plain": "txt",
            "image/png": "png",
            "image/jpeg": "jpg",
            "text/html": "html"
        }

        simple_type = type_map.get(mime_type, mime_type)

        # 6️⃣ Append response
        responses.append(
            DocumentResponse(
                filename=file.filename,
                file_type=simple_type,
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
                content=content
            )
        )

    return {"results": responses}
