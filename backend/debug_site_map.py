import asyncio
import requests
from playwright.async_api import async_playwright

async def debug_crawl(url):
    print(f"Checking connectivity for {url}...")
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        print(f"Requests Status: {response.status_code}")
    except Exception as e:
        print(f"Requests Error: {e}")
        # Try www
        if "www." not in url:
            alt_url = url.replace("://", "://www.")
            print(f"Trying {alt_url}...")
            try:
                response = requests.get(alt_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                print(f"Requests Status (www): {response.status_code}")
                if response.status_code == 200:
                    url = alt_url
            except Exception as e2:
                print(f"Requests Error (www): {e2}")

    print(f"Crawling {url} with Playwright...")
    high_value_keywords = ["about", "team", "leadership", "investor", "financial", "legal", "contact", "careers", "board", "governance"]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            
            title = await page.title()
            print(f"Page title: {title}")
            
            # Extract links
            links = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a')).map(a => ({
                        href: a.href,
                        text: a.innerText.toLowerCase()
                    }));
                }
            """)
            
            print(f"Found {len(links)} total links.")
            
            found_urls = set()
            for link in links:
                href = link['href']
                text = link['text']
                
                # Basic validation
                if not href or href.startswith("javascript") or href.startswith("mailto"):
                    continue

                if any(kw in href.lower() or kw in text for kw in high_value_keywords):
                    print(f"  MATCH: '{text}' -> {href}")
                    # Check if it's the same domain or relative
                    if url in href or href.startswith("/") or "balanced-trust.co" in href: 
                         found_urls.add(href)
            
            print(f"Identified {len(found_urls)} high-value URLs: {found_urls}")
            
            # Try to extract content from one
            if found_urls:
                target = list(found_urls)[0]
                print(f"\nBrowsing target: {target}...")
                await page.goto(target, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                content = await page.evaluate("document.body.innerText")
                print(f"Content length: {len(content)}")
                print(f"Preview: {content[:500]}")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_crawl("https://balanced-trust.co"))
