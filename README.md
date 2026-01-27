File_extractor

small project , a text extractor that works by extracting text from varios file types

🚀 Universal Text Extraction Web App
robust, modular web application designed to extract text from a wide variety of real-world document formats (PDFs, Images, Word Docs, and Tables) and convert them into a standardized, machine-readable JSON structure.

This project implements the Strategy Design Pattern, allowing for seamless expansion to new file types without modifying the core routing logic.

🏗️ Project Architecture

The application is split into a modern decoupled architecture:

Backend: FastAPI (Python) serving as a high-performance REST API.

Frontend: A responsive UI for file uploads and result visualization.

Processing Engine: Utilizes binary signature detection to route files to specialized extractors (Tesseract OCR, OpenCV, PDFPlumber, and Pandas).

📁 Repository Structure

├── app/              # FastAPI Backend logic
├── frontend/         # React/Next.js UI components
├── Dockerfile        # Containerization for easy deployment
├── requirements.txt  # Python dependencies
└── .gitignore        # Standard git exclusion rules

🛠️ Setup & Installation
1. Prerequisites
Python 3.9+

Tesseract OCR Engine:

Windows: Install via UB Mannheim and add to PATH.

Linux: sudo apt-get install tesseract-ocr libmagic1

macOS: brew install tesseract libmagic

2. Local Development
1.Clone the repo:
git clone https://github.com/maczeo11/File_extractor.git
cd File_extractor.

2.Backend Setup:
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

3.Frontend Setup:
cd frontend
npm install
npm run dev

4. Docker Deployment
docker build -t file-extractor .
docker run -p 8000:8000 file-extractor

📜 API Documentation
Once the backend is running, you can access the interactive Swagger documentation at: http://localhost:8000/docs

1. BACKEND DOCUMENTATION
A. Prerequisites
Before running the server, ensure you have the following installed:

Python 3.9+

Tesseract OCR Engine:

Windows: Download from UB Mannheim. Important: Add C:\Program Files\Tesseract-OCR to your System PATH.

Linux: sudo apt-get install tesseract-ocr libmagic1

Mac: brew install tesseract libmagic

2. Installation
Navigate to the project directory and install the required Python libraries:

Bash
# Clone the repository
git clone https://github.com/maczeo11/File_extractor.git

3.Install dependencies
pip install -r requirements.txt
C. Running the Application
Start the FastAPI server using Uvicorn:

Bash
python -m uvicorn app.main:app --reload
Once running, visit http://127.0.0.1:8000/docs to test the API endpoints directly.

4. KEY FEATURES
Multi-Format Support: Handles .pdf, .docx, .jpg, .png, and .csv.

Table Extraction: Intelligently identifies and parses tabular data from within documents.

Scalability: The modular "Strategy" approach allows developers to add new file-type extractors with minimal code changes.

API-First Design: Fully documented REST API via Swagger UI.

5. INSTALLATION & SETUP
Step 1: System Dependencies Install Tesseract OCR on your local machine and ensure it is added to your system environment variables.

Step 2: Environment Setup ```bash git clone https://www.google.com/search?q=https://github.com/maczeo11/File_extractor.git pip install -r requirements.txt

**Step 3: Execution** Run the server using Uvicorn:
```bash
python -m uvicorn app.main:app --reload
