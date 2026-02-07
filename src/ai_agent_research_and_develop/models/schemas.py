from pydantic import BaseModel, Field
from typing import List, Optional


class Trend(BaseModel):
    """Technology trend extracted from data sources"""
    rank: int = Field(description="Rank from 1-5")
    title: str = Field(description="Trend title")
    mentions: int = Field(description="Number of mentions across sources")
    urgency_score: float = Field(description="Urgency score 1-10")
    description: str = Field(description="Brief description")
    primary_source: str = Field(description="Primary data source (HN/ProductHunt/GitHub)")


class Idea(BaseModel):
    """Business idea with evaluation metrics"""
    title: str = Field(description="Business idea title")
    description: str = Field(description="Brief description of the idea")
    target_market: str = Field(description="Target market/segment")
    feasibility: float = Field(ge=1, le=10, description="Feasibility score 1-10")
    market_need: float = Field(ge=1, le=10, description="Market need score 1-10")
    scalability: float = Field(ge=1, le=10, description="Scalability score 1-10")
    competitive_intensity: float = Field(ge=1, le=10, description="Competitive intensity 1-10 (lower better)")
    network_effect: float = Field(ge=1, le=10, description="Network effect potential 1-10")
    time_to_mvp_months: int = Field(ge=1, le=36, description="Months to MVP")
    tam_jpy: int = Field(description="Total Addressable Market in JPY")
    priority_score: float = Field(description="Calculated priority score 1-10")
    rejection_reason: Optional[str] = Field(default=None, description="Reason if filtered out")


class IdeaWithMetrics(BaseModel):
    """Idea with all calculated metrics for filtering"""
    idea: Idea
    priority_score: float = Field(description="Calculated from 4 components")
    is_viable: bool = Field(description="Passes all filtering criteria")
    filtering_notes: str = Field(description="Notes on filtering decision")


class BusinessModel(BaseModel):
    """Validated business model with cost analysis"""
    idea_title: str = Field(description="Original idea title")
    dev_cost_jpy: int = Field(description="Development cost in JPY")
    annual_opex_jpy: int = Field(description="Annual operational expenses in JPY")
    year1_revenue_estimate_jpy: int = Field(description="Conservative Year 1 revenue estimate")
    year1_arpu_jpy: int = Field(description="Year 1 ARPU in JPY")
    break_even_months: float = Field(description="Months to break even")
    roi_percent: float = Field(description="ROI percentage")
    validation_notes: str = Field(description="Validation and assumption notes")


class ResearchOutput(BaseModel):
    """Complete research output with all analysis"""
    trends: List[Trend] = Field(description="Top 5 trends extracted")
    pain_points: List[str] = Field(description="Top 3 pain points")
    ideas: List[Idea] = Field(description="Generated business ideas")
    viable_ideas: List[Idea] = Field(description="Ideas passing filtering criteria")
    business_models: List[BusinessModel] = Field(description="Validated business models")
