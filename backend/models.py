from pydantic import BaseModel
from typing import List, Optional

class CompanyInfo(BaseModel):
    companyName: str
    fullAddress: str
    state: str
    businessSector: str

class ExecutiveSummary(BaseModel):
    overallRiskRating: str
    keyPositiveFactors: List[str]
    keyNegativeFactors: List[str]
    informationGaps: str

class RiskAssessmentMatrix(BaseModel):
    financialRisk: str
    operationalRisk: str
    reputationalRisk: str
    legalRegulatoryRisk: str
    cybersecurityRisk: str
    sanctionsTradeRisk: str
    supplyChainRisk: str
    esgRisk: str
    intellectualPropertyRisk: str
    industryRegulatoryRisk: str

class BusinessRegistration(BaseModel):
    status: str
    summary: str
    sourceURL: Optional[str]

class LegalFinding(BaseModel):
    type: str
    description: str
    date: str
    status: str
    sourceURL: Optional[str]

class LegalAndRegulatoryActions(BaseModel):
    summary: str
    findings: List[LegalFinding]

class PermitsAndLicenses(BaseModel):
    summary: str
    sourceURL: Optional[str]

class CorporateIdentityAndLegalStanding(BaseModel):
    businessRegistration: BusinessRegistration
    legalAndRegulatoryActions: LegalAndRegulatoryActions
    permitsAndLicenses: PermitsAndLicenses

class FinancialMetric(BaseModel):
    metricName: str
    value: str
    period: str
    sourceURL: Optional[str]

class FinancialMetrics(BaseModel):
    summary: str
    metrics: List[FinancialMetric]

class SignsOfDistress(BaseModel):
    summary: str
    sourceURL: Optional[str]

class FinancialViabilityAnalysis(BaseModel):
    companyType: str
    financialMetrics: FinancialMetrics
    signsOfDistress: SignsOfDistress

class Executive(BaseModel):
    name: str
    title: str
    backgroundSummary: str
    negativeNews: Optional[dict]

class ExecutiveTurnover(BaseModel):
    summary: str
    sourceURL: Optional[str]

class CorporateGovernanceStructure(BaseModel):
    summary: str
    boardIndependence: str
    governanceIssues: str
    sourceURL: Optional[str]

class LeadershipAndGovernance(BaseModel):
    executiveTeam: List[Executive]
    executiveTurnover: ExecutiveTurnover
    corporateGovernanceStructure: CorporateGovernanceStructure

class MarketAndOperationalRisk(BaseModel):
    competitiveLandscape: dict
    customerSentiment: dict
    customerConcentration: dict
    technologyDisruption: dict
    operationalIncidents: dict

class ReputationalAnalysis(BaseModel):
    mediaScan: dict
    customerReviewSynthesis: List[dict]
    socialResponsibilityControversies: dict
    digitalFootprint: dict

class RiskReport(BaseModel):
    overallRiskScore: int
    executiveSummary: ExecutiveSummary
    riskAssessmentMatrix: RiskAssessmentMatrix
    corporateIdentityAndLegalStanding: CorporateIdentityAndLegalStanding
    financialViabilityAnalysis: FinancialViabilityAnalysis
    leadershipAndGovernance: LeadershipAndGovernance
    marketAndOperationalRisk: MarketAndOperationalRisk
    reputationalAnalysis: ReputationalAnalysis
    # Add other sections as needed (Bill of Lading, Cybersecurity, etc.)

class FullAssessmentResponse(BaseModel):
    companyInfo: CompanyInfo
    riskReport: RiskReport
