import asyncio
from dotenv import load_dotenv
from agent import RiskAssessmentAgent

load_dotenv()

async def find_url():
    agent = RiskAssessmentAgent()
    query = "BalancedTrust Florida"
    print(f"Searching for: {query}")
    results = agent.search.results(query, 5)
    for i, r in enumerate(results):
        print(f"{i+1}. {r.get('title')} - {r.get('link')}")

if __name__ == "__main__":
    asyncio.run(find_url())
