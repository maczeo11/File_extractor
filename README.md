# File_extractor
small project , a text extractor that works by extracting text from varios file types
# 🚀 Universal Text Extraction Web App

A modular web application that accepts real-world documents (PDF, Docs, Images, Tables) and extracts text into a single, standardized JSON structure. Built for the [Insert Hackathon Name] Hackathon.

---

## 🏗️ Architecture

This project follows the **Strategy Design Pattern**. A central "Router" detects the file type (using binary signatures) and delegates processing to specific "Extractor Modules."

- **Backend:** FastAPI (Python), Tesseract OCR, OpenCV, Pandas, PDFPlumber.
- **Frontend:** [React / Next.js / Streamlit] *(To be updated)*
- **Protocol:** REST API with standardized JSON response.

---

## 📂 Backend Documentation

### 1. Prerequisites
Before running the server, ensure you have the following installed on your machine:
* **Python 3.9+**
* **Tesseract OCR Engine:**
    * *Windows:* Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). **Important:** Add `C:\Program Files\Tesseract-OCR` to your System PATH.
    * *Linux:* `sudo apt-get install tesseract-ocr libmagic1`
    * *Mac:* `brew install tesseract libmagic`

### 2. Installation
Navigate to the `backend` folder and install dependencies:

```bash
cd backend
pip install -r requirements.txt
