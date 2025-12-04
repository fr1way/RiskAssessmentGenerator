import json
import asyncio
import base64
from langchain_core.tools import tool
from playwright.async_api import Page

class BrowserActions:
    def __init__(self, page: Page, event_queue: asyncio.Queue, agent_id: str):
        self.page = page
        self.event_queue = event_queue
        self.agent_id = agent_id

    async def stream_frame(self, status: str):
        """Helper to stream a frame to the frontend."""
        try:
            if not self.page.is_closed():
                screenshot = await self.page.screenshot(type="jpeg", quality=40)
                b64 = base64.b64encode(screenshot).decode("utf-8")
                await self.event_queue.put(json.dumps({
                    "type": "preview",
                    "agent_id": self.agent_id,
                    "url": self.page.url,
                    "status": status,
                    "image": f"data:image/jpeg;base64,{b64}"
                }))
        except Exception:
            pass

    async def log(self, message: str):
        await self.event_queue.put(json.dumps({"type": "log", "message": f"🤖 {self.agent_id}: {message}"}))

    async def move_mouse_human(self, x, y):
        """Moves the mouse naturally."""
        try:
            await self.page.evaluate(f"window.moveCursor({x}, {y})")
            await self.page.mouse.move(x, y, steps=10)
            await self.stream_frame("Moving")
        except: pass

    # --- TOOLS ---

    async def read_page(self) -> str:
        """Reads the visible text content of the current page."""
        await self.log("Reading page content...")
        await self.stream_frame("Reading")
        try:
            text = await self.page.evaluate("document.body.innerText")
            clean_text = ' '.join(text.split())[:5000] # Limit to 5k chars
            return clean_text
        except Exception as e:
            return f"Error reading page: {e}"

    async def scroll_down(self) -> str:
        """Scrolls down the page to reveal more content."""
        await self.log("Scrolling down...")
        try:
            await self.page.evaluate("window.scrollBy(0, window.innerHeight)")
            await asyncio.sleep(1) # Wait for load
            await self.stream_frame("Scrolled")
            return "Scrolled down successfully."
        except Exception as e:
            return f"Error scrolling: {e}"

    async def click_element(self, selector: str) -> str:
        """Clicks on an element matching the CSS selector."""
        await self.log(f"Clicking element: {selector}")
        try:
            loc = self.page.locator(selector).first
            if await loc.count() > 0 and await loc.is_visible():
                box = await loc.bounding_box()
                if box:
                    await self.move_mouse_human(box['x'] + box['width']/2, box['y'] + box['height']/2)
                    await loc.click()
                    await asyncio.sleep(2) # Wait for navigation/action
                    await self.stream_frame("Clicked")
                    return f"Successfully clicked {selector}."
            return f"Element {selector} not found or not visible."
        except Exception as e:
            return f"Error clicking {selector}: {e}"

    async def close_popup(self) -> str:
        """Attempts to close any visible modal or popup."""
        await self.log("Checking for popups...")
        close_selectors = [
            "button[aria-label='Close']", ".close", "#close-button", 
            "button:has-text('No thanks')", "button:has-text('Not now')",
            "button:has-text('Accept all')", "button:has-text('Accept Cookies')",
            "[aria-label='Close modal']", "button:has-text('Continue without logging in')",
            "button:has-text('Maybe later')", "button:has-text('Continue as guest')",
            "svg[data-icon='times']", ".modal-close", "div[role='button']:has-text('Close')",
            "button:has-text('Stay signed out')",
            "button[aria-label='Dismiss']", ".modal__dismiss", "li-icon[type='cancel-icon']",
            "button.artdeco-modal__dismiss", "[data-test-modal-close-btn]",
            "button[data-control-name='overlay.close_overlay_btn']"
        ]
        
        closed_count = 0
        try:
            # 1. Iterate through ALL selectors and click ALL visible ones
            for selector in close_selectors:
                locators = self.page.locator(selector)
                count = await locators.count()
                for i in range(count):
                    loc = locators.nth(i)
                    if await loc.is_visible():
                        await self.log(f"Found popup: {selector}")
                        try:
                            box = await loc.bounding_box()
                            if box:
                                await self.move_mouse_human(box['x'] + box['width']/2, box['y'] + box['height']/2)
                                await loc.click(timeout=1000)
                                await asyncio.sleep(0.5)
                                closed_count += 1
                        except: pass
            
            # 2. If we closed something, wait a bit and stream update
            if closed_count > 0:
                await asyncio.sleep(1)
                await self.stream_frame("Popups Closed")
                return f"Closed {closed_count} popup(s)."
            
            return "No popups found."
        except Exception as e:
            return f"Error closing popup: {e}"

    async def get_links(self, category: str) -> str:
        """
        Finds links matching a category (e.g., 'about', 'team', 'contact').
        Returns a list of URLs.
        """
        await self.log(f"Looking for {category} links...")
        try:
            links = await self.page.evaluate(f"""
                (category) => {{
                    const anchors = Array.from(document.querySelectorAll('a'));
                    const keywords = [category.toLowerCase()];
                    return anchors
                        .filter(a => keywords.some(k => a.innerText.toLowerCase().includes(k)) || keywords.some(k => a.href.toLowerCase().includes(k)))
                        .map(a => a.href)
                        .filter(href => href.startsWith('http'))
                        .slice(0, 5);
                }}
            """, category)
            return f"Found links: {', '.join(links)}" if links else "No links found."
        except Exception as e:
            return f"Error finding links: {e}"
