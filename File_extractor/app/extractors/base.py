from abc import ABC, abstractmethod
from app.schemas import ExtractedUnit
from typing import List

class BaseExtractor(ABC):
    def __init__(self, file_bytes: bytes, filename: str):
        self.file_bytes = file_bytes
        self.filename = filename

    @abstractmethod
    def extract(self) -> List[ExtractedUnit]:
        """
        All extractors must implement this method.
        Returns a list of standardized ExtractedUnits.
        """
        pass