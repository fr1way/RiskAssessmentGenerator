import os
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSearchAPIWrapper

load_dotenv()

def debug_search():
    print("\n--- Debugging Search Quality for 'Groma' ---")
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    
    if not api_key or not cse_id:
        print("Missing keys.")
        return

    search = GoogleSearchAPIWrapper(google_api_key=api_key, google_cse_id=cse_id)
    
    # Queries from agent.py (simulated inputs)
    company_name = "Groma"
    address = "Boston MA" # Assuming this from screenshot
    state = "MA"
    
    queries = [
        f"{company_name} {address} {state} company profile",
        f"{company_name} {state} reviews complaints BBB reddit",
        f"{company_name} {state} lawsuits legal issues",
        f"{company_name} {state} financial funding revenue crunchbase",
        f"{company_name} {state} executive team leadership CEO founder",
        f"{company_name} {state} news scandal controversy",
    ]

    for q in queries:
        print(f"\nQuery: {q}")
        try:
            results = search.results(q, 3)
            if not results:
                print("  [NO RESULTS]")
            for i, r in enumerate(results):
                print(f"  Result {i+1}: {r.get('title')}")
                print(f"    Snippet: {r.get('snippet')}")
                print(f"    Link: {r.get('link')}")
        except Exception as e:
            print(f"  [ERROR] {e}")

if __name__ == "__main__":
    debug_search()
