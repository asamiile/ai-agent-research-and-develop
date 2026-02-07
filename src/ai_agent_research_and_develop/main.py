#!/usr/bin/env python
"""
Main entry point for AI Research & Development Agent
Fetches technology trends and generates business opportunities with financial analysis
"""
import sys
import warnings
import json
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

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


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


def process_ideas_with_filtering(crew_obj: AiAgentResearchAndDevelop, ideas_raw: Any) -> Tuple[List[Idea], List[Idea]]:
    """
    Process and filter ideas from crew output
    """
    ideas = []
    
    # Extract ideas from crew output
    if hasattr(ideas_raw, 'ideas'):
        ideas_list = ideas_raw.ideas
    elif isinstance(ideas_raw, dict) and 'ideas' in ideas_raw:
        ideas_list = ideas_raw['ideas']
    else:
        ideas_list = []
    
    # Convert to Idea objects
    for idea_dict in ideas_list:
        if isinstance(idea_dict, dict):
            # Calculate priority score
            priority = (
                idea_dict.get('feasibility', 5) * 0.25 +
                idea_dict.get('market_need', 5) * 0.35 +
                idea_dict.get('scalability', 5) * 0.25 +
                (10 - idea_dict.get('competitive_intensity', 5)) * 0.15
            )
            idea_dict['priority_score'] = round(min(10, max(1, priority)), 1)
            
            try:
                ideas.append(Idea(**idea_dict))
            except Exception as e:
                print(f"Warning: Failed to create Idea object: {e}")
                continue
    
    # Filter ideas
    viable, filtered = filter_ideas(ideas)
    
    print(f"\n✓ Filtering Results:")
    print(f"  - Total ideas: {len(ideas)}")
    print(f"  - Viable ideas: {len(viable)}")
    print(f"  - Filtered out: {len(filtered)}")
    
    if filtered:
        print(f"\n  Filtered ideas:")
        for idea in filtered:
            print(f"    - {idea.title}: {idea.rejection_reason}")
    
    return viable, filtered


def process_business_models(validation_output: Any, viable_ideas: List[Idea]) -> List[BusinessModel]:
    """
    Create BusinessModel objects from validation task output
    """
    business_models = []
    
    # Extract models from validation output
    if hasattr(validation_output, 'business_models'):
        models_list = validation_output.business_models
    elif isinstance(validation_output, dict) and 'business_models' in validation_output:
        models_list = validation_output['business_models']
    else:
        models_list = []
    
    # Convert to BusinessModel objects
    for model_dict in models_list:
        if isinstance(model_dict, dict):
            try:
                # Ensure all required fields are present
                if 'validation_notes' not in model_dict:
                    model_dict['validation_notes'] = "Model passed validation."
                
                business_models.append(BusinessModel(**model_dict))
            except Exception as e:
                print(f"Warning: Failed to create BusinessModel object: {e}")
                continue
    
    # If validation didn't produce enough models, create them from viable ideas
    if len(business_models) < len(viable_ideas):
        for idea in viable_ideas:
            if not any(m.idea_title == idea.title for m in business_models):
                # Generate metrics
                metrics = calculate_business_metrics(
                    idea_title=idea.title,
                    tam_jpy=idea.tam_jpy,
                    market_need=idea.market_need,
                    scalability=idea.scalability,
                    competitive_intensity=idea.competitive_intensity,
                    time_to_mvp_months=idea.time_to_mvp_months,
                )
                
                model = BusinessModel(
                    idea_title=idea.title,
                    dev_cost_jpy=metrics['dev_cost_jpy'],
                    annual_opex_jpy=metrics['annual_opex_jpy'],
                    year1_revenue_estimate_jpy=metrics['year1_revenue_estimate_jpy'],
                    year1_arpu_jpy=metrics['year1_arpu_jpy'],
                    break_even_months=metrics['break_even_months'],
                    roi_percent=metrics['roi_percent'],
                    validation_notes=f"Based on viable idea '{idea.title}' with {idea.time_to_mvp_months} months to MVP.",
                )
                business_models.append(model)
    
    return business_models


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
    
    # Step 3: Process results through filtering
    print("\n🔍 Processing and filtering ideas...")
    
    # Extract components from result
    if hasattr(result, '__dict__'):
        result_dict = result.__dict__
    else:
        result_dict = result if isinstance(result, dict) else {}
    
    # Get trends from first task
    trends_output = None
    ideas_output = None
    validation_output = None
    
    # Parse results (CrewAI may return dict or object)
    if isinstance(result, str):
        try:
            result = json.loads(result)
        except:
            print("Note: Could not parse crew output as JSON")
    
    # Extract outputs intelligently
    pain_points = []
    all_ideas = []
    trends_list = []
    
    if isinstance(result, dict):
        trends_list = result.get('trends', [])
        pain_points = result.get('pain_points', [])
        all_ideas = result.get('ideas', [])
        business_models = result.get('business_models', [])
    
    # Convert to Idea objects for filtering
    ideas_objects = []
    for idea_dict in all_ideas:
        if isinstance(idea_dict, dict):
            priority = (
                idea_dict.get('feasibility', 5) * 0.25 +
                idea_dict.get('market_need', 5) * 0.35 +
                idea_dict.get('scalability', 5) * 0.25 +
                (10 - idea_dict.get('competitive_intensity', 5)) * 0.15
            )
            idea_dict['priority_score'] = round(min(10, max(1, priority)), 1)
            
            try:
                ideas_objects.append(Idea(**idea_dict))
            except Exception as e:
                print(f"  Warning: Could not create idea object: {e}")
    
    viable_ideas, filtered_ideas = filter_ideas(ideas_objects)
    
    print(f"✓ Filtering Results:")
    print(f"  - Total ideas: {len(ideas_objects)}")
    print(f"  - Viable ideas: {len(viable_ideas)}")
    print(f"  - Filtered out: {len(filtered_ideas)}")
    
    # Step 4: Generate financial models for viable ideas
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
                validation_notes=f"Conservative financial model for {idea.time_to_mvp_months}-month MVP timeline.",
            )
            business_models_list.append(model)
        except Exception as e:
            print(f"  Warning: Failed to create business model: {e}")
    
    print(f"✓ Created {len(business_models_list)} financial models")
    
    # Step 5: Generate notebook
    print("\n📓 Generating analysis notebook...")
    
    notebook_path = create_research_notebook(
        trends=[t.dict() if hasattr(t, 'dict') else t for t in trends_list],
        pain_points=pain_points,
        all_ideas=[i.dict() if hasattr(i, 'dict') else i for i in ideas_objects],
        viable_ideas=[i.dict() if hasattr(i, 'dict') else i for i in viable_ideas],
        filtered_ideas=[i.dict() if hasattr(i, 'dict') else i for i in filtered_ideas],
        business_models=[m.dict() if hasattr(m, 'dict') else m for m in business_models_list],
        output_path="research_analysis.ipynb",
    )
    
    print(f"✓ Notebook generated: {notebook_path}")
    
    # Final summary
    print("\n" + "="*60)
    print("  RESEARCH COMPLETE")
    print("="*60)
    print(f"Trends identified: {len(trends_list)}")
    print(f"Pain points found: {len(pain_points)}")
    print(f"Business ideas generated: {len(ideas_objects)}")
    print(f"Ideas passing viability filter: {len(viable_ideas)}")
    print(f"Business models validated: {len(business_models_list)}")
    print(f"\n📄 Output: {notebook_path}")
    print("="*60 + "\n")
    
    return {
        "trends": trends_list,
        "pain_points": pain_points,
        "ideas": all_ideas,
        "viable_ideas": [i.dict() if hasattr(i, 'dict') else i for i in viable_ideas],
        "business_models": [m.dict() if hasattr(m, 'dict') else m for m in business_models_list],
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
