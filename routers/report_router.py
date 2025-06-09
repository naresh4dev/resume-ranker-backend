from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent


@router.get("/{file_type}/{file_name}")
def get_files(file_type: str, file_name: str):
    
    file_path = BASE_DIR / "data" / file_type / file_name

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume not found")

    return FileResponse(file_path, media_type="application/pdf", filename=file_name)
