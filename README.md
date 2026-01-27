
---

```markdown
# File_extractor

small project , a text extractor that works by extracting text from varios file types

## 🚀 Universal Text Extraction Web App

A robust, modular web application designed to extract text from a wide variety of real-world document formats (PDFs, Images, Word Docs, and Tables) and convert them into a standardized, machine-readable JSON structure.

This project implements the **Strategy Design Pattern**, allowing for seamless expansion to new file types without modifying the core routing logic.

### 🏗️ Project Architecture

The application is split into a modern decoupled architecture:

* **Backend:** FastAPI (Python) serving as a high-performance REST API.
* **Frontend:** A responsive UI for file uploads and result visualization.
* **Processing Engine:** Utilizes binary signature detection to route files to specialized extractors (Tesseract OCR, OpenCV, PDFPlumber, and Pandas).

### 📁 Repository Structure

```text
├── app/                # FastAPI Backend logic
├── frontend/           # Html/Css/Java Script UI components
├── Dockerfile          # Containerization for easy deployment
├── requirements.txt    # Python dependencies
└── .gitignore          # Standard git exclusion rules

```

---

## 📂 Backend Documentation

### 1. Prerequisites

Before running the server, ensure you have the following installed:

* **Python 3.9+**
* **Tesseract OCR Engine:**
* *Windows:* Install via [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and **add `C:\Program Files\Tesseract-OCR` to your System PATH.**
* *Linux:* `sudo apt-get install tesseract-ocr libmagic1`
* *macOS:* `brew install tesseract libmagic`



### 2. Installation & Setup

**Local Development**

1. Clone the repository:
```bash
git clone [https://github.com/maczeo11/File_extractor.git](https://github.com/maczeo11/File_extractor.git)
cd File_extractor

```


2. Backend Setup:
```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

```


3. Frontend Setup:
```bash
cd frontend
npm install
npm run dev

```



**Docker Deployment**

```bash
docker build -t file-extractor .
docker run -p 8000:8000 file-extractor

```

### 3. API Documentation

Once the backend is running, you can access the interactive Swagger documentation at:
👉 **http://localhost:8000/docs**

---

## ✨ Key Features

* **Multi-Format Support:** Handles `.pdf`, `.docx`, `.jpg`, `.png`, and `.csv`.
* **Table Extraction:** Intelligently identifies and parses tabular data from within documents.
* **Scalability:** The modular "Strategy" approach allows developers to add new file-type extractors with minimal code changes.
* **API-First Design:** Fully documented REST API via Swagger UI.

---

### 🛠️ Quick Execution

**Step 1: System Dependencies**
Install Tesseract OCR on your local machine and ensure it is added to your system environment variables.

**Step 2: Environment Setup**

```bash
git clone [https://github.com/maczeo11/File_extractor.git](https://github.com/maczeo11/File_extractor.git)
pip install -r requirements.txt

```

**Step 3: Execution**
Run the server using Uvicorn:

```bash
python -m uvicorn app.main:app --reload

```

```

```
