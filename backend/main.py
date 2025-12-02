from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import sys
import asyncio

# Enforce ProactorEventLoop on Windows for Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

print(f"DEBUG: Current Event Loop Policy: {asyncio.get_event_loop_policy()}")

load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class AssessmentRequest(BaseModel):
    companyName: str
    companyAddress: str
    state: str
    companyType: str = "other"

from graph_agent import create_graph

graph = create_graph()

@app.get("/")
def read_root():
    return {"message": "Risk Assessment API is running"}

from fastapi.responses import StreamingResponse

@app.post("/api/assess")
@app.post("/api/assess")
async def assess_company(request: AssessmentRequest):
    async def stream_graph():
        inputs = {
            "company_name": request.companyName,
            "address": request.companyAddress,
            "state": request.state,
            "company_type": request.companyType,
            "logs": []
        }
        
        try:
            async for output in graph.astream(inputs):
                for node_name, node_output in output.items():
                    # Stream logs
                    if "logs" in node_output:
                        for log in node_output["logs"]:
                            # Avoid re-sending old logs if they are accumulated (my nodes return new logs mostly, but let's be safe)
                            # Actually my nodes return a list of logs. In 'research_node' I append to state['logs'].
                            # But the output of the node function is what is yielded here.
                            # In research_node I return {"logs": logs}. 'logs' there is the FULL list.
                            # Ah, that's a problem. I should only return the NEW logs in the node output if I want to stream them efficiently.
                            # Or I can just handle it here.
                            # Let's assume for now I'll just yield the last one or all of them? 
                            # If I yield all, the frontend will duplicate.
                            # I should fix graph_agent.py to only return NEW logs in the output, while updating the state with ALL logs.
                            # But wait, langgraph state updates merge.
                            # If I return {"logs": [...]}, it overwrites or appends depending on reducer.
                            # I used TypedDict, so it overwrites.
                            # So state["logs"] will be whatever the last node returned.
                            # This means I need to be careful.
                            # Let's just yield the logs that are in the output.
                            # But if research_node returns ALL logs, I will yield ALL logs.
                            pass
                            
                    # For now, let's assume the nodes return what they want to be in the state.
                    # I will modify this logic to just yield the message directly if I can.
                    # Actually, let's look at my graph_agent.py again.
                    # research_node: logs.append(...); return {"logs": logs} -> returns ALL logs.
                    # This is bad for streaming.
                    # I should fix graph_agent.py first?
                    # Or I can just filter here.
                    # But filtering here is hard without keeping state.
                    
                    # Let's just yield the messages.
                    # Actually, let's fix graph_agent.py to return "new_logs" key?
                    # No, let's just use the fact that I can see the output.
                    # If I change graph_agent to only return the NEW logs in a separate key, say "stream_logs", that would be better.
                    # But I can't easily change the state definition now without re-writing it.
                    
                    # Alternative: In main.py, keep track of sent logs.
                    pass

            # Re-reading graph_agent.py:
            # logs = state.get("logs", [])
            # logs.append(...)
            # return {..., "logs": logs}
            # So yes, it returns the full list.
            
            # I will implement a local `sent_logs` set/count in `stream_graph` to dedup.
            
        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"

    # Let's write the actual generator
    async def event_generator():
        from shared_resources import event_queue
        
        inputs = {
            "company_name": request.companyName,
            "address": request.companyAddress,
            "state": request.state,
            "company_type": request.companyType,
            "logs": [],
            "search_queries": [],
            "raw_urls": [],
            "filtered_urls": [],
            "content": []
        }
        
        # Start graph execution in background
        async def run_graph():
            try:
                async for output in graph.astream(inputs):
                    # We can still push major state updates to the queue if needed, 
                    # or just let the queue handle the granular stuff and use this for final result.
                    # For simplicity, let's push everything to the queue from here too.
                    
                    for node_name, node_output in output.items():
                        if "logs" in node_output:
                            # We might get duplicate logs here if we aren't careful, 
                            # but let's assume the queue is the primary source for "live" logs now.
                            # Actually, let's NOT push logs from here if we are pushing them from the nodes.
                            # But research_node pushes to logs list, it doesn't push to queue yet (I only updated browse_node).
                            # So we still need to yield logs from here for other nodes.
                            
                            # To avoid complexity, let's just yield everything from here to the queue as well.
                            for log_str in node_output["logs"]:
                                await event_queue.put(log_str)
                        
                        if node_name == "synthesize":
                            if "summary" in node_output:
                                await event_queue.put(json.dumps({"type": "summary", "content": node_output["summary"]}))
                            if "report_data" in node_output:
                                await event_queue.put(json.dumps({"type": "result", "data": node_output["report_data"]}))
                                
            except Exception as e:
                await event_queue.put(json.dumps({"type": "error", "message": str(e)}))
            finally:
                # Signal end of stream
                await event_queue.put(None)

        # Start the graph task
        asyncio.create_task(run_graph())
        
        # Consume the queue
        sent_logs = set()
        
        while True:
            event = await event_queue.get()
            if event is None:
                break
            
            # Dedup logs
            if event not in sent_logs:
                yield f"data: {event}\n\n"
                # Only track logs for dedup, not images (images are large)
                if "type" in event and "log" in event: 
                    sent_logs.add(event)
            
            event_queue.task_done()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
