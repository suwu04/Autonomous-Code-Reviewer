# app/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware  # <-- ADDED
from celery.result import AsyncResult
from typing import Optional
import os

# Import our Celery task and models
from .celery_tasks import analyze_pr_task
from .worker import celery_app  # Import the celery_app instance
from .models import (
    PRAnalysisRequest, 
    TaskStatus, 
    FinalTaskResult, 
    AnalysisResults
)

app = FastAPI(title="Autonomous Code Reviewer API")

# --- 1. ADD CORS MIDDLEWARE ---
# This allows our front-end (on the same origin) to talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- 2. SETUP STATIC FILES AND TEMPLATES ---
# Mount the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")
# Find templates in the 'static' directory
templates = Jinja2Templates(directory="static")


# --- 3. CREATE ROOT ENDPOINT TO SERVE HTML ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main index.html front-end page.
    """
    return templates.TemplateResponse("index.html", {"request": request})


# --- 4. API ENDPOINTS (No changes here, just for context) ---

# POST /analyze-pr
@app.post("/analyze-pr", response_model=TaskStatus)
async def analyze_pr(request: PRAnalysisRequest):
    github_token = os.getenv("GITHUB_TOKEN")
    task = analyze_pr_task.delay(
        request.repo_url, 
        request.pr_number, 
        github_token
    )
    return TaskStatus(
        task_id=task.id,
        status=task.status,
        message="Analysis task queued successfully."
    )

# GET /status/<task_id>
@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    status = task_result.status
    message = status
    
    if status == 'FAILURE':
        result_info = task_result.info
        if isinstance(result_info, dict):
            message = f"Task failed: {result_info.get('error', 'Unknown error')}"
        elif isinstance(result_info, Exception):
             message = f"Task failed: {result_info}"
        else:
             message = "Task failed with an unknown error."
    elif status == 'PROCESSING':
        message = "Task is currently being processed by a worker."
    elif status == 'PENDING':
        message = "Task is waiting in the queue."
        
    return TaskStatus(
        task_id=task_id,
        status=status,
        message=message
    )

# GET /results/<task_id>
@app.get("/results/{task_id}", response_model=FinalTaskResult)
async def get_task_results(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    
    if not task_result.ready():
        raise HTTPException(
            status_code=409, 
            detail=f"Task {task_id} is still {task_result.status}. Use /status/{task_id} to monitor."
        )
            
    if task_result.status == 'SUCCESS':
        results_data = task_result.result
        try:
            results_model = AnalysisResults.parse_obj(results_data)
            return FinalTaskResult(
                task_id=task_id,
                status="completed",
                results=results_model
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Result schema validation failed: {e}")
            
    elif task_result.status == 'FAILURE':
        result = task_result.info
        error_message = str(result.get('error', 'Unknown error'))
        raise HTTPException(
            status_code=500, 
            detail=f"Task {task_id} failed. Error: {error_message}"
        )
        
    return HTTPException(status_code=404, detail="Task not found.")