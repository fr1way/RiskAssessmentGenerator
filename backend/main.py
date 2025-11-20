from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

class AssessmentRequest(BaseModel):
    companyName: str
    companyAddress: str
    state: str
    companyType: str = "other"

from agent import RiskAssessmentAgent

agent = RiskAssessmentAgent()

@app.get("/")
def read_root():
    return {"message": "Risk Assessment API is running"}

@app.post("/api/assess")
async def assess_company(request: AssessmentRequest):
    result = await agent.run_assessment(
        company_name=request.companyName,
        address=request.companyAddress,
        state=request.state,
        company_type=request.companyType
    )
    return result
