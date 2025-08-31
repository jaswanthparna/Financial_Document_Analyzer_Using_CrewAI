from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models.database import AnalysisResult, FinancialMetrics
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    """Database operations for analysis results."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_analysis_record(self, task_id: str, filename: str, query: str) -> AnalysisResult:
        """Create new analysis record."""
        try:
            db_analysis = AnalysisResult(
                task_id=task_id,
                filename=filename,
                query=query,
                status="queued"
            )
            self.db.add(db_analysis)
            self.db.commit()
            self.db.refresh(db_analysis)
            
            logger.info(f"Created analysis record: {task_id}")
            return db_analysis
            
        except Exception as e:
            logger.error(f"Error creating analysis record: {str(e)}")
            self.db.rollback()
            raise

    def update_analysis_result(self, task_id: str, result: dict, status: str = "completed", 
                             processing_time: float = None) -> Optional[AnalysisResult]:
        """Update analysis with results."""
        try:
            db_analysis = self.db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
            if not db_analysis:
                return None

            db_analysis.result = result
            db_analysis.status = status
            db_analysis.completed_at = datetime.utcnow()
            db_analysis.processing_time = processing_time
            
            # Extract company name from result
            if result and isinstance(result, dict):
                company_name = result.get('company_name')
                if company_name:
                    db_analysis.company_name = company_name

            self.db.commit()
            self.db.refresh(db_analysis)

            # Save financial metrics separately
            if status == "completed" and result:
                self._save_financial_metrics(db_analysis.id, task_id, result)

            logger.info(f"Updated analysis result for task_id: {task_id}")
            return db_analysis
            
        except Exception as e:
            logger.error(f"Error updating analysis result: {str(e)}")
            self.db.rollback()
            raise

    def get_analysis_by_task_id(self, task_id: str) -> Optional[AnalysisResult]:
        """Get analysis by task ID."""
        try:
            return self.db.query(AnalysisResult).filter(AnalysisResult.task_id == task_id).first()
        except Exception as e:
            logger.error(f"Error getting analysis by task_id: {str(e)}")
            return None

    def get_recent_analyses(self, limit: int = 10) -> List[AnalysisResult]:
        """Get recent analyses."""
        try:
            return self.db.query(AnalysisResult)\
                .order_by(desc(AnalysisResult.created_at))\
                .limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting recent analyses: {str(e)}")
            return []

    def _save_financial_metrics(self, analysis_id: int, task_id: str, result: dict):
        """Save financial metrics to separate table."""
        try:
            financial_data = result.get('financial_metrics', {})
            if not financial_data:
                return

            company_name = result.get('company_name')
            
            metrics = FinancialMetrics(
                analysis_id=analysis_id,
                task_id=task_id,
                company_name=company_name,
                revenue=financial_data.get('revenue'),
                net_income=financial_data.get('net_income'),
                total_assets=financial_data.get('total_assets'),
                operating_cash_flow=financial_data.get('operating_cash_flow'),
                profit_margin=financial_data.get('profit_margin')
            )
            
            self.db.add(metrics)
            self.db.commit()
            
            logger.info(f"Saved financial metrics for analysis {analysis_id}")
            
        except Exception as e:
            logger.error(f"Error saving financial metrics: {str(e)}")