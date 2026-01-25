import cv2
import numpy as np
from PIL import Image
import io

def preprocess_image_for_ocr(image_bytes: bytes) -> Image.Image:
    """
    Converts raw bytes -> Grayscale -> Thresholded Image
    Drastically improves Tesseract accuracy.
    """
    # 1. Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 2. Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Threshold (Binarization) using Otsu's method
    # This removes shadows and makes text strictly black/white
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 4. Convert back to PIL Image for Tesseract
    return Image.fromarray(thresh)