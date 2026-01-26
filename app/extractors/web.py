from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.utils import detect_file_type
from app.extractors.documents import PDFExtractor, WordExtractor
from app.extractors.images import ImageExtractor
from app.extractors.tables import TableExtractor
from app.extractors.html import HTMLExtractor

router = APIRouter()


def get_extractor(file_bytes: bytes, filename: str):
    ftype = detect_file_type(file_bytes, filename)

    if ftype == "pdf":
        return PDFExtractor(file_bytes, filename)

    elif ftype == "docx":
        return WordExtractor(file_bytes, filename)

    elif ftype == "image":
        return ImageExtractor(file_bytes, filename)

    elif ftype == "excel":
        return TableExtractor(file_bytes, filename)

    elif ftype == "csv":
        return TableExtractor(file_bytes, filename, is_csv=True)

    elif ftype == "html":
        return HTMLExtractor(file_bytes, filename)

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {filename}"
        )


@router.post("/extract")
async def extract_files(files: List[UploadFile] = File(...)):

    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 files allowed"
        )

    results = []

    for file in files:
        file_bytes = await file.read()
        extractor = get_extractor(file_bytes, file.filename)
        content = extractor.extract()

        results.append({
            "filename": file.filename,
            "file_type": detect_file_type(file_bytes, file.filename),
            "content": content
        })

    return {"results": results}
