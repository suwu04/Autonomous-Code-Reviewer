# app/api_tools/github_fetcher.py
import requests
from urllib.parse import urlparse
from typing import Optional

class GitHubFetcher:
    """A tool to fetch Pull Request data from GitHub."""
    
    def __init__(self, token: Optional[str] = None):
        self.headers = {
            "Accept": "application/vnd.github.v3.diff"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
            
    def _parse_url(self, repo_url: str):
        """Extracts 'owner/repo' from 'https://github.com/owner/repo'."""
        path = urlparse(repo_url).path.strip('/')
        
        # Remove .git suffix if present
        if path.endswith('.git'):
            path = path[:-4]
            
        parts = path.split('/')
        if len(parts) >= 2:
            return f"{parts[0]}/{parts[1]}"
        
        raise ValueError("Invalid GitHub repository URL format. Expected 'https://github.com/owner/repo'.")

    def fetch_pr_diff(self, repo_url: str, pr_number: int) -> str:
        """Fetches the unified diff content of a pull request."""
        
        try:
            repo_path = self._parse_url(repo_url)
            api_url = f"https://api.github.com/repos/{repo_path}/pulls/{pr_number}"
            
            print(f"Fetching diff from: {api_url}")
            
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                # The response.text is the unified diff
                return response.text
            elif response.status_code == 404:
                raise FileNotFoundError(f"PR #{pr_number} not found for {repo_path}")
            elif response.status_code == 403:
                print("GitHub API rate limit exceeded or forbidden.")
                raise PermissionError(f"GitHub API error: {response.json().get('message')}")
            else:
                # Raise an exception for other bad status codes
                response.raise_for_status()
                return "" # Should not be reached

        except requests.exceptions.RequestException as e:
            print(f"HTTP Request failed: {e}")
            raise
        except ValueError as e:
            print(f"URL parsing failed: {e}")
            raise