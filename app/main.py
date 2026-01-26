from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import magic
import time

from app.schemas import DocumentResponse
from app.extractors.documents import PDFExtractor, WordExtractor
from app.extractors.tables import TableExtractor
from app.extractors.images import ImageExtractor
from app.extractors.web import HTMLExtractor

app = FastAPI(title="Universal Text Extractor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXTRACTOR_MAP = {
    "application/pdf": PDFExtractor,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": WordExtractor,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": TableExtractor,
    "application/vnd.ms-excel": TableExtractor,
    "text/csv": lambda f, n: TableExtractor(f, n, is_csv=True),
    "text/plain": lambda f, n: TableExtractor(f, n, is_csv=True),
    "image/png": ImageExtractor,
    "image/jpeg": ImageExtractor,
    "text/html": HTMLExtractor
}

@app.get("/")
def health_check():
    return {"status": "active", "service": "text-extractor-v1"}

# 🔹 SIMPLE TEXT RESPONSE (UI uses this)
@app.post("/api/extract")
def extract_plain_text(file: UploadFile):
    file_bytes = file.file.read()
    mime_type = magic.from_buffer(file_bytes, mime=True)

    extractor_class = EXTRACTOR_MAP.get(mime_type)
    if not extractor_class:
        raise HTTPException(400, detail="Unsupported file type")

    extractor = extractor_class(file_bytes, file.filename)
    units = extractor.extract()

    # ✅ ONLY extracted text
    extracted_text = "\n\n".join([unit.text for unit in units])

    return {
        "filename": file.filename,
        "extracted_text": extracted_text
    }

# 🔹 FULL JSON RESPONSE (for download)
@app.post("/api/extract/json", response_model=DocumentResponse)
def extract_json(file: UploadFile):
    start_time = time.time()
    file_bytes = file.file.read()
    mime_type = magic.from_buffer(file_bytes, mime=True)

    extractor_class = EXTRACTOR_MAP.get(mime_type)
    if not extractor_class:
        raise HTTPException(400, detail="Unsupported file type")

    extractor = extractor_class(file_bytes, file.filename)
    content = extractor.extract()

    return DocumentResponse(
        filename=file.filename,
        file_type=mime_type,
        processing_time_ms=round((time.time() - start_time) * 1000, 2),
        content=content
    )
