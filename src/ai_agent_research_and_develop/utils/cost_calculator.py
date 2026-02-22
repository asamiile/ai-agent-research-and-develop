import math


class RaspberryPiOptimizedCostCalculator:
    """
    Cost calculation with assumptions optimized for small teams and Raspberry Pi deployment
    """
    
    # Default assumptions
    DEV_HOURS_PER_MVP = 120  # 120 hours for MVP
    DEV_HOURLY_RATE_JPY = 5000  # ¥5000/hour (conservative freelancer rate)
    
    # Annual operational costs
    BASE_ANNUAL_OPEX_JPY = 120000  # ¥120k base (infrastructure, tools)
    
    # Revenue assumptions (conservative)
    MONTH_1_USERS = 10  # First month users
    MONTHLY_USER_GROWTH_RATE = 1.15  # 15% MoM growth
    BASE_ARPU_JPY = 1000  # ¥1000 ARPU
    
    @classmethod
    def estimate_dev_cost(cls, time_to_mvp_months: int) -> int:
        """
        Estimate development cost based on time to MVP
        
        Assumes: time_to_mvp_months * 30 days * 8 hours/day / 20 working days
        """
        # More efficient for longer MVP timelines (parallel work in teams)
        efficiency_factor = 1.0 - (min(time_to_mvp_months, 12) * 0.02)  # up to 24% efficiency gain
        hours_needed = (cls.DEV_HOURS_PER_MVP / (time_to_mvp_months / 3)) * time_to_mvp_months
        hours_needed = hours_needed * efficiency_factor
        
        return int(hours_needed * cls.DEV_HOURLY_RATE_JPY)
    
    @classmethod
    def estimate_year1_revenue(
        cls,
        tam_jpy: int,
        market_need_score: float,
        scalability_score: float,
        competitive_intensity_score: float,
        arpu_jpy: int = None
    ) -> int:
        """
        Conservative Year 1 revenue estimate
        
        Accounts for market size, demand, market share, and competitive environment
        """
        if arpu_jpy is None:
            arpu_jpy = cls.BASE_ARPU_JPY
        
        # Market penetration potential (TAM * market score factor)
        market_factor = (market_need_score / 10) * (scalability_score / 10)
        
        # Competitive environment adjustment
        competitive_factor = (10 - competitive_intensity_score) / 10
        
        # Conservative market share in Year 1 (0.1% - 2%)
        market_share = market_factor * competitive_factor * 0.01
        
        # Conservative user acquisition in Year 1
        year1_users = int((tam_jpy / arpu_jpy) * market_share)
        year1_users = max(year1_users, 10)  # At least 10 users
        
        # Average revenue (ramp up from 0)
        avg_users = year1_users / 2  # Linear ramp
        year1_revenue = int(avg_users * arpu_jpy * 12)
        
        return year1_revenue
    
    @classmethod
    def calculate_break_even_months(
        cls,
        dev_cost_jpy: int,
        annual_opex_jpy: int,
        year1_revenue_jpy: int
    ) -> float:
        """
        Calculate months to break even
        
        Assumes: monthly revenue = year1_revenue / 12, then linear growth
        """
        if year1_revenue_jpy <= 0:
            return 999  # Never breaks even
        
        monthly_revenue = year1_revenue_jpy / 12
        
        if monthly_revenue <= 0:
            return 999
        
        monthly_opex = annual_opex_jpy / 12
        monthly_net = monthly_revenue - monthly_opex
        
        if monthly_net <= 0:
            # Loses money monthly - may not be viable
            return 999
        
        # Break even = dev_cost / monthly_net_profit
        months = dev_cost_jpy / monthly_net
        
        return round(months, 1)
    
    @classmethod
    def calculate_roi(
        cls,
        dev_cost_jpy: int,
        annual_opex_jpy: int,
        year1_revenue_jpy: int
    ) -> float:
        """
        Calculate Year 1 ROI percentage
        
        ROI = (Revenue - Dev Cost - Opex) / (Dev Cost + Opex) * 100
        """
        total_cost = dev_cost_jpy + annual_opex_jpy
        
        if total_cost <= 0:
            return 0
        
        net_profit = year1_revenue_jpy - total_cost
        roi = (net_profit / total_cost) * 100
        
        return round(roi, 1)


def calculate_business_metrics(
    idea_title: str,
    tam_jpy: int,
    market_need: float,
    scalability: float,
    competitive_intensity: float,
    time_to_mvp_months: int,
    arpu_jpy: int = None
) -> dict:
    """
    Calculate all business metrics for an idea
    
    Returns dict with all cost, revenue, and ROI metrics
    """
    calc = RaspberryPiOptimizedCostCalculator
    
    dev_cost = calc.estimate_dev_cost(time_to_mvp_months)
    annual_opex = calc.BASE_ANNUAL_OPEX_JPY
    year1_revenue = calc.estimate_year1_revenue(
        tam_jpy,
        market_need,
        scalability,
        competitive_intensity,
        arpu_jpy
    )
    
    return {
        "idea_title": idea_title,
        "dev_cost_jpy": dev_cost,
        "annual_opex_jpy": annual_opex,
        "year1_revenue_estimate_jpy": year1_revenue,
        "year1_arpu_jpy": arpu_jpy or calc.BASE_ARPU_JPY,
        "break_even_months": calc.calculate_break_even_months(dev_cost, annual_opex, year1_revenue),
        "roi_percent": calc.calculate_roi(dev_cost, annual_opex, year1_revenue),
    }
