import sys
import warnings
import json
import re
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple

from ai_agent_research_and_develop.crew import AiAgentResearchAndDevelop
from ai_agent_research_and_develop.tools import fetch_all_trends
from ai_agent_research_and_develop.models import Idea, BusinessModel
from ai_agent_research_and_develop.utils import (
    filter_ideas,
    calculate_business_metrics,
    create_research_notebook,
)

# Suppress warnings and verbose logging
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Suppress LiteLLM logging noise
logging.getLogger("litellm").setLevel(logging.CRITICAL)
logging.getLogger("litellm.proxy").setLevel(logging.CRITICAL)
logging.getLogger("litellm.utils").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract JSON from text, handling markdown code blocks and other formats
    """
    if not text:
        return {}
    
    # Try to parse as JSON directly
    try:
        return json.loads(text)
    except:
        pass
    
    # Try to extract JSON from markdown code block
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_match:
        json_str = json_match.group(1).strip()
        try:
            return json.loads(json_str)
        except:
            pass
    
    # Try to find JSON object pattern
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except:
            pass
    
    return {}


def parse_crew_output(result: Any) -> Dict[str, Any]:
    """
    Parse CrewAI output which can be string, dict, or object
    """
    # Handle string results
    if isinstance(result, str):
        parsed = extract_json_from_text(result)
        if parsed:
            return parsed
        # If no JSON found in string, return as is
        return {"raw_output": result}
    
    # Handle dict results
    if isinstance(result, dict):
        return result
    
    # Handle object results
    if hasattr(result, '__dict__'):
        result_dict = result.__dict__
        # Try to convert nested Pydantic models
        parsed = {}
        for key, value in result_dict.items():
            if hasattr(value, 'dict'):
                parsed[key] = value.dict()
            elif isinstance(value, list):
                parsed[key] = [
                    v.dict() if hasattr(v, 'dict') else v
                    for v in value
                ]
            else:
                parsed[key] = value
        return parsed
    
    return {}


def ensure_required_fields(data_dict: dict, required_fields: List[str]) -> bool:
    """Check if dict has required fields"""
    return all(field in data_dict for field in required_fields)


def format_trends_for_prompt(trends_data: Dict[str, List[Dict]]) -> str:
    """
    Format fetched trends data into a readable prompt for the analyst agent
    """
    prompt = "\n## Recent Technology Trends:\n"
    
    # Hacker News
    if trends_data.get('hacker_news'):
        prompt += "\n### Top Stories from Hacker News:\n"
        for story in trends_data['hacker_news'][:10]:
            prompt += f"- {story.get('title', '')} (Score: {story.get('score', 0)}, Comments: {story.get('descendants', 0)})\n"
    
    # Product Hunt
    if trends_data.get('product_hunt'):
        prompt += "\n### Trending Products from Product Hunt:\n"
        for product in trends_data['product_hunt'][:10]:
            prompt += f"- {product.get('title', '')} - {product.get('description', '')}\n"
    
    # GitHub Trending
    if trends_data.get('github_trending'):
        prompt += "\n### Trending Repositories on GitHub:\n"
        for repo in trends_data['github_trending'][:10]:
            prompt += f"- {repo.get('full_name', '')} - {repo.get('description', '')} (⭐ {repo.get('stars', 0)})\n"
    
    return prompt





def run():
    """
    Run the Research & Development agent to identify business opportunities
    """
    print("\n" + "="*60)
    print("  AI Research & Development Agent")
    print("  Identifying Business Opportunities from Tech Trends")
    print("="*60 + "\n")
    
    # Step 1: Fetch trends
    print("📊 Fetching technology trends...")
    trends_data = fetch_all_trends(hn_limit=30, ph_limit=20, gh_limit=25)
    trends_summary = format_trends_for_prompt(trends_data)
    
    print("✓ Trends fetched successfully")
    print(f"  - Hacker News: {len(trends_data.get('hacker_news', []))} stories")
    print(f"  - Product Hunt: {len(trends_data.get('product_hunt', []))} products")
    print(f"  - GitHub: {len(trends_data.get('github_trending', []))} repositories")
    
    # Step 2: Run crew with trend data
    print("\n🤖 Starting Research Crew...")
    
    crew_instance = AiAgentResearchAndDevelop()
    
    inputs = {
        'trends_data': trends_summary,
        'current_date': datetime.now().strftime("%Y-%m-%d"),
    }
    
    try:
        result = crew_instance.crew().kickoff(inputs=inputs)
        print("\n✓ Crew execution completed successfully")
    except Exception as e:
        print(f"\n✗ Error during crew execution: {e}")
        raise
    
    # Step 3: Parse crew output more robustly
    print("\n🔍 Processing crew results...")
    
    crew_output = parse_crew_output(result)
    
    # Extract data - be flexible with field names
    pain_points = crew_output.get('pain_points', [])
    all_ideas = crew_output.get('ideas', [])
    business_models_from_crew = crew_output.get('business_models', [])
    trends_list = crew_output.get('trends', [])
    
    # If no direct fields, try to find them in nested structure
    if not trends_list and 'raw_output' in crew_output:
        raw = crew_output.get('raw_output', '')
        parsed = extract_json_from_text(raw)
        if parsed:
            trends_list = parsed.get('trends', [])
            pain_points = parsed.get('pain_points', [])
    
    # Ensure pain_points are strings (not dicts)
    if pain_points and isinstance(pain_points[0], dict):
        pain_points = [p.get('name', str(p)) if isinstance(p, dict) else str(p) for p in pain_points]
    
    # Convert ideas to Idea objects
    ideas_objects = []
    for idea_dict in all_ideas:
        try:
            if not isinstance(idea_dict, dict):
                continue
            
            # Add missing required fields with defaults
            if 'title' not in idea_dict:
                idea_dict['title'] = idea_dict.get('name', 'Unnamed Idea')
            if 'description' not in idea_dict:
                idea_dict['description'] = idea_dict.get('summary', '')
            if 'target_market' not in idea_dict:
                idea_dict['target_market'] = 'General Market'
            
            # Set default values for numeric fields
            for field in ['feasibility', 'market_need', 'scalability', 'competitive_intensity', 'network_effect']:
                if field not in idea_dict:
                    idea_dict[field] = 5.0
            
            if 'time_to_mvp_months' not in idea_dict:
                idea_dict['time_to_mvp_months'] = 3
            if 'tam_jpy' not in idea_dict:
                idea_dict['tam_jpy'] = 1000000000
            
            # Calculate priority score
            priority = (
                idea_dict.get('feasibility', 5) * 0.25 +
                idea_dict.get('market_need', 5) * 0.35 +
                idea_dict.get('scalability', 5) * 0.25 +
                (10 - idea_dict.get('competitive_intensity', 5)) * 0.15
            )
            idea_dict['priority_score'] = round(min(10, max(1, priority)), 1)
            
            ideas_objects.append(Idea(**idea_dict))
        
        except Exception as e:
            pass  # Silently skip problematic ideas
    
    viable_ideas, filtered_ideas = filter_ideas(ideas_objects)
    
    print(f"\n✓ Filtering Results:")
    print(f"  - Total ideas: {len(ideas_objects)}")
    print(f"  - Viable ideas: {len(viable_ideas)}")
    print(f"  - Filtered out: {len(filtered_ideas)}")
    
    if filtered_ideas:
        for idea in filtered_ideas:
            print(f"    ✗ {idea.title}: {idea.rejection_reason}")
    
    # Step 4: Generate financial models
    print("\n💰 Generating financial analysis...")
    
    business_models_list = []
    for idea in viable_ideas:
        metrics = calculate_business_metrics(
            idea_title=idea.title,
            tam_jpy=idea.tam_jpy,
            market_need=idea.market_need,
            scalability=idea.scalability,
            competitive_intensity=idea.competitive_intensity,
            time_to_mvp_months=idea.time_to_mvp_months,
        )
        
        try:
            model = BusinessModel(
                idea_title=idea.title,
                dev_cost_jpy=metrics['dev_cost_jpy'],
                annual_opex_jpy=metrics['annual_opex_jpy'],
                year1_revenue_estimate_jpy=metrics['year1_revenue_estimate_jpy'],
                year1_arpu_jpy=metrics['year1_arpu_jpy'],
                break_even_months=metrics['break_even_months'],
                roi_percent=metrics['roi_percent'],
                validation_notes=f"Conservative model: {idea.time_to_mvp_months}mo MVP, TAM ¥{idea.tam_jpy:,.0f}",
            )
            business_models_list.append(model)
        except Exception as e:
            pass  # Silently skip problematic models
    
    print(f"✓ Created {len(business_models_list)} financial models")
    
    # Step 5: Generate notebook
    print("\n📓 Generating analysis notebook...")
    
    # Convert models to dicts for notebook
    trends_for_notebook = [
        t.dict() if hasattr(t, 'dict') else t
        for t in trends_list
    ] if isinstance(trends_list, list) else []
    
    ideas_for_notebook = [
        i.dict() if hasattr(i, 'dict') else i
        for i in ideas_objects
    ]
    
    viable_for_notebook = [
        i.dict() if hasattr(i, 'dict') else i
        for i in viable_ideas
    ]
    
    models_for_notebook = [
        m.dict() if hasattr(m, 'dict') else m
        for m in business_models_list
    ]
    
    notebook_path = create_research_notebook(
        trends=trends_for_notebook,
        pain_points=pain_points,
        all_ideas=ideas_for_notebook,
        viable_ideas=viable_for_notebook,
        filtered_ideas=[
            f.dict() if hasattr(f, 'dict') else f
            for f in filtered_ideas
        ],
        business_models=models_for_notebook,
        output_path="research_analysis.ipynb",
    )
    
    print(f"✓ Notebook: {notebook_path}")
    
    # Final summary
    print("\n" + "="*60)
    print("  RESEARCH COMPLETE")
    print("="*60)
    print(f"Trends identified: {len(trends_for_notebook)}")
    print(f"Pain points found: {len(pain_points)}")
    print(f"Business ideas: {len(ideas_objects)}")
    print(f"Viable ideas: {len(viable_ideas)}")
    print(f"Business models: {len(business_models_list)}")
    print(f"\n📄 Output: {notebook_path}")
    print("="*60 + "\n")
    
    return {
        "trends": trends_for_notebook,
        "pain_points": pain_points,
        "ideas": ideas_for_notebook,
        "viable_ideas": viable_for_notebook,
        "business_models": models_for_notebook,
        "notebook_path": notebook_path,
    }




def main():
    """Entry point"""
    try:
        run()
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
