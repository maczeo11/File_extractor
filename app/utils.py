import cv2
import numpy as np
from PIL import Image
import io
import os

# ---------- IMAGE PREPROCESSING (USED BY OCR) ----------
def preprocess_image_for_ocr(image_bytes: bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = np.array(image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255,
                          cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    return gray


# ---------- FILE TYPE DETECTION ----------
def detect_file_type(file_bytes: bytes, filename: str) -> str:
    """
    Detect file type using filename extension.
    """

    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return "pdf"
    elif ext in [".docx"]:
        return "docx"
    elif ext in [".jpg", ".jpeg", ".png"]:
        return "image"
    elif ext in [".xls", ".xlsx"]:
        return "excel"
    elif ext == ".csv":
        return "csv"
    elif ext in [".html", ".htm"]:
        return "html"
    else:
        return "unknown"
