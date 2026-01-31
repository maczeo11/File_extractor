import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from app.main import app

# Create a test client
client = TestClient(app)

# ==========================================
# 1. POSITIVE CASES (Happy Path)
# ==========================================

def test_health_check():
    """
    Verify the server is running and returns 200.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "active", "service": "text-extractor-v1"}

@patch("app.main.magic.from_buffer")
@patch("app.extractors.documents.PDFExtractor.extract")
def test_extract_pdf_valid(mock_extract, mock_magic):
    """
    Positive Case: Upload a valid PDF.
    """
    # 1. Mock Detection
    mock_magic.return_value = "application/pdf"
    
    # 2. Mock Extraction Result
    mock_response_content = [{
        "text": "Mocked PDF Content",
        "source": "page_1",
        "location": {"type": "page", "number": 1}
    }]
    mock_extract.return_value = mock_response_content

    # 3. Simulate File Upload
    files = {"file": ("test.pdf", b"%PDF-1.4...", "application/pdf")}
    response = client.post("/api/extract", files=files)

    # 4. Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["file_type"] == "pdf"
    assert data["content"][0]["text"] == "Mocked PDF Content"

@patch("app.main.magic.from_buffer")
@patch("app.extractors.images.ImageExtractor.extract")
def test_extract_image_valid(mock_extract, mock_magic):
    """
    Positive Case: Upload a valid PNG image.
    """
    mock_magic.return_value = "image/png"
    mock_extract.return_value = [{"text": "OCR Text", "source": "ocr", "location": {"type": "pixel_box", "number": 1}}]

    files = {"file": ("image.png", b"fake_image_bytes", "image/png")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json()["file_type"] == "png"
    assert response.json()["content"][0]["text"] == "OCR Text"

@patch("app.main.magic.from_buffer")
@patch("app.extractors.tables.TableExtractor.extract")
def test_extract_excel_valid(mock_extract, mock_magic):
    """
    Positive Case: Upload a valid Excel file (.xlsx).
    """
    mock_magic.return_value = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    mock_extract.return_value = [{"text": "Row 1 Col A | Row 1 Col B", "source": "Sheet1", "location": {"type": "row", "number": 1}}]

    files = {"file": ("financials.xlsx", b"PK...", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json()["file_type"] == "xlsx"
    assert "Row 1 Col A" in response.json()["content"][0]["text"]

# ==========================================
# 2. NEGATIVE CASES (Error Handling)
# ==========================================

@patch("app.main.magic.from_buffer")
def test_unsupported_file_type(mock_magic):
    """
    Negative Case: Upload a file type that is not supported (e.g., .exe).
    """
    # Mock magic to return an unsupported mime type
    mock_magic.return_value = "application/x-dosexec"

    files = {"file": ("virus.exe", b"MZ...", "application/octet-stream")}
    response = client.post("/api/extract", files=files)

    # Should return 400 Bad Request
    assert response.status_code == 400
    
    #  FIX: Match the actual error message in your main.py
    error_detail = response.json()["detail"]
    assert "Unsupported format" in error_detail
    assert "Supported types" in error_detail

def test_upload_no_file():
    """
    Negative Case: Call the endpoint without sending a file (Missing field).
    """
    response = client.post("/api/extract") 
    # FastAPI handles missing required fields with 422
    assert response.status_code == 422
 
@patch("app.main.magic.from_buffer")
@patch("app.extractors.documents.WordExtractor.extract")
def test_fallback_extension_logic(mock_extract, mock_magic):
    """
    Edge Case: 'python-magic' fails to detect type (returns octet-stream),
    but the file extension is valid (.docx). The app should fallback to extension.
    """
    mock_magic.return_value = "application/octet-stream"
    
    mock_extract.return_value = [{"text": "Word Doc", "source": "para", "location": {"type": "row", "number": 1}}]
 
    files = {"file": ("report.docx", b"PK...", "application/octet-stream")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json()["file_type"] == "docx"
    assert response.json()["content"][0]["text"] == "Word Doc"

@patch("app.main.magic.from_buffer")
def test_corrupt_file_handling(mock_magic):
    """
    Edge Case: The file bytes are corrupt, causing the Extractor class to raise an Exception.
    """
    mock_magic.return_value = "application/pdf"
     
    with patch("app.extractors.documents.PDFExtractor.extract", side_effect=Exception("EOF Error")):
        files = {"file": ("corrupt.pdf", b"garbage", "application/pdf")}
        response = client.post("/api/extract", files=files)
 
        assert response.status_code == 500
        assert "Extraction failed" in response.json()["detail"]

@patch("app.main.magic.from_buffer")
@patch("app.extractors.tables.TableExtractor.extract")
def test_empty_csv_file(mock_extract, mock_magic):
    """
    Edge Case: A valid CSV file that is completely empty.
    """
    mock_magic.return_value = "text/csv" 
    mock_extract.return_value = [] 

    files = {"file": ("empty.csv", b"", "text/csv")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json()["content"] == [] 