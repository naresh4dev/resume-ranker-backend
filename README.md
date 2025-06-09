## ⚙️ Backend Setup (FastAPI + Python)



### 1. Create a virtual environment (Recommended):

```bash
python -m venv backend
source backend/bin/activate  # On Windows: backend\Scripts\activate
```
### 2. Navigate to the backend directory:

```bash
cd backend
```

### 3. Install required packages:

```bash
pip install -r requirements.txt
```

### 4. Download required models:

```bash
# spaCy model
python -m spacy download en_core_web_sm
```

### 5. Run the FastAPI server:

```bash
uvicorn server:app --reload
```

> 🔗 **API Base URL:** `http://localhost:8000`

---

### 📡 API Endpoints

| Method | Endpoint                                | Description                             |
|--------|-----------------------------------------|-----------------------------------------|
| POST   | `/api/upload`                           | Upload resumes and job description      |
| GET    | `/api/assets/{file_type}/{file_name}`   | Get generated reports/resumes as PDF    |
| GET    |  `/health`                              | Application running state check         |
