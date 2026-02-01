#
import pytest
import os
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

# Create a test client
client = TestClient(app)

# Looks one level up from 'tests/' to find 'test_data/' in the project root
EXTRA_FOLDER = os.path.join(os.path.dirname(__file__), "..", "test_data")

def get_test_files():
    """Scans the test_data directory for real input documents."""
    if not os.path.exists(EXTRA_FOLDER):
        return []
    return [f for f in os.listdir(EXTRA_FOLDER) if os.path.isfile(os.path.join(EXTRA_FOLDER, f))]

# 👋 SECTION 1: POSITIVE TEST CASES (Happy Path - Mocked)

def test_health_check():
    """Verify the server is running and returns 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

@patch("app.main.magic.from_buffer")
@patch("app.extractors.documents.PDFExtractor.extract")
def test_extract_pdf_mock(mock_extract, mock_magic):
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
def test_extract_html_mock(mock_extract, mock_magic):
    """Positive Case: Extract from a valid HTML file."""
    mock_magic.return_value = "text/html"
    mock_extract.return_value = [{
        "text": "Hello World", 
        "source": "body", 
        "location": {"type": "tag", "number": 1} 
    }]

    files = {"file": ("index.html", b"<html><body>Hello</body></html>", "text/html")}
    response = client.post("/api/extract", files=files)

    assert response.status_code == 200
    assert response.json()["file_type"] == "html"

# 🛑 SECTION 2: NEGATIVE TEST CASES (Error Handling - Mocked)

@patch("app.main.magic.from_buffer")
def test_unsupported_file_type(mock_magic):
    """Negative Case: Upload a file type that is not supported."""
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

# ⚠️ SECTION 3: EDGE CASES (Boundary Conditions - Mocked)

@patch("app.main.magic.from_buffer")
@patch("app.extractors.images.ImageExtractor.extract")
def test_extension_fallback_success(mock_extract, mock_magic):
    """Edge Case: Magic detection fails, fallback to extension for images."""
    mock_magic.return_value = "application/octet-stream"
    mock_extract.return_value = [{
        "text": "OCR Text", 
        "source": "ocr", 
        "location": {"type": "pixel_box", "number": 1} 
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

# 🚀 SECTION 4: DYNAMIC INTEGRATION TESTS (Real Data CLI Display)

@pytest.mark.parametrize("filename", get_test_files())
def test_extract_real_documents_cli(filename):
    """
    Automatically tests every file in 'test_data' and displays 
    detailed extraction data on the command line.
    """
    file_path = os.path.join(EXTRA_FOLDER, filename)
     
    ext = filename.lower().split('.')[-1]
    mime_map = {
        'pdf': 'application/pdf',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'csv': 'text/csv',
        'txt': 'text/plain',
        'png': 'image/png',
        'jpg': 'image/jpeg'
    }
    mime_type = mime_map.get(ext, "application/octet-stream")

    print(f"\n\n[DOCKER TEST] Processing: {filename}")
    
    with open(file_path, "rb") as f:
        files = {"file": (filename, f, mime_type)}
        response = client.post("/api/extract", files=files)

    assert response.status_code == 200, f"Critical Failure on {filename}: {response.text}"
    data = response.json()
    
    # CLI OUTPUT BLOCK FOR TEACHER
    print(f" Success Status: 200 OK")
    print(f"  Backend Processing: {data['processing_time_ms']}ms")
    print(f" Type Detected: {data['file_type']}")
    print("-" * 50)
    print("EXTRACTED CONTENT PREVIEW:")
    
    if data['content']:
        for i, unit in enumerate(data['content'][:5]): # Display first 5 units
            snippet = unit['text'][:150].replace('\n', ' ')
            print(f"  Unit {i+1} [{unit['source']}]: {snippet}...")
    else:
        print("  No text content found.")
    
    print("=" * 70)