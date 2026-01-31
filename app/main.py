import magic
import sys
import time
import pytesseract
import os
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import DocumentResponse
from app.extractors.documents import PDFExtractor, WordExtractor
from app.extractors.tables import TableExtractor
from app.extractors.images import ImageExtractor
from app.extractors.web import HTMLExtractor

if sys.platform.startswith('win'):
    tesseract_base_path = r'C:\Program Files\Tesseract-OCR'
    executable_path = os.path.join(tesseract_base_path, 'tesseract.exe')
    tessdata_path = os.path.join(tesseract_base_path, 'tessdata')

    if os.path.exists(executable_path):
        pytesseract.pytesseract.tesseract_cmd = executable_path
        os.environ['TESSDATA_PREFIX'] = tessdata_path
    else:
        print("⚠️ WARNING: Tesseract.exe not found on Windows.")

app = FastAPI(title="Universal Text Extractor API")

#

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=False, 
    allow_methods=["*"],     
    allow_headers=["*"],     
)
#THIS IS USED TO MAP EACH FILE TYPE TO RESPECTIVE METHODS
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
#THIS IS THE MAIN ROUTE
@app.get("/")
def health_check():
    return {"status": "active", "service": "text-extractor-v1"}


@app.post("/api/extract", response_model=DocumentResponse)
def extract_file(file: UploadFile):
    start_time = time.time()
    #REASDS THE FILE
    try:
        file_bytes = file.file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Corrupt or unreadable file")

    #  Detect Type
    try:
        mime_type = magic.from_buffer(file_bytes, mime=True)
    except Exception:
        mime_type = "application/octet-stream"

    print(f"DEBUG: Processing '{file.filename}' ({mime_type})")

    extractor_class = EXTRACTOR_MAP.get(mime_type)
    
    if not extractor_class or mime_type == "application/octet-stream":
        lower_name = file.filename.lower()
        if lower_name.endswith('.docx'):
             extractor_class = WordExtractor
             mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif lower_name.endswith('.pdf'):
             extractor_class = PDFExtractor
             mime_type = "application/pdf"
        elif lower_name.endswith('.xlsx'):
             extractor_class = TableExtractor
             mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif lower_name.endswith('.csv'):
             extractor_class = lambda f, n: TableExtractor(f, n, is_csv=True)
             mime_type = "text/csv"
        elif lower_name.endswith('.txt'):
             extractor_class = lambda f, n: TableExtractor(f, n, is_csv=True)
             mime_type = "text/plain"
        elif lower_name.endswith(('.png', '.jpg', '.jpeg')):
             extractor_class = ImageExtractor
             mime_type = "image/png"
        else: 
            supported_formats = "PDF, DOCX, XLSX, CSV, TXT, HTML, PNG, JPG"
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported format: {mime_type}. Supported types: {supported_formats}"
            )

    try:
        extractor = extractor_class(file_bytes, file.filename)
        content = extractor.extract()
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail=f"Extraction failed: {str(e)}")

    type_mapping = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/csv": "csv",
        "text/plain": "txt",
        "image/png": "png", "image/jpeg": "jpg", "text/html": "html"
    }
    
    return DocumentResponse(
        filename=file.filename,
        file_type=type_mapping.get(mime_type, mime_type),
        processing_time_ms=round((time.time() - start_time) * 1000, 2),
        content=content
    )