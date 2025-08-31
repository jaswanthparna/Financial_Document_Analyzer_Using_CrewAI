from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import uuid
import logging
from datetime import datetime
from models.database import get_db, create_tables, AnalysisResult
from workers.celery_app import celery_app
from workers.tasks import analyze_financial_document_task
from services.analysis_service import FinancialAnalysisService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Initialize database
create_tables()

# Initialize FastAPI
app = FastAPI(
    title="AI Financial Document Analyzer",
    version="1.0.0",
    description="AI-powered financial document analysis with investment insights"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """API health check."""
    return {
        "message": "AI Financial Document Analyzer API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """System health check."""
    try:
        # Test database
        db = next(get_db())
        db.execute("SELECT 1")
        db.close()
        
        # Test AI service
        analysis_service = FinancialAnalysisService()
        
        return {
            "status": "healthy",
            "database": "connected",
            "ai_service": "available",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)
):
    """Upload and analyze financial document (queued processing)."""
    task_id = str(uuid.uuid4())
    
    try:
        # Validate file
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Save uploaded file
        content = await file.read()
        file_path = os.path.join("data", f"doc_{task_id}.pdf")
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create database record
        db_analysis = AnalysisResult(
            task_id=task_id,
            filename=file.filename,
            query=query.strip(),
            status="queued"
        )
        db.add(db_analysis)
        db.commit()
        
        # Queue analysis task
        task = analyze_financial_document_task.delay(
            task_id=task_id,
            file_path=file_path,
            query=query.strip(),
            filename=file.filename
        )
        
        logger.info(f"Analysis queued - Task ID: {task_id}")
        
        return {
            "status": "queued",
            "task_id": task_id,
            "message": "Analysis queued for processing",
            "estimated_time": "2-5 minutes"
        }

    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-fast")
async def analyze_fast(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)
):
    """Fast analysis with immediate results."""
    task_id = str(uuid.uuid4())
    
    try:
        # Validate file
        if not file.filename or not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        content = await file.read()
        
        # Create database record
        db_analysis = AnalysisResult(
            task_id=task_id,
            filename=file.filename,
            query=query.strip(),
            status="processing"
        )
        db.add(db_analysis)
        db.commit()
        
        # Perform immediate analysis
        start_time = datetime.now()
        analysis_service = FinancialAnalysisService()
        result = analysis_service.analyze_document(content, file.filename, query.strip())
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Update database
        db_analysis.result = result
        db_analysis.status = "completed"
        db_analysis.completed_at = datetime.utcnow()
        db_analysis.processing_time = processing_time
        db_analysis.company_name = result.get('company_name')
        db.commit()
        
        return {
            "status": "completed",
            "task_id": task_id,
            "result": result,
            "processing_time": f"{processing_time:.2f}s"
        }

    except Exception as e:
        # Update database with error
        db_analysis.status = "failed"
        db_analysis.error_message = str(e)
        db_analysis.completed_at = datetime.utcnow()
        db.commit()
        
        logger.error(f"Fast analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()

@app.get("/analysis/{task_id}")
async def get_analysis_status(task_id: str, db: Session = Depends(get_db)):
    """Get analysis status and results."""
    try:
        analysis = db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        response = analysis.to_dict()

        # Get Celery task status for queued/processing tasks
        if analysis.status in ['queued', 'processing']:
            try:
                celery_task = celery_app.AsyncResult(task_id)
                response["celery_status"] = celery_task.status
                
                if celery_task.status == "PROGRESS" and isinstance(celery_task.info, dict):
                    response["progress"] = celery_task.info
                    
            except Exception as e:
                logger.warning(f"Could not get Celery status: {str(e)}")

        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses")
async def get_recent_analyses(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent analyses."""
    try:
        analyses = db.query(AnalysisResult)\
            .order_by(AnalysisResult.created_at.desc())\
            .limit(limit).all()
        
        return {
            "analyses": [analysis.to_dict() for analysis in analyses],
            "total": len(analyses)
        }
        
    except Exception as e:
        logger.error(f"Error getting analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/analysis/{task_id}")
async def delete_analysis(task_id: str, db: Session = Depends(get_db)):
    """Delete an analysis record."""
    try:
        analysis = db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        db.delete(analysis)
        db.commit()
        
        return {"message": f"Analysis {task_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics."""
    try:
        total = db.query(AnalysisResult).count()
        completed = db.query(AnalysisResult).filter(AnalysisResult.status == "completed").count()
        failed = db.query(AnalysisResult).filter(AnalysisResult.status == "failed").count()
        
        return {
            "total_analyses": total,
            "completed": completed,
            "failed": failed,
            "success_rate": f"{(completed/total*100):.1f}%" if total > 0 else "0%"
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Financial Document Analyzer API")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)