import sys
import os
import asyncio
import uvicorn

# Add parent directory to sys.path to allow 'backend' imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # CRITICAL: Enforce ProactorEventLoop on Windows for Playwright support
    # This must be done BEFORE any asyncio loop is created
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    print("Starting Risk Assessment Backend with ProactorEventLoop...")
    
    # Run Uvicorn without reload to ensure the Event Loop Policy is preserved
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
