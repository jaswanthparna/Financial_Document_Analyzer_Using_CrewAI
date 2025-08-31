from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class AnalysisRequest(BaseModel):
    query: str
    filename: str

class FinancialMetrics(BaseModel):
    revenue: Optional[float] = Field(None, description="Total revenue in millions")
    net_income: Optional[float] = Field(None, description="Net income in millions")
    total_assets: Optional[float] = Field(None, description="Total assets in millions")
    operating_cash_flow: Optional[float] = Field(None, description="Operating cash flow in millions")
    profit_margin: Optional[float] = Field(None, description="Profit margin percentage")
    debt_to_equity: Optional[float] = Field(None, description="Debt to equity ratio")
    eps: Optional[float] = Field(None, description="Earnings per share")

class InvestmentRecommendation(BaseModel):
    action: str = Field(..., description="Investment action: buy, sell, hold")
    asset: str = Field(..., description="Specific asset or investment vehicle")
    rationale: str = Field(..., description="Detailed reasoning for the recommendation")
    risk_level: str = Field(..., description="Risk level: Low, Medium, High")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")

class RiskAssessment(BaseModel):
    category: str = Field(..., description="Risk category")
    level: str = Field(..., description="Risk level: Low, Medium, High")
    description: str = Field(..., description="Detailed risk description")
    mitigation: str = Field(..., description="Risk mitigation strategy")

class AnalysisOutput(BaseModel):
    financial_metrics: FinancialMetrics
    investment_recommendations: List[InvestmentRecommendation]
    risk_assessments: List[RiskAssessment]
    summary: str
    market_insights: List[str]
    company_name: str