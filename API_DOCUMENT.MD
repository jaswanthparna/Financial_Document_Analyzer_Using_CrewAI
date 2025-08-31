Financial Document Analyzer API Documentation
Overview
The Financial Document Analyzer API provides AI-powered analysis of financial documents (PDFs), delivering financial metrics, investment recommendations, risk assessments, and market insights. Built with FastAPI, it supports both immediate and queued analysis using Gemini AI, Celery, and PostgreSQL.
Base URL
http://localhost:8000
Authentication
No authentication is currently required. All endpoints are publicly accessible.
Endpoints
GET /
Description: Health check and API information.Response:  

200 OK: API status and version information.

{
  "message": "AI Financial Document Analyzer API",
  "version": "1.0.0",
  "status": "operational",
  "timestamp": "2025-08-31T21:44:00.123456Z"
}

GET /health
Description: System health check for database and AI services.Response:  

200 OK: Health status of services.

{
  "status": "healthy",
  "database": "connected",
  "ai_service": "available",
  "timestamp": "2025-08-31T21:44:00.123456Z"
}


200 Unhealthy: If services are unavailable.

{
  "status": "unhealthy",
  "error": "Database connection failed",
  "timestamp": "2025-08-31T21:44:00.123456Z"
}

POST /analyze
Description: Queues a financial document for comprehensive AI analysis using Celery.Parameters:  

file (file, required): PDF financial document.  
query (string, optional): Analysis query (default: "Analyze this financial document for investment insights").Response:  
200 OK: Task queued successfully.

{
  "status": "queued",
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Analysis queued for processing",
  "estimated_time": "2-5 minutes"
}


400 Bad Request: Invalid file type.  
500 Internal Server Error: Analysis failure.

Example:  
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@sample.pdf" \
  -F "query=Analyze for investment insights"

POST /analyze-fast
Description: Performs immediate financial document analysis (synchronous).Parameters: Same as /analyze.Response:  

200 OK: Analysis results.

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


400 Bad Request: Invalid file type.  
500 Internal Server Error: Analysis failure.

GET /analysis/{task_id}
Description: Retrieves the status and results of a queued analysis.Parameters:  

task_id (string, required): Unique task identifier.Response:  
200 OK: Analysis status and results (if completed).

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


404 Not Found: Analysis not found.  
500 Internal Server Error: Server error.

GET /analyses
Description: Retrieves recent analysis records (default: last 10).Parameters:  

limit (integer, optional): Number of records to return (default: 10).Response:  
200 OK: List of recent analyses.

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


500 Internal Server Error: Server error.

DELETE /analysis/{task_id}
Description: Deletes an analysis record.Parameters:  

task_id (string, required): Unique task identifier.Response:  
200 OK: Deletion confirmation.

{
  "message": "Analysis 123e4567-e89b-12d3-a456-426614174000 deleted successfully"
}


404 Not Found: Analysis not found.  
500 Internal Server Error: Server error.

GET /stats
Description: Retrieves system statistics (e.g., total analyses, success rate).Response:  

200 OK: System statistics.

{
  "total_analyses": 10,
  "completed": 8,
  "failed": 2,
  "success_rate": "80.0%"
}


500 Internal Server Error: Server error.

Error Codes

400 Bad Request: Invalid input (e.g., non-PDF file).  
404 Not Found: Resource not found (e.g., invalid task_id).  
500 Internal Server Error: Unexpected server error.

Example Workflow

Queue Analysis:  
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@sample.pdf" \
  -F "query=Analyze for investment insights"

Response: {"status": "queued", "task_id": "123e4567-e89b-12d3-a456-426614174000", ...}

Check Status:  
curl "http://localhost:8000/analysis/123e4567-e89b-12d3-a456-426614174000"

Response: {"status": "completed", "result": {...}, ...}

View Recent Analyses:  
curl "http://localhost:8000/analyses?limit=5"



Notes

The API uses Celery for asynchronous processing (/analyze) and supports immediate analysis (/analyze-fast).  
Ensure Redis, PostgreSQL, and API keys (GEMINI_API_KEY, SERPER_API_KEY) are configured in .env.  
Access interactive documentation at /docs (FastAPI Swagger UI).
