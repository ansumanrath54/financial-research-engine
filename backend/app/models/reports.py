from typing import List, Literal
from pydantic import BaseModel, Field

class FinancialMetricRow(BaseModel):
    metric: str = Field(description="Financial metric name")
    ticker_a_value: str = Field(description="Reported value for Ticker A")
    ticker_b_value: str = Field(description="Reported value for Ticker B")
    delta_commentary: str = Field(description="Analytical insight or spread commentary")

class SECRiskFactor(BaseModel):
    ticker: str = Field(description="Associated stock ticker")
    risk_title: str = Field(description="Filing risk factor title")
    summary: str = Field(description="Summary of operational headwind")
    citation: str = Field(description="Exact filing citation anchor")

class ResearchReport(BaseModel):
    tickers: List[str] = Field(min_length=1, max_length=5)
    executive_summary: str = Field(description="Comparative executive summary")
    metrics_table: List[FinancialMetricRow] = Field(default_factory=list)
    risk_factors: List[SECRiskFactor] = Field(default_factory=list)
    validation_status: Literal["VERIFIED", "FLAGGED"] = "VERIFIED"