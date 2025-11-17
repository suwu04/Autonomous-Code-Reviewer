# _test_fetcher.py
import sys
import os
from dotenv import load_dotenv # <-- Import dotenv

# --- NEW: Load environment variables from .env file ---
load_dotenv()
# ----------------------------------------------------

# This magic line adds your 'app' folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from api_tools.github_fetcher import GitHubFetcher

# --- CONFIGURATION ---
# _test_fetcher.py

TEST_REPO_URL = "https://github.com/pallets/flask"
TEST_PR_NUMBER = 5384 # A simple documentation fix
...

# --- NEW: Read token from environment ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") 
# ----------------------------------------

print("--- Testing GitHubFetcher ---")
print(f"Target: {TEST_REPO_URL}/pull/{TEST_PR_NUMBER}\n")

if not GITHUB_TOKEN:
    print("NOTE: GITHUB_TOKEN not found in .env file. Running test without authentication.")
    print("You may hit rate limits quickly.\n")
else:
    print("NOTE: Using GITHUB_TOKEN from .env file for authentication.\n")

try:
    # 1. Initialize the fetcher
    fetcher = GitHubFetcher(token=GITHUB_TOKEN)
    
    # 2. Call the method
    diff_content = fetcher.fetch_pr_diff(TEST_REPO_URL, TEST_PR_NUMBER)
    
    # 3. Check the result
    if diff_content and len(diff_content) > 0:
        print("✅ SUCCESS: Successfully fetched diff content.\n")
        print("--- First 500 characters of diff ---")
        print(diff_content[:500])
        print("--------------------------------------")
    else:
        print("❌ FAILURE: No diff content was returned.")
        
except Exception as e:
    print(f"❌ TEST FAILED WITH ERROR: {e}")

print("\n--- Test complete ---")