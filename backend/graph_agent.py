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
    
    async def fetch_url(url, agent_id):
        try:
            async with async_playwright() as p:
                # HEADLESS=FALSE allows the user to "literally see" the agent working
                browser = await p.chromium.launch(headless=False, slow_mo=100, args=["--disable-blink-features=AutomationControlled"]) 
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720},
                    device_scale_factor=1,
                )
                
                # STEALTH & VISUALS: Inject scripts
                await context.add_init_script("""
                    // 1. Stealth
                    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                    window.chrome = { runtime: {} };
                    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

                    // 2. Visual AI Cursor
                    window.installCursor = () => {
                        if (document.getElementById('ai-cursor')) return;
                        const cursor = document.createElement('div');
                        cursor.id = 'ai-cursor';
                        cursor.style.position = 'fixed';
                        cursor.style.width = '20px';
                        cursor.style.height = '20px';
                        cursor.style.borderRadius = '50%';
                        cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.7)';
                        cursor.style.border = '2px solid white';
                        cursor.style.boxShadow = '0 0 10px rgba(255, 0, 0, 0.5)';
                        cursor.style.zIndex = '999999';
                        cursor.style.pointerEvents = 'none';
                        cursor.style.transition = 'all 0.2s ease-out';
                        cursor.style.transform = 'translate(-50%, -50%)';
                        document.body.appendChild(cursor);
                    };

                    window.moveCursor = (x, y) => {
                        const cursor = document.getElementById('ai-cursor');
                        if (cursor) {
                            cursor.style.left = x + 'px';
                            cursor.style.top = y + 'px';
                        }
                    };
                """)
                
                page = await context.new_page()
                
                # Resource Blocking
                await page.route("**/*", lambda route: 
                    route.abort() if route.request.resource_type in ["image", "media", "font"] 
                    else route.continue_()
                )
                
                # Helper to stream frame
                async def stream_frame(status="Active"):
                    try:
                        screenshot = await page.screenshot(type="jpeg", quality=40)
                        b64 = base64.b64encode(screenshot).decode("utf-8")
                        await event_queue.put(json.dumps({
                            "type": "preview",
                            "agent_id": agent_id,
                            "url": url,
                            "status": status,
                            "image": f"data:image/jpeg;base64,{b64}"
                        }))
                    except: pass

                # Helper to move cursor visibly
                async def move_mouse_human(x, y):
                    try:
                        await page.evaluate(f"window.moveCursor({x}, {y})")
                        await page.mouse.move(x, y, steps=5)
                        await stream_frame("Moving")
                    except: pass

                try:
                    await event_queue.put(json.dumps({"type": "log", "message": f"🌐 {agent_id} connecting to: {url}"}))
                    
                    await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                    await page.evaluate("window.installCursor()")
                    
                    # Initial "Wake Up" Move
                    await move_mouse_human(random.randint(100, 500), random.randint(100, 500))
                    await page.wait_for_timeout(random.uniform(500, 1000))
                    
                    # --- Human Verification Logic ---
                    try:
                        turnstile = page.locator("iframe[src*='challenges.cloudflare.com']")
                        if await turnstile.count() > 0:
                            await event_queue.put(json.dumps({"type": "log", "message": f"🤖 {agent_id} detected Cloudflare..."}))
                            frame = turnstile.content_frame
                            if frame:
                                checkbox = frame.locator("input[type='checkbox']")
                                if await checkbox.count() > 0:
                                    box = await checkbox.bounding_box()
                                    if box:
                                        await move_mouse_human(box['x'] + 10, box['y'] + 10)
                                        await checkbox.click()
                                        await stream_frame("Verifying")
                                        await page.wait_for_timeout(3000)
                    except: pass
                    # --------------------------------

                    # --- Popup Killer ---
                    try:
                        close_selectors = [
                            "button[aria-label='Close']", ".close", "#close-button", 
                            "button:has-text('No thanks')", "button:has-text('Not now')",
                            "button:has-text('Accept all')", "button:has-text('Accept Cookies')",
                            "[aria-label='Close modal']", "button:has-text('Continue without logging in')"
                        ]
                        for selector in close_selectors:
                            if await page.locator(selector).count() > 0:
                                loc = page.locator(selector).first
                                box = await loc.bounding_box()
                                if box:
                                    await move_mouse_human(box['x'] + box['width']/2, box['y'] + box['height']/2)
                                    await loc.click(timeout=1000)
                                    await stream_frame("Closing Popup")
                                    await page.wait_for_timeout(500)
                    except: pass
                    # ---------------------

                    # --- Smooth Scrolling with Live Updates ---
                    scroll_height = await page.evaluate("document.body.scrollHeight")
                    viewport_height = await page.evaluate("window.innerHeight")
                    current_scroll = 0
                    
                    while current_scroll < scroll_height:
                        # Scroll
                        await page.evaluate(f"window.scrollTo(0, {current_scroll + viewport_height})")
                        current_scroll += viewport_height
                        
                        # Move mouse randomly while reading
                        await move_mouse_human(random.randint(100, 1000), random.randint(100, 600))
                        
                        # Stream update
                        await stream_frame("Reading")
                        
                        # Random pause
                        await page.wait_for_timeout(random.uniform(500, 1200))
                        
                        if current_scroll > viewport_height * 5: break
                    # -------------------------------------------------------

                    text = await page.evaluate("document.body.innerText")
                    clean_text = ' '.join(text.split())[:8000]
                    return f"Source: {url}\nContent: {clean_text}\n"
                finally:
                    await browser.close()
        except Exception as e:
            await event_queue.put(json.dumps({"type": "log", "message": f"❌ {agent_id} error: {str(e)[:50]}"}))
            return f"Source: {url}\nError: {e}\n"

    # Run in parallel with IDs
    tasks = []
    for i, url in enumerate(urls):
        tasks.append(fetch_url(url, f"Agent-{i+1}"))
    
    results = await asyncio.gather(*tasks)
    extracted_content.extend(results)
    
    logs.append(json.dumps({"type": "log", "message": "📂 Field Agents: Mission complete."}))
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
        "overallRiskScore": 0,  // MUST be an integer between 0 (Safe) and 10 (High Risk)
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
            
            # SAFETY: Clamp Risk Score to 0-10
            if "riskReport" in json_data and "overallRiskScore" in json_data["riskReport"]:
                score = json_data["riskReport"]["overallRiskScore"]
                if isinstance(score, (int, float)):
                    # If LLM gave 0-100, normalize it. If > 10, assume it's out of scale.
                    if score > 10:
                        score = round(score / 10) # Try to normalize 85 -> 8.5 -> 9
                    
                    # Hard clamp
                    score = max(0, min(10, int(score)))
                    json_data["riskReport"]["overallRiskScore"] = score
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
