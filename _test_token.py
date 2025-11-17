# _test_token.py
import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("❌ ERROR: GITHUB_TOKEN not found in your .env file.")
    print("Please make sure it's added and spelled correctly.")
    exit()

print("--- Testing Token Authentication and Scopes ---")

# We will hit the root API endpoint. 
# It doesn't require any scopes to *access*, 
# but it will tell us *which* scopes the token has.
api_url = "https://api.github.com"
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

try:
    response = requests.get(api_url, headers=headers)

    # Check for bad token
    if response.status_code == 401:
        print(f"❌ TEST FAILED (401 Unauthorized)")
        print("This means your GITHUB_TOKEN string is incorrect or has been revoked.")
        print("Please re-copy the token from GitHub into your .env file.")

    # Check for other errors
    elif response.status_code != 200:
        print(f"❌ TEST FAILED (Status Code: {response.status_code})")
        print(response.json())

    # If successful, check the scopes
    else:
        print("✅ TEST SUCCEEDED (Authenticated successfully)")
        scopes = response.headers.get('X-OAuth-Scopes')
        print(f"\nYour token has the following scopes:")
        print(f"X-OAuth-Scopes: {scopes}")

        # This is the check we care about
        if 'repo' in str(scopes) or 'public_repo' in str(scopes):
            print("\n✅ --- PERMISSIONS ARE CORRECT --- ✅")
            print("Your token has the 'repo' or 'public_repo' scope.")
        else:
            print("\n❌ --- PERMISSIONS ARE MISSING --- ❌")
            print("Your token is VALID, but it LACKS the required 'public_repo' or 'repo' scope.")
            print("This is why you are getting a '404 Not Found' error.")

except Exception as e:
    print(f"❌ TEST FAILED WITH EXCEPTION: {e}")

print("\n--- Test complete ---")