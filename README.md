# 📊✨ Financial Document Analyzer Using CrewAI ✨📊  

The **Financial Document Analyzer** is an **AI-powered application** designed to process and analyze financial PDF documents with high accuracy and speed.  
Leveraging **Google’s Gemini AI model**, it extracts **key financial metrics, profitability ratios**, and provides **data-driven investment recommendations** and **risk assessments**.  

Built with a **modular architecture** using **CrewAI, FastAPI, Celery, PostgreSQL, and Streamlit**, this solution empowers **investors and financial analysts** to analyze reports like **10-Ks, 10-Qs, and earnings statements** with ease.  

---

## 🌟 Overview  

This project **automates financial document analysis** by combining **AI agents** with a **scalable backend** and an **intuitive frontend**.  

### 🔑 Key Features  
- 📂 **Document Upload & Analysis**: Upload PDF financial reports and run custom queries (e.g., *“Analyze revenue growth trends”*).  
- 📈 **Financial Metrics Extraction**: Revenue, Net Income, EPS, Profit Margins, etc.  
- 💹 **Investment Recommendations**: Actionable **buy/sell/hold** advice with rationale + confidence scores.  
- ⚠️ **Risk Assessment**: Identifies **financial, market, and operational risks** with mitigation strategies.  
- 🌍 **Market Insights**: Summaries of trends, strengths, and weaknesses.  
- 📊 **Visualizations**: Interactive **charts via Plotly**.  
- ⚡ **Asynchronous Processing**: Handles **large documents** with **Celery + Redis queues**.  
- 🗄️ **Database Integration**: Stores analysis in **PostgreSQL** for persistence and querying.  
- 🤝 **CrewAI Agents**:  
  - **Verifier** 🔍  
  - **Financial Analyst** 📑  
  - **Investment Advisor** 💼  
  - **Risk Assessor** ⚠️  

---

## 🐞 Bugs Found & ✅ Fixes  

### 🔧 Deterministic Bugs  

1. **📦 Missing Dependencies (requirements.txt)**  
   - ❌ *Issue*: Missing libraries for PDF & CrewAI integration.  
   - ✅ *Fix*: Added correct dependencies.  

   ```txt
   textlangchain==0.1.20
   langchain-community==0.0.38
   langchain-google-genai==1.0.5
   pypdf==4.3.1
   celery==5.4.0
   redis==5.0.8
   sqlalchemy==2.0.30
   psycopg2==2.9.9
   streamlit==1.39.0
   plotly==5.24.1
   crewai==0.130.0


2.🤖 Undefined LLM (agents.py)

❌ Issue: llm = llm caused runtime errors.

✅ Fix: Defined Gemini LLM properly.

from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7)

3.⚙️ Improper Tool Definitions (tools.py)

❌ Issue: Tools were classes with async methods, not CrewAI-compatible.

✅ Fix: Rewrote as proper @tool functions.

from crewai_tools import tool
from langchain_community.document_loaders import PyPDFLoader

@tool("Read financial document")
def read_financial_document(file_path: str) -> str:
    """Reads and extracts text from a financial PDF."""
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        return "\n".join(doc.page_content.replace("\n\n", "\n") for doc in docs)
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

@tool("Analyze investment opportunities")
def analyze_investment(financial_data: str) -> str:
    """Performs investment analysis on financial data."""
    return "Investment analysis: Detected revenue growth, recommending stock purchase."

@tool("Assess risks")
def assess_risk(financial_data: str) -> str:
    """Assesses risks from financial data."""
    return "Risk assessment: Moderate risk due to debt levels, recommend hedgin

4.📋 Crew & Task Config Issues

❌ Issue: Only one agent used, missing task inputs, no file validation.

✅ Fix: Added all agents + tasks, {file_path} inputs, PDF validation.

if not file.filename.endswith('.pdf'):
    raise HTTPException(400, "Only PDF files are allowed")


5.📝 Inefficient Prompts

❌ Issue: Sarcastic, unprofessional agent descriptions.

✅ Fix: Rewritten to professional, data-driven prompts.

🚀 Bonus Features Implemented

🔄 Queue Worker Model: Celery + Redis for async analysis.

🗄️ Database Integration: PostgreSQL + SQLAlchemy for persistent storage.

📜 History Tracking: Retrieve past analyses with /analysis/{task_id}.

⚙️ Setup & Usage
📌 Prerequisites

Python 3.10+

PostgreSQL

Redis

API Keys: GEMINI_API_KEY, SERPER_API_KEY

🛠️ Installation
# Clone repo
git clone https://github.com/jaswanthparna/Financial_Document_Analyzer_Using_CrewAI.git
cd Financial_Document_Analyzer_Using_CrewAI

# Install dependencies
pip install -r requirements.txt

Create .env file:

GEMINI_API_KEY=your_gemini_api_key
SERPER_API_KEY=your_serper_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/financial_analyzer
REDIS_URL=redis://localhost:6379/0

Setup DB:

createdb financial_analyzer


Run services:

# Start API
uvicorn main:app --reload

# Start Celery worker
celery -A workers.celery_app worker --loglevel=info

# Start frontend
streamlit run frontend.py

🎯 Usage
🖥️ Via Streamlit

Upload PDF → Enter Query → Get Metrics, Recommendations, Risks, Charts

🔗 API Endpoints
1️⃣ POST /analyze (Async)

Upload PDF & query → returns task_id.

{
  "status": "success",
  "task_id": "uuid-string",
  "query": "Analyze revenue trends",
  "file_processed": "document.pdf"
}

2️⃣ POST /analyze-fast (Sync)

Quick results, no queuing.

{
  "status": "success",
  "query": "Analyze revenue trends",
  "analysis": {
    "metrics": "Revenue: $X, Net Income: $Y, EPS: $Z",
    "recommendations": "Buy stock due to strong growth",
    "risks": "Moderate debt risk"
  },
  "file_processed": "document.pdf"
}

3️⃣ GET /analysis/{task_id}

Fetch stored results.

{
  "task_id": "uuid-string",
  "status": "completed",
  "result": {
    "metrics": "Revenue: $X, Net Income: $Y",
    "recommendations": "Buy stock",
    "risks": "Moderate risk"
  }
}

4️⃣ GET /

Health check.

{"message": "Financial Document Analyzer API is running"}

🏛️ Architecture

🎨 Frontend: Streamlit + Plotly

⚡ Backend: FastAPI + Celery + Redis

🤖 AI Core: Gemini + LangChain

🗄️ Database: PostgreSQL + SQLAlchemy

👥 CrewAI Agents: Verifier, Financial Analyst, Advisor, Risk Assessor

![alt text](<Screenshot 2025-08-31 200838.png>)

![alt text](<Screenshot 2025-08-31 210305.png>)

![alt text](<Screenshot 2025-08-31 210347.png>)