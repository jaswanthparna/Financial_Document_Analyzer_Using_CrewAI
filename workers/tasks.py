from celery import shared_task
from models.database import SessionLocal
from services.analysis_service import FinancialAnalysisService
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def analyze_financial_document_task(self, task_id: str, file_path: str, query: str, filename: str):
    """Celery task for financial document analysis."""
    db = SessionLocal()
    start_time = datetime.now()
    
    try:
        logger.info(f"Starting analysis for task {task_id}")
        
        # Update progress
        self.update_state(state='PROGRESS', meta={
            'current': 20, 
            'total': 100, 
            'status': 'Reading document...'
        })
        
        # Verify file exists
        if not os.path.exists(file_path):
            raise Exception(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Update progress
        self.update_state(state='PROGRESS', meta={
            'current': 40, 
            'total': 100, 
            'status': 'Analyzing with AI...'
        })
        
        # Perform analysis
        analysis_service = FinancialAnalysisService()
        result = analysis_service.analyze_document(file_content, filename, query)
        
        # Update progress
        self.update_state(state='PROGRESS', meta={
            'current': 80, 
            'total': 100, 
            'status': 'Saving results...'
        })
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Update database
        from models.database import AnalysisResult
        analysis = db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
        if analysis:
            analysis.result = result
            analysis.status = "completed"
            analysis.completed_at = datetime.utcnow()
            analysis.processing_time = processing_time
            analysis.company_name = result.get('company_name')
            db.commit()
        
        # Update progress
        self.update_state(state='SUCCESS', meta={
            'current': 100, 
            'total': 100, 
            'status': 'Analysis completed!'
        })
        
        return {
            'task_id': task_id,
            'status': 'completed',
            'result': result,
            'processing_time': processing_time
        }

    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        logger.error(error_msg)
        
        # Update database with error
        try:
            from models.database import AnalysisResult
            analysis = db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.error_message = error_msg
                analysis.completed_at = datetime.utcnow()
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to save error to database: {str(db_error)}")

        raise Exception(error_msg)

    finally:
        db.close()
        # Clean up file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up file: {str(cleanup_error)}")