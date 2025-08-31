from crewai import Crew, Process, Agent, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from tools import search_tool, EnhancedFinancialDocumentTool, EnhancedInvestmentTool, EnhancedRiskTool
import os
import logging
import yaml

load_dotenv()
logger = logging.getLogger(__name__)

# Validate API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Initialize LLM with proper configuration
llm = LLM(
    model="gemini/gemini-1.5-flash",
    google_api_key=api_key,
    temperature=0.1,
    max_tokens=4096
)

@CrewBase
class FinancialCrew:
    """Enhanced Financial Analysis Crew with AI-powered agents."""
    
    def __init__(self):
        # Use absolute paths for configuration files
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.agents_config_path = os.path.join(project_root, 'config', 'agents.yaml')
        self.tasks_config_path = os.path.join(project_root, 'config', 'tasks.yaml')
        
        # Load configurations
        self.agents_config = self._load_config(self.agents_config_path)
        self.tasks_config = self._load_config(self.tasks_config_path)

    def _load_config(self, config_path: str) -> dict:
        """Load YAML configuration file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {str(e)}")
            return {}

    @agent
    def financial_analyst(self) -> Agent:
        """Senior Financial Analyst with AI-enhanced document processing."""
        agent_config = self.agents_config.get('financial_analyst_agent', {})
        
        tools = [EnhancedFinancialDocumentTool(), EnhancedInvestmentTool()]
        if search_tool:
            tools.append(search_tool)
        
        return Agent(
            role=agent_config.get('role', 'Senior Financial Analyst'),
            goal=agent_config.get('goal', 'Analyze financial documents'),
            backstory=agent_config.get('backstory', 'Financial analysis expert'),
            tools=tools,
            llm=llm,
            verbose=True,
            memory=True,
            max_iter=3,
            allow_delegation=False
        )

    @agent
    def document_verifier(self) -> Agent:
        """Document verification specialist."""
        agent_config = self.agents_config.get('document_verifier_agent', {})
        
        return Agent(
            role=agent_config.get('role', 'Document Verification Expert'),
            goal=agent_config.get('goal', 'Verify document authenticity'),
            backstory=agent_config.get('backstory', 'Document verification specialist'),
            tools=[EnhancedFinancialDocumentTool()],
            llm=llm,
            verbose=True,
            max_iter=2,
            allow_delegation=False
        )

    @agent
    def investment_advisor(self) -> Agent:
        """Investment strategy advisor with market intelligence."""
        agent_config = self.agents_config.get('investment_advisor_agent', {})
        
        tools = [EnhancedFinancialDocumentTool(), EnhancedInvestmentTool()]
        if search_tool:
            tools.append(search_tool)
        
        return Agent(
            role=agent_config.get('role', 'Investment Strategist'),
            goal=agent_config.get('goal', 'Provide investment recommendations'),
            backstory=agent_config.get('backstory', 'Investment advisor expert'),
            tools=tools,
            llm=llm,
            verbose=True,
            memory=True,
            max_iter=3,
            allow_delegation=True
        )

    @agent
    def risk_assessor(self) -> Agent:
        """Comprehensive risk analysis specialist."""
        agent_config = self.agents_config.get('risk_assessor_agent', {})
        
        tools = [EnhancedFinancialDocumentTool(), EnhancedRiskTool()]
        if search_tool:
            tools.append(search_tool)
        
        return Agent(
            role=agent_config.get('role', 'Risk Analysis Specialist'),
            goal=agent_config.get('goal', 'Assess investment risks'),
            backstory=agent_config.get('backstory', 'Risk management expert'),
            tools=tools,
            llm=llm,
            verbose=True,
            memory=True,
            max_iter=3,
            allow_delegation=False
        )

    @task
    def verification_task(self) -> Task:
        """Document verification and metadata extraction task."""
        task_config = self.tasks_config.get('verification_task', {})
        
        return Task(
            description=task_config.get('description', 'Verify financial document'),
            expected_output=task_config.get('expected_output', 'Document verification results'),
            agent=self.document_verifier(),
            output_json=True
        )

    @task
    def document_analysis_task(self) -> Task:
        """Comprehensive financial document analysis task."""
        task_config = self.tasks_config.get('analyze_financial_document_task', {})
        
        return Task(
            description=task_config.get('description', 'Analyze financial document'),
            expected_output=task_config.get('expected_output', 'Financial analysis results'),
            agent=self.financial_analyst(),
            context=[self.verification_task()],
            output_json=True
        )

    @task
    def investment_analysis_task(self) -> Task:
        """Investment recommendation generation task."""
        task_config = self.tasks_config.get('investment_analysis_task', {})
        
        return Task(
            description=task_config.get('description', 'Generate investment recommendations'),
            expected_output=task_config.get('expected_output', 'Investment recommendations'),
            agent=self.investment_advisor(),
            context=[self.document_analysis_task()],
            output_json=True
        )

    @task
    def risk_assessment_task(self) -> Task:
        """Comprehensive risk assessment task."""
        task_config = self.tasks_config.get('risk_assessment_task', {})
        
        return Task(
            description=task_config.get('description', 'Assess investment risks'),
            expected_output=task_config.get('expected_output', 'Risk assessment results'),
            agent=self.risk_assessor(),
            context=[self.document_analysis_task()],
            output_json=True
        )

    @crew
    def financial_crew(self) -> Crew:
        """Create the enhanced financial analysis crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=10,
            memory=True,
            embedder={
                "provider": "google",
                "config": {
                    "api_key": api_key,
                    "model": "models/embedding-001"
                }
            }
        )