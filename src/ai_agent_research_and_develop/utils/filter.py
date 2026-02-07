from typing import List, Tuple
from ..models import Idea


class FilteringConfig:
    """Filtering thresholds and criteria"""
    PRIORITY_MIN = 7.0
    FEASIBILITY_MIN = 5
    MARKET_NEED_MIN = 7
    COMPETITIVE_INTENSITY_MAX = 8


def calculate_priority_score(idea: Idea) -> float:
    """
    Calculate composite priority score (1-10) from 4 components
    
    Components:
    - Feasibility (1-10) → weight 0.25
    - Market Need (1-10) → weight 0.35
    - Scalability (1-10) → weight 0.25
    - Inverse Competitive Intensity (10 - score) → weight 0.15
    
    Priority = (F * 0.25 + MN * 0.35 + S * 0.25 + (10-CI) * 0.15)
    """
    score = (
        idea.feasibility * 0.25 +
        idea.market_need * 0.35 +
        idea.scalability * 0.25 +
        (10 - idea.competitive_intensity) * 0.15
    )
    return min(10.0, max(1.0, score))


def is_viable_idea(idea: Idea) -> Tuple[bool, str]:
    """
    Check if idea meets minimum viability criteria
    
    Returns: (is_viable, reason_if_not_viable)
    """
    reason = ""
    
    if idea.priority_score < FilteringConfig.PRIORITY_MIN:
        reason = f"Priority score {idea.priority_score:.1f} < {FilteringConfig.PRIORITY_MIN}"
        return False, reason
    
    if idea.feasibility < FilteringConfig.FEASIBILITY_MIN:
        reason = f"Feasibility {idea.feasibility:.1f} < {FilteringConfig.FEASIBILITY_MIN}"
        return False, reason
    
    if idea.market_need < FilteringConfig.MARKET_NEED_MIN:
        reason = f"Market need {idea.market_need:.1f} < {FilteringConfig.MARKET_NEED_MIN}"
        return False, reason
    
    if idea.competitive_intensity > FilteringConfig.COMPETITIVE_INTENSITY_MAX:
        reason = f"Competitive intensity {idea.competitive_intensity:.1f} > {FilteringConfig.COMPETITIVE_INTENSITY_MAX}"
        return False, reason
    
    return True, ""


def filter_ideas(ideas: List[Idea]) -> Tuple[List[Idea], List[Idea]]:
    """
    Filter ideas into viable and non-viable lists
    
    Returns: (viable_ideas, filtered_out_ideas)
    """
    viable = []
    filtered_out = []
    
    for idea in ideas:
        # Recalculate priority score if not already done
        if idea.priority_score == 0:
            idea.priority_score = calculate_priority_score(idea)
        
        is_viable, reason = is_viable_idea(idea)
        if is_viable:
            viable.append(idea)
        else:
            idea.rejection_reason = reason
            filtered_out.append(idea)
    
    return viable, filtered_out
