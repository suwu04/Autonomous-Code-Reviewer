# app/agent/code_reviewer.py
from crewai import Agent, Task, Crew
from app.models import AnalysisResults
from typing import List
import os
import json
import re  # Import regular expressions
from pydantic import ValidationError

class CodeReviewerCrew:
    
    def __init__(self):
        api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not api_token:
            raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables.")
        os.environ["HF_TOKEN"] = api_token
        
        # --- GOING BACK TO THE FIRST MODEL THAT WORKED ---
        self.model_name = "huggingface/meta-llama/Meta-Llama-3-8B-Instruct"
        
        self.reviewer_agent = Agent(
            role='Senior Code Quality Reviewer',
            goal=(
                "Analyze GitHub pull request diffs to find bugs, style issues, "
                "performance bottlenecks, and best practice violations."
            ),
            backstory=(
                "You are an AI assistant specialized in code review. "
                "You have a keen eye for detail and a deep understanding of "
                "software engineering principles. Your goal is to provide "
                "constructive, actionable feedback in a structured JSON format. "
                "You must identify the specific file and line number for every issue."
            ),
            verbose=True,
            allow_delegation=False,
            llm=self.model_name
        )
    
    def _parse_diff(self, diff_content: str) -> str:
        """Helper function to truncate the diff."""
        max_length = 15000 
        if len(diff_content) > max_length:
            return diff_content[:max_length] + "\n... (diff truncated) ..."
        return diff_content

    def _extract_json_from_text(self, text: str) -> dict:
        """
        Finds and parses the first valid JSON block (from { to }) 
        in a potentially messy string.
        
        If no JSON is found, returns an empty result.
        """
        # Use regex to find the first complete JSON object
        match = re.search(r'\{.*\}', text, re.DOTALL)
        
        if not match:
            # --- THIS IS THE FIX ---
            # If no JSON is found, assume no issues were found.
            # This is common if the AI just says "Looks good!"
            print("No JSON block found in AI response. Assuming no issues.")
            return {
                "files": [],
                "summary": {
                    "total_files": 0,
                    "total_issues": 0,
                    "critical_issues": 0
                }
            }
            # ---------------------
            
        json_str = match.group(0)
        
        try:
            # Try to parse the extracted string
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"AI returned malformed JSON that could not be parsed. Error: {e}")

    # In app/agent/code_reviewer.py

    def review_code(self, repo_url: str, pr_number: int, diff_content: str) -> AnalysisResults:
        
        parsed_diff = self._parse_diff(diff_content)
        
        # --- THIS IS THE NEW, STRICTER PROMPT ---
        # We are giving the AI the exact schema to follow.
        json_schema = """
        {
          "files": [
            {
              "name": "path/to/file.py",
              "issues": [
                {
                  "type": "bug" | "style" | "performance" | "best_practice",
                  "line": 123,
                  "description": "A description of the issue.",
                  "suggestion": "A suggestion to fix the issue."
                }
              ]
            }
          ],
          "summary": {
            "total_files": 1,
            "total_issues": 1,
            "critical_issues": 0
          }
        }
        """

        review_task = Task(
            description=f"""
                Review the code diff below for PR #{pr_number} from {repo_url}.
                Identify bugs, style issues, performance issues, and best practices.

                Code Diff:
                ---
                {parsed_diff}
                ---

                You MUST return your analysis in this EXACT JSON format.
                Pay close attention to the field names ("name", "type", "line", "suggestion").

                SCHEMA:
                {json_schema}

                If no issues are found, return:
                {{"files": [], "summary": {{"total_files": 0, "total_issues": 0, "critical_issues": 0}}}}
            """,
            agent=self.reviewer_agent,
            expected_output="A single, valid JSON code block containing the analysis."
        )

        # Create and Run the Crew
        crew = Crew(
            agents=[self.reviewer_agent],
            tasks=[review_task],
            verbose=True
        )
        
        result = crew.kickoff()

        # Get the raw text, no matter what object type
        raw_output = ""
        if hasattr(result, 'raw') and isinstance(result.raw, str):
            raw_output = result.raw
        elif isinstance(result, str):
            raw_output = result
        else:
            raw_output = str(result)

        try:
            # Clean and parse the raw text
            json_data = self._extract_json_from_text(raw_output)
            
            # Validate the clean JSON with Pydantic
            return AnalysisResults.parse_obj(json_data)

        except (ValueError, json.JSONDecodeError, TypeError) as e:
            # If our manual parsing fails, raise the clean error
            print(f"Failed to parse extracted JSON: {e}")
            raise ValueError("The AI agent returned a malformed or incomplete response. This can happen under high load. Please try again.")