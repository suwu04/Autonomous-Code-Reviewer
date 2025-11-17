# _test_agent.py
import sys
import os
from dotenv import load_dotenv

# --- CLEANED UP SETUP ---
# Just load the .env file to get GitHub + HF tokens
load_dotenv()
# ------------------------

# Add 'app' folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

# Now we can import our modules
from api_tools.github_fetcher import GitHubFetcher
from agent.code_reviewer import CodeReviewerCrew
from models import AnalysisResults

# --- CONFIGURATION ---
TEST_REPO_URL = "https://github.com/pallets/flask"
TEST_PR_NUMBER = 5384
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# ---------------------

print("--- Testing CodeReviewerCrew (LiteLLM + Hugging Face) ---")
print(f"Target: {TEST_REPO_URL}/pull/{TEST_PR_NUMBER}\n")
print("NOTE: This test will connect to the Hugging Face Inference API via LiteLLM.")
print("It may take 30-60 seconds for the AI to generate a response...\n")

if not os.getenv("HUGGINGFACE_API_TOKEN"):
    print("❌ ERROR: HUGGINGFACE_API_TOKEN not found in .env file.")
    print("Please make sure it's added (hf_...) and spelled correctly.")
    exit()

try:
    # 1. Fetch real diff data
    print("Step 1: Fetching PR diff...")
    fetcher = GitHubFetcher(token=GITHUB_TOKEN)
    diff_content = fetcher.fetch_pr_diff(TEST_REPO_URL, TEST_PR_NUMBER)
    
    if not diff_content:
        raise Exception("Failed to fetch diff. Test cannot continue.")
    
    print("Step 1: Success. Diff fetched.\n")

    # 2. Initialize and run the agent
    print("Step 2: Initializing CodeReviewerCrew...")
    reviewer = CodeReviewerCrew()
    
    print("Step 2: Success. Crew initialized.")
    print("Step 3: Calling review_code()... (This is the slow part)\n")
    
    results: AnalysisResults = reviewer.review_code(
        TEST_REPO_URL, 
        TEST_PR_NUMBER, 
        diff_content
    )
    
    print("\nStep 3: Success. Agent finished.\n")

    # 4. Print the final structured JSON output
    print("--- ✅ TEST SUCCEEDED ---")
    print("Final Structured Output:")
    print(results.model_dump_json(indent=2))

except Exception as e:
    print(f"❌ TEST FAILED WITH ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Test complete ---")