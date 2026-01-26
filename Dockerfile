# 1. Use Python 3.9
FROM python:3.9-slim

# 2. Install Tesseract and system tools (The "Engine")
# This is the Linux equivalent of the .exe installer
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libmagic1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Python libraries
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy your code
COPY . .

# 5. Run the app# Use "sh -c" to read the variable $PORT from Railway (or default to 8000 locally)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]