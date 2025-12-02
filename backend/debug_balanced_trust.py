import asyncio
import os
from dotenv import load_dotenv
from agent import RiskAssessmentAgent

# Load environment variables
load_dotenv()

async def debug_balanced_trust():
    agent = RiskAssessmentAgent()
    company_name = "BalancedTrust"
    address = "Florida"
    state = "Florida"
    company_type = "Financial Services"

    print(f"--- Debugging Assessment for {company_name} ---")
    
    # We will manually run the search logic here to inspect it, 
    # mirroring the logic in agent.py but with print statements instead of yields
    
    search_queries = [
        f"site:balanced-trust.co", # Check if indexed
        f"BalancedTrust homepage",
        f"BalancedTrust",
    ]
    
    all_results = []

    for query in search_queries:
        print(f"\n🔎 Query: {query}")
        try:
            results = agent.search.results(query, 10) # Using 10 as per V2
            print(f"   Found {len(results)} results.")
            
            for i, r in enumerate(results):
                print(f"   {i+1}. {r.get('title')} - {r.get('link')}")
            
            all_results.extend(results)

        except Exception as e:
            print(f"   ⚠️ Error: {e}")

    # Identify if the official site is found
    official_site = None
    for r in all_results:
        link = r.get("link", "")
        if "balanced-trust.co" in link:
            official_site = link
            print(f"\n✅ FOUND OFFICIAL SITE: {link}")
            break
    
    if not official_site:
        print("\n❌ OFFICIAL SITE (balanced-trust.co) NOT FOUND IN SEARCH RESULTS.")
    
    print("\n--- End Debug ---")

if __name__ == "__main__":
    asyncio.run(debug_balanced_trust())
