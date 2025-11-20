import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from models import FullAssessmentResponse, RiskReport, CompanyInfo

class RiskAssessmentAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        if not api_key or not cse_id:
            print("Warning: GOOGLE_API_KEY or GOOGLE_CSE_ID not found.")
        
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key, temperature=0.2)
        self.search = GoogleSearchAPIWrapper(google_api_key=api_key, google_cse_id=cse_id)

    async def run_assessment(self, company_name: str, address: str, state: str, company_type: str) -> dict:
        # 1. Gather Information
        print(f"Searching for {company_name}...")
        search_queries = [
            f"{company_name} {address} {state} company profile",
            f"{company_name} {state} reviews complaints BBB reddit",
            f"{company_name} {state} lawsuits legal issues",
            f"{company_name} {state} financial funding revenue",
            f"{company_name} {state} executive team leadership",
        ]
        
        search_results = []
        for query in search_queries:
            try:
                results = self.search.results(query, 3)
                search_results.extend([r.get("snippet", "") for r in results])
            except Exception as e:
                print(f"Search error for {query}: {e}")

        context = "\n".join(search_results)
        
        # 2. Synthesize with Gemini
        print("Synthesizing report...")
        prompt_template = """
        You are a Risk Assessment Expert. Your goal is to analyze the following search results for the company "{company_name}" located in "{state}" and generate a detailed risk assessment report in JSON format.
        
        Context from web search:
        {context}
        
        Company Details:
        Name: {company_name}
        Address: {address}
        State: {state}
        Type: {company_type}
        
        Instructions:
        - Analyze the search results to fill out the JSON structure below.
        - Be objective and factual.
        - If information is missing, state "Not available in public records" or similar, but try to infer reasonable conclusions if possible (e.g., low risk if no bad news found).
        - Calculate an overall risk score (1-10) based on the findings.
        - Return ONLY the JSON object. Do not include markdown formatting like ```json.
        
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
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response_text = await chain.arun(
            company_name=company_name,
            address=address,
            state=state,
            company_type=company_type,
            context=context
        )
        
        # Clean up response if it contains markdown
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError:
            print("Error decoding JSON from LLM response")
            print(response_text)
            return {"error": "Failed to generate report", "raw_response": response_text}

