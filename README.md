Overview:

The AI Financial Document Analyzer is a sophisticated, AI-powered platform designed to revolutionize how investors and analysts process financial documents. Built with cutting-edge AI technologies, this tool automates the extraction of key financial metrics, generates data-driven investment recommendations, and performs comprehensive risk assessments—all from uploaded PDF documents like 10-Ks, 10-Qs, annual reports, and earnings statements.

Whether you're a seasoned financial analyst, an investment advisor, or a curious investor, this application streamlines complex financial analysis, saving hours of manual review while providing actionable insights backed by real-time AI processing. It combines the power of large language models (like Google's Gemini) with a robust backend infrastructure to deliver professional-grade results in minutes.

Key highlights:

AI-Driven Insights: Leverage Gemini AI for intelligent extraction and interpretation of financial data.
Dual Processing Modes: Choose "Fast Analysis" for quick results or "Queued Analysis" for in-depth, comprehensive evaluations.
User-Friendly Interface: A sleek Streamlit frontend makes uploading documents and viewing results intuitive and visual.
Secure and Scalable: Built with enterprise-grade tools like FastAPI, Celery, and PostgreSQL for reliable performance.

This project demonstrates a full-stack AI application, from document ingestion and AI analysis to database storage and interactive visualization—perfect for fintech enthusiasts, developers, or anyone interested in AI's role in finance.

✨ Key Features

Document Upload & Analysis: Upload PDF financial documents and specify custom queries (e.g., "Focus on revenue growth trends").
Financial Metrics Extraction: Automatically pulls key figures like revenue, net income, profit margins, EPS, and more.
Investment Recommendations: AI-generated advice on buy/sell/hold actions, with rationale, confidence scores, and risk levels.
Risk Assessment: Evaluates financial, market, operational, and strategic risks, complete with mitigation strategies.
Market Insights & Summaries: Concise overviews of trends, strengths, weaknesses, and query-specific responses.
Visualization: Interactive charts and metrics displays using Plotly for easy comprehension.
Analysis History: Track recent analyses with status updates and detailed results.
Asynchronous Processing: Handle large documents efficiently with Celery queues.
Database Integration: Stores results in PostgreSQL for persistence and querying.
CrewAI Agents: Modular AI agents (Financial Analyst, Investment Advisor, Risk Assessor) collaborate for multi-faceted analysis.

Architecture

The project follows a modular, microservices-inspired design:

Frontend: Streamlit app for user interaction, file uploads, and result visualization.
Backend: FastAPI API for handling requests, with endpoints for analysis, status checks, and stats.
AI Core: Google Gemini (via google-generativeai) for natural language processing and data extraction from PDFs.
Task Queue: Celery with Redis for asynchronous, queued analyses.
Database: PostgreSQL managed by SQLAlchemy for storing analysis results and metrics.
Tools & Agents: CrewAI framework with custom tools for enhanced document processing, investment analysis, and risk evaluation.
Configuration: YAML files for agents/tasks, .env for secrets, and Pydantic for schema validation.

Data flow: Upload PDF → AI Extraction → Agent Collaboration → Database Storage → Frontend Display.
Technologies Used

AI/ML: Google Gemini (generative AI), CrewAI (multi-agent orchestration)
Backend: FastAPI (API framework), Celery (task queue), Redis (broker)
Database: PostgreSQL with SQLAlchemy (ORM)
Frontend: Streamlit (interactive web app), Plotly & Pandas (data visualization)
Document Processing: PyPDF (PDF reading)
Other: Pydantic (data validation), Logging, UUID (task IDs), dotenv (env management)

Installation

Clone the Repository:
textgit clone https://github.com/yourusername/ai-financial-document-analyzer.git
cd ai-financial-document-analyzer

Set Up Environment:

Install dependencies: pip install -r requirements.txt (ensure you have Python 3.10+).
Create a .env file based on the provided template and add your keys (e.g., GEMINI_API_KEY, DATABASE_URL).


Database Setup:

Install PostgreSQL and create a database (e.g., financial_analyzer).
Update DATABASE_URL in .env.
Run migrations: The app auto-creates tables on startup.


Redis Setup:

Install Redis and ensure it's running on localhost:6379 (or update REDIS_URL).


Start Services:

Backend API: uvicorn main:app --reload (runs on http://localhost:8000).
Celery Worker: celery -A workers.celery_app worker --loglevel=info.
Frontend: streamlit run frontend.py (runs on http://localhost:8501).


Usage

Open the Streamlit app in your browser.
Upload a PDF financial document.
Select an analysis type or enter a custom query.
Choose "Fast Analysis" for quick results or "Queued Analysis" for detailed processing.
View results: Metrics, recommendations, risks, charts, and summaries.
Check history for past analyses.

API Example (for integration):

POST /analyze or /analyze-fast with file and query.

GET /analysis/{task_id} for status/results.

Screenshot:

![alt text](<Screenshot 2025-08-31 200838.png>)

![alt text](<Screenshot 2025-08-31 210305.png>)

![alt text](<Screenshot 2025-08-31 210347.png>)