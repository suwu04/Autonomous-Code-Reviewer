# app/models.py
from pydantic import BaseModel, Field
from typing import List, Optional

# --- API Input Model ---
class PRAnalysisRequest(BaseModel):
    """Input model for the POST /analyze-pr endpoint."""
    repo_url: str = Field(..., example="https://github.com/fastapi/fastapi")
    pr_number: int = Field(..., example=123)
    github_token: Optional[str] = Field(None, description="Optional GitHub PAT")

# --- Structured AI Output Models ---
class Issue(BaseModel):
    """Represents a single issue found in a file."""
    type: str = Field(..., description="Type of issue: 'style', 'bug', 'performance', 'best_practice'")
    line: int = Field(..., description="Line number where the issue was found")
    description: str = Field(..., description="Detailed description of the issue")
    suggestion: str = Field(..., description="Proposed fix or improvement")

class FileAnalysis(BaseModel):
    """Analysis results for a single file."""
    name: str = Field(..., description="Name of the file (e.g., 'app/main.py')")
    issues: List[Issue] = Field(..., description="List of issues found in the file")

class AnalysisSummary(BaseModel):
    """Summary of the overall analysis."""
    total_files: int
    total_issues: int
    critical_issues: int = Field(..., description="Count of issues marked as 'bug' or 'critical'")

class AnalysisResults(BaseModel):
    """The final structured output from the AI agent."""
    files: List[FileAnalysis]
    summary: AnalysisSummary

# --- API Output Models (for tracking tasks) ---
class TaskStatus(BaseModel):
    task_id: str
    status: str
    message: Optional[str] = None
    
class FinalTaskResult(BaseModel):
    """Model for the GET /results/<task_id> endpoint."""
    task_id: str
    status: str
    results: Optional[AnalysisResults] = None