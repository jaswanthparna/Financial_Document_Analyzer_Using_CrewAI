# 📘 Financial Document Analyzer API Documentation

## 🔎 Overview
The **Financial Document Analyzer API** provides **AI-powered analysis of financial documents (PDFs)**, delivering:

- 📊 Financial metrics  
- 💡 Investment recommendations  
- ⚠️ Risk assessments  
- 🌍 Market insights  

The API is built with **FastAPI**, uses **Gemini AI** for intelligence, **Celery + Redis** for asynchronous processing, and **PostgreSQL** for persistent storage.  

---

## 🌐 Base URL
http://localhost:8000

## 🔐 Authentication
> **No authentication required** – all endpoints are publicly accessible.  
(Pluggable auth can be added for production deployments.)

---

## 📡 Endpoints

1️⃣ `GET /`
**Description:** Health check & API information.  

**Response – 200 OK**  
```json
{
  "message": "AI Financial Document Analyzer API",
  "version": "1.0.0",
  "status": "operational",
  "timestamp": "2025-08-31T21:44:00.123456Z"
}

2️⃣ GET /health

Description: System health check for database and AI services.

Response – 200 Healthy

{
  "status": "healthy",
  "database": "connected",
  "ai_service": "available",
  "timestamp": "2025-08-31T21:44:00.123456Z"
}


Response – 200 Unhealthy

{
  "status": "unhealthy",
  "error": "Database connection failed",
  "timestamp": "2025-08-31T21:44:00.123456Z"
}

3️⃣ POST /analyze

Description: Queues a financial document for comprehensive AI analysis (async, Celery).

Parameters:

file (PDF, required) – Financial document

query (string, optional) – Custom analysis query

Default: "Analyze this financial document for investment insights"

Response – 200 OK

{
  "status": "queued",
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Analysis queued for processing",
  "estimated_time": "2-5 minutes"
}


Errors:

400 – Invalid file type

500 – Analysis failure

Example:

curl -X POST "http://localhost:8000/analyze" \
  -F "file=@sample.pdf" \
  -F "query=Analyze for investment insights"

4️⃣ POST /analyze-fast

Description: Performs immediate AI analysis (synchronous).

Parameters: Same as /analyze.

Response – 200 OK

{
  "status": "completed",
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "result": {
    "company_name": "Example Corp",
    "financial_metrics": {
      "revenue": 22496,
      "net_income": 1172,
      "total_assets": 128567,
      "operating_cash_flow": 4567,
      "profit_margin": 17.2,
      "debt_to_equity": null,
      "eps": null
    },
    "investment_recommendations": [
      {
        "action": "buy",
        "asset": "Example Corp stock",
        "rationale": "Strong revenue growth with no significant debt reported.",
        "risk_level": "Low",
        "confidence": 0.85
      }
    ],
    "risk_assessments": [
      {
        "category": "Market Risk",
        "level": "Medium",
        "description": "General market volatility affects all investments",
        "mitigation": "Diversify portfolio"
      }
    ],
    "market_insights": ["Market analysis requires additional data"],
    "summary": "Financial Analysis Summary for Example Corp..."
  },
  "processing_time": "2.34s"
}


Errors:

400 – Invalid file type

500 – Analysis failure

5️⃣ GET /analysis/{task_id}

Description: Retrieves status & results of a queued analysis.

Parameters:

task_id (string, required)

Response – 200 OK

{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "filename": "sample.pdf",
  "query": "Analyze for investment insights",
  "created_at": "2025-08-31T21:44:00.123456Z",
  "completed_at": "2025-08-31T21:46:00.123456Z",
  "result": {...},
  "error_message": null
}


Errors:

404 – Task not found

500 – Server error

6️⃣ GET /analyses

Description: Retrieves recent analysis records.

Parameters:

limit (int, optional) – Number of records (default: 10)

Response – 200 OK

{
  "analyses": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "completed",
      "filename": "sample.pdf",
      ...
    }
  ],
  "total": 1
}

7️⃣ DELETE /analysis/{task_id}

Description: Deletes an analysis record.

Response – 200 OK

{
  "message": "Analysis 123e4567-e89b-12d3-a456-426614174000 deleted successfully"
}


Errors:

404 – Task not found

500 – Server error

8️⃣ GET /stats

Description: Retrieves system statistics.

Response – 200 OK

{
  "total_analyses": 10,
  "completed": 8,
  "failed": 2,
  "success_rate": "80.0%"
}

🚨 Error Codes

400 Bad Request – Invalid input (e.g., non-PDF file)

404 Not Found – Resource not found (invalid task_id)

500 Internal Server Error – Unexpected system failure

🔄 Example Workflow

Queue Analysis

curl -X POST "http://localhost:8000/analyze" \
  -F "file=@sample.pdf" \
  -F "query=Analyze for investment insights"


✅ Response:

{"status": "queued", "task_id": "123e4567-e89b-12d3-a456-426614174000"}


Check Status

curl "http://localhost:8000/analysis/123e4567-e89b-12d3-a456-426614174000"


View Recent Analyses

curl "http://localhost:8000/analyses?limit=5"