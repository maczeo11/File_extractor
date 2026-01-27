import magic
import sys
import time
import pytesseract
import os
from typing import List

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.schemas import DocumentResponse
from app.extractors.documents import PDFExtractor, WordExtractor
from app.extractors.tables import TableExtractor
from app.extractors.images import ImageExtractor
from app.extractors.web import HTMLExtractor

# =========================================================
# 🛠️ TESSERACT CONFIGURATION
# =========================================================
if sys.platform.startswith("win"):
    tesseract_base_path = r"C:\Program Files\Tesseract-OCR"
    executable_path = os.path.join(tesseract_base_path, "tesseract.exe")
    tessdata_path = os.path.join(tesseract_base_path, "tessdata")

    if os.path.exists(executable_path):
        pytesseract.pytesseract.tesseract_cmd = executable_path
        os.environ["TESSDATA_PREFIX"] = tessdata_path
        print("✅ Windows Tesseract configured")
    else:
        print("⚠️ Tesseract not found on Windows")
else:
    print("✅ Running on Linux/Cloud. Using system Tesseract")

# =========================================================
# 🚀 FASTAPI APP
# =========================================================
app = FastAPI(title="Universal Text Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# 🎨 FRONTEND SERVING
# =========================================================
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse("frontend/index.html")


@app.get("/health")
def health_check():
    return {"status": "active", "service": "text-extractor-v1"}

# =========================================================
# 📦 EXTRACTOR MAP
# =========================================================
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
    "text/html": HTMLExtractor,
}

# =========================================================
# 📤 MULTI-FILE EXTRACTION API (FIXED)
# =========================================================
@app.post("/api/extract")
def extract_files(files: List[UploadFile]):
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files allowed")

    results = []

    for file in files:
        start_time = time.time()

        try:
            file_bytes = file.file.read()
        except Exception:
            raise HTTPException(status_code=400, detail=f"Unreadable file: {file.filename}")

        try:
            mime_type = magic.from_buffer(file_bytes, mime=True)
        except Exception:
            mime_type = "application/octet-stream"

        print(f"DEBUG: {file.filename} | MIME: {mime_type}")

        extractor_class = EXTRACTOR_MAP.get(mime_type)

        # 🔁 Fallback to extension
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
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file: {file.filename}")

        try:
            extractor = extractor_class(file_bytes, file.filename)
            content = extractor.extract()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Extraction failed for {file.filename}: {str(e)}"
            )

        type_mapping = {
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
            "text/csv": "csv",
            "text/plain": "txt",
            "image/png": "png",
            "image/jpeg": "jpg",
            "text/html": "html",
        }

        simple_type = type_mapping.get(mime_type, mime_type)

        results.append(
            DocumentResponse(
                filename=file.filename,
                file_type=simple_type,
                processing_time_ms=round((time.time() - start_time) * 1000, 2),
                content=content,
            )
        )

    return {"results": results}
