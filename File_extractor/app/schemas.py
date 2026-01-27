from pydantic import BaseModel
from typing import List, Literal, Union, Optional

class Location(BaseModel):
    """Polymorphic location to handle different file types"""
    type: Literal["page", "row", "pixel_box"]
    number: Optional[int] = None
    sheet: Optional[str] = None
    # For OCR bounding boxes (x, y, width, height) if needed later
    coordinates: Optional[List[int]] = None 

class ExtractedUnit(BaseModel):
    """The atomic unit of extracted data"""
    text: str
    source: str  # e.g., "page_1" or "sheet_financials"
    location: Location

class DocumentResponse(BaseModel):
    """The final standardized output sent to the UI"""
    filename: str
    file_type: str
    processing_time_ms: float
    content: List[ExtractedUnit]