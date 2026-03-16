from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from src.rag.pipeline import ingest_documents
from src.security.rate_limiter import validate_pdf
from src.config.settings import settings
import tempfile
import os

router = APIRouter()

@router.post("/upload")
async def upload_documents(file: UploadFile = File(...)):

    content = await file.read()

    validate_pdf(
        filename=file.filename,
        file_size=len(content)
    )

    file_path = None
    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:
            tmp.write(content)
            file_path = tmp.name


        result = ingest_documents([(file_path, file.filename)])

        return {
            "status": "success",
            "message": f"{file.filename} uploaded and processed successfully",
            **result
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )

    finally:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)