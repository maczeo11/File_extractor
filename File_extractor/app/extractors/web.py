from bs4 import BeautifulSoup
from app.extractors.base import BaseExtractor
from app.schemas import ExtractedUnit, Location

class HTMLExtractor(BaseExtractor):
    def extract(self):
        soup = BeautifulSoup(self.file_bytes, 'html.parser')
        
        # Security: Remove JS and CSS
        for script in soup(["script", "style", "meta", "noscript"]):
            script.decompose()
        
        # Get text with newlines
        text = soup.get_text(separator='\n')
        
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        return [ExtractedUnit(
            text=line,
            source="html_body",
            location=Location(type="row", number=i+1)
        ) for i, line in enumerate(lines)]