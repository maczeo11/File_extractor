#
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from app.main import app

# Create a test client
client = TestClient(app)

# ==============================================================================
# 👋 POSITIVE TEST CASES (Happy Path)
# ==============================================================================

def test_health_check():
    """Verify the server is running and returns 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "active", "service": "text-extractor-v1"}

@patch("app.main.magic.from_buffer")
@patch("app.extractors.documents.PDFExtractor.extract")
def test_extract_pdf_valid(mock_extract, mock_magic):
    """Positive Case: Upload a valid PDF."""
    mock_magic.return_value = "application/pdf"
    mock_extract.return_value = [{
        "text": "Mocked PDF Content",
        "source": "page_1",
        "location": {"type": "page", "number": 1}
    }]

    files = {"file": ("test.pdf", b"%PDF-1.4...", "application/pdf")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json()["file_type"] == "pdf"
    assert response.json()["content"][0]["text"] == "Mocked PDF Content"

@patch("app.main.magic.from_buffer")
@patch("app.extractors.web.HTMLExtractor.extract")
def test_extract_html_valid(mock_extract, mock_magic):
    """Positive Case: Extract from a valid HTML file."""
    mock_magic.return_value = "text/html"
    mock_extract.return_value = [{
        "text": "Hello World", 
        "source": "body", 
        "location": {"type": "tag", "number": 1} # ✅ 'tag' is now valid
    }]

    files = {"file": ("index.html", b"<html><body>Hello</body></html>", "text/html")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json()["file_type"] == "html"

# ==============================================================================
# 🛑 NEGATIVE TEST CASES (Error Handling)
# ==============================================================================

@patch("app.main.magic.from_buffer")
def test_unsupported_file_type(mock_magic):
    """Negative Case: Upload a file type that is not supported (e.g., .exe)."""
    mock_magic.return_value = "application/x-dosexec"

    files = {"file": ("virus.exe", b"MZ...", "application/octet-stream")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 400
    error_detail = response.json()["detail"]
    assert "Unsupported format" in error_detail
    assert "Supported types" in error_detail

def test_upload_no_file():
    """Negative Case: Call the endpoint without sending a file."""
    response = client.post("/api/extract") 
    assert response.status_code == 422

# ==============================================================================
# ⚠️ EDGE CASES (Boundary Conditions)
# ==============================================================================

@patch("app.main.magic.from_buffer")
@patch("app.extractors.images.ImageExtractor.extract")
def test_extension_fallback_success(mock_extract, mock_magic):
    """Edge Case: Magic detection fails, fallback to extension for images."""
    mock_magic.return_value = "application/octet-stream"
    mock_extract.return_value = [{
        "text": "OCR Text", 
        "source": "ocr", 
        "location": {"type": "pixel_box", "number": 1} # ✅ Matches Literal
    }]

    files = {"file": ("scan.jpg", b"fake_bytes", "application/octet-stream")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json()["file_type"] == "png"

@patch("app.main.magic.from_buffer")
def test_corrupt_file_handling(mock_magic):
    """Edge Case: The extractor engine crashes."""
    mock_magic.return_value = "application/pdf"
    with patch("app.extractors.documents.PDFExtractor.extract", side_effect=Exception("Parser Error")):
        files = {"file": ("bad.pdf", b"garbage", "application/pdf")}
        response = client.post("/api/extract", files=files)
        assert response.status_code == 500
        assert "Extraction failed" in response.json()["detail"]

@patch("app.main.magic.from_buffer")
@patch("app.extractors.tables.TableExtractor.extract")
def test_empty_csv_file(mock_extract, mock_magic):
    """Edge Case: A valid CSV file that is completely empty."""
    mock_magic.return_value = "text/csv" 
    mock_extract.return_value = [] 

    files = {"file": ("empty.csv", b"", "text/csv")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json()["content"] == []