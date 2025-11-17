# app/celery_tasks.py
import traceback
from typing import Optional
import requests
from pydantic import ValidationError  # Correct import

from .worker import celery_app
from .api_tools.github_fetcher import GitHubFetcher
from .agent.code_reviewer import CodeReviewerCrew
from .models import AnalysisResults

@celery_app.task(bind=True)
def analyze_pr_task(self, repo_url: str, pr_number: int, github_token: Optional[str] = None):
    
    print(f"Starting task {self.request.id} for {repo_url}/pull/{pr_number}")
    
    try:
        # 1. Update status to PROCESSING
        self.update_state(state='PROCESSING', meta={'repo': repo_url, 'pr': pr_number})

        # 2. Fetch Code Diff
        print(f"[{self.request.id}] Fetching diff...")
        fetcher = GitHubFetcher(token=github_token)
        pr_diff = fetcher.fetch_pr_diff(repo_url, pr_number)
        
        if not pr_diff or pr_diff.strip() == "":
            print(f"[{self.request.id}] No diff content found.")
            raise ValueError("No diff content found for the specified PR.")

        # 3. Run AI Agent Review
        print(f"[{self.request.id}] Starting AI review...")
        
        reviewer = CodeReviewerCrew()
        analysis_results: AnalysisResults = reviewer.review_code(repo_url, pr_number, pr_diff)
        
        print(f"[{self.request.id}] AI review complete.")

        # 4. Store Result
        return analysis_results.dict()

    # --- CORRECT ERROR HANDLING ---
    except requests.exceptions.ConnectionError as e:
        print(f"[{self.request.id}] NETWORK ERROR: {e}")
        user_message = "Network Error: Could not connect to GitHub or AI service. Please check your internet connection and try again."
        
        self.update_state(state='FAILED', meta={
            'error': user_message,
            'traceback': traceback.format_exc()
        })
        raise
    
    except (ValidationError, ValueError) as e:
        # This catches Pydantic errors AND our custom ValueError
        print(f"[{self.request.id}] VALIDATION/VALUE ERROR: {e}")
        
        # Get the clean error message we raised from the agent
        user_message = str(e)

        self.update_state(state='FAILED', meta={
            'error': user_message,
            'traceback': traceback.format_exc()
        })
        raise
        
    except Exception as e:
        # This catches all other unexpected errors
        print(f"[{self.request.id}] TASK FAILED: {e}")
        user_message = f"An unexpected error occurred: {str(e)}"

        self.update_state(state='FAILED', meta={
            'error': user_message,
            'traceback': traceback.format_exc()
        })
        raise