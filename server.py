from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.upload_router import router as upload_router
from routers.report_router import router as assest_router

app = FastAPI()
# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(assest_router,prefix="/api/assets", tags=["assets"])
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Server is running"}