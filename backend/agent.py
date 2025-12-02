import os
import asyncio
import random
import json
from playwright.async_api import async_playwright
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.prompts import PromptTemplate

async def browse_url_content(url: str) -> str:
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                # Wait a bit for dynamic content
                await page.wait_for_timeout(3000)
                
                # Extract text from body
                text = await page.evaluate("document.body.innerText")
                
                # Simple cleaning
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return text[:5000]  # Increased limit for browser content
            finally:
                await browser.close()
    except Exception as e:
        print(f"Error browsing {url}: {e}")
        return ""

async def crawl_site_map(url: str):
    """
    Crawls the homepage to find high-value sub-pages (Team, About, Investors, etc.).
    Yields log messages and finally the list of found URLs.
    """
    high_value_keywords = ["about", "team", "leadership", "investor", "financial", "legal", "contact", "careers", "board", "governance"]
    found_urls = set()
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                yield json.dumps({"type": "log", "message": f"🕷️ Crawling homepage: {url}..."}) + "\n"
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                
                # Extract all links
                links = await page.evaluate("""
                    () => {
                        return Array.from(document.querySelectorAll('a')).map(a => ({
                            href: a.href,
                            text: a.innerText.toLowerCase()
                        }));
                    }
                """)
                
                yield json.dumps({"type": "log", "message": f"🕸️ Found {len(links)} links on homepage."}) + "\n"
                
                for link in links:
                    href = link['href']
                    text = link['text']
                    
                    # Basic validation
                    if not href or href.startswith("javascript") or href.startswith("mailto"):
                        continue
                        
                    # Check if it matches keywords (in URL or text)
                    if any(kw in href.lower() or kw in text for kw in high_value_keywords):
                        # Ensure it's the same domain (or subdomain)
                        if url in href or href.startswith("/"):
                            if href not in found_urls:
                                found_urls.add(href)
                                yield json.dumps({"type": "log", "message": f"✨ Discovered high-value link: {text} -> {href}"}) + "\n"
                            
            finally:
                await browser.close()
                
    except Exception as e:
        yield json.dumps({"type": "log", "message": f"⚠️ Error crawling site map: {e}"}) + "\n"
        
    # Yield the final list as a special message or just return it?
    # Generators can return values in Python 3.3+, but async generators cannot return values (only yield).
    # So we yield a special type.
    yield json.dumps({"type": "mapped_urls", "urls": list(found_urls)[:5]}) + "\n"

class RiskAssessmentAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        if not api_key or not cse_id:
            print("Warning: GOOGLE_API_KEY or GOOGLE_CSE_ID not found.")
        
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key, temperature=0.2)
        self.search = GoogleSearchAPIWrapper(google_api_key=api_key, google_cse_id=cse_id)



    async def discover_official_site(self, company_name: str, state: str) -> str | None:
        """Attempts to find the official website of the company."""
        queries = [
            f"{company_name} official site",
            f"{company_name} {state} official website",
            f"{company_name} homepage"
        ]
        
        for query in queries:
            try:
                results = self.search.results(query, 3)
                for r in results:
                    link = r.get("link", "")
                    # Basic filter to avoid social media/news aggregators if possible
                    # This is a heuristic; can be improved
                    if "linkedin.com" in link or "facebook.com" in link or "bloomberg.com" in link:
                        continue
                    return link
            except Exception:
                continue
        return None

    async def run_assessment(self, company_name: str, address: str, state: str, company_type: str):
        # 1. Gather Information
        yield json.dumps({"type": "log", "message": f"🔍 Initializing deep research for {company_name}..."}) + "\n"
        
        # Phase 0: Discover Official Site
        official_site = await self.discover_official_site(company_name, state)
        
        mapped_urls = []
        if official_site:
             yield json.dumps({"type": "log", "message": f"🎯 Identified potential official site: {official_site}"}) + "\n"
             
             # Phase 1: Map the Site (Perplexity-style)
             yield json.dumps({"type": "log", "message": f"🗺️ Mapping site structure for {official_site}..."}) + "\n"
             
             async for msg in crawl_site_map(official_site):
                 # Check if it's the result list
                 try:
                     data = json.loads(msg)
                     if data.get("type") == "mapped_urls":
                         mapped_urls = data.get("urls", [])
                         if mapped_urls:
                             yield json.dumps({"type": "log", "message": f"📍 Found {len(mapped_urls)} high-value pages to browse."}) + "\n"
                     else:
                         yield msg # Pass through logs
                 except:
                     pass
        
        search_queries = [
            f"{company_name} {address} {state} company profile",
            f"site:opencorporates.com {company_name} {state}",
            f"site:crunchbase.com {company_name}",
            f"site:linkedin.com/company {company_name}",
            f"{company_name} {state} reviews complaints BBB reddit",
            f"{company_name} {state} lawsuits legal issues",
            f"{company_name} {state} news scandal controversy",
        ]
        
        # Add targeted queries if official site found
        if official_site:
            from urllib.parse import urlparse
            domain = urlparse(official_site).netloc
            # Remove www.
            if domain.startswith("www."):
                domain = domain[4:]
                
            search_queries.extend([
                f"site:{domain} leadership team management",
                f"site:{domain} about us history",
                f"site:{domain} financial reports investor relations",
                f"site:{domain} legal terms privacy",
            ])
        
        search_results = []
        for query in search_queries:
            try:
                yield json.dumps({"type": "log", "message": f"🔎 Searching: {query}..."}) + "\n"
                results = self.search.results(query, 10)
                
                # Add snippets from all results
                search_results.extend([f"Snippet: {r.get('snippet', '')}" for r in results])
                
                # Deep Search: Fetch content from the top 5 results for each query
                if results:
                    # Take up to 5 results
                    top_urls = [r.get("link") for r in results[:5] if r.get("link")]
                    
                    # Add mapped URLs to the top of the list if this is the first query or relevant
                    if mapped_urls and query == search_queries[0]:
                        top_urls = mapped_urls + top_urls
                    
                    # Deduplicate
                    top_urls = list(dict.fromkeys(top_urls))
                    
                    for url in top_urls:
                        yield json.dumps({"type": "log", "message": f"🌐 Browsing: {url}..."}) + "\n"
                        content = await browse_url_content(url)
                        
                        # Simulate reading time (randomized 3-6 seconds)
                        read_time = random.uniform(3, 6)
                        yield json.dumps({"type": "log", "message": f"📖 Reading content from {url} ({read_time:.1f}s)..."}) + "\n"
                        await asyncio.sleep(read_time)
                        
                        if content:
                            search_results.append(f"--- Content from {url} ---\n{content}\n--- End Content ---")
                            
            except Exception as e:
                yield json.dumps({"type": "log", "message": f"⚠️ Search error: {e}"}) + "\n"

        context = "\n".join(search_results)
        
        # 2. Synthesize with Gemini
        yield json.dumps({"type": "log", "message": "🧠 Synthesizing comprehensive findings..."}) + "\n"
        prompt_template = """
        You are a Risk Assessment Expert. Your goal is to analyze the following search results for the company "{company_name}" located in "{state}" and generate a detailed risk assessment report.
        
        Context from web search:
        {context}
        
        Company Details:
        Name: {company_name}
        Address: {address}
        State: {state}
        Type: {company_type}
        
        Instructions:
        1. **Comprehensive Findings (Markdown)**: First, write a detailed, natural language summary of your findings. This should be like a research report or a Perplexity answer. Use markdown headers (##), bullet points, and bold text. Cover:
           - Company Background & Legitimacy
           - Key Risks Identified
           - Reputation & Reviews
           - Financial Health Indicators
           - Legal/Compliance Issues
           - Conclusion
        
        2. **Structured Data (JSON)**: After the findings, provide the structured JSON data for the dashboard.
        
        Separator:
        Use the string "---JSON_START---" to separate the text summary from the JSON object.
        
        Target JSON Structure (adhere strictly to this):
        {{
          "companyInfo": {{
            "companyName": "{company_name}",
            "fullAddress": "{address}",
            "state": "{state}",
            "businessSector": "Infer from context"
          }},
          "riskReport": {{
            "overallRiskScore": <int 1-10>,
            "executiveSummary": {{
              "overallRiskRating": "Low/Medium/High",
              "keyPositiveFactors": ["list of strings"],
              "keyNegativeFactors": ["list of strings"],
              "informationGaps": "string"
            }},
            "riskAssessmentMatrix": {{
              "financialRisk": "Low/Medium/High",
              "operationalRisk": "Low/Medium/High",
              "reputationalRisk": "Low/Medium/High",
              "legalRegulatoryRisk": "Low/Medium/High",
              "cybersecurityRisk": "Low/Medium/High",
              "sanctionsTradeRisk": "Low/Medium/High",
              "supplyChainRisk": "Low/Medium/High",
              "esgRisk": "Low/Medium/High",
              "intellectualPropertyRisk": "Low/Medium/High",
              "industryRegulatoryRisk": "Low/Medium/High"
            }},
            "corporateIdentityAndLegalStanding": {{
               "businessRegistration": {{ "status": "string", "summary": "string", "sourceURL": "string/null" }},
               "legalAndRegulatoryActions": {{ "summary": "string", "findings": [] }},
               "permitsAndLicenses": {{ "summary": "string", "sourceURL": "string/null" }}
            }},
            "financialViabilityAnalysis": {{
               "companyType": "Private/Public",
               "financialMetrics": {{ "summary": "string", "metrics": [] }},
               "signsOfDistress": {{ "summary": "string", "sourceURL": "string/null" }}
            }},
            "leadershipAndGovernance": {{
               "executiveTeam": [],
               "executiveTurnover": {{ "summary": "string", "sourceURL": "string/null" }},
               "corporateGovernanceStructure": {{ "summary": "string", "boardIndependence": "string", "governanceIssues": "string", "sourceURL": "string/null" }}
            }},
            "marketAndOperationalRisk": {{
               "competitiveLandscape": {{ "summary": "string", "marketPosition": "string", "industryTrend": "string", "sourceURL": "string/null" }},
               "customerSentiment": {{ "summary": "string", "churnRisk": "string", "sourceURL": "string/null" }},
               "customerConcentration": {{ "summary": "string", "concentrationRisk": "string", "majorCustomers": "string", "sourceURL": "string/null" }},
               "technologyDisruption": {{ "summary": "string", "disruptionRisk": "string", "emergingThreats": "string", "sourceURL": "string/null" }},
               "operationalIncidents": {{ "summary": "string", "incidents": [] }}
            }},
            "reputationalAnalysis": {{
               "mediaScan": {{ "summary": "string", "sentiment": "string", "sourceURL": "string/null" }},
               "customerReviewSynthesis": [],
               "socialResponsibilityControversies": {{ "summary": "string", "sourceURL": "string/null" }},
               "digitalFootprint": {{ "summary": "string", "sentiment": "string", "viralIssues": "string", "sourceURL": "string/null" }}
            }}
          }}
        }}
        """
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["company_name", "address", "state", "company_type", "context"]
        )
        
        formatted_prompt = prompt.format(
            company_name=company_name,
            address=address,
            state=state,
            company_type=company_type,
            context=context
        )
        
        response = await self.llm.ainvoke(formatted_prompt)
        response_text = response.content
        
        # Split findings and JSON
        parts = response_text.split("---JSON_START---")
        
        if len(parts) >= 1:
            findings = parts[0].strip()
            yield json.dumps({"type": "summary", "content": findings}) + "\n"
            
        if len(parts) >= 2:
            json_text = parts[1].replace("```json", "").replace("```", "").strip()
            try:
                data = json.loads(json_text)
                yield json.dumps({"type": "result", "data": data}) + "\n"
            except json.JSONDecodeError:
                yield json.dumps({"type": "error", "message": "Failed to parse JSON report"}) + "\n"
        else:
             # Fallback if separator missing, try to find JSON
             yield json.dumps({"type": "error", "message": "Could not separate findings from data"}) + "\n"
