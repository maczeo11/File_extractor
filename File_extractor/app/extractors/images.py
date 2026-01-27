import pytesseract
from app.extractors.base import BaseExtractor
from app.schemas import ExtractedUnit, Location
from app.utils import preprocess_image_for_ocr

class ImageExtractor(BaseExtractor):
    def extract(self):
        # 1. Preprocess using OpenCV (defined in utils.py)
        processed_image = preprocess_image_for_ocr(self.file_bytes)
        
        # 2. Run Tesseract
        text = pytesseract.image_to_string(processed_image)
        
        if not text.strip():
            return []

        return [ExtractedUnit(
            text=text.strip(),
            source="ocr_engine",
            location=Location(type="pixel_box", number=1)
        )]