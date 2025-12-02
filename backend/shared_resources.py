import asyncio

# Global event queue for real-time streaming (logs, screenshots, etc.)
# This allows deep-nested agents to push updates directly to the frontend stream
event_queue = asyncio.Queue()
