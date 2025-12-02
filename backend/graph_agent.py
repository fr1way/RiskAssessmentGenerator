import os
import json
import asyncio
import random
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from playwright.async_api import async_playwright

# Define the state of our agent
class AgentState(TypedDict):
    company_name: str
    address: str
    state: str
    company_type: str
    
    # Data accumulation
    search_queries: List[str]
    raw_urls: List[str]
    filtered_urls: List[str]
    content: List[str]
    logs: List[str] # For streaming to frontend
    
    # Final Output
    summary: str
    report_data: dict

# --- Nodes ---

async def research_node(state: AgentState):
    """The Gatherer: Finds potential sources."""
    company = state["company_name"]
    location = state["state"]
    
    # Log
    logs = state.get("logs", [])
    logs.append(json.dumps({"type": "log", "message": f"🕵️‍♀️ Gatherer Agent: Scouting for {company} in {location}..."}))
    
    search = GoogleSearchAPIWrapper(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        google_cse_id=os.getenv("GOOGLE_CSE_ID")
    )
    
    # 1. Discovery Phase (Official Site)
    official_site = None
    try:
        results = search.results(f"{company} {location} official site", 3)
        for r in results:
            link = r.get("link", "")
            if "linkedin" not in link and "facebook" not in link:
                official_site = link
                logs.append(json.dumps({"type": "log", "message": f"🎯 Gatherer Agent: Found official site candidate: {official_site}"}))
                break
    except Exception as e:
        logs.append(json.dumps({"type": "log", "message": f"⚠️ Gatherer Agent: Discovery error: {e}"}))

    # 2. Broad Search
    ctype = state["company_type"]
    queries = [
        f"{company} {location} {ctype} company profile",
        f"{company} {location} {ctype} reviews complaints",
        f"{company} {location} {ctype} lawsuits legal",
        f"site:linkedin.com/company {company} {ctype}",
        f"site:opencorporates.com {company} {location}",
    ]
    
    if official_site:
        from urllib.parse import urlparse
        domain = urlparse(official_site).netloc.replace("www.", "")
        queries.extend([
            f"site:{domain} leadership team",
            f"site:{domain} about us",
            f"site:{domain} investor relations",
        ])

    raw_urls = []
    if official_site:
        raw_urls.append(official_site)

    for q in queries:
        try:
            results = search.results(q, 5)
            for r in results:
                link = r.get("link")
                if link:
                    raw_urls.append(link)
        except Exception:
            pass
            
    # Deduplicate
    raw_urls = list(set(raw_urls))
    logs.append(json.dumps({"type": "log", "message": f"📚 Gatherer Agent: Collected {len(raw_urls)} potential sources."}))
    
    return {"raw_urls": raw_urls, "logs": logs}

async def filter_node(state: AgentState):
    """The Filter: Grades relevance of URLs using LLM."""
    logs = []
    logs.append(json.dumps({"type": "log", "message": "🛡️ Filter Agent: Analyzing source relevance with LLM..."}))
    
    company = state["company_name"]
    location = state["state"]
    ctype = state["company_type"]
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0)
    
    # Batch process or process in parallel? For speed, let's do a single batch prompt if list is small, 
    # or parallel calls. Parallel calls are better for independent reasoning.
    
    async def grade_url(url):
        try:
            prompt = f"""
            You are a strict Relevance Filter.
            Target: "{company}" located in "{location}" doing business in "{ctype}".
            
            URL to Evaluate: {url}
            
            Is this URL likely to contain relevant information about THIS SPECIFIC company?
            - If it's a different company with the same name (e.g. manufacturing vs real estate), REJECT it.
            - If it's a general dictionary/social media home page, REJECT it.
            - If it's a specific profile, news article, or official site, ACCEPT it.
            
            Reply in this format: "YES | [Reasoning]" or "NO | [Reasoning]"
            """
            response = await llm.ainvoke(prompt)
            return url, response.content.strip()
        except:
            return url, "NO | Error"

    # Limit to checking top 15 raw urls to save time
    urls_to_check = state["raw_urls"][:15]
    
    # Run grading in parallel
    tasks = [grade_url(url) for url in urls_to_check]
    results = await asyncio.gather(*tasks)
    
    filtered_urls = []
    for url, result in results:
        if "|" in result:
            grade, reason = result.split("|", 1)
            grade = grade.strip().upper()
            reason = reason.strip()
        else:
            grade = result.strip().upper()
            reason = "No reason provided"
            
        if "YES" in grade:
            filtered_urls.append(url)
            logs.append(json.dumps({"type": "log", "message": f"✅ Filter: Approved {url} ({reason})"}))
        else:
            # logs.append(json.dumps({"type": "log", "message": f"🗑️ Filter: Rejected {url} ({reason})"}))
            pass
            
    # Fallback: If nothing passed, take top 3 raw urls to ensure we have something
    if not filtered_urls:
        logs.append(json.dumps({"type": "log", "message": "⚠️ Filter Agent: Strict filter rejected all. Using top raw results fallback."}))
        filtered_urls = state["raw_urls"][:3]
    
    # Limit to top 8 for browsing
    filtered_urls = filtered_urls[:8]
    
    logs.append(json.dumps({"type": "log", "message": f"✅ Filter Agent: Final selection: {len(filtered_urls)} sources."}))
    return {"filtered_urls": filtered_urls, "logs": logs}

from shared_resources import event_queue
import base64

async def browse_node(state: AgentState):
    """The Researchers: Parallel browsing."""
    logs = []
    urls = state["filtered_urls"]
    logs.append(json.dumps({"type": "log", "message": f"🕵️‍♂️ Field Agents: Dispatching {len(urls)} agents to browse sites..."}))
    
    extracted_content = []
    
    async def fetch_url(url):
        try:
            async with async_playwright() as p:
                # HEADLESS=FALSE allows the user to "literally see" the agent working
                browser = await p.chromium.launch(headless=False, slow_mo=1000, args=["--disable-blink-features=AutomationControlled"]) 
                
                # Randomize user agent slightly
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720},
                    device_scale_factor=1,
                )
                
                # STEALTH: Inject scripts to hide automation
                await context.add_init_script("""
                    // Remove webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // Override automation indicators
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // Fake plugin array
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // Pass languages check
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                """)
                
                page = await context.new_page()
                
                # Resource Blocking (Speed + Stealth: Mimic AdBlock)
                await page.route("**/*", lambda route: 
                    route.abort() if route.request.resource_type in ["image", "media", "font"] 
                    else route.continue_()
                )
                
                try:
                    await event_queue.put(json.dumps({
                        "type": "log", 
                        "message": f"🌐 Agent connecting to: {url}"
                    }))
                    
                    await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    
                    # Human-like random delay
                    await page.wait_for_timeout(random.uniform(1000, 2000)) 
                    
                    # Human-like Mouse Movement (Simulate "waking up")
                    await page.mouse.move(random.randint(100, 500), random.randint(100, 500), steps=10)
                    
                    # --- Human Verification Logic ---
                    try:
                        # Check for common "Verify you are human" checkboxes (Cloudflare, etc.)
                        # 1. Look for Cloudflare Turnstile
                        turnstile = page.locator("iframe[src*='challenges.cloudflare.com']")
                        if await turnstile.count() > 0:
                            await event_queue.put(json.dumps({"type": "log", "message": "🤖 Agent detected Cloudflare challenge. Attempting to verify..."}))
                            # Sometimes the checkbox is inside the iframe
                            frame = turnstile.content_frame
                            if frame:
                                checkbox = frame.locator("input[type='checkbox']")
                                if await checkbox.count() > 0:
                                    await checkbox.click()
                                    await page.wait_for_timeout(3000) # Wait for challenge to solve
                        
                        # 2. Generic "Verify" buttons
                        verify_btn = page.locator("button:has-text('Verify you are human'), button:has-text('I am human')")
                        if await verify_btn.count() > 0:
                            await event_queue.put(json.dumps({"type": "log", "message": "🤖 Agent clicking verification button..."}))
                            await verify_btn.first.click()
                            await page.wait_for_timeout(3000)
                            
                    except Exception as e:
                        # Don't fail the whole browse if verification logic fails
                        pass
                    # --------------------------------
                    
                    # --- Popup Killer & Cookie Consent ---
                    try:
                        # Common selectors for modals/overlays
                        close_selectors = [
                            "button[aria-label='Close']", 
                            ".close", 
                            "#close-button", 
                            "button:has-text('No thanks')", 
                            "button:has-text('Not now')",
                            "button:has-text('Accept all')", 
                            "button:has-text('Accept Cookies')",
                            "[aria-label='Close modal']",
                            # Reddit Specific
                            "button:has-text('Continue without logging in')",
                            "button:has-text('Not now')",
                            "shreddit-async-loader[bundlename='comment_body_header']", # Sometimes blocks content
                            "button._2Btn269-rG1-T1gU-e0-n", # Obfuscated reddit close button (example)
                            "div[role='dialog'] button[aria-label='Close']"
                        ]
                        for selector in close_selectors:
                            if await page.locator(selector).count() > 0:
                                # await event_queue.put(json.dumps({"type": "log", "message": "🧹 Agent clearing popup/overlay..."}))
                                try:
                                    await page.locator(selector).first.click(timeout=1000)
                                    await page.wait_for_timeout(500)
                                except:
                                    pass
                    except:
                        pass
                    # -------------------------------------

                    # Capture Screenshot for Live Preview (Clean of popups)
                    try:
                        screenshot_bytes = await page.screenshot(type="jpeg", quality=50)
                        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                        await event_queue.put(json.dumps({
                            "type": "preview",
                            "url": url,
                            "image": f"data:image/jpeg;base64,{screenshot_b64}"
                        }))
                    except:
                        pass

                    # --- Smooth Scrolling for Visibility & Lazy Loading ---
                    # await event_queue.put(json.dumps({"type": "log", "message": "📜 Agent reading (scrolling)..."}))
                    
                    # Get scroll height
                    scroll_height = await page.evaluate("document.body.scrollHeight")
                    viewport_height = await page.evaluate("window.innerHeight")
                    
                    # Scroll in chunks
                    current_scroll = 0
                    while current_scroll < scroll_height:
                        await page.evaluate(f"window.scrollTo(0, {current_scroll + viewport_height})")
                        
                        # Human-like reading pause (Randomized)
                        await page.wait_for_timeout(random.uniform(500, 1200)) 
                        
                        current_scroll += viewport_height
                        
                        # Break if taking too long (max 5 scrolls)
                        if current_scroll > viewport_height * 5:
                            break
                    
                    # Scroll back to top for a final screenshot or just take it where we are?
                    # Let's take it where we are or maybe the top is better for context. 
                    # Actually, let's take a screenshot of the *full page* if possible, or just the visible part.
                    # The previous screenshot was early. Let's take another one here if we want to show progress.
                    # For now, just the scrolling action is enough visual feedback.
                    # -------------------------------------------------------

                    text = await page.evaluate("document.body.innerText")
                    clean_text = ' '.join(text.split())[:8000] # Limit content size
                    return f"Source: {url}\nContent: {clean_text}\n"
                finally:
                    await browser.close()
        except Exception as e:
            await event_queue.put(json.dumps({
                "type": "log", 
                "message": f"❌ Error browsing {url}: {str(e)[:100]}"
            }))
            return f"Source: {url}\nError: {e}\n"

    # Run in parallel
    results = await asyncio.gather(*[fetch_url(url) for url in urls])
    extracted_content.extend(results)
    
    logs.append(json.dumps({"type": "log", "message": "📂 Field Agents: Mission complete. All data extracted."}))
    return {"content": extracted_content, "logs": logs}

async def synthesize_node(state: AgentState):
    """The Analyst: Compiles the report."""
    logs = []
    logs.append(json.dumps({"type": "log", "message": "🧠 Analyst Agent: Synthesizing final report..."}))
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0.2)
    
    # Token Safety: Truncate context if it's too large to prevent token explosion
    full_context = "\n\n".join(state["content"])
    if len(full_context) > 100000:
        logs.append(json.dumps({"type": "log", "message": "⚠️ Analyst Agent: Context too large, truncating to 100k chars..."}))
        context = full_context[:100000] + "\n...(truncated)..."
    else:
        context = full_context
    
    prompt = f"""
    You are a Risk Assessment Expert. Analyze the following gathered intelligence for "{state['company_name']}".
    
    Intelligence:
    {context}
    
    Instructions:
    1. **Comprehensive Findings (Markdown)**: Write a detailed research report. Use headers, bullets, and bold text.
    2. **Structured Data (JSON)**: Provide the JSON dashboard data.
    
    Separator: "---JSON_START---"
    
    Target JSON Structure:
    {{
      "companyInfo": {{
        "companyName": "string",
        "fullAddress": "string",
        "businessSector": "string",
        "state": "string"
      }},
      "riskReport": {{
        "overallRiskScore": 0,
        "executiveSummary": {{
          "overallRiskRating": "Low/Medium/High",
          "keyPositiveFactors": ["string"],
          "keyNegativeFactors": ["string"],
          "informationGaps": "string"
        }},
        "riskAssessmentMatrix": {{
          "marketRisk": "Low/Medium/High",
          "operationalRisk": "Low/Medium/High",
          "financialRisk": "Low/Medium/High",
          "complianceRisk": "Low/Medium/High",
          "reputationalRisk": "Low/Medium/High"
        }},
        "financialViabilityAnalysis": {{
          "companyType": "string",
          "financialMetrics": {{
            "summary": "string",
            "metrics": [{{ "metricName": "string", "value": "string", "period": "string" }}]
          }},
          "signsOfDistress": {{ "summary": "string" }}
        }},
        "leadershipAndGovernance": {{
          "executiveTeam": [{{ "name": "string", "title": "string", "backgroundSummary": "string" }}],
          "executiveTurnover": {{ "summary": "string" }},
          "corporateGovernanceStructure": {{ "summary": "string" }}
        }},
        "reputationalAnalysis": {{
          "mediaScan": {{ "summary": "string", "sentiment": "Positive/Neutral/Negative" }},
          "customerReviewSynthesis": [{{ "platform": "string", "overallRating": "string", "commonComplaints": ["string"] }}],
          "socialResponsibilityControversies": {{ "summary": "string" }},
          "digitalFootprint": {{ "summary": "string", "sentiment": "string", "viralIssues": "string" }}
        }},
        "corporateIdentityAndLegalStanding": {{
          "businessRegistration": {{ "status": "string", "summary": "string" }},
          "legalAndRegulatoryActions": {{ "summary": "string", "findings": [] }},
          "permitsAndLicenses": {{ "summary": "string" }}
        }}
      }}
    }}
    
    IMPORTANT: Ensure the JSON is valid and strictly follows the schema. Do not wrap the JSON in markdown code blocks within the JSON section.
    """
    
    response = await llm.ainvoke(prompt)
    text = response.content
    
    # Robust Parsing Logic
    import re
    
    summary = ""
    json_data = {}
    
    try:
        if "---JSON_START---" in text:
            parts = text.split("---JSON_START---")
            summary = parts[0].strip()
            json_part = parts[1].strip()
        else:
            # Fallback: Regex to find the last JSON object
            summary = text # Assume everything is summary if separator missing, then try to extract JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            json_part = json_match.group(0) if json_match else ""
            
        # Clean JSON part (remove markdown code blocks if present)
        json_part = json_part.replace("```json", "").replace("```", "").strip()
        
        if json_part:
            json_data = json.loads(json_part)
        else:
            logs.append(json.dumps({"type": "log", "message": "⚠️ Analyst Agent: No JSON found in response."}))
            
    except json.JSONDecodeError as e:
        logs.append(json.dumps({"type": "log", "message": f"⚠️ Analyst Agent: JSON parsing failed: {e}"}))
        # Log raw text for debugging (truncated)
        logs.append(json.dumps({"type": "log", "message": f"⚠️ Raw JSON text: {json_part[:100]}..."}))
    except Exception as e:
        logs.append(json.dumps({"type": "log", "message": f"⚠️ Analyst Agent: Extraction error: {e}"}))

    return {"summary": summary, "report_data": json_data, "logs": logs}

# --- Graph Construction ---

def create_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("gather", research_node)
    workflow.add_node("filter", filter_node)
    workflow.add_node("browse", browse_node)
    workflow.add_node("synthesize", synthesize_node)
    
    workflow.set_entry_point("gather")
    
    workflow.add_edge("gather", "filter")
    workflow.add_edge("filter", "browse")
    workflow.add_edge("browse", "synthesize")
    workflow.add_edge("synthesize", END)
    
    return workflow.compile()
