import os
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

def parse_file(filepath: str) -> str:
    
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    if ext == ".pdf":
        reader = PdfReader(filepath)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif ext == ".docx":
        doc = DocxDocument(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported file type")
    text = " ".join(text.split()) 
    return text
