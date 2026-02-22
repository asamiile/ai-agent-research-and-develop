import json
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Any

from .tools import fetch_all_trends
from .utils import (
    filter_ideas,
    calculate_priority_score,
    calculate_business_metrics,
    create_research_notebook,
)


@CrewBase
class AiAgentResearchAndDevelop():
    """AI Research & Development Agent - Identifies business opportunities from tech trends"""

    agents: List[Agent]
    tasks: List[Task]

    @agent
    def trend_analyst(self) -> Agent:
        """Agent for analyzing technology trends"""
        return Agent(
            config=self.agents_config['trend_analyst'],
            verbose=True,
            tools=[],  # Data fetching done in main.py
        )

    @agent
    def ideation_manager(self) -> Agent:
        """Agent for generating and evaluating business ideas"""
        return Agent(
            config=self.agents_config['ideation_manager'],
            verbose=True,
            tools=[],
        )

    @agent
    def validation_specialist(self) -> Agent:
        """Agent for financial analysis and validation"""
        return Agent(
            config=self.agents_config['validation_specialist'],
            verbose=True,
            tools=[],
        )

    @task
    def trend_extraction_task(self) -> Task:
        """Extract trends and pain points from data"""
        return Task(
            config=self.tasks_config['trend_extraction_task'],
            agent=self.trend_analyst(),
        )

    @task
    def ideation_task(self) -> Task:
        """Generate and evaluate business ideas"""
        return Task(
            config=self.tasks_config['ideation_task'],
            agent=self.ideation_manager(),
            context=[self.trend_extraction_task()],
        )

    @task
    def validation_task(self) -> Task:
        """Validate and analyze business models"""
        return Task(
            config=self.tasks_config['validation_task'],
            agent=self.validation_specialist(),
            context=[self.ideation_task()],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Research & Development crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
