import io
import pandas as pd
from app.extractors.base import BaseExtractor
from app.schemas import ExtractedUnit, Location

class TableExtractor(BaseExtractor):
    def __init__(self, file_bytes, filename, is_csv=False):
        super().__init__(file_bytes, filename)
        self.is_csv = is_csv

    def extract(self):
        units = []
        file_io = io.BytesIO(self.file_bytes)
        
        try:
            if self.is_csv:
                dfs = {'csv': pd.read_csv(file_io, header=None)}
            else:
                # Read all sheets from Excel
                dfs = pd.read_excel(file_io, sheet_name=None)
        except Exception:
            return [] # Return empty if parsing fails

        for sheet_name, df in dfs.items():
            # Replace NaNs with empty string
            df = df.fillna("")
            
            # Iterate rows
            for index, row in df.iterrows():
                # Join row values with a pipe delimiter for readability
                row_values = [str(x) for x in row.values if str(x).strip()]
                if not row_values:
                    continue
                    
                row_text = " | ".join(row_values)
                
                units.append(ExtractedUnit(
                    text=row_text,
                    source=str(sheet_name),
                    location=Location(type="row", number=index+1, sheet=str(sheet_name))
                ))
        return units