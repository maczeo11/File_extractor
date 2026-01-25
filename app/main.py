import magic
import time
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import DocumentResponse
from app.extractors.documents import PDFExtractor, WordExtractor
from app.extractors.tables import TableExtractor
from app.extractors.images import ImageExtractor
from app.extractors.web import HTMLExtractor

app = FastAPI(title="Universal Text Extractor API")

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Strategy Map: Connects MIME types to specific logic
EXTRACTOR_MAP = {
    # PDF
    "application/pdf": PDFExtractor,
    
    # Word
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": WordExtractor,
    
    # Excel
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": TableExtractor,
    "application/vnd.ms-excel": TableExtractor,
    
    # CSV / Text
    "text/csv": lambda f, n: TableExtractor(f, n, is_csv=True),
    "text/plain": lambda f, n: TableExtractor(f, n, is_csv=True),
    
    # Images
    "image/png": ImageExtractor,
    "image/jpeg": ImageExtractor,
    "image/tiff": ImageExtractor,
    
    # Web
    "text/html": HTMLExtractor
}

@app.get("/")
def health_check():
    return {"status": "active", "service": "text-extractor-v1"}

@app.post("/api/extract", response_model=DocumentResponse)
def extract_file(file: UploadFile):
    """
    Main endpoint that accepts a file, detects its type, 
    chooses the right strategy, and returns standardized JSON.
    """
    start_time = time.time()
    
    # 1. Read Bytes
    try:
        file_bytes = file.file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="Corrupt or unreadable file")

    # 2. Detect Type (Magic Numbers)
    try:
        # mime=True returns 'application/pdf' etc.
        mime_type = magic.from_buffer(file_bytes, mime=True)
    except Exception:
        # Fallback if magic crashes
        mime_type = "application/octet-stream"

    print(f"DEBUG: Filename='{file.filename}' Detected MIME='{mime_type}'")

    # 3. Router Logic (Strategy Pattern)
    extractor_class = EXTRACTOR_MAP.get(mime_type)
    
    # 🛡️ SAFETY NET: Fallback to extension if magic fails (Common on Windows)
    if not extractor_class or mime_type == "application/octet-stream":
        print("DEBUG: Magic detection failed or unknown. Checking extension...")
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
             mime_type = "image/png" # Generic image type
        else:
            raise HTTPException(400, detail=f"Unsupported file type: {mime_type} (Extension not recognized)")

    # 4. Extract
    try:
        # Initialize the selected extractor with bytes and filename
        extractor = extractor_class(file_bytes, file.filename)
        content = extractor.extract()
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(500, detail=f"Extraction failed: {str(e)}")

    # 5. Simplify Output Type (Map long MIME to short name)
    type_mapping = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
        "text/csv": "csv",
        "text/plain": "txt",
        "image/png": "png",
        "image/jpeg": "jpg",
        "text/html": "html"
    }
    simple_type = type_mapping.get(mime_type, mime_type)

    # 6. Return Response
    return DocumentResponse(
        filename=file.filename,
        file_type=simple_type,
        processing_time_ms=round((time.time() - start_time) * 1000, 2),
        content=content
    )