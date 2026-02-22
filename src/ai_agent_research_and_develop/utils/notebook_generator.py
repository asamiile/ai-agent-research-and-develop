import json
from datetime import datetime
from typing import List, Dict, Any
import nbformat as nbf


def create_research_notebook(
    trends: List[Dict[str, Any]],
    pain_points: List[str],
    all_ideas: List[Dict[str, Any]],
    viable_ideas: List[Dict[str, Any]],
    filtered_ideas: List[Dict[str, Any]],
    business_models: List[Dict[str, Any]],
    output_path: str = "research_analysis.ipynb"
) -> str:
    """
    Create a Jupyter notebook with research analysis results
    
    Args:
        trends: List of extracted trends
        pain_points: List of identified pain points
        all_ideas: All generated ideas
        viable_ideas: Ideas passing filtering criteria
        filtered_ideas: Ideas that were filtered out
        business_models: Validated business models
        output_path: Output notebook path
    
    Returns:
        output_path: Path to created notebook
    """
    nb = nbf.v4.new_notebook()
    
    # Add title
    nb.cells.append(nbf.v4.new_markdown_cell("# AI-Driven R&D Research Analysis"))
    nb.cells.append(nbf.v4.new_markdown_cell(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"))
    
    # Section 1: Market Trends
    nb.cells.append(nbf.v4.new_markdown_cell("## 1. Market Trends Analysis"))
    nb.cells.append(nbf.v4.new_markdown_cell("### Top 5 Technology Trends"))
    
    trends_md = "| Rank | Trend | Urgency | Mentions | Source |\n"
    trends_md += "|------|-------|---------|----------|--------|\n"
    for trend in trends:
        trends_md += f"| {trend.get('rank', '')} | {trend.get('title', '')} | {trend.get('urgency_score', '')} | {trend.get('mentions', '')} | {trend.get('primary_source', '')} |\n"
    
    nb.cells.append(nbf.v4.new_markdown_cell(trends_md))
    
    # Pain points
    nb.cells.append(nbf.v4.new_markdown_cell("### Identified Pain Points"))
    pain_points_md = ""
    for i, pain_point in enumerate(pain_points, 1):
        pain_points_md += f"{i}. {pain_point}\n"
    nb.cells.append(nbf.v4.new_markdown_cell(pain_points_md))
    
    # Section 2: Business Ideas
    nb.cells.append(nbf.v4.new_markdown_cell("## 2. Generated Business Ideas"))
    nb.cells.append(nbf.v4.new_markdown_cell(f"**Total Ideas:** {len(all_ideas)} | **Viable:** {len(viable_ideas)} | **Filtered:** {len(filtered_ideas)}"))
    
    # All ideas table
    nb.cells.append(nbf.v4.new_markdown_cell("### All Ideas (Pre-Filtering)"))
    ideas_md = """| Title | Market | Feasibility | Market Need | Scalability | Competitive | Priority | Status |
|-------|--------|-------------|-------------|-------------|-------------|----------|--------|
"""
    for idea in all_ideas:
        status = "✓ Viable" if idea.get("priority_score", 0) >= 7.0 else "✗ Filtered"
        ideas_md += f"| {idea.get('title', '')} | {idea.get('target_market', '')} | {idea.get('feasibility', '')} | {idea.get('market_need', '')} | {idea.get('scalability', '')} | {idea.get('competitive_intensity', '')} | {idea.get('priority_score', '-')} | {status} |\n"
    
    nb.cells.append(nbf.v4.new_markdown_cell(ideas_md))
    
    # Filtered ideas explanation
    if filtered_ideas:
        nb.cells.append(nbf.v4.new_markdown_cell("### Filtering Results"))
        filtered_md = "The following ideas did not meet viability criteria:\n\n"
        for idea in filtered_ideas:
            filtered_md += f"- **{idea.get('title', 'Unknown')}**: {idea.get('rejection_reason', 'Low priority score')}\n"
        nb.cells.append(nbf.v4.new_markdown_cell(filtered_md))
    
    # Section 3: Viable Ideas Details
    nb.cells.append(nbf.v4.new_markdown_cell("## 3. Viable Business Opportunities"))
    nb.cells.append(nbf.v4.new_markdown_cell(f"**Count:** {len(viable_ideas)} ideas passed filtering criteria"))
    
    for i, idea in enumerate(viable_ideas, 1):
        nb.cells.append(nbf.v4.new_markdown_cell(f"### {i}. {idea.get('title', 'Untitled')}"))
        
        idea_details = f"""
**Description:** {idea.get('description', 'N/A')}

**Target Market:** {idea.get('target_market', 'N/A')}

**Metrics:**
- Feasibility: {idea.get('feasibility', '-')}/10
- Market Need: {idea.get('market_need', '-')}/10
- Scalability: {idea.get('scalability', '-')}/10
- Competitive Intensity: {idea.get('competitive_intensity', '-')}/10
- Network Effect: {idea.get('network_effect', '-')}/10
- **Priority Score: {idea.get('priority_score', '-')}/10**

**Timeline & Scale:**
- Time to MVP: {idea.get('time_to_mvp_months', '-')} months
- TAM: ¥{idea.get('tam_jpy', 0):,.0f}
"""
        nb.cells.append(nbf.v4.new_markdown_cell(idea_details))
    
    # Section 4: Business Models & Financial Analysis
    nb.cells.append(nbf.v4.new_markdown_cell("## 4. Financial Analysis & Business Models"))
    nb.cells.append(nbf.v4.new_markdown_cell(f"**Validated Models:** {len(business_models)}"))
    
    if business_models:
        # Financial summary table
        finance_md = """| Idea | Dev Cost | Annual Opex | Year1 Revenue | Year1 ARPU | Break-even | ROI |
|------|----------|-------------|---------------|-----------|------------|-----|
"""
        for model in business_models:
            dev_cost = f"¥{model.get('dev_cost_jpy', 0):,.0f}"
            opex = f"¥{model.get('annual_opex_jpy', 0):,.0f}"
            revenue = f"¥{model.get('year1_revenue_estimate_jpy', 0):,.0f}"
            arpu = f"¥{model.get('year1_arpu_jpy', 0):,.0f}"
            breakeven = f"{model.get('break_even_months', '-')} mo"
            roi = f"{model.get('roi_percent', '-')}%"
            
            finance_md += f"| {model.get('idea_title', '')} | {dev_cost} | {opex} | {revenue} | {arpu} | {breakeven} | {roi} |\n"
        
        nb.cells.append(nbf.v4.new_markdown_cell(finance_md))
    
    # Detailed financial analysis for each model
    for model in business_models:
        nb.cells.append(nbf.v4.new_markdown_cell(f"### {model.get('idea_title', 'Unknown')}"))
        
        model_details = f"""
**Financial Metrics:**
- Development Cost: ¥{model.get('dev_cost_jpy', 0):,.0f}
- Annual Operational Expenses: ¥{model.get('annual_opex_jpy', 0):,.0f}
- Year 1 Revenue Estimate: ¥{model.get('year1_revenue_estimate_jpy', 0):,.0f}
- Year 1 ARPU: ¥{model.get('year1_arpu_jpy', 0):,.0f}

**Key Metrics:**
- Break-even Timeline: {model.get('break_even_months', '-')} months
- Year 1 ROI: {model.get('roi_percent', '-')}%

**Validation Notes:**
{model.get('validation_notes', 'N/A')}
"""
        nb.cells.append(nbf.v4.new_markdown_cell(model_details))
    
    # Section 5: Summary & Recommendations
    nb.cells.append(nbf.v4.new_markdown_cell("## 5. Summary & Recommendations"))
    
    summary = f"""
### Analysis Summary
- **Total Trends Identified:** {len(trends)}
- **Pain Points Found:** {len(pain_points)}
- **Business Ideas Generated:** {len(all_ideas)}
- **Ideas Passing Viability Filter:** {len(viable_ideas)}
- **Business Models Validated:** {len(business_models)}

### Next Steps
1. **Research:** Validate assumptions with target users (5-10 interviews per idea)
2. **Prototyping:** Develop MVP for top 1-2 ideas
3. **Market Testing:** Launch beta with early adopters
4. **Iteration:** Collect feedback and refine business model

### Key Success Factors
- Fast MVP deployment (focus on core value)
- Quick user validation and feedback loops
- Flexible cost model (outsource non-core functions)
- Regular financial review and pivot triggers
"""
    nb.cells.append(nbf.v4.new_markdown_cell(summary))
    
    # Add editable notes cell
    nb.cells.append(nbf.v4.new_markdown_cell("## 6. Team Notes & Decisions"))
    nb.cells.append(nbf.v4.new_markdown_cell("""
### Decision Log
_Edit this section to track team decisions and rationale_

| Date | Decision | Rationale | Action Items |
|------|----------|-----------|--------------|
|      |          |           |              |

### Follow-up Actions
- [ ] Create detailed market research for top ideas
- [ ] Identify potential co-founders or team members
- [ ] Set up rapid prototyping process
- [ ] Define success metrics and KPIs
"""))
    
    # Save notebook
    with open(output_path, 'w') as f:
        nbf.write(nb, f)
    
    return output_path
