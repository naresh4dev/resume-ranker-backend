from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from uuid import uuid4
from services.file_parser import parse_file
from pathlib import Path
from services.nlp_processor import process_candidates
import os
from services.report_generator import generate_final_report
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
router = APIRouter()
@router.post("/upload")
def upload_file(
    files: List[UploadFile] = File(...),
    job_description: str = Form(...)
):
    
    BASE_DIR= Path(__file__).resolve().parent.parent
    resumes = []
    for file in files:
        ext = os.path.splitext(file.filename)[1]
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file extension: {file.filename}")
        file_id = str(uuid4())
    # Save the file to a specific path
        fileName = f"{file_id}${file.filename}"
        path = f"{BASE_DIR}/data/resume/{fileName}"
        with open(path, "wb") as f:
            f.write(file.file.read())
    # Call the file parser service to parse the file
        resume_text = parse_file(path)
        resumes.append((fileName, resume_text))
    job_summary,top_skills,common_skill_gaps,results = process_candidates(job_description, resumes)
    if not results:
        raise HTTPException(status_code=404, detail="No matching resumes found")
    response_json = {
        "job_summary":job_summary,
        "report_path":"",
        "top_skills":top_skills,
        "common_skill_gaps":common_skill_gaps,
        "results":results,

        }
    report_path = generate_final_report(response_json)
    response_json["report_path"] = f"http://localhost:8000/api/assets/reports/{report_path}"
    return response_json